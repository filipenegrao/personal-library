import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    book_id: uuid.UUID
    borrower_name: str
    due_date: datetime | None = None
    notes: str | None = None


class LoanReturn(BaseModel):
    returned_at: datetime | None = None


class LoanOut(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    borrower_name: str
    loaned_at: datetime
    due_date: datetime | None = None
    returned_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
