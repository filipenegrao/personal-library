import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://localhost/personal_library")
os.environ.setdefault(
    "TEST_DATABASE_URL", "postgresql+asyncpg://localhost/personal_library_test"
)
os.environ.setdefault("LIBRARY_USERNAME", "admin")
os.environ.setdefault("LIBRARY_PASSWORD", "changeme")
os.environ.setdefault("JWT_SECRET", "super-secret-key-at-least-32-characters-long")

from app.config import settings
from app.database import Base
from app.deps import get_db
from app.main import app

TEST_URL = settings.test_database_url or settings.database_url.replace(
    "/personal_library", "/personal_library_test"
)


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.state.engine = test_engine
    app.state.session_factory = factory

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    resp = await client.post("/auth/login", json={"username": "admin", "password": "changeme"})
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
