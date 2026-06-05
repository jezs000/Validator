import pandas as pd
import pytest

from validator import validate_file

def test_missing_required_column(
    tmp_path
):

    data = pd.DataFrame(
        {
            "Issue Date": ["01.05.2026"]
        }
    )

    file = tmp_path / "bad.xlsx"

    data.to_excel(
        file,
        index=False
    )

    with pytest.raises(
        ValueError
    ):
        validate_file(
            input_path=str(file),
            output_dir=str(tmp_path),
            config_path="config.yaml"
        )