import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Book, LabelTemplate
from app.schemas.label_template import (
    LabelGenerateRequest,
    LabelTemplateCreate,
    LabelTemplateOut,
)
from app.services.pdf_labels import generate_labels_pdf

router = APIRouter()


async def _get_template_or_404(template_id: uuid.UUID, db: AsyncSession) -> LabelTemplate:
    result = await db.execute(select(LabelTemplate).where(LabelTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.post("/templates/", status_code=status.HTTP_201_CREATED)
async def create_template(
    body: LabelTemplateCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> LabelTemplateOut:
    template = LabelTemplate(
        name=body.name,
        width_mm=body.width_mm,
        height_mm=body.height_mm,
        font_size=body.font_size,
        show_dewey=body.show_dewey,
        show_title=body.show_title,
        show_barcode=body.show_barcode,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return LabelTemplateOut.model_validate(template)


@router.get("/templates/")
async def list_templates(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> list[LabelTemplateOut]:
    result = await db.execute(select(LabelTemplate).order_by(LabelTemplate.name))
    return [LabelTemplateOut.model_validate(t) for t in result.scalars().all()]


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    template = await _get_template_or_404(template_id, db)
    await db.delete(template)
    await db.commit()


@router.post("/generate")
async def generate_labels(
    body: LabelGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> Response:
    template = await _get_template_or_404(body.template_id, db)

    if not body.book_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No books found"
        )

    result = await db.execute(
        select(Book).where(Book.id.in_(body.book_ids)).order_by(Book.title)
    )
    books = result.scalars().all()

    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No books found"
        )

    pdf_bytes = generate_labels_pdf(list(books), template)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
    )
