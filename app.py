import streamlit as st
import tempfile
from pathlib import Path
import pandas as pd
from validator import validate_file
import yaml
import zipfile
import os
from business_rules.parser import load_local_rules, save_local_rules, clear_local_rules


IS_LOCAL = "CODESPACES" not in os.environ
custom_rules_text = None
st.set_page_config(page_title="Invoice Validator", layout="wide")
st.title("OCR Invoice Validator")

uploaded_file = st.file_uploader("Nahraj OCR export", type=["xlsx"])


if uploaded_file:

    df_preview = pd.read_excel(uploaded_file)
    all_columns = list(df_preview.columns)

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    default_required = config["required_columns"]

    st.subheader("Vyber povinné sloupce")
    selected_required = st.multiselect(
        "Povinné sloupce",
        options=all_columns,
        default=[c for c in default_required if c in all_columns]
    )

    if st.button("Spustit validaci"):

        with st.spinner("Probíhá validace..."):

            temp_dir = tempfile.mkdtemp()
            input_file = Path(temp_dir) / uploaded_file.name

            with open(input_file, "wb") as f:
                f.write(uploaded_file.getbuffer())

            result = validate_file(
                input_path=str(input_file),
                output_dir=temp_dir,
                required_columns_override=selected_required,
                custom_rules_text=custom_rules_text if IS_LOCAL else None
            )

        st.success("Hotovo")

        col1, col2, col3 = st.columns(3)
        col1.metric("Celkem", result["total_rows"])
        col2.metric("Validní", result["valid_rows"])
        col3.metric("Chybné", result["error_rows"])

        with open(result["valid_csv"], "rb") as f:
            st.download_button(
                "Stáhnout Salesforce CSV",
                data=f,
                file_name="salesforce_import.csv",
                mime="text/csv",
                key="download_salesforce"
            )

        with open(result["error_xlsx"], "rb") as f:
            st.download_button(
                "Stáhnout Error Excel",
                data=f,
                file_name="invoice_errors.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_errors"
            )

        if result.get("due_date_filled"):
            with open(result["due_date_filled"], "rb") as f:
                st.download_button(
                    "Stáhnout log doplněných splatností",
                    data=f,
                    file_name="due_date_filled.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_due_log"
                )

        zip_path = Path(temp_dir) / "validator_output.zip"

        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(result["valid_csv"], arcname="salesforce_import.csv")
            zipf.write(result["error_xlsx"], arcname="invoice_errors.xlsx")
            if result.get("due_date_filled"):
                zipf.write(result["due_date_filled"], arcname="due_date_filled.xlsx")

        with open(zip_path, "rb") as f:
            st.download_button(
                "Stáhnout vše (ZIP)",
                data=f,
                file_name="validator_output.zip",
                mime="application/zip",
                key="download_zip"
            )


if IS_LOCAL:
    st.subheader("Vlastní business rules")

    if "rules_open" not in st.session_state:
        st.session_state.rules_open = False

    if st.button("Spravovat vlastní pravidla"):
        st.session_state.rules_open = not st.session_state.rules_open

    if st.session_state.rules_open:
        st.info("Pravidla se ukládají pouze lokálně. Validátor je načítá automaticky.")

        existing_rules = load_local_rules()

        new_rules = st.text_area(
            "Upravit pravidla:",
            value=existing_rules,
            height=200
        )

        colA, colB = st.columns(2)

        if colA.button("💾 Uložit pravidla"):
            save_local_rules(new_rules)
            st.success("Pravidla byla uložena.")

        if colB.button("🗑️ Smazat všechna pravidla"):
            clear_local_rules()
            st.warning("Všechna pravidla byla smazána.")


        st.markdown("""
        ### 📘 Jak psát vlastní business rules

        Vlastní pravidla používají jednoduchý jazyk ve stylu:

        ```
        IF <sloupec> <operátor> <hodnota> THEN <ERROR|WARNING> "zpráva"
        ```

        #### ✨ Podporované operátory
        - `==` … rovná se  
        - `!=` … nerovná se  
        - `<` a `>` … porovnání čísel  
        - `IN [A, B, C]` … hodnota je v seznamu  
        - `NOT IN [A, B, C]` … hodnota není v seznamu  
        - `IS EMPTY` … prázdná hodnota  
        - `IS NOT EMPTY` … neprázdná hodnota  

        #### 🧠 Příklady pravidel
        ```
        IF Vendor Name == Buyer Name THEN ERROR "Dodavatel a odběratel jsou stejní"
        IF Total Amount < 0 THEN ERROR "Částka nesmí být záporná"
        IF Currency NOT IN ["CZK", "EUR", "USD"] THEN WARNING "Neobvyklá měna"
        IF Description IS EMPTY THEN WARNING "Chybí popis"
        ```

        #### 💾 Ukládání pravidel
        - klikni na **Uložit pravidla**  
        - pravidla se uloží do `business_rules/local_rules.txt`  
        - validátor je bude automaticky používat při každé validaci  

        #### 🗑️ Mazání pravidel
        - klikni na **Smazat všechna pravidla**  
        - soubor se vyprázdní  
        - validátor přestane pravidla používat  

        ---
        """)

        custom_rules_text = new_rules

else:
    st.subheader("Vlastní business rules")
    st.info("Pro přidání vlastních pravidel stáhněte aplikaci.")

