import uuid

import pytest
from httpx import AsyncClient


async def _create_book(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/books/", json={"title": "Loan Test Book", "authors": []}
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_loan(auth_client: AsyncClient):
    book_id = await _create_book(auth_client)

    resp = await auth_client.post(
        "/loans/",
        json={"book_id": book_id, "borrower_name": "Alice"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["borrower_name"] == "Alice"
    assert data["book_id"] == book_id
    assert data["returned_at"] is None


@pytest.mark.asyncio
async def test_create_loan_nonexistent_book(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/loans/",
        json={"book_id": str(uuid.uuid4()), "borrower_name": "Alice"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_return_loan(auth_client: AsyncClient):
    book_id = await _create_book(auth_client)
    create_resp = await auth_client.post(
        "/loans/",
        json={"book_id": book_id, "borrower_name": "Bob"},
    )
    loan_id = create_resp.json()["id"]

    resp = await auth_client.post(f"/loans/{loan_id}/return")
    assert resp.status_code == 200
    data = resp.json()
    assert data["returned_at"] is not None


@pytest.mark.asyncio
async def test_return_loan_not_found(auth_client: AsyncClient):
    resp = await auth_client.post(f"/loans/{uuid.uuid4()}/return")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_loans(auth_client: AsyncClient):
    book_id = await _create_book(auth_client)
    await auth_client.post(
        "/loans/",
        json={"book_id": book_id, "borrower_name": "Alice"},
    )
    await auth_client.post(
        "/loans/",
        json={"book_id": book_id, "borrower_name": "Bob"},
    )

    resp = await auth_client.get("/loans/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_list_loans_open_only(auth_client: AsyncClient):
    book_id = await _create_book(auth_client)
    create_resp = await auth_client.post(
        "/loans/",
        json={"book_id": book_id, "borrower_name": "Alice"},
    )
    loan_id = create_resp.json()["id"]
    await auth_client.post(f"/loans/{loan_id}/return")

    resp = await auth_client.get("/loans/?open_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0
