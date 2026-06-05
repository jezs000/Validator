from validator import is_valid_ico


def test_valid_ico():
    assert is_valid_ico("27074358")


def test_invalid_checksum():
    assert not is_valid_ico("12345678")


def test_invalid_length():
    assert not is_valid_ico("123")


def test_letters():
    assert not is_valid_ico("ABC12345")