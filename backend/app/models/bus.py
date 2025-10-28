"""Bus model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Bus(SQLModel, table=True):
    """Bus model for tracking vehicles."""

    __tablename__ = "buses"

    id: Optional[int] = Field(default=None, primary_key=True)
    ppu: str = Field(max_length=10, unique=True, index=True)  # Patent/License plate
    alias: Optional[str] = Field(default=None, max_length=100)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
