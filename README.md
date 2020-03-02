# ing_compactor

Converteste extrasele de cont de la ING Bank in fisiere csv compacte, cu cate o tranzactie pe linie pentru a usura analiza lor.
Face si cateva statistici legate de felul in care s-au cheltuit banii.

## Cum functioneaza
Scriptul va procesa toate fisierle csv din directorul curent care pastreaza numele in formatul original: *ING Bank - Extras de cont LUNA_AN_IBAN_MONEDA.CSV*
Scriptul va genera cate un fisier nou cu prefixul "compact_" care va contine categoriile 
Toate debitarile apar cu valoare negativa iar toate creditarile apar cu valoare pozitiva

