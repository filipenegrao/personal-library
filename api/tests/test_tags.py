import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tag(auth_client: AsyncClient):
    resp = await auth_client.post("/tags/", json={"name": "fiction", "color": "#ff0000"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "fiction"
    assert data["color"] == "#ff0000"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tags(auth_client: AsyncClient):
    await auth_client.post("/tags/", json={"name": "fiction"})
    await auth_client.post("/tags/", json={"name": "non-fiction"})

    resp = await auth_client.get("/tags/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    names = [t["name"] for t in data]
    assert "fiction" in names
    assert "non-fiction" in names


@pytest.mark.asyncio
async def test_update_tag(auth_client: AsyncClient):
    create_resp = await auth_client.post("/tags/", json={"name": "old-name"})
    tag_id = create_resp.json()["id"]

    resp = await auth_client.patch(f"/tags/{tag_id}", json={"name": "new-name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "new-name"


@pytest.mark.asyncio
async def test_delete_tag(auth_client: AsyncClient):
    create_resp = await auth_client.post("/tags/", json={"name": "temp"})
    tag_id = create_resp.json()["id"]

    del_resp = await auth_client.delete(f"/tags/{tag_id}")
    assert del_resp.status_code == 204

    list_resp = await auth_client.get("/tags/")
    names = [t["name"] for t in list_resp.json()]
    assert "temp" not in names


@pytest.mark.asyncio
async def test_tag_not_found(auth_client: AsyncClient):
    resp = await auth_client.patch(f"/tags/{uuid.uuid4()}", json={"name": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_in_use(auth_client: AsyncClient):
    tag_resp = await auth_client.post("/tags/", json={"name": "in-use"})
    tag_id = tag_resp.json()["id"]

    await auth_client.post(
        "/books/",
        json={"title": "With Tag", "authors": [], "tag_ids": [tag_id]},
    )

    del_resp = await auth_client.delete(f"/tags/{tag_id}")
    assert del_resp.status_code == 409
