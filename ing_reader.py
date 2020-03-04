import csv
import json
from os import listdir
from bullet import Bullet, Input 
import os
from tabulate import tabulate
from shutil import copyfile
from tqdm import tqdm



class ING_Transaction:
    def __init__(self, timestamp, type, incoming ,outgoing, id):
        self.id = id
        self.timestamp = self._toDate(timestamp)
        self.type = type
        self.incoming = incoming
        self.outgoing = outgoing
        self.meta = dict()
        self.category = 'unknown'
        self.party = 'unknown'
        if self.type == 'Suma transferata din linia de credit':
            self.party = 'ExtraROL'
            self.category = 'credit_line'
        elif self.type == 'Retragere numerar':
            self.party = "ATM"
            self.category = 'cash'
        elif self.type == "Schimb valutar Home'Bank":
            self.party = "Home'Bank"
            self.category = 'schimb_valutar'
        elif self.type == "Realimentare Extra'ROL Home'Bank":
            self.party = 'ExtraROL'
            self.category = 'credit_line'
        elif self.type == "Alimentare Card Credit Home'Bank":
            self.party = 'CreditCard'
            self.category = 'credit_cards'
        elif self.type == 'Rata Credit':
            self.party = 'ExtraROL'
            self.category = 'credit_line'
    def add_meta(self, name, value):
        self.meta.update({name: value})
        if name in ['Terminal', 'Ordonator', 'Beneficiar']:
            self.party = self.meta[name]
        if name in ['In contul', 'Din contul']:
            self.party = self.party + " " + self.meta[name]

    def set_category(self, category):
        self.category = category
        
    def __str__(self):
        return ("{}: {}, {}, {}, {}, {}, {}".format(self.id, self.timestamp, self.type, self.incoming, self.outgoing, self.party, self.category))
    
    def asList(self):
        return (self.id, self.timestamp, self.type, self.incoming, self.outgoing, self.party, self.category)
    def get_meta(self, name='ALL'):
        if name == 'ALL':
            return self.meta
        else:
            return self.meta[name]
    def _toDate(self,timestamp):
        months = {
            'ianuarie':1,
            'februarie':2,
            'martie':3,
            'aprilie':4,
            'mai':5,
            'iunie':6,
            'iulie':7,
            'august':8,
            'septembrie':9,
            'octombrie':10,
            'noiembrie':11,
            'decembrie':12
        }
        date = timestamp.split(" ")
        return "{}/{}/{}".format(date[0], months[date[1]], date[2])
        
    

class ING_Reader:
    def __init__(self, fileName):
        self.fileName = fileName
        self.transactions = []
        with open(fileName, newline='') as csvfile:
            csv_lines = csv.reader(csvfile, delimiter=',', quotechar='"')
            new_transaction = None
            for row in csv_lines:
                if row[0] != '':
                    #New transaction:
                    try:
                        if row[5] != '':
                        ## Cumparare
                            incoming = 0
                            outgoing = float(row[5].replace('.','').replace(',','.'))
                        elif row[7] !='':
                            incoming = float(row[7].replace('.','').replace(',','.'))
                            outgoing = 0
                        else:
                            raise ValueError('No ammount!')
                        new_transaction = ING_Transaction(row[0], row[2], incoming, outgoing, len(self.transactions)+1)
                        self.transactions.append(new_transaction)
                        
                        
                    except Exception as e:
                        pass
                else:
                    if ":" in row[2]:
                        (name,value) = row[2].split(':')
                        new_transaction.add_meta(name, value)
                    
            
        
    def getTransactions(self):
        return self.transactions
    
    def save(self):
        with open("compact_" + self.fileName, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for t in self.transactions:
                writer.writerow(t.asList())
    
    
class ParticipantsOperator:
    def __init__(self, filename):
        self.participants_dict = {}
        self.filename = filename
        copyfile(filename, filename+".bkp")
        with open(filename) as csvfile:
            lines = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in lines:
                self.participants_dict.update({row[0]:row[1]})
    
    def get_participants(self):
        return self.participants_dict
    
    def get_categories(self):
        return set(self.participants_dict.values())
    
    def add_participant(self, participant, category):
        self.participants_dict.update({participant:category})
        
    def save(self):
        with open(self.filename, 'w+') as csvfile:
            writer = csv.writer(csvfile)
            for (k,v) in sorted(self.participants_dict.items(), key = lambda x: x[1]):
                writer.writerow([k,v])
            

class Analytics:
    def __init__(self, transactions):
        self.transactions = transactions
        
    def get_SumByCategory(self, category='_any_'):
        totals = {
            '_any_': {'in':0, 'out':0}
        }
        for t in self.transactions:
            if t.category in totals:
                totals[t.category]['in'] = totals[t.category]['in'] + t.incoming
                totals[t.category]['out'] = totals[t.category]['out'] + t.outgoing
            else:
                totals[t.category] = {'in':t.incoming, 'out':t.outgoing}
            totals['_any_']['in'] = totals['_any_']['in'] + t.incoming
            totals['_any_']['out'] = totals['_any_']['out'] + t.outgoing
        return totals
        

class ING_FileCompactor:
    def __init__(self, fileName):
        self.ing_reader = ING_Reader(fileName)
        operator = ParticipantsOperator('categories.csv')
        participants = operator.get_participants()
        for transaction in self.ing_reader.getTransactions():
            if transaction.category == 'unknown':
                if transaction.party in participants:
                    transaction.set_category(participants[transaction.party])
                else:
                    print(transaction)
                    #print(transaction.get_meta())
                    choices = list(operator.get_categories())
                    choices.append('NEW*')
                    if os.name == 'nt':
                        category = None
                        while category not in choices:
                            if category is not None:
                                print ("Incorrect Category! Use NEW* to add a new category!")
                            category = input("Set category [{}]:".format(sorted(choices)))
                            if category == 'NEW*':
                                category = input("Set new category: ")
                                break
                    else:
                        cli = Bullet(prompt = "Choose category: ", choices = sorted(choices))   # Create a Bullet or Check object
                        category = cli.launch()  # Launch a prompt
                        if category == 'NEW*':
                            new_cli = Input(prompt = "Add new category: " )  # Create a Bullet or Check object
                            category = new_cli.launch()  # Launch a prompt
                    transaction.set_category(category)
                    operator.add_participant(transaction.party, category)
            operator.save()
        self.ing_reader.save()
     
    def get_analysis(self):
        analysis = Analytics(self.ing_reader.getTransactions())
        return analysis.get_SumByCategory()

if __name__ == '__main__':
    suffix = '.csv'
    prefix = 'ING Bank - Extras de cont'
    filenames = listdir('.')
    totals = dict()
    files_list = []
    print ('Parsing files')
    for f in tqdm([ filename for filename in filenames if filename.endswith( suffix ) and filename.startswith(prefix) ]):
        files_list.append(f)
        file_analysis = ING_FileCompactor(f).get_analysis()
        for category in file_analysis:
            if category in totals:
                totals[category]['in'] = totals[category]['in'] + file_analysis[category]['in']
                totals[category]['out'] = totals[category]['out'] + file_analysis[category]['out']
            else:
                totals[category] = {
                    'in':  file_analysis[category]['in'],
                    'out': file_analysis[category]['out']
                }
    rows = []
    headers = [
        'category', 
        'incoming',
        'outgoing', 
        'diff', 
        'avg_in[{}]'.format(len(files_list)), 
        'avg_out[{}]'.format(len(files_list)), 
        'avg_diff[{}]'.format(len(files_list)), 
        'percent_in', 
        'percent_out',
        ]
    floatfmt = ['0', '.2f', '.2f', '.2f', '.2f', '.2f', '.2f', '.2%' , '.2%', ]
    add_line = False
    for key, value in sorted(totals.items(), key = lambda e: e[1]['out']-e[1]['in']  , reverse = True):
        if key not in ['_any_']:
            rows.append([
                key,
                totals[key]['in'],
                totals[key]['out'], 
                totals[key]['in'] - totals[key]['out'],
                totals[key]['in']/len(files_list), 
                totals[key]['out']/len(files_list), 
                totals[key]['in']/len(files_list) - totals[key]['out']/len(files_list), 
                totals[key]['in']/totals['_any_']['in'], 
                totals[key]['out']/totals['_any_']['out'],
                ] )
    rows.append(['-------'])
    rows.append([
        'Total', 
        totals['_any_']['in'], 
        totals['_any_']['out'],
        totals['_any_']['in'] - totals['_any_']['out'],  
        totals['_any_']['in']/len(files_list), 
        totals['_any_']['out']/len(files_list), 
        totals['_any_']['in']/len(files_list) - totals['_any_']['out']/len(files_list), 
        totals['_any_']['in']/totals['_any_']['in'], 
        totals['_any_']['out']/totals['_any_']['out']
        ])
    
    print (tabulate(rows, headers = headers, floatfmt=floatfmt))
    output_file_name = 'summary.txt'
    copyfile(output_file_name, output_file_name+".bkp")
    with open(output_file_name, 'w+') as output_file:
        output_file.write(tabulate(rows, headers = headers, floatfmt=floatfmt))
        
        output_file.write('\n\n\nFiles included:\n')
        for f in files_list:
            output_file.write(f + '\n')

            