import uuid

import pytest


@pytest.mark.asyncio
async def test_create_template(auth_client):
    resp = await auth_client.post(
        "/labels/templates/",
        json={"name": "Standard 50x30", "width_mm": 50.0, "height_mm": 30.0},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Standard 50x30"
    assert data["width_mm"] == 50.0
    assert data["height_mm"] == 30.0
    assert data["font_size"] == 8
    assert data["show_dewey"] is True
    assert data["show_title"] is True
    assert data["show_barcode"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_templates(auth_client):
    await auth_client.post("/labels/templates/", json={"name": "A"})
    await auth_client.post("/labels/templates/", json={"name": "B"})

    resp = await auth_client.get("/labels/templates/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    names = [t["name"] for t in data]
    assert "A" in names
    assert "B" in names


@pytest.mark.asyncio
async def test_delete_template(auth_client):
    create_resp = await auth_client.post("/labels/templates/", json={"name": "temp"})
    template_id = create_resp.json()["id"]

    del_resp = await auth_client.delete(f"/labels/templates/{template_id}")
    assert del_resp.status_code == 204

    list_resp = await auth_client.get("/labels/templates/")
    names = [t["name"] for t in list_resp.json()]
    assert "temp" not in names


@pytest.mark.asyncio
async def test_template_not_found(auth_client):
    resp = await auth_client.delete(f"/labels/templates/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_pdf(auth_client):
    book_resp = await auth_client.post(
        "/books/",
        json={
            "title": "The Pragmatic Programmer",
            "authors": ["David Thomas", "Andrew Hunt"],
            "isbn_13": "9780135957059",
            "dewey_code": "005.1",
        },
    )
    book_id = book_resp.json()["id"]

    tmpl_resp = await auth_client.post(
        "/labels/templates/",
        json={"name": "Standard", "width_mm": 50.0, "height_mm": 30.0, "font_size": 8},
    )
    template_id = tmpl_resp.json()["id"]

    resp = await auth_client.post(
        "/labels/generate",
        json={"book_ids": [book_id], "template_id": template_id},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 200  # meaningfully non-trivial PDF


@pytest.mark.asyncio
async def test_generate_pdf_template_not_found(auth_client):
    resp = await auth_client.post(
        "/labels/generate",
        json={"book_ids": [str(uuid.uuid4())], "template_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404
    assert "Template not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_generate_pdf_no_books(auth_client):
    tmpl_resp = await auth_client.post(
        "/labels/templates/",
        json={"name": "Standard"},
    )
    template_id = tmpl_resp.json()["id"]

    resp = await auth_client.post(
        "/labels/generate",
        json={"book_ids": [], "template_id": template_id},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No books found"


@pytest.mark.asyncio
async def test_generate_pdf_bogus_book_ids(auth_client):
    tmpl_resp = await auth_client.post(
        "/labels/templates/",
        json={"name": "Standard"},
    )
    template_id = tmpl_resp.json()["id"]

    resp = await auth_client.post(
        "/labels/generate",
        json={"book_ids": [str(uuid.uuid4())], "template_id": template_id},
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No books found"
