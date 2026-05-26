import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Tag
from app.schemas.tag import TagCreate, TagOut, TagUpdate

router = APIRouter()


async def _get_tag_or_404(tag_id: uuid.UUID, db: AsyncSession) -> Tag:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tag(
    body: TagCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> TagOut:
    tag = Tag(name=body.name, color=body.color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagOut.model_validate(tag)


@router.get("/")
async def list_tags(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> list[TagOut]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return [TagOut.model_validate(t) for t in result.scalars().all()]


@router.patch("/{tag_id}")
async def update_tag(
    tag_id: uuid.UUID,
    body: TagUpdate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> TagOut:
    tag = await _get_tag_or_404(tag_id, db)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)
    return TagOut.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> None:
    tag = await _get_tag_or_404(tag_id, db)
    try:
        await db.delete(tag)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete tag: it is currently assigned to one or more books",
        )
