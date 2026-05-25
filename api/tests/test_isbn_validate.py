from app.services.isbn_validate import normalize_isbn, validate_isbn13


def test_validate_isbn13_valid():
    assert validate_isbn13("9780306406157") is True


def test_validate_isbn13_wrong_checksum():
    assert validate_isbn13("9780306406150") is False


def test_validate_isbn13_too_short():
    assert validate_isbn13("978030640615") is False


def test_normalize_isbn_with_hyphens():
    assert normalize_isbn("978-0-306-40615-7") == "9780306406157"


def test_normalize_isbn_with_spaces():
    assert normalize_isbn("978 0 306 40615 7") == "9780306406157"


def test_normalize_isbn_invalid():
    assert normalize_isbn("not-an-isbn") is None


def test_normalize_isbn_nondigit_last_char():
    assert normalize_isbn("978030640615X") is None
