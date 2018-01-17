"""Converteste un extras de cont in format CSV de la ING Bank
in unul mai compact si mai usor de folosit"""

import os
import re
import locale
from datetime import date
import csv

locale.setlocale(locale.LC_ALL, 'ro')


def parse_chunk(chunk):
    """proceseaza mai multe linii (un chunk) intr-o singura linie compacta"""
    data_tip_pattern = re.compile(r'^([0-9]{2}) (ianuarie|februarie|martie|aprilie|mai|iunie|iulie|august|septembrie|octombrie|noiembrie|decembrie) ([0-9]{4}),+([^,]+),+"([0-9.,]+)",')
    data_pattern = re.compile(r'^([0-9]{2})/([0-9]{2})/([0-9]{4}),+"([0-9.,]+)",')
    #suma_pattern = re.compile (r',"([0-9,]+)"')
    beneficiar_pattern = re.compile(r',,Beneficiar:([^,]+),')
    pos_pattern = re.compile(r',{2,3}Terminal:([^,]+),')
    ordonator_pattern = re.compile(r',{2,3}Ordonator:([^,]+),')

    dc = "debit"
    suma = 0
    cine = ""
    detalii = []
    tip_is_next = False

    for line in chunk:
        if re.match(data_tip_pattern, line):
            match = re.search(data_tip_pattern, line)
            (zi, luna, an, tip, suma_txt) = match.groups()
            suma = -locale.atof(suma_txt)
            data = date(locale.atoi(an), LUNI[luna], locale.atoi(zi))
            if tip == "Suma transferata din linia de credit":
                dc = "credit"
        elif re.match(beneficiar_pattern, line):
            match = re.search(beneficiar_pattern, line)
            cine = match.group(1)
            #dc = "debit"
        elif re.match(pos_pattern, line):
            match = re.search(pos_pattern, line)
            cine = match.group(1)
            #dc = "debit"
        elif re.match(ordonator_pattern, line):
            match = re.search(ordonator_pattern, line)
            cine = match.group(1)
            dc = "credit"
        elif re.match(data_pattern, line):
            match = re.search(data_pattern, line)
            (zi, luna, an, suma_txt) = match.groups()
            suma = -locale.atof(suma_txt)
            data = date(locale.atoi(an), locale.atoi(luna), locale.atoi(zi))
            tip_is_next = True
        else:
            if tip_is_next:
                tip = re.search(re.compile(r'^,,,([^,]+),'), line).group(1)
                tip_is_next = False
            else:
                detalii.append(line.replace(",,,", "").replace(",,", "").replace("\"", "").replace("\n", ""))
                #TODO De curatat detaliile mai bine
    if dc == "credit":
        suma = -suma
    if VERBOSE:
        print(data.strftime(DATE_FORMAT), suma)
    return (iban, data.strftime(DATE_FORMAT), tip, suma, dc, cine, JOIN_CHAR.join(detalii))


def parse_lines(lines):
    """Cauta chunk-uri pentru a le transofrma intr-o singura linie"""
    next_line_pattern = re.compile(r'^,{2,3}')
    new_chunk_pattern = re.compile(r'^[0-9]+')
    chunk = []
    newlines = []
    for line in lines:
        if re.search(next_line_pattern, line):
            chunk.append(line)
        elif re.search(new_chunk_pattern, line):
            if chunk:
                newlines.append(parse_chunk(chunk))
            chunk = []
            chunk.append(line)
    if chunk:
        newlines.append(parse_chunk(chunk))
    return newlines


def parse_file(file_name):
    """Determina liniile utile si le trimite spre procesare"""
    start_debit_pattern = re.compile(r'^,Data,+Detalii tranzactie,+Debit,+Credit')
    start_credit_pattern = re.compile(r'^Data,+Descriere,+Sume iesite din cont,+Sume intrate in cont,')
    start_credit2_pattern = re.compile(r'^,Data,+Detalii tranzactie,+Debit,+Credit')
    end_debit_pattern = re.compile(r'^Sold initial:')
    end_credit_pattern = re.compile(r'^TOTAL')
    end_credit2_pattern = re.compile(r'^,+INFO PLANURI DE RATE,+')
    file = open(file_name, mode='r')
    started = False
    lines = []
    newlines = []
    for line in file:
        if (re.search(start_debit_pattern, line) or re.search(start_credit_pattern, line) or re.search(start_credit2_pattern, line)):
            started = True
        elif (re.search(end_debit_pattern, line) or re.search(end_credit_pattern, line) or re.search(end_credit2_pattern, line)):
            newlines = parse_lines(lines)
        elif started:
            lines.append(line)
    return newlines


### START CONFIG ###
# Formatul zilelor:
DATE_FORMAT = "%d-%m-%Y"
# Cum se concateneaza detaliile:
JOIN_CHAR = "|"
# False: Fisierle de iesire doar adauga un sufix la fisierul de intrare
# True: Fisierle de iesire sunt redenumite cu luna in format numeric
SORTABLE_FILES = False
# Sufixul fisierelor de iesire:
SUFIX = "_compact"
# Genereaza si fisierul cu toate tranzactiile?
ALL_IN_ONE = True
# Printeaza mai multe detalii
VERBOSE = False
### END CONFIG ###

FILE_PATTERN = re.compile(r'Extras de cont ([a-z]+)_([0-9]{4})_(RO\d{2}INGB[a-zA-Z0-9]{1,16})_([A-Z]+).CSV')

LUNI = {
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
file_list = []
for file in os.listdir("./"):
    if re.search(FILE_PATTERN, file):
        file_list.append(file)
if ALL_IN_ONE:
    all_in_one_file = "ING Bank - Extras de cont - All in one.csv"
    out_all = open(all_in_one_file, 'w', newline='')
    csv_out_all = csv.writer(out_all, delimiter=';')
    csv_out_all.writerow(['iban', 'data', 'tip', 'suma', 'debit/credit', 'cine', 'detalii'])
for file in file_list:
    match = re.search(FILE_PATTERN, file)
    (luna, an, iban, moneda) = match.groups()
    print("Proceseaza fisirul:", luna, an, iban, moneda)
    new_file = "ING Bank - Extras de cont "
    if SORTABLE_FILES:
        new_file += an+"_"+format(LUNI[luna], '02d')
    else:
        new_file += luna + "_" + an
    new_file += "_" + iban + "_" + moneda + SUFIX +".csv"
    with open(new_file, 'w', newline='') as out:
        csv_out = csv.writer(out, delimiter=';')
        csv_out.writerow(['iban', 'data', 'tip', 'suma', 'debit/credit', 'cine', 'detalii'])
        lines = parse_file(file)
        print ("..Tranzactii:", len(lines))
        csv_out.writerows(lines)
        if ALL_IN_ONE:
            csv_out_all.writerows(lines)

