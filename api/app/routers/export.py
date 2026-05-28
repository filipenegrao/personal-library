from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Book
from app.services.bibtex_io import generate_bibtex
from app.services.csv_io import generate_csv

router = APIRouter()


@router.get("/csv")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Response:
    result = await db.execute(select(Book).order_by(Book.title))
    books = list(result.scalars().all())
    csv_content = generate_csv(books)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=library_export.csv"},
    )


@router.get("/bibtex")
async def export_bibtex(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Response:
    result = await db.execute(select(Book).order_by(Book.title))
    books = list(result.scalars().all())
    bibtex_content = generate_bibtex(books)
    return Response(
        content=bibtex_content,
        media_type="application/x-bibtex",
        headers={"Content-Disposition": "attachment; filename=library_export.bib"},
    )
