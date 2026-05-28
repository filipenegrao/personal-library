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
