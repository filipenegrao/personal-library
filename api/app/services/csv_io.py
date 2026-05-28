import csv
import io
from typing import Any
from urllib.parse import urlparse

from app.models import Book

_FORMULA_PREFIXES = ("=", "+", "-", "@", "|", "\t", "\r", "\n")


def _safe_csv_cell(value: object) -> str:
    text = "" if value is None else str(value)
    if text.startswith(_FORMULA_PREFIXES):
        return "'" + text
    return text


def _to_optional_https_url(value: str) -> str | None:
    stripped = value.strip()
    if not stripped:
        return None
    parsed = urlparse(stripped)
    if parsed.scheme == "https":
        return stripped
    return None


def _to_optional_isbn(value: str, *, length: int) -> str | None:
    stripped = value.strip()
    if not stripped:
        return None
    normalized = "".join(char for char in stripped if char not in {" ", "-"}).upper()
    if length == 13 and len(normalized) == 13 and normalized.isdigit():
        return normalized
    if length == 10 and len(normalized) == 10 and normalized[:-1].isdigit() and (
        normalized[-1].isdigit() or normalized[-1] == "X"
    ):
        return normalized
    return None


def generate_csv(books: list[Book]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "id",
        "isbn_13",
        "isbn_10",
        "title",
        "subtitle",
        "authors",
        "publisher",
        "published_year",
        "language",
        "pages",
        "cover_url",
        "dewey_code",
        "notes",
        "created_at",
    ]
    writer.writerow(headers)
    for book in books:
        writer.writerow([
            _safe_csv_cell(book.id),
            _safe_csv_cell(book.isbn_13),
            _safe_csv_cell(book.isbn_10),
            _safe_csv_cell(book.title),
            _safe_csv_cell(book.subtitle),
            _safe_csv_cell("; ".join(book.authors) if book.authors else ""),
            _safe_csv_cell(book.publisher),
            _safe_csv_cell(book.published_year),
            _safe_csv_cell(book.language),
            _safe_csv_cell(book.pages),
            _safe_csv_cell(book.cover_url),
            _safe_csv_cell(book.dewey_code),
            _safe_csv_cell(book.notes),
            _safe_csv_cell(book.created_at.isoformat() if book.created_at else ""),
        ])
    return output.getvalue()


def parse_csv(content: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None or not any(field.strip() for field in reader.fieldnames if field):
        raise ValueError("CSV file has no header row")
    rows: list[dict[str, str]] = []
    for row in reader:
        normalized = {str(key): "" if value is None else value for key, value in row.items() if key}
        if not any(value.strip() for value in normalized.values()):
            continue
        rows.append(normalized)
    return rows


def _to_optional_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError:
        return None


def map_csv_row_to_book_data(row: dict[str, str]) -> dict[str, Any]:
    authors_str = row.get("authors", "").strip()
    if authors_str:
        authors = [a.strip() for a in authors_str.split(";") if a.strip()]
    else:
        authors = []

    isbn_13 = _to_optional_isbn(row.get("isbn_13", ""), length=13)
    isbn_10 = _to_optional_isbn(row.get("isbn_10", ""), length=10)

    return {
        "isbn_13": isbn_13,
        "isbn_10": isbn_10,
        "title": row.get("title", "").strip(),
        "subtitle": row.get("subtitle", "").strip() or None,
        "authors": authors,
        "publisher": row.get("publisher", "").strip() or None,
        "published_year": _to_optional_int(row.get("published_year", "")),
        "language": row.get("language", "").strip() or None,
        "pages": _to_optional_int(row.get("pages", "")),
        "cover_url": _to_optional_https_url(row.get("cover_url", "")),
        "dewey_code": row.get("dewey_code", "").strip() or None,
        "notes": row.get("notes", "").strip() or None,
    }
