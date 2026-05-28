import csv
import io

from app.models import Book


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
            str(book.id),
            book.isbn_13 or "",
            book.isbn_10 or "",
            book.title or "",
            book.subtitle or "",
            "; ".join(book.authors) if book.authors else "",
            book.publisher or "",
            str(book.published_year) if book.published_year else "",
            book.language or "",
            str(book.pages) if book.pages else "",
            book.cover_url or "",
            book.dewey_code or "",
            book.notes or "",
            book.created_at.isoformat() if book.created_at else "",
        ])
    return output.getvalue()
