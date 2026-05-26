import re
from dataclasses import dataclass, field

import httpx

from app.config import settings


@dataclass
class BookData:
    title: str
    authors: list[str] = field(default_factory=list)
    publisher: str | None = None
    published_year: int | None = None
    pages: int | None = None
    language: str | None = None
    cover_url: str | None = None
    isbn_13: str | None = None
    isbn_10: str | None = None
    dewey_code: str | None = None


async def lookup_isbn(isbn: str) -> BookData | None:
    result = await _try_open_library(isbn)
    if result is not None:
        return result
    return await _try_google_books(isbn)


async def _try_open_library(isbn: str) -> BookData | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://openlibrary.org/api/books",
                params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    book_key = f"ISBN:{isbn}"
    info = data.get(book_key)
    if not info:
        return None

    authors = [a["name"] for a in info.get("authors", []) if "name" in a]
    publisher = None
    if info.get("publishers"):
        publisher = info["publishers"][0].get("name")

    year = None
    raw_date = info.get("publish_date", "")
    match = re.search(r"\d{4}", raw_date)
    if match:
        year = int(match.group())

    cover = info.get("cover")
    cover_url = None
    if isinstance(cover, dict):
        cover_url = cover.get("medium") or cover.get("small")

    return BookData(
        title=info.get("title", ""),
        authors=authors,
        publisher=publisher,
        published_year=year,
        pages=info.get("number_of_pages"),
        cover_url=cover_url,
    )


async def _try_google_books(isbn: str) -> BookData | None:
    try:
        params: dict = {"q": f"isbn:{isbn}"}
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/books/v1/volumes",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    if not data.get("totalItems"):
        return None

    items = data.get("items")
    if not items:
        return None

    info = items[0].get("volumeInfo", {})

    authors = info.get("authors", []) or []
    if not isinstance(authors, list):
        authors = []

    year = None
    raw_date = info.get("publishedDate", "")
    if raw_date and len(raw_date) >= 4:
        match = re.search(r"\d{4}", raw_date)
        if match:
            year = int(match.group())

    images = info.get("imageLinks") or {}
    cover_url = None
    if isinstance(images, dict):
        cover_url = images.get("thumbnail") or images.get("smallThumbnail")

    identifiers = info.get("industryIdentifiers") or []
    isbn_13 = None
    isbn_10 = None
    for ident in identifiers:
        t = ident.get("type", "")
        val = ident.get("identifier", "")
        if t == "ISBN_13":
            isbn_13 = val
        elif t == "ISBN_10":
            isbn_10 = val

    return BookData(
        title=info.get("title", ""),
        authors=authors,
        publisher=info.get("publisher"),
        published_year=year,
        pages=info.get("pageCount"),
        language=info.get("language"),
        cover_url=cover_url,
        isbn_13=isbn_13,
        isbn_10=isbn_10,
    )
