import re


def normalize_isbn(raw: str) -> str | None:
    digits = re.sub(r"[\s\-]", "", raw)
    if len(digits) not in (10, 13) or not digits.isdigit():
        return None
    return digits


def validate_isbn13(isbn: str) -> bool:
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(
        int(d) * (1 if i % 2 == 0 else 3)
        for i, d in enumerate(isbn[:12])
    )
    check = (10 - (total % 10)) % 10
    return check == int(isbn[12])
