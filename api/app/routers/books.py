import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps import get_current_user, get_db
from app.models import Book, BookTag
from app.schemas.book import BookCreate, BookOut, BookUpdate, TagOut
from app.services.isbn_lookup import BookData, lookup_isbn
from app.services.isbn_validate import normalize_isbn, validate_isbn13

router = APIRouter()


def _book_to_out(book: Book) -> BookOut:
    tags = [
        TagOut(id=bt.tag.id, name=bt.tag.name, color=bt.tag.color)
        for bt in book.book_tags
        if bt.tag is not None
    ]
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
    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
        .where(Book.id == book_id)
    )
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


async def _sync_tags(db: AsyncSession, book: Book, tag_ids: list[uuid.UUID]) -> None:
    db.add_all(BookTag(book_id=book.id, tag_id=tid) for tid in tag_ids)


@router.get("/lookup/{isbn}")
async def lookup_book_isbn(
    isbn: str,
    _user: str = Depends(get_current_user),
) -> BookData:
    normalized = normalize_isbn(isbn)
    if normalized is None or not validate_isbn13(normalized):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid ISBN format",
        )

    result = await lookup_isbn(normalized)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ISBN not found")

    if result.isbn_13 is None and len(normalized) == 13:
        result.isbn_13 = normalized

    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    body: BookCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
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

    if body.tag_ids:
        await _sync_tags(db, book, body.tag_ids)
        await db.flush()

    await db.commit()
    await db.refresh(book, ["book_tags"])

    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
        .where(Book.id == book.id)
    )
    result = await db.execute(stmt)
    return _book_to_out(result.scalar_one())


@router.get("/")
async def list_books(
    search: str | None = None,
    language: str | None = None,
    tag_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> list[BookOut]:
    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
    )

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            Book.title.ilike(pattern) | Book.subtitle.ilike(pattern)
        )
    if language:
        stmt = stmt.where(Book.language == language)
    if tag_id:
        stmt = stmt.where(
            Book.book_tags.any(BookTag.tag_id == tag_id)
        )

    stmt = stmt.order_by(Book.created_at.desc())
    result = await db.execute(stmt)
    books = result.scalars().unique().all()
    return [_book_to_out(book) for book in books]


@router.get("/{book_id}")
async def get_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> BookOut:
    book = await _get_book_or_404(book_id, db)
    return _book_to_out(book)


@router.patch("/{book_id}")
async def update_book(
    book_id: uuid.UUID,
    body: BookUpdate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> BookOut:
    book = await _get_book_or_404(book_id, db)

    update_data = body.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for field, value in update_data.items():
        setattr(book, field, value)

    if tag_ids is not None:
        existing = await db.execute(
            select(BookTag).where(BookTag.book_id == book.id)
        )
        for bt in existing.scalars().all():
            await db.delete(bt)
        if tag_ids:
            await _sync_tags(db, book, tag_ids)

    await db.commit()
    await db.refresh(book, ["book_tags"])

    stmt = (
        select(Book)
        .options(selectinload(Book.book_tags).selectinload(BookTag.tag))
        .where(Book.id == book.id)
    )
    result = await db.execute(stmt)
    return _book_to_out(result.scalar_one())


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    book = await _get_book_or_404(book_id, db)
    await db.delete(book)
    await db.commit()
