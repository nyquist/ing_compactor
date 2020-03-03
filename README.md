# ing_compactor

Converteste extrasele de cont de la ING Bank in fisiere csv compacte, cu cate o tranzactie pe linie pentru a usura analiza lor.
Face si cateva statistici legate de felul in care s-au cheltuit banii.

## Cum functioneaza
Scriptul va procesa toate fisierle csv din directorul curent care pastreaza numele in formatul original: *ING Bank - Extras de cont[].csv*
Scriptul va genera cate un fisier nou cu prefixul "compact_" care va contine cate o linie pentru fiecare tranzactie.
Scriptul va intreba carei categorii sa asocieze fiecare creditor/debitor identificat intr-o tranzactie.
Scriptul va genera si cateva statistici pe care le va afisa pe ecran si in fisierul summary.txt

## Pentru a instala librariile necesare:
`pip3 install -r requirements.txt`

## Pentru a rula:
`python3 ing_reader.py`

