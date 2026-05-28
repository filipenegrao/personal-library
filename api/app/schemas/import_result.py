from pydantic import BaseModel

from app.schemas.book import BookOut


class ImportResult(BaseModel):
    total: int
    created: int
    errors: list[str]
    books: list[BookOut]
