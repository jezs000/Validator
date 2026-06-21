import pandas as pd

def is_empty(value):
    return pd.isna(value) or str(value).strip() == ""
