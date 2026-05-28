from typing import Any

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

from app.models import Book


def _make_cite_key(book: Book) -> str:
    if book.authors and book.published_year:
        parts = book.authors[0].split()
        last_name = parts[-1] if parts else book.authors[0]
        last_name = "".join(c for c in last_name if c.isalpha())
        year = str(book.published_year)
        return f"{last_name.lower()}{year}"
    return str(book.id).replace("-", "")[:16]


def generate_bibtex(books: list[Book]) -> str:
    db = BibDatabase()
    entries: list[dict[str, str]] = []
    seen: dict[str, int] = {}

    for book in books:
        key = _make_cite_key(book)
        if key in seen:
            seen[key] += 1
            key = f"{key}{seen[key]}"
        else:
            seen[key] = 0

        entry: dict[str, str] = {"ENTRYTYPE": "book", "ID": key}

        title = book.title or ""
        if book.subtitle:
            title = f"{title}: {book.subtitle}"
        if title:
            entry["title"] = title

        if book.authors:
            entry["author"] = " and ".join(book.authors)

        if book.publisher:
            entry["publisher"] = book.publisher

        if book.published_year:
            entry["year"] = str(book.published_year)

        isbn = book.isbn_13 or book.isbn_10
        if isbn:
            entry["isbn"] = isbn

        if book.language:
            entry["language"] = book.language

        if book.notes:
            entry["note"] = book.notes

        entries.append(entry)

    db.entries = entries
    return bibtexparser.dumps(db)


def parse_bibtex(content: str) -> list[dict[str, str]]:
    db = bibtexparser.loads(content)
    entries: list[dict[str, str]] = []
    for entry in db.entries:
        if entry.get("ENTRYTYPE", "").lower() != "book":
            continue
        entries.append(entry)
    return entries


def _to_optional_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError:
        return None


def _split_isbn(value: str) -> tuple[str | None, str | None]:
    stripped = value.strip()
    if not stripped:
        return None, None
    isbn = "".join(char for char in stripped if char not in {" ", "-"}).upper()
    if len(isbn) == 13 and isbn.isdigit():
        return isbn, None
    if len(isbn) == 10 and isbn[:-1].isdigit() and (isbn[-1].isdigit() or isbn[-1] == "X"):
        return None, isbn
    return None, None


def map_bibtex_entry_to_book_data(entry: dict[str, str]) -> dict[str, Any]:
    authors_str = entry.get("author", "").strip()
    if authors_str:
        authors = [a.strip() for a in authors_str.split(" and ") if a.strip()]
    else:
        authors = []

    isbn_13, isbn_10 = _split_isbn(entry.get("isbn", ""))

    return {
        "isbn_13": isbn_13,
        "isbn_10": isbn_10,
        "title": entry.get("title", "").strip(),
        "authors": authors,
        "publisher": entry.get("publisher", "").strip() or None,
        "published_year": _to_optional_int(entry.get("year", "")),
        "language": entry.get("language", "").strip() or None,
        "notes": entry.get("note", "").strip() or None,
    }
