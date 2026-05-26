import uuid

from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)
