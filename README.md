# ing_compactor

Converteste extrasele de cont de la ING Bank in fisiere csv compacte, cu cate o tranzactie pe linie pentru a usura analiza lor.

## Cum functioneaza
Scriptul va procesa toate fisierle csv din directorul curent care pastreaza numele in formatul original: *ING Bank - Extras de cont LUNA_AN_IBAN_MONEDA.CSV*

Scriptul va genera cate un fisier nou cu numele ING Bank - *Extras de cont LUNA_AN_IBAN_MONEDA_compact.CSV* precum si un fisier care contine toate tranzactiile din toate fisiere cu numele *ING Bank - Extras de cont - All in one.csv*

Toate debitarile apar cu valoare negativa iar toate creditarile apar cu valoare pozitiva

Fisierele generate vor contine cate o tranzactie pe linie, in formatul:

iban|data|tip|suma|debit/credit|cine|detalii

## Setari
```python
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
```