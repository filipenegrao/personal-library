import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LabelTemplateCreate(BaseModel):
    name: str
    width_mm: float = 50.0
    height_mm: float = 30.0
    font_size: int = 8
    show_dewey: bool = True
    show_title: bool = True
    show_barcode: bool = True


class LabelTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    width_mm: float
    height_mm: float
    font_size: int
    show_dewey: bool
    show_title: bool
    show_barcode: bool
    created_at: datetime


class LabelGenerateRequest(BaseModel):
    book_ids: list[uuid.UUID]
    template_id: uuid.UUID
