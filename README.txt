OCR Invoice Validator

## Spustit aplikaci jedním klikem
Klikněte zde pro otevření projektu v GitHub Codespaces:

[**Spustit v GitHub Codespaces**](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=jezs000%2FValidator)
Po otevření Codespace se aplikace spustí automaticky.
Stačí kliknout na tlačítko „Open in Browser“ u portu 8501.
Celé spouštění trvá přibližně 2 minuty.


Přehled
OCR Invoice Validator je webová aplikace umožňující ověřovat data extrahovaná z OCR faktur před importem do Salesforce.

Aplikace umožňuje:
nahrát Excel export z OCR systému
zvolit, které sloupce mají být povinné
provést automatickou validaci dat

stáhnout:
CSV soubor připravený pro Salesforce
Excel se záznamy obsahujícími chyby
Aplikace běží nad Python validační vrstvou a uživatelským rozhraním ve Streamlitu.

Hlavní funkcionalita
Nahrání OCR exportu
Uživatel nahraje soubor:
.xlsx
obsahující data z OCR systému

Výběr povinných sloupců
Uživatel může:
vybrat libovolné sloupce, které mají být povinné
pokud nevybere žádné, použijí se výchozí hodnoty z config.yaml

Validace dat
Validator kontroluje:
prázdné hodnoty v povinných sloupcích
formát dat (datum, částka, měna)
strukturu IČO, DIČ, IBAN
další pravidla definovaná v validator.py

Výstupy

Salesforce Import CSV
Soubor salesforce_import.csv obsahuje:
pouze validní řádky
přemapované názvy sloupců podle salesforce_mapping
odstraněné validační sloupce

Error Excel
Soubor invoice_errors.xlsx obsahuje:
pouze chybné řádky
popis nalezených chyb

Uživatelské rozhraní
Aplikace využívá Streamlit.
Workflow
Nahrát Excel soubor
Vybrat povinné sloupce
Spustit validaci
Zobrazit výsledky
Stáhnout CSV pro Salesforce
Stáhnout Excel s chybami

Struktura projektu
invoice-validator/
│
├── app.py
├── validator.py
├── config.yaml
├── requirements.txt
│
├── input/
├── output/
└── logs/

Konfigurace
Veškerá obchodní pravidla jsou uložena v config.yaml.

Příklad konfigurace
yaml
required_columns:
  - Invoice Number
  - Issue Date
  - Due Date
  - Vendor Name
  - Vendor Company ID
  - Total Amount
  - Currency

valid_currencies:
  - CZK
  - EUR
  - USD

salesforce_mapping:
  Invoice Number: Invoice_Number__c
  Issue Date: Issue_Date__c
  Vendor Company ID: Vendor_ICO__c
  Total Amount: Amount__c
Uživatel může tato pravidla přepsat přímo ve Streamlitu výběrem sloupců.

Instalace
Instalace závislostí
pip install -r requirements.txt

Spuštění aplikace
streamlit run app.py

Aplikace bude dostupná na:
http://localhost:8501

Použité technologie
Python 3.11+
Streamlit
Pandas
OpenPyXL
PyYAML
Python-DateUtil
Schwifty