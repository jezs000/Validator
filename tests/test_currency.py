from validator import is_valid_currency


ALLOWED = ["CZK", "EUR", "USD"]


def test_valid_currency():
    assert is_valid_currency("CZK", ALLOWED)


def test_lowercase_currency():
    assert is_valid_currency("eur", ALLOWED)


def test_invalid_currency():
    assert not is_valid_currency("BTC", ALLOWED)