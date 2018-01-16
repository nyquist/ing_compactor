"""Converste un extras de cont in format CSV de la ING Bank
in unul mai compact si mai usor de folosit"""

import os
import re
import locale
from datetime import date
import csv

locale.setlocale(locale.LC_ALL, 'ro')


def parse_chunk(lines):
    """parseaza mai multe linii intr-o singura linie compacta"""
    data_tip_pattern = re.compile(r'^([0-9]{2}) (ianuarie|februarie|martie|aprilie|mai|iunie|iulie|august|septembrie|octombrie|noiembrie|decembrie) ([0-9]{4}),,([^,]+),+"([0-9.,]+)",')
    #suma_pattern = re.compile (r',"([0-9,]+)"')
    beneficiar_pattern = re.compile(r',,Beneficiar:([^,]+),')
    pos_pattern = re.compile(r',,Terminal:([^,]+),')
    ordonator_pattern = re.compile(r',,Ordonator:([^,]+),')

    dc = "debit"
    suma = 0
    cine = ""
    detalii = []

    for line in lines:
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
        else:
            detalii.append(line.replace(",,", "").replace("\"", "").replace("\n", "|"))
    if dc == "credit":
        suma = -suma
    return (data.strftime(DATE_FORMAT), tip, suma, dc, cine, "".join(detalii))


def parse_file(file_name):
    """parseaza un fisier pentru a gasi chunk-uri"""
    next_line_pattern = re.compile(r'^,,')
    #first_line_pattern = re.compile(r'^,Data,,Detalii tranzactie,,,Debit,,Credit')
    new_chunk_pattern = re.compile(r'^[0-9]+')
    sold_initial_pattern = re.compile(r'^Sold initial:,,"([0-9\.]+)"')
    sold_final_pattern = re.compile(r'Sold final ,,"[0-9\.]+"')

    file = open(file_name, mode='r')
    chunk = []
    newlines = []
    for line in file:
        if re.search(next_line_pattern, line):
            chunk.append(line)
        elif re.search(new_chunk_pattern, line):
            if len(chunk) > 0:
                newlines.append(parse_chunk(chunk))
                #print (parse_chunk(chunk))
            chunk = []
            chunk.append(line)

        elif re.search(sold_initial_pattern, line):
            if len(chunk) > 0:
                newlines.append(parse_chunk(chunk))
                return newlines
                #print (parse_chunk(chunk))
                #TODO ce fac cu sold initial?
        elif re.search(sold_final_pattern, line):
            #TODO ce fac cu sold final?
            return newlines
    #TODO final. Mai e necesar?
    return newlines




DATE_FORMAT = "%d-%m-%Y"
JOIN_CHAR = ""
SORTABLE_FILES = False
SUFIX = "_compact"
# PATTERNS

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
for file in file_list:
    match = re.search(FILE_PATTERN, file)
    (luna, an, iban, moneda) = match.groups()
    print("Parsing file for:", luna, an, iban, moneda)
    new_file = "ING Bank - Extras de cont "
    if SORTABLE_FILES:
        new_file += an+"_"+format(LUNI[luna], '02d')
    else:
        new_file += luna + "_" + an
    new_file += "_" + iban + "_" + moneda + SUFIX +".csv"
    with open(new_file, 'w', newline='') as out:
        csv_out = csv.writer(out, delimiter=';')
        csv_out.writerow(['data', 'tip', 'suma', 'debit/credit', 'cine', 'detalii'])
        csv_out.writerows(parse_file(file))
