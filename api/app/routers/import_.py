from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Book
from app.schemas.book import BookOut
from app.schemas.import_result import ImportResult
from app.services.bibtex_io import map_bibtex_entry_to_book_data, parse_bibtex
from app.services.csv_io import map_csv_row_to_book_data, parse_csv

router = APIRouter()
MAX_IMPORT_BYTES = 1_000_000
MAX_IMPORT_ROWS = 5_000
READ_CHUNK_SIZE = 64 * 1024


async def _read_utf8_upload(file: UploadFile) -> str:
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(READ_CHUNK_SIZE):
        total += len(chunk)
        if total > MAX_IMPORT_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Import file is too large",
            )
        chunks.append(chunk)
    content = b"".join(chunks)
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded",
        )


def _validate_import_count(count: int) -> None:
    if count > MAX_IMPORT_ROWS:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Import file has too many records; maximum is {MAX_IMPORT_ROWS}",
        )


@router.post("/csv", response_model=ImportResult)
async def import_csv(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .csv file",
        )

    text = await _read_utf8_upload(file)

    try:
        rows = parse_csv(text)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    _validate_import_count(len(rows))

    errors: list[str] = []
    books: list[Book] = []

    for i, row in enumerate(rows, start=1):
        data = map_csv_row_to_book_data(row)
        title = data.get("title", "")
        if not title:
            errors.append(f"Row {i}: missing required field 'title'")
            continue

        book = Book(
            isbn_13=data.get("isbn_13"),
            isbn_10=data.get("isbn_10"),
            title=data["title"],
            subtitle=data.get("subtitle"),
            authors=data.get("authors", []),
            publisher=data.get("publisher"),
            published_year=data.get("published_year"),
            language=data.get("language"),
            pages=data.get("pages"),
            cover_url=data.get("cover_url"),
            dewey_code=data.get("dewey_code"),
            notes=data.get("notes"),
        )
        db.add(book)
        books.append(book)

    await db.commit()
    for book in books:
        await db.refresh(book)

    return ImportResult(
        total=len(rows),
        created=len(books),
        errors=errors,
        books=[BookOut.model_validate(book) for book in books],
    )


@router.post("/bibtex", response_model=ImportResult)
async def import_bibtex(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".bib"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .bib file",
        )

    text = await _read_utf8_upload(file)

    entries = parse_bibtex(text)
    _validate_import_count(len(entries))

    errors: list[str] = []
    books: list[Book] = []

    for i, entry in enumerate(entries, start=1):
        data = map_bibtex_entry_to_book_data(entry)
        title = data.get("title", "")
        if not title:
            errors.append(f"Entry {i} ({entry.get('ID', '?')}): missing required field 'title'")
            continue

        book = Book(
            isbn_13=data.get("isbn_13"),
            isbn_10=data.get("isbn_10"),
            title=data["title"],
            authors=data.get("authors", []),
            publisher=data.get("publisher"),
            published_year=data.get("published_year"),
            language=data.get("language"),
            notes=data.get("notes"),
        )
        db.add(book)
        books.append(book)

    await db.commit()
    for book in books:
        await db.refresh(book)

    return ImportResult(
        total=len(entries),
        created=len(books),
        errors=errors,
        books=[BookOut.model_validate(book) for book in books],
    )
