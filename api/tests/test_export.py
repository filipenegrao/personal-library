import csv
import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_csv_export_with_books(auth_client: AsyncClient):
    await auth_client.post("/books/", json={
        "title": "CSV Book",
        "authors": ["Author One"],
        "isbn_13": "9780306406157",
        "publisher": "Test Press",
        "published_year": 2025,
    })

    resp = await auth_client.get("/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert "attachment" in resp.headers.get("content-disposition", "")

    reader = csv.DictReader(io.StringIO(resp.text))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["title"] == "CSV Book"
    assert rows[0]["isbn_13"] == "9780306406157"
    assert rows[0]["publisher"] == "Test Press"
    assert rows[0]["published_year"] == "2025"
    assert rows[0]["authors"] == "Author One"


@pytest.mark.asyncio
async def test_csv_export_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")

    reader = csv.reader(io.StringIO(resp.text))
    headers = next(reader)
    assert len(headers) == 14
    rows = list(reader)
    assert len(rows) == 0


@pytest.mark.asyncio
async def test_bibtex_export_with_books(auth_client: AsyncClient):
    await auth_client.post("/books/", json={
        "title": "BibTeX Book",
        "subtitle": "A Story",
        "authors": ["Jane Author"],
        "publisher": "Acme Press",
        "published_year": 2024,
        "isbn_13": "9781234567897",
    })

    resp = await auth_client.get("/export/bibtex")
    assert resp.status_code == 200
    assert "attachment" in resp.headers.get("content-disposition", "")

    text = resp.text
    assert "@book{" in text
    assert "BibTeX Book: A Story" in text
    assert "Jane Author" in text
    assert "Acme Press" in text
    assert "9781234567897" in text


@pytest.mark.asyncio
async def test_bibtex_export_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/export/bibtex")
    assert resp.status_code == 200
    assert resp.text.strip() == ""


@pytest.mark.asyncio
async def test_export_csv_auth_required(client: AsyncClient):
    resp = await client.get("/export/csv")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_export_bibtex_auth_required(client: AsyncClient):
    resp = await client.get("/export/bibtex")
    assert resp.status_code == 401
