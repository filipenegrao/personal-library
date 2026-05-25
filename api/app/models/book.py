from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.loan import Loan
    from app.models.tag import BookTag


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    isbn_13: Mapped[str | None] = mapped_column(String(13), index=True, nullable=True)
    isbn_10: Mapped[str | None] = mapped_column(String(10), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    publisher: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    dewey_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    book_tags: Mapped[list["BookTag"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    loans: Mapped[list["Loan"]] = relationship(back_populates="book")
