import pandas as pd
from pathlib import Path

from validator import validate_file

def test_validate_file(tmp_path):

    data = pd.DataFrame(
        {
            "Invoice Number": ["INV-001"],
            "Issue Date": ["01.05.2026"],
            "Due Date": ["15.05.2026"],
            "Vendor Name": ["Test Company"],
            "Vendor Company ID": ["27074358"],
            "Total Amount": [1000],
            "Currency": ["CZK"]
        }
    )

    input_file = tmp_path / "input.xlsx"

    data.to_excel(
        input_file,
        index=False
    )

    result = validate_file(
        input_path=str(input_file),
        output_dir=str(tmp_path),
        config_path="config.yaml"
    )

    assert result["total_rows"] == 1
    assert result["valid_rows"] == 1
    assert result["error_rows"] == 0