import csv
import json
import collections
from os import listdir
from bullet import Bullet, Input 
import os



class ING_Transaction:
    def __init__(self, timestamp, type, ammount, id):
        self.id = id
        self.timestamp = self._toDate(timestamp)
        self.type = type
        self.ammount = ammount
        self.meta = dict()
        self.category = 'unknown'
        self.party = 'unknown'
        if self.type == 'Suma transferata din linia de credit':
            self.party = 'ExtraROL'
            self.category = 'credit_line'
        elif self.type == 'Retragere numerar':
            self.category = 'cash'
        elif self.type == "Realimentare Extra'ROL Home'Bank":
            self.party = 'ExtraROL'
            self.category = 'credit'
        elif self.type == "Alimentare Card Credit Home'Bank":
            self.party = 'CreditCard'
            self.category = 'credit'
        elif self.type == 'Rata Credit':
            self.party = 'ExtraROL'
            self.category = 'credit'
    def add_meta(self, name, value):
        self.meta.update({name: value})
        if name in ['Terminal', 'Ordonator', 'Beneficiar']:
            self.party = self.meta[name]
        if name in ['In contul']:
            self.party = self.party + " " + self.meta[name]

    def set_category(self, category):
        self.category = category
        
    def __str__(self):
        return ("{}: {}, {}, {}, {}, {}".format(self.id, self.timestamp, self.type, self.ammount, self.party, self.category))
    
    def asList(self):
        return (self.id, self.timestamp, self.type, self.ammount, self.party, self.category)
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
                            ammount = -float(row[5].replace('.','').replace(',','.'))
                        elif row[7] !='':
                            ammount = float(row[7].replace('.','').replace(',','.'))
                        else:
                            raise ('No ammount!')
                        new_transaction = ING_Transaction(row[0], row[2], ammount, len(self.transactions)+1)
                        self.transactions.append(new_transaction)
                        
                        
                    except Exception as e:
                        #print (e)
                        pass
                else:
                    try:
                        (name,value) = row[2].split(':')
                        
                        new_transaction.add_meta(name, value)
                    except Exception as e:
                        #print (e)
                        pass
                    
            
        
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
        with open(self.filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for (k,v) in sorted(self.participants_dict.items()):
                writer.writerow([k,v])
            

class Analytics:
    def __init__(self, transactions):
        self.transactions = transactions
    
    def get_Sum(self, type='_total_'):
        # type = _all_, in, out
        valid_params = ['_total_', '_in_', '_out_']
        if type not in valid_params:
            raise ("Wrong parameter for type. {} in {}".format(type, valid_params))
        total = 0
        for t in self.transactions:
            if type == '_out_':
                total = total + min (0, t.ammount)
            elif type == '_in_':
                total = total + max (0, t.ammount)
            else:
                total = total + t.ammount
        return total
    def get_SumByCategory(self, category='_total_'):
        total = dict()
        total['_total_'] = 0
        total['_in_'] = 0
        total['_out_'] = 0
        for t in self.transactions:
            if t.category in total:
                total[t.category] = total[t.category] + t.ammount
            else:
                total[t.category] = t.ammount
            if t.ammount >= 0:
                total['_in_'] = total['_in_'] + t.ammount
            else:
                total['_out_'] = total['_out_'] + t.ammount
            total['_total_'] = total['_total_'] + t.ammount
        return total
        
    def get_All(self):
        total_in = self.get_Sum(type = '_in_')
        total_out = self.get_Sum(type = '_out_')
        print ("Total: IN:{:.2f}, OUT:{:.2f}, DIFF:{:.2f} ".format(total_in, total_out, self.get_Sum()))
        ####
        categories = self.get_SumByCategory()
        
        for key, value in sorted(categories.items(), key=lambda item: item[1]):
            if value < 0:
                total = total_out
            else:
                total = total_in
            percentage = 100*value/total
            if key != '_total_':
                print("{} {:10.2f} {:5.2f}% of {:10.2f} ".format(key.ljust(10), value, percentage, total))

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
                    choices.append('NEW')
                    if os.name == 'nt':
                        category = input("Set category [{}]:".format(operator.get_categories()))
                    else:
                        cli = Bullet(prompt = "Choose from the items below: ", choices = sorted(choices))   # Create a Bullet or Check object
                        category = cli.launch()  # Launch a prompt
                        if category == 'NEW':
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
    files_count = 0
    for f in [ filename for filename in filenames if filename.endswith( suffix ) and filename.startswith(prefix) ]:
        print(f)
        files_count = files_count + 1
        analysis = ING_FileCompactor(f).get_analysis()
        for key in analysis:
            if key in totals:
                totals[key] = totals[key] + analysis[key]
            else:
                totals[key] = analysis[key]
    rows = []
    rows.append(['category', 'ammount', 'percentage', 'total', 'average'])
    print("{:15} {:15}, {:6} of {:10} {} ".format('category', 'ammount', 'percentage', 'total', 'average' ))
    print("------------------------"*3)
    add_line = False
    for key, value in sorted(totals.items(), key=lambda item: item[1]):
        if value < 0:
            total = totals['_out_']
        else:
            total = totals['_in_']
        percentage = 100*value/total
        if value > 0 and add_line is False:
                print("------------------------"*3)
                add_line = True
        if key not in ['_total_']:
            rows.append([key, "{:.2f}".format(value), "{:.2f}%".format(percentage), "{:.2f}".format(total), "{:.2f}".format(value/files_count)])
            print("{:15} {:15,.2f}, {:6.2f}% of {:10,.2f}. {:,.2f} ".format(key.ljust(10), value, percentage, total, value/files_count ))
    print("------------------------"*3)
    rows.append(['_total_', "{:.2f}".format(totals['_total_']), '-', '-', "{:.2f}".format(value/files_count)])
    print("{:15} {:15,.2f}, {:6} of {:10} {:,.2f} ".format('_total_'.ljust(10), totals['_total_'], '-', '-', totals['_total_']/files_count ))
    with open('summary.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for item in rows:
            writer.writerow(item)
    

            