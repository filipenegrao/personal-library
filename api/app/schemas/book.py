import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


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


class BookOut(BaseModel):
    id: uuid.UUID
    isbn_13: str | None = None
    isbn_10: str | None = None
    title: str
    subtitle: str | None = None
    authors: list[str]
    publisher: str | None = None
    published_year: int | None = None
    language: str | None = None
    pages: int | None = None
    cover_url: str | None = None
    dewey_code: str | None = None
    notes: str | None = None
    created_at: datetime
    tags: list[TagOut] = []

    model_config = ConfigDict(from_attributes=True)
