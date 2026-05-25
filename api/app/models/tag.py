from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.book import Book


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#6366f1")

    book_tags: Mapped[list["BookTag"]] = relationship(back_populates="tag")


class BookTag(Base):
    __tablename__ = "book_tags"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="RESTRICT"), primary_key=True
    )

    book: Mapped["Book"] = relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = relationship(back_populates="book_tags")
