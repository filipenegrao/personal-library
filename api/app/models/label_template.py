import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LabelTemplate(Base):
    __tablename__ = "label_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    width_mm: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    height_mm: Mapped[float] = mapped_column(Float, nullable=False, default=30.0)
    font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    show_dewey: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    show_title: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    show_barcode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
