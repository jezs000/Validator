import logging
import re
from pathlib import Path

import pandas as pd
import yaml

from dateutil.parser import parse
from schwifty import IBAN




def is_empty(value):
    return pd.isna(value) or str(value).strip() == ""


def is_valid_date(value):
    try:
        parse(str(value), dayfirst=True)
        return True
    except Exception:
        return False


def is_valid_amount(value):
    try:
        return float(value) > 0
    except Exception:
        return False


def is_valid_currency(value, valid_currencies):
    return str(value).upper().strip() in valid_currencies


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

def validate_row(row, df_columns, required_columns, valid_currencies):
    errors = []

    # Required fields
    for col in required_columns:
        if is_empty(row[col]):
            errors.append(f"Missing: {col}")

    # Field-specific validation ONLY if column is required
    if "Issue Date" in required_columns:
        if not is_valid_date(row["Issue Date"]):
            errors.append("Invalid Issue Date")

    if "Due Date" in required_columns:
        if not is_valid_date(row["Due Date"]):
            errors.append("Invalid Due Date")

    if "Vendor Company ID" in required_columns:
        if not is_valid_ico(row["Vendor Company ID"]):
            errors.append("Invalid ICO")

    if "Vendor VAT Number" in required_columns and "Vendor VAT Number" in df_columns:
        if not pd.isna(row["Vendor VAT Number"]):
            if not is_valid_dic(row["Vendor VAT Number"]):
                errors.append("Invalid DIC")

    if "Total Amount" in required_columns:
        if not is_valid_amount(row["Total Amount"]):
            errors.append("Invalid Amount")

    if "Currency" in required_columns:
        if not is_valid_currency(row["Currency"], valid_currencies):
            errors.append("Invalid Currency")

    if "IBAN" in required_columns and "IBAN" in df_columns:
        if not pd.isna(row["IBAN"]):
            if not is_valid_iban(row["IBAN"]):
                errors.append("Invalid IBAN")

    status = "ERROR" if errors else "VALID"
    return status, "; ".join(errors)

def validate_dataframe(df, required_columns, valid_currencies):
    statuses = []
    errors = []

    for _, row in df.iterrows():
        status, err = validate_row(row, df.columns, required_columns, valid_currencies)
        statuses.append(status)
        errors.append(err)

    df["Validation Status"] = statuses
    df["Validation Errors"] = errors

    return df



def validate_file(
    input_path: str,
    output_dir: str,
    config_path: str = "config.yaml",
    required_columns_override=None
):


    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if required_columns_override is not None and len(required_columns_override) > 0:
        required_columns = required_columns_override
    else:
        required_columns = config["required_columns"]

    valid_currencies = config["valid_currencies"]
    salesforce_mapping = config["salesforce_mapping"]

    # Prepare output
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    valid_csv = output_dir / "salesforce_import.csv"
    error_xlsx = output_dir / "invoice_errors.xlsx"

    # Load input Excel
    df = pd.read_excel(input_path)

    # Check missing columns
    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    # Validate rows
    df = validate_dataframe(df, required_columns, valid_currencies)

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

    return {
        "total_rows": len(df),
        "valid_rows": len(valid_df),
        "error_rows": len(error_df),
        "valid_csv": str(valid_csv),
        "error_xlsx": str(error_xlsx),
        "errors_dataframe": error_df
    }
