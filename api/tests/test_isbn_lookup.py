import pytest

from app.services.isbn_lookup import lookup_isbn


@pytest.mark.asyncio
async def test_open_library_success(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").respond(
        json={
            "ISBN:9780306406157": {
                "title": "The Lord of the Rings",
                "authors": [{"name": "J.R.R. Tolkien"}],
                "publishers": [{"name": "Houghton Mifflin"}],
                "publish_date": "2005",
                "number_of_pages": 1200,
                "cover": {"medium": "https://covers.example.com/123-M.jpg"},
            }
        }
    )

    result = await lookup_isbn("9780306406157")

    assert result is not None
    assert result.title == "The Lord of the Rings"
    assert result.authors == ["J.R.R. Tolkien"]
    assert result.publisher == "Houghton Mifflin"


@pytest.mark.asyncio
async def test_google_books_fallback(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").respond(json={})

    respx_mock.get("https://www.googleapis.com/books/v1/volumes").respond(
        json={
            "totalItems": 1,
            "items": [
                {
                    "volumeInfo": {
                        "title": "Test Book",
                        "authors": ["Test Author"],
                        "publisher": "Test Publisher",
                        "publishedDate": "2020-01-15",
                        "pageCount": 250,
                        "language": "en",
                        "imageLinks": {"thumbnail": "https://example.com/thumb.jpg"},
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9780306406157"},
                            {"type": "ISBN_10", "identifier": "0306406152"},
                        ],
                    }
                }
            ],
        }
    )

    result = await lookup_isbn("9780306406157")

    assert result is not None
    assert result.title == "Test Book"


@pytest.mark.asyncio
async def test_both_fail(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").respond(json={})

    respx_mock.get("https://www.googleapis.com/books/v1/volumes").respond(
        json={"totalItems": 0}
    )

    result = await lookup_isbn("9780306406157")

    assert result is None
