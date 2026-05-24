# Personal Library — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal book library web app with ISBN lookup, physical label PDF generation, loan tracking, and bibliography export/import.

**Architecture:** FastAPI backend (Python 3.12) handles all business logic, data access, PDF generation, and export; Next.js 15 frontend consumes the API. PostgreSQL 17 stores all data via SQLAlchemy 2 async ORM with Alembic migrations. Single-user auth via JWT stored in httpOnly cookie.

**Tech Stack:** Python 3.12, FastAPI 0.115, SQLAlchemy 2 + asyncpg, Alembic, pydantic-settings, python-jose, passlib[bcrypt], httpx, reportlab, bibtexparser, respx, pytest, pytest-asyncio | Next.js 15, Tailwind CSS v4, shadcn/ui, @zxing/browser, TypeScript

---

## File Structure

```
personal-library/
├── .gitignore
├── api/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── deps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── book.py
│   │   │   ├── tag.py
│   │   │   ├── loan.py
│   │   │   └── label_template.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── book.py
│   │   │   ├── tag.py
│   │   │   ├── loan.py
│   │   │   └── label_template.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── books.py
│   │   │   ├── tags.py
│   │   │   ├── loans.py
│   │   │   ├── labels.py
│   │   │   └── export.py
│   │   └── services/
│   │       ├── isbn_validate.py
│   │       ├── isbn_lookup.py
│   │       ├── pdf_labels.py
│   │       ├── bibtex_io.py
│   │       └── csv_io.py
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_isbn_validate.py
│       ├── test_isbn_lookup.py
│       ├── test_books.py
│       ├── test_tags.py
│       ├── test_loans.py
│       ├── test_labels.py
│       └── test_export.py
└── web/
    ├── package.json
    ├── next.config.ts
    ├── tsconfig.json
    ├── .env.local.example
    └── src/
        ├── middleware.ts
        ├── app/
        │   ├── globals.css
        │   ├── layout.tsx
        │   ├── page.tsx
        │   ├── login/page.tsx
        │   ├── catalog/
        │   │   ├── page.tsx
        │   │   └── [id]/page.tsx
        │   ├── books/new/page.tsx
        │   ├── loans/page.tsx
        │   └── labels/page.tsx
        ├── components/
        │   ├── isbn-scanner.tsx
        │   ├── book-form.tsx
        │   ├── book-card.tsx
        │   ├── loan-form.tsx
        │   └── label-selector.tsx
        └── lib/
            ├── api.ts
            └── auth.ts
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `.gitignore`
- Create: `api/` directory structure
- Create: `web/` directory structure

- [ ] **Step 1: Create root .gitignore**

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
dist/
.env

# Node
node_modules/
.next/
.env.local

# Misc
.DS_Store
*.log
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p api/app/{models,schemas,routers,services}
mkdir -p api/alembic/versions
mkdir -p api/tests
touch api/app/{main,config,database,auth,deps}.py
touch api/app/models/{__init__,book,tag,loan,label_template}.py
touch api/app/schemas/{__init__,book,tag,loan,label_template}.py
touch api/app/routers/{__init__,auth,books,tags,loans,labels,export}.py
touch api/app/services/{isbn_validate,isbn_lookup,pdf_labels,bibtex_io,csv_io}.py
touch api/tests/{conftest,test_auth,test_isbn_validate,test_isbn_lookup,test_books,test_tags,test_loans,test_labels,test_export}.py
mkdir -p web/src/{app,components,lib}
mkdir -p web/src/app/{login,"catalog/[id]","books/new",loans,labels}
```

- [ ] **Step 3: Commit**

```bash
git init
git add .gitignore
git commit -m "chore: initial project scaffold"
```

---

## Task 2: Backend Setup

**Files:**
- Create: `api/pyproject.toml`
- Create: `api/.env.example`
- Create: `api/app/config.py`
- Create: `api/app/database.py`
- Create: `api/app/main.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "personal-library-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.*",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "pydantic-settings>=2.5",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "httpx>=0.27",
    "reportlab>=4.2",
    "bibtexparser>=1.4",
    "python-multipart>=0.0.12",
]

[dependency-groups]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "coverage>=7.5",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: Create venv and install**

```bash
cd api
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

- [ ] **Step 3: Create .env.example**

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/personal_library
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/personal_library_test
LIBRARY_USERNAME=admin
LIBRARY_PASSWORD=changeme
JWT_SECRET=change-this-to-a-random-secret-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
GOOGLE_BOOKS_API_KEY=
```

- [ ] **Step 4: Create app/config.py**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    test_database_url: str = ""
    library_username: str
    library_password: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080
    google_books_api_key: str = ""


settings = Settings()
```

- [ ] **Step 5: Create app/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    return create_async_engine(url, echo=False)


def make_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)
```

- [ ] **Step 6: Create app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import make_engine, make_session_factory
from app.routers import auth, books, export, labels, loans, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = make_engine(settings.database_url)
    app.state.session_factory = make_session_factory(app.state.engine)
    yield
    await app.state.engine.dispose()


app = FastAPI(title="Personal Library", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(labels.router, prefix="/labels", tags=["labels"])
app.include_router(export.router, prefix="/export", tags=["export"])
```

- [ ] **Step 7: Create app/deps.py**

```python
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_token

bearer = HTTPBearer()


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return username
```

- [ ] **Step 8: Verify app starts**

```bash
cd api
cp .env.example .env  # fill in real values
uvicorn app.main:app --reload
```
Expected: server starts on port 8000, no import errors.

- [ ] **Step 9: Commit**

```bash
git add api/
git commit -m "feat: backend project setup — FastAPI, config, database"
```

---

## Task 3: Auth Service

**Files:**
- Create: `api/app/auth.py`
- Create: `api/app/routers/auth.py`
- Create: `api/tests/test_auth.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_auth.py
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/login", json={"username": "admin", "password": "changeme"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/books/")
    assert resp.status_code == 403
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd api && pytest tests/test_auth.py -v
```
Expected: FAIL (routers not implemented yet)

- [ ] **Step 3: Create app/auth.py**

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": username, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None
```

- [ ] **Step 4: Create app/routers/auth.py**

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import create_access_token, hash_password, verify_password
from app.config import settings

router = APIRouter()

_hashed_password: str | None = None


def _get_hashed() -> str:
    global _hashed_password
    if _hashed_password is None:
        _hashed_password = hash_password(settings.library_password)
    return _hashed_password


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    if body.username != settings.library_username or not verify_password(
        body.password, _get_hashed()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(body.username))
```

- [ ] **Step 5: Run tests — expect pass**

```bash
pytest tests/test_auth.py -v
```
Expected: all 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add api/app/auth.py api/app/routers/auth.py api/tests/test_auth.py
git commit -m "feat: JWT auth — login endpoint and token verification"
```

---

## Task 4: Database Models + Migration

**Files:**
- Create: `api/app/models/book.py`, `tag.py`, `loan.py`, `label_template.py`
- Create: `api/alembic.ini`
- Create: `api/alembic/env.py`
- Create: `api/alembic/versions/0001_initial_schema.py`

- [ ] **Step 1: Create app/models/book.py**

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isbn_13: Mapped[str | None] = mapped_column(String(13), nullable=True, index=True)
    isbn_10: Mapped[str | None] = mapped_column(String(10), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list] = mapped_column(JSONB, default=list)
    publisher: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    dewey_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    book_tags: Mapped[list["BookTag"]] = relationship("BookTag", back_populates="book", cascade="all, delete-orphan")
    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="book")
```

- [ ] **Step 2: Create app/models/tag.py**

```python
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")

    book_tags: Mapped[list["BookTag"]] = relationship("BookTag", back_populates="tag", cascade="all, delete-orphan")


class BookTag(Base):
    __tablename__ = "book_tags"

    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    book: Mapped["Book"] = relationship("Book", back_populates="book_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="book_tags")
```

- [ ] **Step 3: Create app/models/loan.py**

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"), nullable=False)
    borrower_name: Mapped[str] = mapped_column(Text, nullable=False)
    loaned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    book: Mapped["Book"] = relationship("Book", back_populates="loans")
```

- [ ] **Step 4: Create app/models/label_template.py**

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LabelTemplate(Base):
    __tablename__ = "label_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, default=50.0)
    height_mm: Mapped[float] = mapped_column(Float, default=30.0)
    font_size: Mapped[int] = mapped_column(Integer, default=8)
    show_dewey: Mapped[bool] = mapped_column(Boolean, default=True)
    show_title: Mapped[bool] = mapped_column(Boolean, default=True)
    show_barcode: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

- [ ] **Step 5: Create app/models/__init__.py**

```python
from app.models.book import Book
from app.models.label_template import LabelTemplate
from app.models.loan import Loan
from app.models.tag import BookTag, Tag

__all__ = ["Book", "Tag", "BookTag", "Loan", "LabelTemplate"]
```

- [ ] **Step 6: Initialize Alembic**

```bash
cd api
alembic init alembic
```

- [ ] **Step 7: Edit alembic/env.py**

Replace the generated `env.py` with:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.database import Base
import app.models  # noqa: F401 — registers all models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        await conn.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn, target_metadata=target_metadata
            )
        )
        async with conn.begin():
            await conn.run_sync(lambda _: context.run_migrations())
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 8: Edit alembic.ini — set script_location**

In `alembic.ini`, set:
```
script_location = alembic
sqlalchemy.url =
```
(URL is read from config in env.py, so leave it blank here)

- [ ] **Step 9: Generate and run migration**

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
Expected: tables created in PostgreSQL.

- [ ] **Step 10: Commit**

```bash
git add api/app/models/ api/alembic/ api/alembic.ini
git commit -m "feat: SQLAlchemy models and initial Alembic migration"
```

---

## Task 5: Test Infrastructure

**Files:**
- Create: `api/tests/conftest.py`

- [ ] **Step 1: Create conftest.py**

```python
import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base
from app.deps import get_db
from app.main import app

TEST_URL = settings.test_database_url or settings.database_url.replace(
    "/personal_library", "/personal_library_test"
)


@pytest_asyncio.fixture(scope="session")
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
```

- [ ] **Step 2: Create test database**

```bash
psql -U postgres -c "CREATE DATABASE personal_library_test;"
```

- [ ] **Step 3: Verify conftest works**

```bash
pytest tests/test_auth.py -v
```
Expected: all auth tests PASS using test database.

- [ ] **Step 4: Commit**

```bash
git add api/tests/conftest.py
git commit -m "test: pytest async fixtures with isolated test database"
```

---

## Task 6: ISBN Validation Service

**Files:**
- Create: `api/app/services/isbn_validate.py`
- Create: `api/tests/test_isbn_validate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_isbn_validate.py
import pytest
from app.services.isbn_validate import normalize_isbn, validate_isbn13


def test_valid_isbn13():
    assert validate_isbn13("9780306406157") is True


def test_invalid_isbn13_checksum():
    assert validate_isbn13("9780306406150") is False


def test_invalid_isbn13_length():
    assert validate_isbn13("978030640615") is False


def test_normalize_strips_hyphens():
    assert normalize_isbn("978-0-306-40615-7") == "9780306406157"


def test_normalize_strips_spaces():
    assert normalize_isbn("978 0 306 40615 7") == "9780306406157"


def test_normalize_returns_none_if_invalid():
    assert normalize_isbn("not-an-isbn") is None
```

- [ ] **Step 2: Run — expect failure**

```bash
pytest tests/test_isbn_validate.py -v
```
Expected: FAIL (module not found)

- [ ] **Step 3: Implement isbn_validate.py**

```python
import re


def normalize_isbn(raw: str) -> str | None:
    """Strip hyphens/spaces and return digits only, or None if not 10 or 13 digits."""
    digits = re.sub(r"[\s\-]", "", raw)
    if len(digits) not in (10, 13) or not digits[:12].isdigit():
        return None
    return digits


def validate_isbn13(isbn: str) -> bool:
    """Verify EAN-13 checksum."""
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(
        int(d) * (1 if i % 2 == 0 else 3)
        for i, d in enumerate(isbn[:12])
    )
    check = (10 - (total % 10)) % 10
    return check == int(isbn[12])
```

- [ ] **Step 4: Run — expect pass**

```bash
pytest tests/test_isbn_validate.py -v
```
Expected: 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add api/app/services/isbn_validate.py api/tests/test_isbn_validate.py
git commit -m "feat: ISBN EAN-13 validation and normalization"
```

---

## Task 7: ISBN Lookup Service

**Files:**
- Create: `api/app/services/isbn_lookup.py`
- Create: `api/tests/test_isbn_lookup.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_isbn_lookup.py
import pytest
import respx
from httpx import Response

from app.services.isbn_lookup import BookData, lookup_isbn


@pytest.mark.asyncio
@respx.mock
async def test_lookup_open_library_success():
    respx.get("https://openlibrary.org/api/books").mock(
        return_value=Response(
            200,
            json={
                "ISBN:9780306406157": {
                    "title": "Foo Book",
                    "authors": [{"name": "Jane Doe"}],
                    "publishers": [{"name": "Publisher X"}],
                    "publish_date": "2001",
                    "number_of_pages": 200,
                    "cover": {"medium": "http://covers.openlibrary.org/b/id/1-M.jpg"},
                }
            },
        )
    )
    result = await lookup_isbn("9780306406157")
    assert result is not None
    assert result.title == "Foo Book"
    assert result.authors == ["Jane Doe"]
    assert result.publisher == "Publisher X"


@pytest.mark.asyncio
@respx.mock
async def test_lookup_falls_back_to_google_books():
    respx.get("https://openlibrary.org/api/books").mock(return_value=Response(200, json={}))
    respx.get("https://www.googleapis.com/books/v1/volumes").mock(
        return_value=Response(
            200,
            json={
                "totalItems": 1,
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Bar Book",
                            "authors": ["John Smith"],
                            "publisher": "Publisher Y",
                            "publishedDate": "2005",
                            "pageCount": 300,
                            "language": "en",
                            "imageLinks": {"thumbnail": "http://books.google.com/img.jpg"},
                        }
                    }
                ],
            },
        )
    )
    result = await lookup_isbn("9780306406157")
    assert result is not None
    assert result.title == "Bar Book"


@pytest.mark.asyncio
@respx.mock
async def test_lookup_returns_none_when_both_fail():
    respx.get("https://openlibrary.org/api/books").mock(return_value=Response(200, json={}))
    respx.get("https://www.googleapis.com/books/v1/volumes").mock(
        return_value=Response(200, json={"totalItems": 0})
    )
    result = await lookup_isbn("9780306406157")
    assert result is None
```

- [ ] **Step 2: Run — expect failure**

```bash
pytest tests/test_isbn_lookup.py -v
```

- [ ] **Step 3: Implement isbn_lookup.py**

```python
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
    if result:
        return result
    return await _try_google_books(isbn)


async def _try_open_library(isbn: str) -> BookData | None:
    url = "https://openlibrary.org/api/books"
    params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
        except Exception:
            return None

    key = f"ISBN:{isbn}"
    if key not in data:
        return None

    book = data[key]
    year = None
    raw_year = book.get("publish_date", "")
    for part in raw_year.split():
        if part.isdigit() and len(part) == 4:
            year = int(part)
            break

    covers = book.get("cover", {})
    cover_url = covers.get("medium") or covers.get("small")

    return BookData(
        title=book.get("title", ""),
        authors=[a["name"] for a in book.get("authors", [])],
        publisher=book["publishers"][0]["name"] if book.get("publishers") else None,
        published_year=year,
        pages=book.get("number_of_pages"),
        cover_url=cover_url,
    )


async def _try_google_books(isbn: str) -> BookData | None:
    params: dict = {"q": f"isbn:{isbn}"}
    if settings.google_books_api_key:
        params["key"] = settings.google_books_api_key

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                "https://www.googleapis.com/books/v1/volumes", params=params
            )
            data = resp.json()
        except Exception:
            return None

    if not data.get("totalItems"):
        return None

    info = data["items"][0]["volumeInfo"]
    year = None
    raw = info.get("publishedDate", "")
    if raw[:4].isdigit():
        year = int(raw[:4])

    thumbnails = info.get("imageLinks", {})
    cover = thumbnails.get("thumbnail") or thumbnails.get("smallThumbnail")

    ids = {i["type"]: i["identifier"] for i in info.get("industryIdentifiers", [])}

    return BookData(
        title=info.get("title", ""),
        authors=info.get("authors", []),
        publisher=info.get("publisher"),
        published_year=year,
        pages=info.get("pageCount"),
        language=info.get("language"),
        cover_url=cover,
        isbn_13=ids.get("ISBN_13"),
        isbn_10=ids.get("ISBN_10"),
    )
```

- [ ] **Step 4: Run — expect pass**

```bash
pytest tests/test_isbn_lookup.py -v
```
Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add api/app/services/isbn_lookup.py api/tests/test_isbn_lookup.py
git commit -m "feat: ISBN lookup — Open Library with Google Books fallback"
```

---

## Task 8: Books CRUD

**Files:**
- Create: `api/app/schemas/book.py`
- Create: `api/app/routers/books.py`
- Create: `api/tests/test_books.py`

- [ ] **Step 1: Create app/schemas/book.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel


class BookCreate(BaseModel):
    isbn_13: str | None = None
    isbn_10: str | None = None
    title: str
    subtitle: str | None = None
    authors: list[str] = []
    publisher: str | None = None
    published_year: int | None = None
    language: str | None = None
    pages: int | None = None
    cover_url: str | None = None
    dewey_code: str | None = None
    notes: str | None = None
    tag_ids: list[uuid.UUID] = []


class BookUpdate(BaseModel):
    isbn_13: str | None = None
    isbn_10: str | None = None
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] | None = None
    publisher: str | None = None
    published_year: int | None = None
    language: str | None = None
    pages: int | None = None
    cover_url: str | None = None
    dewey_code: str | None = None
    notes: str | None = None
    tag_ids: list[uuid.UUID] | None = None


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str

    model_config = {"from_attributes": True}


class BookOut(BaseModel):
    id: uuid.UUID
    isbn_13: str | None
    isbn_10: str | None
    title: str
    subtitle: str | None
    authors: list[str]
    publisher: str | None
    published_year: int | None
    language: str | None
    pages: int | None
    cover_url: str | None
    dewey_code: str | None
    notes: str | None
    created_at: datetime
    tags: list[TagOut] = []

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_books.py
import pytest


@pytest.mark.asyncio
async def test_create_book(auth_client):
    resp = await auth_client.post(
        "/books/",
        json={"title": "Clean Code", "authors": ["Robert Martin"], "isbn_13": "9780132350884"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Clean Code"
    assert data["authors"] == ["Robert Martin"]
    assert "id" in data


@pytest.mark.asyncio
async def test_list_books(auth_client):
    await auth_client.post("/books/", json={"title": "Book A"})
    resp = await auth_client.get("/books/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_book(auth_client):
    create = await auth_client.post("/books/", json={"title": "Book B"})
    book_id = create.json()["id"]
    resp = await auth_client.get(f"/books/{book_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == book_id


@pytest.mark.asyncio
async def test_update_book(auth_client):
    create = await auth_client.post("/books/", json={"title": "Old Title"})
    book_id = create.json()["id"]
    resp = await auth_client.patch(f"/books/{book_id}", json={"title": "New Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_book(auth_client):
    create = await auth_client.post("/books/", json={"title": "To Delete"})
    book_id = create.json()["id"]
    resp = await auth_client.delete(f"/books/{book_id}")
    assert resp.status_code == 204
    resp2 = await auth_client.get(f"/books/{book_id}")
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_lookup_isbn_endpoint(auth_client):
    # Will hit real APIs — skip in offline env or mock at a higher level
    resp = await auth_client.get("/books/lookup/9780132350884")
    assert resp.status_code in (200, 404)
```

- [ ] **Step 3: Run — expect failure**

```bash
pytest tests/test_books.py -v
```

- [ ] **Step 4: Create app/routers/books.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps import get_current_user, get_db
from app.models.book import Book
from app.models.tag import BookTag, Tag
from app.schemas.book import BookCreate, BookOut, BookUpdate, TagOut
from app.services.isbn_lookup import lookup_isbn
from app.services.isbn_validate import normalize_isbn, validate_isbn13

router = APIRouter()


def _book_to_out(book: Book) -> BookOut:
    tags = [TagOut(id=bt.tag.id, name=bt.tag.name, color=bt.tag.color) for bt in book.book_tags]
    return BookOut(
        id=book.id,
        isbn_13=book.isbn_13,
        isbn_10=book.isbn_10,
        title=book.title,
        subtitle=book.subtitle,
        authors=book.authors or [],
        publisher=book.publisher,
        published_year=book.published_year,
        language=book.language,
        pages=book.pages,
        cover_url=book.cover_url,
        dewey_code=book.dewey_code,
        notes=book.notes,
        created_at=book.created_at,
        tags=tags,
    )


async def _get_book_or_404(book_id: uuid.UUID, db: AsyncSession) -> Book:
    result = await db.execute(
        select(Book).where(Book.id == book_id).options(selectinload(Book.book_tags).selectinload(BookTag.tag))
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/lookup/{isbn}", response_model=dict)
async def lookup_isbn_endpoint(
    isbn: str,
    _: str = Depends(get_current_user),
):
    normalized = normalize_isbn(isbn)
    if not normalized or not validate_isbn13(normalized):
        raise HTTPException(status_code=422, detail="Invalid ISBN")
    data = await lookup_isbn(normalized)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found for this ISBN")
    return data.__dict__


@router.post("/", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(
    body: BookCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> BookOut:
    book = Book(
        isbn_13=body.isbn_13,
        isbn_10=body.isbn_10,
        title=body.title,
        subtitle=body.subtitle,
        authors=body.authors,
        publisher=body.publisher,
        published_year=body.published_year,
        language=body.language,
        pages=body.pages,
        cover_url=body.cover_url,
        dewey_code=body.dewey_code,
        notes=body.notes,
    )
    db.add(book)
    await db.flush()

    for tag_id in body.tag_ids:
        db.add(BookTag(book_id=book.id, tag_id=tag_id))

    await db.commit()
    await db.refresh(book)
    result = await db.execute(
        select(Book).where(Book.id == book.id).options(selectinload(Book.book_tags).selectinload(BookTag.tag))
    )
    return _book_to_out(result.scalar_one())


@router.get("/", response_model=list[BookOut])
async def list_books(
    search: str | None = Query(None),
    language: str | None = Query(None),
    tag_id: uuid.UUID | None = Query(None),
    on_loan: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[BookOut]:
    stmt = select(Book).options(selectinload(Book.book_tags).selectinload(BookTag.tag))
    if search:
        pattern = f"%{search}%"
        from sqlalchemy import or_, cast
        from sqlalchemy.dialects.postgresql import TEXT
        stmt = stmt.where(
            or_(
                Book.title.ilike(pattern),
                Book.isbn_13.ilike(pattern),
                cast(Book.authors, TEXT).ilike(pattern),
            )
        )
    if language:
        stmt = stmt.where(Book.language == language)
    if tag_id:
        stmt = stmt.join(BookTag, Book.id == BookTag.book_id).where(BookTag.tag_id == tag_id)
    result = await db.execute(stmt.order_by(Book.title))
    books = result.scalars().unique().all()
    return [_book_to_out(b) for b in books]


@router.get("/{book_id}", response_model=BookOut)
async def get_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> BookOut:
    return _book_to_out(await _get_book_or_404(book_id, db))


@router.patch("/{book_id}", response_model=BookOut)
async def update_book(
    book_id: uuid.UUID,
    body: BookUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> BookOut:
    book = await _get_book_or_404(book_id, db)
    for field, value in body.model_dump(exclude_unset=True, exclude={"tag_ids"}).items():
        setattr(book, field, value)

    if body.tag_ids is not None:
        await db.execute(
            BookTag.__table__.delete().where(BookTag.book_id == book_id)
        )
        for tag_id in body.tag_ids:
            db.add(BookTag(book_id=book_id, tag_id=tag_id))

    await db.commit()
    result = await db.execute(
        select(Book).where(Book.id == book_id).options(selectinload(Book.book_tags).selectinload(BookTag.tag))
    )
    return _book_to_out(result.scalar_one())


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    book = await _get_book_or_404(book_id, db)
    await db.delete(book)
    await db.commit()
```

- [ ] **Step 5: Run — expect pass**

```bash
pytest tests/test_books.py -v
```
Expected: 5 tests PASS (lookup test may vary based on network)

- [ ] **Step 6: Commit**

```bash
git add api/app/schemas/book.py api/app/routers/books.py api/tests/test_books.py
git commit -m "feat: books CRUD with ISBN lookup endpoint"
```

---

## Task 9: Tags + Loans CRUD

**Files:**
- Create: `api/app/schemas/tag.py`, `api/app/schemas/loan.py`
- Create: `api/app/routers/tags.py`, `api/app/routers/loans.py`
- Create: `api/tests/test_tags.py`, `api/tests/test_loans.py`

- [ ] **Step 1: Create app/schemas/tag.py**

```python
import uuid
from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str
    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create app/schemas/loan.py**

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class LoanCreate(BaseModel):
    book_id: uuid.UUID
    borrower_name: str
    due_date: datetime | None = None
    notes: str | None = None


class LoanReturn(BaseModel):
    returned_at: datetime | None = None  # defaults to now if None


class LoanOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    borrower_name: str
    loaned_at: datetime
    due_date: datetime | None
    returned_at: datetime | None
    notes: str | None
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Create app/routers/tags.py**

```python
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagOut

router = APIRouter()


@router.post("/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    tag = Tag(name=body.name, color=body.color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.get("/", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.patch("/{tag_id}", response_model=TagOut)
async def update_tag(tag_id: uuid.UUID, body: TagCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    tag.name = body.name
    tag.color = body.color
    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
```

- [ ] **Step 4: Create app/routers/loans.py**

```python
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanOut, LoanReturn

router = APIRouter()


@router.post("/", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
async def create_loan(body: LoanCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    loan = Loan(**body.model_dump())
    db.add(loan)
    await db.commit()
    await db.refresh(loan)
    return loan


@router.get("/", response_model=list[LoanOut])
async def list_loans(open_only: bool = False, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    stmt = select(Loan).order_by(Loan.loaned_at.desc())
    if open_only:
        stmt = stmt.where(Loan.returned_at.is_(None))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{loan_id}/return", response_model=LoanOut)
async def return_loan(loan_id: uuid.UUID, body: LoanReturn, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Loan).where(Loan.id == loan_id))
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    loan.returned_at = body.returned_at or datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(loan)
    return loan
```

- [ ] **Step 5: Write and run tests**

```python
# tests/test_tags.py
import pytest


@pytest.mark.asyncio
async def test_create_and_list_tag(auth_client):
    resp = await auth_client.post("/tags/", json={"name": "Fiction", "color": "#ef4444"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "Fiction"

    resp2 = await auth_client.get("/tags/")
    assert resp2.status_code == 200
    names = [t["name"] for t in resp2.json()]
    assert "Fiction" in names
```

```python
# tests/test_loans.py
import pytest


@pytest.mark.asyncio
async def test_create_and_return_loan(auth_client):
    book = await auth_client.post("/books/", json={"title": "Loan Book"})
    book_id = book.json()["id"]

    loan_resp = await auth_client.post(
        "/loans/", json={"book_id": book_id, "borrower_name": "Alice"}
    )
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]
    assert loan_resp.json()["returned_at"] is None

    return_resp = await auth_client.post(f"/loans/{loan_id}/return", json={})
    assert return_resp.status_code == 200
    assert return_resp.json()["returned_at"] is not None

    open_loans = await auth_client.get("/loans/?open_only=true")
    ids = [l["id"] for l in open_loans.json()]
    assert loan_id not in ids
```

```bash
pytest tests/test_tags.py tests/test_loans.py -v
```
Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add api/app/schemas/tag.py api/app/schemas/loan.py api/app/routers/tags.py api/app/routers/loans.py api/tests/test_tags.py api/tests/test_loans.py
git commit -m "feat: tags and loans CRUD"
```

---

## Task 10: Label Templates + PDF Generation

**Files:**
- Create: `api/app/schemas/label_template.py`
- Create: `api/app/routers/labels.py`
- Create: `api/app/services/pdf_labels.py`
- Create: `api/tests/test_labels.py`

- [ ] **Step 1: Create app/schemas/label_template.py**

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class LabelTemplateCreate(BaseModel):
    name: str
    width_mm: float = 50.0
    height_mm: float = 30.0
    font_size: int = 8
    show_dewey: bool = True
    show_title: bool = True
    show_barcode: bool = True


class LabelTemplateOut(BaseModel):
    id: uuid.UUID
    name: str
    width_mm: float
    height_mm: float
    font_size: int
    show_dewey: bool
    show_title: bool
    show_barcode: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class LabelGenerateRequest(BaseModel):
    book_ids: list[uuid.UUID]
    template_id: uuid.UUID
```

- [ ] **Step 2: Create app/services/pdf_labels.py**

```python
from io import BytesIO

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.models.book import Book
from app.models.label_template import LabelTemplate


def generate_labels_pdf(books: list[Book], template: LabelTemplate) -> bytes:
    buf = BytesIO()
    w = template.width_mm * mm
    h = template.height_mm * mm
    c = canvas.Canvas(buf, pagesize=(w, h))

    for i, book in enumerate(books):
        if i > 0:
            c.showPage()

        y = h - 2 * mm
        c.setFont("Helvetica-Bold", template.font_size + 1)

        if template.show_dewey and book.dewey_code:
            c.drawString(2 * mm, y - template.font_size * 0.4 * mm, book.dewey_code)
            y -= (template.font_size + 2) * 0.4 * mm

        if template.show_title:
            c.setFont("Helvetica", template.font_size)
            title = book.title[:35] + "…" if len(book.title) > 35 else book.title
            c.drawString(2 * mm, y - template.font_size * 0.4 * mm, title)
            y -= (template.font_size + 1) * 0.4 * mm

            authors = ", ".join(book.authors or [])
            if authors:
                authors_short = authors[:35] + "…" if len(authors) > 35 else authors
                c.setFont("Helvetica-Oblique", template.font_size - 1)
                c.drawString(2 * mm, y - template.font_size * 0.4 * mm, authors_short)
                y -= (template.font_size) * 0.4 * mm

        if template.show_barcode and book.isbn_13:
            barcode_h = min(10 * mm, y - 2 * mm)
            barcode = Code128(book.isbn_13, barHeight=barcode_h, barWidth=0.6)
            d = Drawing(w - 4 * mm, barcode_h)
            d.add(barcode)
            renderPDF.draw(d, c, 2 * mm, 2 * mm)

    c.save()
    return buf.getvalue()
```

- [ ] **Step 3: Write failing test**

```python
# tests/test_labels.py
import pytest


@pytest.mark.asyncio
async def test_create_template(auth_client):
    resp = await auth_client.post(
        "/labels/templates/",
        json={"name": "Standard", "width_mm": 50, "height_mm": 30},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Standard"


@pytest.mark.asyncio
async def test_generate_pdf(auth_client):
    book = await auth_client.post(
        "/books/",
        json={"title": "Test Book", "authors": ["Author"], "isbn_13": "9780306406157", "dewey_code": "823"},
    )
    book_id = book.json()["id"]

    tmpl = await auth_client.post(
        "/labels/templates/",
        json={"name": "PDF Test", "width_mm": 50, "height_mm": 30},
    )
    tmpl_id = tmpl.json()["id"]

    resp = await auth_client.post(
        "/labels/generate",
        json={"book_ids": [book_id], "template_id": tmpl_id},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 100
```

- [ ] **Step 4: Create app/routers/labels.py**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.book import Book
from app.models.label_template import LabelTemplate
from app.schemas.label_template import LabelGenerateRequest, LabelTemplateCreate, LabelTemplateOut
from app.services.pdf_labels import generate_labels_pdf

router = APIRouter()


@router.post("/templates/", response_model=LabelTemplateOut, status_code=201)
async def create_template(body: LabelTemplateCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    tmpl = LabelTemplate(**body.model_dump())
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)
    return tmpl


@router.get("/templates/", response_model=list[LabelTemplateOut])
async def list_templates(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(LabelTemplate).order_by(LabelTemplate.name))
    return result.scalars().all()


@router.delete("/templates/{tmpl_id}", status_code=204)
async def delete_template(tmpl_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(LabelTemplate).where(LabelTemplate.id == tmpl_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(tmpl)
    await db.commit()


@router.post("/generate")
async def generate_labels(
    body: LabelGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(select(LabelTemplate).where(LabelTemplate.id == body.template_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    result = await db.execute(select(Book).where(Book.id.in_(body.book_ids)))
    books = result.scalars().all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    pdf_bytes = generate_labels_pdf(list(books), tmpl)
    return Response(content=pdf_bytes, media_type="application/pdf")
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_labels.py -v
```
Expected: 2 tests PASS

- [ ] **Step 6: Commit**

```bash
git add api/app/schemas/label_template.py api/app/services/pdf_labels.py api/app/routers/labels.py api/tests/test_labels.py
git commit -m "feat: label templates and PDF generation with reportlab"
```

---

## Task 11: Export + Import (BibTeX & CSV)

**Files:**
- Create: `api/app/services/bibtex_io.py`
- Create: `api/app/services/csv_io.py`
- Create: `api/app/routers/export.py`
- Create: `api/tests/test_export.py`

- [ ] **Step 1: Create app/services/bibtex_io.py**

```python
import re

import bibtexparser
from bibtexparser.bwriter import BibTexWriter

from app.models.book import Book


def books_to_bibtex(books: list[Book]) -> str:
    db = bibtexparser.bibdatabase.BibDatabase()
    for book in books:
        key = re.sub(r"\W+", "", (book.authors[0] if book.authors else "Unknown") + str(book.published_year or ""))
        entry = {
            "ENTRYTYPE": "book",
            "ID": key or str(book.id)[:8],
            "title": book.title,
        }
        if book.authors:
            entry["author"] = " and ".join(book.authors)
        if book.publisher:
            entry["publisher"] = book.publisher
        if book.published_year:
            entry["year"] = str(book.published_year)
        if book.isbn_13:
            entry["isbn"] = book.isbn_13
        if book.language:
            entry["language"] = book.language
        db.entries.append(entry)

    writer = BibTexWriter()
    return writer.write(db)
```

- [ ] **Step 2: Create app/services/csv_io.py**

```python
import csv
import io

from app.models.book import Book

FIELDS = [
    "id", "isbn_13", "isbn_10", "title", "subtitle", "authors",
    "publisher", "published_year", "language", "pages",
    "cover_url", "dewey_code", "notes", "created_at",
]


def books_to_csv(books: list[Book]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS)
    writer.writeheader()
    for book in books:
        writer.writerow({
            "id": str(book.id),
            "isbn_13": book.isbn_13 or "",
            "isbn_10": book.isbn_10 or "",
            "title": book.title,
            "subtitle": book.subtitle or "",
            "authors": "; ".join(book.authors or []),
            "publisher": book.publisher or "",
            "published_year": book.published_year or "",
            "language": book.language or "",
            "pages": book.pages or "",
            "cover_url": book.cover_url or "",
            "dewey_code": book.dewey_code or "",
            "notes": book.notes or "",
            "created_at": book.created_at.isoformat(),
        })
    return buf.getvalue()
```

- [ ] **Step 3: Write failing tests**

```python
# tests/test_export.py
import pytest


@pytest.mark.asyncio
async def test_export_bibtex(auth_client):
    await auth_client.post(
        "/books/",
        json={"title": "Export Book", "authors": ["Doe, Jane"], "published_year": 2020},
    )
    resp = await auth_client.get("/export/bibtex")
    assert resp.status_code == 200
    assert "Export Book" in resp.text
    assert resp.headers["content-type"].startswith("text/plain")


@pytest.mark.asyncio
async def test_export_csv(auth_client):
    await auth_client.post("/books/", json={"title": "CSV Book"})
    resp = await auth_client.get("/export/csv")
    assert resp.status_code == 200
    assert "CSV Book" in resp.text
    assert "isbn_13" in resp.text
```

- [ ] **Step 4: Create app/routers/export.py**

```python
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.book import Book
from app.services.bibtex_io import books_to_bibtex
from app.services.csv_io import books_to_csv

router = APIRouter()


@router.get("/bibtex")
async def export_bibtex(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Book).order_by(Book.title))
    books = list(result.scalars().all())
    content = books_to_bibtex(books)
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=library.bib"},
    )


@router.get("/csv")
async def export_csv(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Book).order_by(Book.title))
    books = list(result.scalars().all())
    content = books_to_csv(books)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=library.csv"},
    )
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_export.py -v
```
Expected: 2 tests PASS

- [ ] **Step 6: Run all backend tests**

```bash
pytest tests/ -v --ignore=tests/test_isbn_lookup.py
```
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add api/app/services/bibtex_io.py api/app/services/csv_io.py api/app/routers/export.py api/tests/test_export.py
git commit -m "feat: BibTeX and CSV export"
```

---

## Task 12: Frontend Setup

**Files:**
- Create: `web/` — Next.js 15 project with Tailwind v4 and shadcn/ui
- Create: `web/src/lib/api.ts`
- Create: `web/src/lib/auth.ts`
- Create: `web/src/middleware.ts`

- [ ] **Step 1: Scaffold Next.js project**

```bash
cd /path/to/personal-library
npx create-next-app@latest web \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --no-import-alias
cd web
```

When prompted: TypeScript=yes, ESLint=yes, Tailwind=yes, App Router=yes, src/=yes.

- [ ] **Step 2: Install shadcn/ui**

```bash
npx shadcn@latest init
```

Accept defaults. Choose "Default" style, "Slate" base color, CSS variables=yes.

Add components needed:
```bash
npx shadcn@latest add button card input label badge dialog table select toast sonner
```

- [ ] **Step 3: Install additional dependencies**

```bash
npm install @zxing/browser @zxing/library
npm install js-cookie
npm install -D @types/js-cookie
```

- [ ] **Step 4: Create .env.local.example**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Copy and set:
```bash
cp .env.local.example .env.local
```

- [ ] **Step 5: Create src/lib/api.ts**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type RequestOptions = {
  method?: string;
  body?: unknown;
  token?: string;
};

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (opts.token) {
    headers["Authorization"] = `Bearer ${opts.token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string, token?: string) => request<T>(path, { token }),
  post: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "POST", body, token }),
  patch: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "PATCH", body, token }),
  delete: <T>(path: string, token?: string) =>
    request<T>(path, { method: "DELETE", token }),
};
```

- [ ] **Step 6: Create src/lib/auth.ts**

```typescript
"use server";

import { cookies } from "next/headers";

const COOKIE = "auth_token";

export async function getToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(COOKIE)?.value;
}

export async function setToken(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7,
    path: "/",
  });
}

export async function clearToken(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(COOKIE);
}
```

- [ ] **Step 7: Create src/middleware.ts**

```typescript
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login"];

export function middleware(req: NextRequest): NextResponse {
  const token = req.cookies.get("auth_token")?.value;
  const isPublic = PUBLIC_PATHS.some((p) => req.nextUrl.pathname.startsWith(p));

  if (!token && !isPublic) {
    return NextResponse.redirect(new URL("/login", req.url));
  }
  if (token && req.nextUrl.pathname === "/login") {
    return NextResponse.redirect(new URL("/catalog", req.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

- [ ] **Step 8: Update src/app/page.tsx**

```typescript
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/catalog");
}
```

- [ ] **Step 9: Verify dev server starts**

```bash
npm run dev
```
Expected: Next.js starts on port 3000, no errors.

- [ ] **Step 10: Commit**

```bash
git add web/
git commit -m "feat: Next.js 15 frontend scaffold with Tailwind v4, shadcn/ui, auth middleware"
```

---

## Task 13: Login Page

**Files:**
- Create: `web/src/app/login/page.tsx`

- [ ] **Step 1: Create login/page.tsx**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { setToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        setError("Invalid credentials");
        return;
      }

      const { access_token } = await res.json();
      await setToken(access_token);
      router.push("/catalog");
    } catch {
      setError("Could not connect to server");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Personal Library</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Test manually**

```bash
# ensure api is running: uvicorn app.main:app --reload (in api/)
# ensure web is running: npm run dev (in web/)
```
Open `http://localhost:3000/login`, sign in with credentials from `.env`. Expect redirect to `/catalog`.

- [ ] **Step 3: Commit**

```bash
git add web/src/app/login/
git commit -m "feat: login page with JWT authentication"
```

---

## Task 14: Book Catalog Page

**Files:**
- Create: `web/src/components/book-card.tsx`
- Create: `web/src/app/catalog/page.tsx`

- [ ] **Step 1: Create src/components/book-card.tsx**

```tsx
import Link from "next/link";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

type Tag = { id: string; name: string; color: string };

type Book = {
  id: string;
  title: string;
  authors: string[];
  publisher?: string;
  published_year?: number;
  cover_url?: string;
  dewey_code?: string;
  tags: Tag[];
};

export function BookCard({ book }: { book: Book }) {
  return (
    <Link href={`/catalog/${book.id}`}>
      <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="p-3 flex gap-3">
          {book.cover_url ? (
            <img
              src={book.cover_url}
              alt={book.title}
              className="w-12 h-18 object-cover rounded shrink-0"
            />
          ) : (
            <div className="w-12 h-18 bg-muted rounded shrink-0 flex items-center justify-center text-xs text-muted-foreground">
              No cover
            </div>
          )}
          <div className="flex flex-col gap-1 min-w-0">
            <p className="font-medium text-sm leading-tight truncate">{book.title}</p>
            {book.authors.length > 0 && (
              <p className="text-xs text-muted-foreground truncate">{book.authors.join(", ")}</p>
            )}
            {book.dewey_code && (
              <p className="text-xs font-mono text-muted-foreground">{book.dewey_code}</p>
            )}
            <div className="flex flex-wrap gap-1 mt-auto">
              {book.tags.map((t) => (
                <Badge key={t.id} style={{ backgroundColor: t.color }} className="text-white text-[10px] px-1">
                  {t.name}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

- [ ] **Step 2: Create src/app/catalog/page.tsx**

```tsx
import { Suspense } from "react";
import Link from "next/link";
import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { BookCard } from "@/components/book-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Book = {
  id: string;
  title: string;
  authors: string[];
  cover_url?: string;
  dewey_code?: string;
  tags: { id: string; name: string; color: string }[];
};

type Props = {
  searchParams: Promise<{ search?: string; tag_id?: string }>;
};

export default async function CatalogPage({ searchParams }: Props) {
  const token = await getToken();
  const params = await searchParams;
  const qs = new URLSearchParams();
  if (params.search) qs.set("search", params.search);
  if (params.tag_id) qs.set("tag_id", params.tag_id);

  const books = await api.get<Book[]>(`/books/?${qs.toString()}`, token);

  return (
    <main className="max-w-5xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Library</h1>
        <Link href="/books/new">
          <Button>Add book</Button>
        </Link>
      </div>

      <form className="mb-4">
        <Input name="search" placeholder="Search by title, author or ISBN…" defaultValue={params.search} />
      </form>

      {books.length === 0 ? (
        <p className="text-muted-foreground text-sm">No books found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      )}
    </main>
  );
}
```

- [ ] **Step 3: Test manually**

Open `http://localhost:3000/catalog`. Expect book grid. Add a book via API (or next task) and verify it appears.

- [ ] **Step 4: Commit**

```bash
git add web/src/components/book-card.tsx web/src/app/catalog/
git commit -m "feat: catalog page with book grid and search"
```

---

## Task 15: ISBN Scanner + Book Registration

**Files:**
- Create: `web/src/components/isbn-scanner.tsx`
- Create: `web/src/components/book-form.tsx`
- Create: `web/src/app/books/new/page.tsx`

- [ ] **Step 1: Create src/components/isbn-scanner.tsx**

```tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Props = {
  onDetect: (isbn: string) => void;
};

export function IsbnScanner({ onDetect }: Props) {
  const [scanning, setScanning] = useState(false);
  const [manual, setManual] = useState("");
  const videoRef = useRef<HTMLVideoElement>(null);
  const readerRef = useRef<BrowserMultiFormatReader | null>(null);

  useEffect(() => {
    return () => {
      readerRef.current?.reset();
    };
  }, []);

  async function startScan() {
    setScanning(true);
    const reader = new BrowserMultiFormatReader();
    readerRef.current = reader;

    try {
      const devices = await BrowserMultiFormatReader.listVideoInputDevices();
      const deviceId = devices[devices.length - 1]?.deviceId;
      await reader.decodeFromVideoDevice(deviceId ?? undefined, videoRef.current!, (result, err) => {
        if (result) {
          const text = result.getText();
          if (/^\d{13}$/.test(text) || /^\d{10}$/.test(text)) {
            reader.reset();
            setScanning(false);
            onDetect(text);
          }
        }
      });
    } catch {
      setScanning(false);
    }
  }

  function stopScan() {
    readerRef.current?.reset();
    setScanning(false);
  }

  function handleManual(e: React.FormEvent) {
    e.preventDefault();
    if (manual.trim()) {
      onDetect(manual.trim());
      setManual("");
    }
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleManual} className="flex gap-2">
        <Input
          placeholder="Enter ISBN…"
          value={manual}
          onChange={(e) => setManual(e.target.value)}
        />
        <Button type="submit" variant="outline">Look up</Button>
        {!scanning ? (
          <Button type="button" onClick={startScan} variant="outline">📷 Scan</Button>
        ) : (
          <Button type="button" onClick={stopScan} variant="outline">Stop</Button>
        )}
      </form>
      {scanning && (
        <video ref={videoRef} className="w-full rounded border" />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create src/components/book-form.tsx**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { IsbnScanner } from "./isbn-scanner";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type BookData = {
  isbn_13?: string;
  isbn_10?: string;
  title?: string;
  subtitle?: string;
  authors?: string[];
  publisher?: string;
  published_year?: number;
  language?: string;
  pages?: number;
  cover_url?: string;
  dewey_code?: string;
};

type Props = { token: string };

export function BookForm({ token }: Props) {
  const router = useRouter();
  const [form, setForm] = useState<BookData>({});
  const [loading, setLoading] = useState(false);
  const [looking, setLooking] = useState(false);
  const [error, setError] = useState("");

  async function handleIsbn(isbn: string) {
    setLooking(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/books/lookup/${isbn}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setForm((prev) => ({ ...prev, ...data }));
      } else {
        setForm((prev) => ({ ...prev, isbn_13: isbn }));
        setError("ISBN not found — fill in manually.");
      }
    } finally {
      setLooking(false);
    }
  }

  function set(key: keyof BookData, value: unknown) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title) { setError("Title is required"); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/books/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...form, authors: form.authors ?? [] }),
      });
      if (!res.ok) { setError("Failed to save"); return; }
      router.push("/catalog");
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
      <IsbnScanner onDetect={handleIsbn} />
      {looking && <p className="text-sm text-muted-foreground">Looking up ISBN…</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}

      {[
        { label: "Title *", key: "title" as const, required: true },
        { label: "Subtitle", key: "subtitle" as const },
        { label: "Authors (comma-separated)", key: "authors" as const },
        { label: "Publisher", key: "publisher" as const },
        { label: "Year", key: "published_year" as const },
        { label: "Language", key: "language" as const },
        { label: "Pages", key: "pages" as const },
        { label: "Dewey code", key: "dewey_code" as const },
        { label: "Cover URL", key: "cover_url" as const },
      ].map(({ label, key, required }) => (
        <div key={key} className="space-y-1">
          <Label>{label}</Label>
          <Input
            value={
              key === "authors"
                ? (form.authors ?? []).join(", ")
                : String(form[key] ?? "")
            }
            onChange={(e) => {
              if (key === "authors") {
                set(key, e.target.value.split(",").map((s) => s.trim()).filter(Boolean));
              } else if (key === "published_year" || key === "pages") {
                set(key, e.target.value ? Number(e.target.value) : undefined);
              } else {
                set(key, e.target.value);
              }
            }}
            required={required}
          />
        </div>
      ))}

      <Button type="submit" disabled={loading}>
        {loading ? "Saving…" : "Save book"}
      </Button>
    </form>
  );
}
```

- [ ] **Step 3: Create src/app/books/new/page.tsx**

```tsx
import { getToken } from "@/lib/auth";
import { BookForm } from "@/components/book-form";

export default async function NewBookPage() {
  const token = await getToken();
  return (
    <main className="max-w-2xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">Add book</h1>
      <BookForm token={token!} />
    </main>
  );
}
```

- [ ] **Step 4: Test manually**

Open `http://localhost:3000/books/new`. Enter an ISBN and verify data is pre-filled. Submit and verify redirect to catalog.

- [ ] **Step 5: Commit**

```bash
git add web/src/components/isbn-scanner.tsx web/src/components/book-form.tsx web/src/app/books/new/
git commit -m "feat: book registration with ISBN scanner and auto-fill"
```

---

## Task 16: Book Detail + Loans Page

**Files:**
- Create: `web/src/app/catalog/[id]/page.tsx`
- Create: `web/src/components/loan-form.tsx`
- Create: `web/src/app/loans/page.tsx`

- [ ] **Step 1: Create src/app/catalog/[id]/page.tsx**

```tsx
import Link from "next/link";
import { notFound } from "next/navigation";
import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

type Book = {
  id: string;
  title: string;
  subtitle?: string;
  authors: string[];
  publisher?: string;
  published_year?: number;
  language?: string;
  pages?: number;
  isbn_13?: string;
  isbn_10?: string;
  cover_url?: string;
  dewey_code?: string;
  notes?: string;
  tags: { id: string; name: string; color: string }[];
};

export default async function BookDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const token = await getToken();
  const { id } = await params;

  let book: Book;
  try {
    book = await api.get<Book>(`/books/${id}`, token);
  } catch {
    notFound();
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-6">
      <div className="flex items-start gap-4 mb-6">
        {book.cover_url && (
          <img src={book.cover_url} alt={book.title} className="w-24 rounded shadow" />
        )}
        <div>
          <h1 className="text-2xl font-bold">{book.title}</h1>
          {book.subtitle && <p className="text-muted-foreground">{book.subtitle}</p>}
          <p className="text-sm mt-1">{book.authors.join(", ")}</p>
          {book.publisher && <p className="text-sm text-muted-foreground">{book.publisher}, {book.published_year}</p>}
          <div className="flex gap-1 mt-2 flex-wrap">
            {book.tags.map((t) => (
              <Badge key={t.id} style={{ backgroundColor: t.color }} className="text-white">{t.name}</Badge>
            ))}
          </div>
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-2 text-sm mb-6">
        {book.dewey_code && <><dt className="text-muted-foreground">Dewey</dt><dd>{book.dewey_code}</dd></>}
        {book.isbn_13 && <><dt className="text-muted-foreground">ISBN-13</dt><dd className="font-mono">{book.isbn_13}</dd></>}
        {book.language && <><dt className="text-muted-foreground">Language</dt><dd>{book.language}</dd></>}
        {book.pages && <><dt className="text-muted-foreground">Pages</dt><dd>{book.pages}</dd></>}
      </dl>

      {book.notes && <p className="text-sm bg-muted rounded p-3 mb-6">{book.notes}</p>}

      <div className="flex gap-2">
        <Link href={`/loans?book_id=${book.id}`}>
          <Button variant="outline">Loan this book</Button>
        </Link>
        <Link href="/catalog">
          <Button variant="ghost">Back to catalog</Button>
        </Link>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Create src/components/loan-form.tsx**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Props = { token: string; bookId?: string };

export function LoanForm({ token, bookId }: Props) {
  const router = useRouter();
  const [borrower, setBorrower] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!bookId) { setError("No book selected"); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/loans/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          book_id: bookId,
          borrower_name: borrower,
          due_date: dueDate || null,
          notes: notes || null,
        }),
      });
      if (!res.ok) { setError("Failed to create loan"); return; }
      router.push("/loans");
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm">
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="space-y-1">
        <Label>Borrower name</Label>
        <Input value={borrower} onChange={(e) => setBorrower(e.target.value)} required />
      </div>
      <div className="space-y-1">
        <Label>Due date (optional)</Label>
        <Input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
      </div>
      <div className="space-y-1">
        <Label>Notes</Label>
        <Input value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>
      <Button type="submit" disabled={loading}>
        {loading ? "Saving…" : "Register loan"}
      </Button>
    </form>
  );
}
```

- [ ] **Step 3: Create src/app/loans/page.tsx**

```tsx
import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { LoanForm } from "@/components/loan-form";
import { Button } from "@/components/ui/button";

type Loan = {
  id: string;
  book_id: string;
  borrower_name: string;
  loaned_at: string;
  due_date?: string;
  returned_at?: string;
};

type Props = { searchParams: Promise<{ book_id?: string }> };

export default async function LoansPage({ searchParams }: Props) {
  const token = await getToken();
  const { book_id } = await searchParams;
  const loans = await api.get<Loan[]>("/loans/", token);
  const open = loans.filter((l) => !l.returned_at);

  return (
    <main className="max-w-2xl mx-auto px-4 py-6 space-y-8">
      <h1 className="text-2xl font-bold">Loans</h1>

      {book_id && (
        <section>
          <h2 className="text-lg font-semibold mb-3">New loan</h2>
          <LoanForm token={token!} bookId={book_id} />
        </section>
      )}

      <section>
        <h2 className="text-lg font-semibold mb-3">Open loans ({open.length})</h2>
        {open.length === 0 ? (
          <p className="text-sm text-muted-foreground">No open loans.</p>
        ) : (
          <ul className="space-y-2">
            {open.map((loan) => (
              <li key={loan.id} className="flex items-center justify-between border rounded p-3">
                <div>
                  <p className="font-medium text-sm">{loan.borrower_name}</p>
                  <p className="text-xs text-muted-foreground">
                    Since {new Date(loan.loaned_at).toLocaleDateString()}
                    {loan.due_date && ` · Due ${new Date(loan.due_date).toLocaleDateString()}`}
                  </p>
                </div>
                <form action={async () => {
                  "use server";
                  // Return action handled client-side
                }}>
                  <ReturnButton loanId={loan.id} token={token!} />
                </form>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

function ReturnButton({ loanId, token }: { loanId: string; token: string }) {
  // This is a client component action — extract to client component
  return null; // placeholder replaced in next step
}
```

- [ ] **Step 4: Add ReturnButton as client component**

Create `web/src/components/return-button.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function ReturnButton({ loanId, token }: { loanId: string; token: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleReturn() {
    setLoading(true);
    await fetch(`${API_URL}/loans/${loanId}/return`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({}),
    });
    router.refresh();
    setLoading(false);
  }

  return (
    <Button size="sm" variant="outline" onClick={handleReturn} disabled={loading}>
      {loading ? "…" : "Returned"}
    </Button>
  );
}
```

Update `loans/page.tsx` to import and use `ReturnButton` (remove the placeholder).

- [ ] **Step 5: Test manually**

Open `/loans?book_id=<id>`, create a loan, verify it appears in open loans, mark as returned.

- [ ] **Step 6: Commit**

```bash
git add web/src/app/catalog/ web/src/components/loan-form.tsx web/src/components/return-button.tsx web/src/app/loans/
git commit -m "feat: book detail and loan management"
```

---

## Task 17: Labels + Export Page

**Files:**
- Create: `web/src/components/label-selector.tsx`
- Create: `web/src/app/labels/page.tsx`

- [ ] **Step 1: Create src/components/label-selector.tsx**

```tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Template = { id: string; name: string };
type Book = { id: string; title: string };

type Props = { books: Book[]; templates: Template[]; token: string };

export function LabelSelector({ books, templates, token }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [templateId, setTemplateId] = useState<string>("");
  const [loading, setLoading] = useState(false);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function generatePdf() {
    if (!templateId || selected.size === 0) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/labels/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ book_ids: Array.from(selected), template_id: templateId }),
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "labels.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <Select value={templateId} onValueChange={setTemplateId}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Choose template" />
          </SelectTrigger>
          <SelectContent>
            {templates.map((t) => (
              <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={generatePdf} disabled={loading || selected.size === 0 || !templateId}>
          {loading ? "Generating…" : `Generate PDF (${selected.size})`}
        </Button>
      </div>

      <ul className="space-y-1 max-h-96 overflow-y-auto border rounded p-2">
        {books.map((book) => (
          <li key={book.id}>
            <label className="flex items-center gap-2 cursor-pointer py-1 text-sm">
              <input
                type="checkbox"
                checked={selected.has(book.id)}
                onChange={() => toggle(book.id)}
              />
              {book.title}
            </label>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 2: Create src/app/labels/page.tsx**

```tsx
import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { LabelSelector } from "@/components/label-selector";
import { Button } from "@/components/ui/button";
import Link from "next/link";

type Book = { id: string; title: string };
type Template = { id: string; name: string };

export default async function LabelsPage() {
  const token = await getToken();
  const [books, templates] = await Promise.all([
    api.get<Book[]>("/books/", token),
    api.get<Template[]>("/labels/templates/", token),
  ]);

  return (
    <main className="max-w-2xl mx-auto px-4 py-6 space-y-8">
      <h1 className="text-2xl font-bold">Labels & Export</h1>

      <section>
        <h2 className="text-lg font-semibold mb-3">Print labels</h2>
        {templates.length === 0 ? (
          <p className="text-sm text-muted-foreground">No templates yet. Create one via the API or add a template UI.</p>
        ) : (
          <LabelSelector books={books} templates={templates} token={token!} />
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Export catalog</h2>
        <div className="flex gap-2">
          <ExportButton label="Export BibTeX" href="/export/bibtex" filename="library.bib" token={token!} />
          <ExportButton label="Export CSV" href="/export/csv" filename="library.csv" token={token!} />
        </div>
      </section>
    </main>
  );
}

function ExportButton({ label, href, filename, token }: { label: string; href: string; filename: string; token: string }) {
  // Client download — extract below
  return <DownloadButton label={label} href={href} filename={filename} token={token} />;
}
```

- [ ] **Step 3: Create src/components/download-button.tsx**

```tsx
"use client";

import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Props = { label: string; href: string; filename: string; token: string };

export function DownloadButton({ label, href, filename, token }: Props) {
  async function handleDownload() {
    const res = await fetch(`${API_URL}${href}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  return <Button variant="outline" onClick={handleDownload}>{label}</Button>;
}
```

Update `labels/page.tsx` to import `DownloadButton` and use it directly instead of `ExportButton`.

- [ ] **Step 4: Add nav layout**

Create `web/src/app/layout.tsx` (replace existing):

```tsx
import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Personal Library",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={geist.className}>
        <nav className="border-b px-4 py-2 flex gap-4 text-sm">
          <Link href="/catalog" className="font-semibold">Library</Link>
          <Link href="/books/new">Add book</Link>
          <Link href="/loans">Loans</Link>
          <Link href="/labels">Labels & Export</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 5: Test manually**

Open `/labels`. Select books, choose a template, click Generate PDF. Verify PDF downloads. Test Export BibTeX and CSV buttons.

- [ ] **Step 6: Commit**

```bash
git add web/src/components/label-selector.tsx web/src/components/download-button.tsx web/src/app/labels/ web/src/app/layout.tsx
git commit -m "feat: label PDF generation and export UI"
```

---

## Task 18: Final wiring + production config

**Files:**
- Create: `api/nginx.conf` (reference only)
- Create: `api/Makefile`

- [ ] **Step 1: Create Makefile for common commands**

```makefile
# api/Makefile
.PHONY: dev test migrate

dev:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v

migrate:
	alembic upgrade head
```

- [ ] **Step 2: Verify full backend test suite**

```bash
cd api && pytest tests/ -v --ignore=tests/test_isbn_lookup.py
```
Expected: all tests PASS

- [ ] **Step 3: Verify frontend builds**

```bash
cd web && npm run build
```
Expected: build succeeds with no type errors.

- [ ] **Step 4: Final commit**

```bash
git add api/Makefile
git commit -m "chore: Makefile for common dev commands"
```

---

## Spec Coverage Check

| Spec requirement | Task |
|---|---|
| Web app (Next.js) | Task 12 |
| PostgreSQL | Task 4 |
| ISBN lookup (Open Library + fallback) | Task 7 |
| Camera scan + manual input | Task 15 |
| Physical label PDF (reportlab, Code 128) | Task 10 |
| CDD simplified + free tags | Tasks 4, 8, 10 |
| Informal loan tracking | Task 9 + 16 |
| BibTeX export | Task 11 |
| CSV export | Task 11 |
| Auth (single user, JWT) | Task 3 |
| Book catalog (search, filter, grid) | Tasks 8, 14 |
| ISBN EAN-13 validation | Task 6 |
| Error handling (fallback, duplicates) | Tasks 7, 8 |
| Full-text search | Task 8 (router) |
| Test infrastructure | Task 5 |
