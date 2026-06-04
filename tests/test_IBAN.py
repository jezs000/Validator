from validator import is_valid_iban


def test_valid_iban():
    assert is_valid_iban(
        "CZ6508000000192000145399"
    )


def test_invalid_iban():
    assert not is_valid_iban(
        "CZ6508000000192000145398"
    )


def test_empty_iban():
    assert not is_valid_iban("")