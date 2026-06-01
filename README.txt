OCR Invoice Validator
Přehled
OCR Invoice Validator je jednoduchá webová aplikace postavená nad Python validační vrstvou pro kontrolu dat extrahovaných z OCR faktur před jejich importem do Salesforce.
Aplikace umožňuje uživateli nahrát Excel export z OCR systému, automaticky provést sadu validačních kontrol a vrátit:
čistý CSV soubor připravený pro Salesforce Data Loader
Excel soubor obsahující chybné záznamy se zvýrazněnými chybami
souhrn validace přímo v uživatelském rozhraní

Hlavní funkcionalita
Nahrání OCR exportu
Uživatel nahraje soubor:
.xlsx
obsahující data získaná z OCR systému.

Povinná pole:
Invoice Number
Issue Date
Due Date
Vendor Name
Vendor Company ID
Total Amount

Currency

Konfigurace povinných polí je definována v:
config.yaml


Výstupy
Salesforce Import CSV
Soubor:
salesforce_import.csv
Obsahuje pouze validní řádky.

Před exportem probíhá:
odstranění validačních sloupců
přemapování názvů sloupců na Salesforce API názvy

Například:
OCR Pole	Salesforce Pole
Invoice Number	Invoice_Number__c
Issue Date	Issue_Date__c
Vendor Company ID	Vendor_ICO__c
Total Amount	Amount__c

Error Excel soubor:
invoice_errors.xlsx

Obsahuje:
pouze chybné řádky
validační status
seznam nalezených chyb
červené zvýraznění řádků s chybami

Příklad:
Invoice Number	Validation Errors
2026-001	Missing Due Date
2026-002	Invalid ICO
2026-003	Invalid Currency

Uživatelské rozhraní
Aplikace využívá Streamlit.

Workflow uživatele:
1. Nahraj Excel soubor
2. Klikni na "Spustit validaci"
3. Zobrazí se výsledky
4. Stáhni Salesforce CSV
5. Stáhni Error Excel
Struktura projektu

invoice-validator/
│
├── app.py
├── validator.py
├── config.yaml
├── requirements.txt
│
├── input/
│
├── output/
│
└── logs/

Konfigurace
Veškerá obchodní pravidla jsou uložena v:
config.yaml

Příklad:
YAML

required_columns:
  - Invoice Number
  - Issue Date
  - Due Date

valid_currencies:
  - CZK
  - EUR
  - USD

salesforce_mapping:
  Invoice Number: Invoice_Number__c
  Issue Date: Issue_Date__c
Díky tomu lze většinu změn provádět bez úprav zdrojového kódu.



Instalace
Instalace závislostí
Bash

pip install -r requirements.txt

Spuštění aplikace
Bash
streamlit run app.py
Po spuštění bude aplikace dostupná na:
http://localhost:8501

Použité technologie
Python 3.11+
Streamlit
Pandas
OpenPyXL
PyYAML
Python-DateUtil
Schwifty

