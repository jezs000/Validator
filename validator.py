import logging
import re
from pathlib import Path

import pandas as pd
import yaml

from dateutil.parser import parse
from schwifty import IBAN

from business_rules.rule_engine import apply_rules
from business_rules.helpers import is_empty


def is_valid_date(value):
    try:
        parse(str(value), dayfirst=True)
        return True
    except Exception:
        return False


def is_valid_amount(value):
    s = str(value).strip().replace(" ", "")

    if "," in s and "." not in s:
        s = s.replace(",", ".")

    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")

    try:
        return float(s) > 0
    except Exception:
        return False


def is_valid_currency(value, valid_currencies):
    return str(value).strip().upper() in valid_currencies


def is_valid_dic(value):
    if is_empty(value):
        return False
    value = str(value).strip().upper()
    return bool(re.fullmatch(r"CZ\d{8,10}", value))


def is_valid_iban(value):
    try:
        return IBAN(str(value).replace(" ", "")).is_valid
    except Exception:
        return False


def is_valid_ico(value):
    if is_empty(value):
        return False

    value = str(value).strip()

    if not re.fullmatch(r"\d{8}", value):
        return False

    digits = [int(x) for x in value]

    checksum = (
        digits[0] * 8 +
        digits[1] * 7 +
        digits[2] * 6 +
        digits[3] * 5 +
        digits[4] * 4 +
        digits[5] * 3 +
        digits[6] * 2
    )

    mod = checksum % 11

    if mod == 0:
        expected = 1
    elif mod == 1:
        expected = 0
    else:
        expected = 11 - mod

    return expected == digits[7]



def validate_row(row, df_columns, required_columns, valid_currencies, custom_rules):
    errors = []

    # Required fields
    for col in required_columns:
        if is_empty(row[col]):
            errors.append(f"Missing: {col}")

    # Issue Date
    if "Issue Date" in required_columns:
        if not is_valid_date(row["Issue Date"]):
            errors.append("Invalid Issue Date")

    # ICO starting with zero
    if "Vendor Company ID" in required_columns:
        ico = str(row["Vendor Company ID"]).strip()
        if ico.startswith("0"):
            errors.append("ICO starts with zero – may be truncated in target system")

    # ICO checksum
    if "Vendor Company ID" in required_columns:
        if not is_valid_ico(row["Vendor Company ID"]):
            errors.append("Invalid ICO")

    # DIC
    if "Vendor VAT Number" in required_columns and "Vendor VAT Number" in df_columns:
        if not pd.isna(row["Vendor VAT Number"]):
            if not is_valid_dic(row["Vendor VAT Number"]):
                errors.append("Invalid DIC")

    # Amount
    if "Total Amount" in required_columns:
        if not is_valid_amount(row["Total Amount"]):
            errors.append("Invalid Amount")

    # Currency
    if "Currency" in required_columns:
        if not is_valid_currency(row["Currency"], valid_currencies):
            errors.append("Invalid Currency")

    # IBAN
    if "IBAN" in required_columns and "IBAN" in df_columns:
        if not pd.isna(row["IBAN"]):
            if not is_valid_iban(row["IBAN"]):
                errors.append("Invalid IBAN")

    # Description length
    if "Description" in df_columns:
        if len(str(row["Description"])) > 255:
            errors.append("Description too long (max 255 chars)")

    # VAT looks like ICO
    if "Vendor VAT Number" in df_columns:
        vat = str(row["Vendor VAT Number"]).strip()
        if re.fullmatch(r"\d{8}", vat):
            errors.append("VAT Number looks like ICO – possible field swap")

    # Apply custom business rules
    if custom_rules:
        rule_errors = apply_rules(row, custom_rules)
        errors.extend(rule_errors)

    # Rozdělit chyby na ERROR a WARNING
    hard_errors = [e for e in errors if not e.startswith("Warning:")]
    status = "ERROR" if hard_errors else "VALID"

    return status, "; ".join(errors)



def validate_dataframe(df, required_columns, valid_currencies, custom_rules):
    statuses = []
    errors = []
    filled_due_dates = []

    if "Validation Errors" not in df.columns:
        df["Validation Errors"] = ""

    # Detect duplicates
    if all(col in df.columns for col in ["Vendor Company ID", "Total Amount", "Issue Date"]):
        dupes = df.duplicated(subset=["Vendor Company ID", "Total Amount", "Issue Date"], keep=False)
        df.loc[dupes, "Validation Errors"] += "; Potential duplicate invoice"

    for idx, row in df.iterrows():

        # Auto-fill Due Date
        if "Due Date" in required_columns:
            if is_empty(row["Due Date"]) and not is_empty(row["Issue Date"]):
                df.at[idx, "Due Date"] = row["Issue Date"]
                filled_due_dates.append(idx)

        status, err = validate_row(row, df.columns, required_columns, valid_currencies, custom_rules)
        statuses.append(status)
        errors.append(err)

    df["Validation Status"] = statuses
    df["Validation Errors"] = errors

    return df, filled_due_dates


def validate_file(
    input_path: str,
    output_dir: str,
    config_path: str = "config.yaml",
    required_columns_override=None,
    custom_rules_text=None
):

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required_columns = (
        required_columns_override
        if required_columns_override
        else config["required_columns"]
    )

    valid_currencies = config["valid_currencies"]
    salesforce_mapping = config["salesforce_mapping"]

    # Parse custom rules
    from business_rules.parser import load_local_rules, parse_custom_rules

    local_rules_text = load_local_rules()
    local_rules = parse_custom_rules(local_rules_text)

    ui_rules = parse_custom_rules(custom_rules_text) if custom_rules_text else []

    custom_rules = local_rules + ui_rules

    # Prepare output
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    valid_csv = output_dir / "salesforce_import.csv"
    error_xlsx = output_dir / "invoice_errors.xlsx"
    due_filled_xlsx = output_dir / "due_date_filled.xlsx"

    # Load input Excel
    df = pd.read_excel(input_path)

    if "Currency" in df.columns:
        df["Currency"] = df["Currency"].astype(str).str.strip().str.upper()

    # Check missing columns
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    # Validate rows
    df, filled_due_dates = validate_dataframe(df, required_columns, valid_currencies, custom_rules)

    # Split valid/error
    valid_df = df[df["Validation Status"] == "VALID"].copy()
    error_df = df[df["Validation Status"] == "ERROR"].copy()

    # Map Salesforce columns
    valid_df = valid_df.rename(columns=salesforce_mapping)
    valid_df.drop(columns=["Validation Status", "Validation Errors"], errors="ignore", inplace=True)

    # Save CSV
    valid_df.to_csv(valid_csv, index=False, encoding="utf-8-sig")

    # Save error Excel
    error_df.to_excel(error_xlsx, index=False)

    # Save Due Date auto-filled rows
    if filled_due_dates:
        df.loc[filled_due_dates].to_excel(due_filled_xlsx, index=False)
        due_filled_path = str(due_filled_xlsx)
    else:
        due_filled_path = None

    return {
        "total_rows": len(df),
        "valid_rows": len(valid_df),
        "error_rows": len(error_df),
        "valid_csv": str(valid_csv),
        "error_xlsx": str(error_xlsx),
        "due_date_filled": due_filled_path,
        "errors_dataframe": error_df
    }
