import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Book, BookTag, Tag
from app.services.isbn_lookup import BookData


@pytest.mark.asyncio
async def test_create_book(db_session: AsyncSession):
    book = Book(title="Test Book", subtitle="A Test", isbn_13="9780306406157")
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    assert book.id is not None
    assert book.title == "Test Book"
    assert book.created_at is not None


@pytest.mark.asyncio
async def test_list_books(db_session: AsyncSession):
    for i in range(3):
        db_session.add(Book(title=f"Book {i}", authors=[]))
    await db_session.commit()

    stmt = select(Book).order_by(Book.created_at.desc())
    result = await db_session.execute(stmt)
    books = result.scalars().all()
    titles = [b.title for b in books]
    for i in range(3):
        assert f"Book {i}" in titles
    assert titles.index("Book 2") < titles.index("Book 0")


@pytest.mark.asyncio
async def test_get_book(db_session: AsyncSession):
    book = Book(title="Single Book", authors=[])
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    stmt = select(Book).where(Book.id == book.id)
    result = await db_session.execute(stmt)
    assert result.scalar_one().title == "Single Book"


@pytest.mark.asyncio
async def test_get_book_not_found(db_session: AsyncSession):
    stmt = select(Book).where(Book.id == uuid.uuid4())
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_update_book(db_session: AsyncSession):
    book = Book(title="Original", authors=[])
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    book.title = "Updated"
    await db_session.commit()
    await db_session.refresh(book)
    assert book.title == "Updated"


@pytest.mark.asyncio
async def test_delete_book(db_session: AsyncSession):
    book = Book(title="To Delete", authors=[])
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    await db_session.delete(book)
    await db_session.commit()

    stmt = select(Book).where(Book.id == book.id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_create_book_with_tags(db_session: AsyncSession):
    tag = Tag(name="fiction", color="#ff0000")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    book = Book(title="Tagged Book", authors=[])
    db_session.add(book)
    await db_session.flush()

    db_session.add(BookTag(book_id=book.id, tag_id=tag.id))
    await db_session.commit()

    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
        .where(Book.id == book.id)
    )
    result = await db_session.execute(stmt)
    loaded = result.scalar_one()
    assert len(loaded.book_tags) == 1
    assert loaded.book_tags[0].tag.name == "fiction"


@pytest.mark.asyncio
async def test_list_books_filter_by_tag(db_session: AsyncSession):
    tag = Tag(name="scifi", color="#00ff00")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    book1 = Book(title="SciFi Book", authors=[])
    book2 = Book(title="Other Book", authors=[])
    db_session.add_all([book1, book2])
    await db_session.flush()
    db_session.add(BookTag(book_id=book1.id, tag_id=tag.id))
    await db_session.commit()

    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
        .where(Book.book_tags.any(BookTag.tag_id == tag.id))
    )
    result = await db_session.execute(stmt)
    books = result.scalars().all()
    assert len(books) == 1
    assert books[0].title == "SciFi Book"


@pytest.mark.asyncio
async def test_list_books_search(db_session: AsyncSession):
    db_session.add_all([
        Book(title="Python Programming", authors=[]),
        Book(title="Java Basics", authors=[]),
    ])
    await db_session.commit()

    stmt = select(Book).where(Book.title.ilike("%python%"))
    result = await db_session.execute(stmt)
    books = result.scalars().all()
    assert len(books) == 1
    assert books[0].title == "Python Programming"


@pytest.mark.asyncio
async def test_lookup_invalid_isbn(auth_client: AsyncClient):
    resp = await auth_client.get("/books/lookup/not-an-isbn")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_lookup_success(auth_client: AsyncClient):
    mock_data = BookData(
        title="Lord of the Rings",
        authors=["J.R.R. Tolkien"],
        publisher="Houghton Mifflin",
        published_year=2005,
    )

    async def mock_lookup(isbn: str) -> BookData | None:
        return mock_data

    with patch("app.routers.books.lookup_isbn", side_effect=mock_lookup):
        resp = await auth_client.get("/books/lookup/9780306406157")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Lord of the Rings"
        assert data["isbn_13"] == "9780306406157"


@pytest.mark.asyncio
async def test_lookup_not_found(auth_client: AsyncClient):
    async def mock_lookup(isbn: str) -> BookData | None:
        return None

    with patch("app.routers.books.lookup_isbn", side_effect=mock_lookup):
        resp = await auth_client.get("/books/lookup/9780306406157")
        assert resp.status_code == 404
