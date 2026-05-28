import pytest
from httpx import AsyncClient


CSV_WITH_BOOKS = (
    "isbn_13,isbn_10,title,subtitle,authors,publisher,published_year,language,"
    "pages,cover_url,dewey_code,notes,id,created_at\r\n"
    "9780306406157,,Test Book,,Author One; Author Two,Test Press,2025,en,"
    "300,,005.1,Test note,,\r\n"
    "9781234567897,123456789X,Second Book,Subtitle Here,Jane Author,,2024,pt,"
    "150,,,,,\r\n"
)

CSV_WITH_MISSING_TITLE = (
    "isbn_13,title,subtitle,authors\r\n"
    "9780306406157,Valid Book,,Author One\r\n"
    "9781234567897,,,Missing Title Author\r\n"
)

CSV_HEADERS_ONLY = (
    "id,isbn_13,isbn_10,title,subtitle,authors,publisher,published_year,"
    "language,pages,cover_url,dewey_code,notes,created_at\r\n"
)
CSV_EMPTY_HEADER = "\r\nBook without header\r\n"

CSV_WITH_EXTRA_COLUMNS = "title,authors\r\nExtra Columns Book,Author One,ignored\r\n"
CSV_WITH_COVER_URLS = (
    "title,cover_url\r\n"
    "Valid URL,https://example.com/cover.jpg\r\n"
    "Plain HTTP URL,http://example.com/cover.jpg\r\n"
    "Invalid URL,javascript:alert(1)\r\n"
)
CSV_WITH_INVALID_ISBN = (
    "isbn_13,isbn_10,title\r\n"
    "9780306406157000,123456789000,Invalid ISBNs\r\n"
)

BIBTEX_WITH_BOOKS = """
@book{smith2025,
  title     = {Test Book},
  author    = {John Smith and Jane Doe},
  publisher = {Test Press},
  year      = {2025},
  isbn      = {9780306406157},
  language  = {en},
  note      = {Test note}
}

@book{jane2024,
  title     = {Second Book},
  author    = {Jane Author},
  year      = {2024},
  language  = {pt}
}
"""

BIBTEX_WITH_ARTICLES = """
@article{key2025,
  title   = {Some Article},
  author  = {John Smith},
  journal = {Test Journal},
  year    = {2025}
}

@book{book2025,
  title  = {Only Book},
  author = {Author Name},
  year   = {2025}
}
"""

BIBTEX_WITH_HYPHENATED_ISBN = """
@book{hyphen2025,
  title  = {Hyphen ISBN},
  author = {Author Name},
  year   = {2025},
  isbn   = {978-0-306-40615-7}
}
"""

BIBTEX_WITH_INVALID_ISBN = """
@book{invalid2025,
  title  = {Invalid ISBN},
  author = {Author Name},
  year   = {2025},
  isbn   = {not-a-valid-isbn-value}
}
"""

BIBTEX_EMPTY = ""

BIBTEX_INVALID = "not valid bibtex content {"

BIBTEX_MISSING_TITLE = """
@book{smith2025,
  author = {John Smith},
  year   = {2025}
}
"""


@pytest.mark.asyncio
async def test_csv_import_with_books(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_BOOKS, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["created"] == 2
    assert len(data["errors"]) == 0
    assert len(data["books"]) == 2

    book1 = data["books"][0]
    assert book1["title"] == "Test Book"
    assert book1["isbn_13"] == "9780306406157"
    assert book1["authors"] == ["Author One", "Author Two"]
    assert book1["publisher"] == "Test Press"
    assert book1["published_year"] == 2025
    assert book1["language"] == "en"
    assert book1["pages"] == 300
    assert book1["dewey_code"] == "005.1"
    assert book1["notes"] == "Test note"

    book2 = data["books"][1]
    assert book2["title"] == "Second Book"
    assert book2["subtitle"] == "Subtitle Here"
    assert book2["isbn_13"] == "9781234567897"
    assert book2["isbn_10"] == "123456789X"
    assert book2["published_year"] == 2024
    assert book2["language"] == "pt"
    assert book2["pages"] == 150


@pytest.mark.asyncio
async def test_csv_import_missing_title(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_MISSING_TITLE, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["created"] == 1
    assert len(data["errors"]) == 1
    assert "missing required field" in data["errors"][0].lower()
    assert data["books"][0]["title"] == "Valid Book"


@pytest.mark.asyncio
async def test_csv_import_empty(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("empty.csv", CSV_HEADERS_ONLY, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["created"] == 0
    assert len(data["errors"]) == 0
    assert len(data["books"]) == 0


@pytest.mark.asyncio
async def test_csv_import_rejects_empty_header(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_EMPTY_HEADER, "text/csv")},
    )
    assert resp.status_code == 400
    assert "header" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csv_import_auth_required(client: AsyncClient):
    resp = await client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_BOOKS, "text/csv")},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_csv_import_wrong_extension(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.txt", CSV_WITH_BOOKS, "text/plain")},
    )
    assert resp.status_code == 400
    assert "csv" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csv_import_ignores_extra_columns(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_EXTRA_COLUMNS, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 1
    assert data["books"][0]["title"] == "Extra Columns Book"


@pytest.mark.asyncio
async def test_csv_import_rejects_large_file(auth_client: AsyncClient):
    content = "title\r\n" + ("A" * 1_000_001)
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("large.csv", content, "text/csv")},
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_csv_import_rejects_non_utf8(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", b"\xff\xfe\x00\x00", "text/csv")},
    )
    assert resp.status_code == 400
    assert "utf-8" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csv_import_filters_cover_url_scheme(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_COVER_URLS, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 3
    assert data["books"][0]["cover_url"] == "https://example.com/cover.jpg"
    assert data["books"][1]["cover_url"] is None
    assert data["books"][2]["cover_url"] is None


@pytest.mark.asyncio
async def test_csv_import_rejects_too_many_rows(auth_client: AsyncClient):
    content = "title\r\n" + "\r\n".join(f"Book {i}" for i in range(5001))
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", content, "text/csv")},
    )
    assert resp.status_code == 413
    assert "too many" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csv_import_drops_invalid_isbn_values(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/csv",
        files={"file": ("books.csv", CSV_WITH_INVALID_ISBN, "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 1
    assert data["books"][0]["isbn_13"] is None
    assert data["books"][0]["isbn_10"] is None


@pytest.mark.asyncio
async def test_bibtex_import_with_books(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_WITH_BOOKS, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["created"] == 2
    assert len(data["errors"]) == 0
    assert len(data["books"]) == 2

    book1 = data["books"][0]
    assert book1["title"] == "Test Book"
    assert book1["authors"] == ["John Smith", "Jane Doe"]
    assert book1["publisher"] == "Test Press"
    assert book1["published_year"] == 2025
    assert book1["isbn_13"] == "9780306406157"
    assert book1["language"] == "en"
    assert book1["notes"] == "Test note"

    book2 = data["books"][1]
    assert book2["title"] == "Second Book"
    assert book2["authors"] == ["Jane Author"]
    assert book2["published_year"] == 2024
    assert book2["language"] == "pt"


@pytest.mark.asyncio
async def test_bibtex_import_normalizes_hyphenated_isbn13(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_WITH_HYPHENATED_ISBN, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 1
    assert data["books"][0]["isbn_13"] == "9780306406157"


@pytest.mark.asyncio
async def test_bibtex_import_drops_invalid_isbn_values(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_WITH_INVALID_ISBN, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 1
    assert data["books"][0]["isbn_13"] is None
    assert data["books"][0]["isbn_10"] is None


@pytest.mark.asyncio
async def test_bibtex_import_filters_articles(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_WITH_ARTICLES, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["created"] == 1
    assert data["books"][0]["title"] == "Only Book"


@pytest.mark.asyncio
async def test_bibtex_import_empty(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("empty.bib", BIBTEX_EMPTY, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["created"] == 0
    assert len(data["books"]) == 0


@pytest.mark.asyncio
async def test_bibtex_import_auth_required(client: AsyncClient):
    resp = await client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_WITH_BOOKS, "application/x-bibtex")},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_bibtex_import_wrong_extension(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.txt", BIBTEX_WITH_BOOKS, "text/plain")},
    )
    assert resp.status_code == 400
    assert "bib" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_bibtex_import_malformed_returns_empty(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("bad.bib", BIBTEX_INVALID, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["created"] == 0


@pytest.mark.asyncio
async def test_bibtex_import_missing_title(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/import/bibtex",
        files={"file": ("library.bib", BIBTEX_MISSING_TITLE, "application/x-bibtex")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["created"] == 0
    assert len(data["errors"]) == 1
    assert "missing required field" in data["errors"][0].lower()
