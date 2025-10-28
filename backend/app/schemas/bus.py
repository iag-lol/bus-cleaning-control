"""Bus schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BusCreate(BaseModel):
    """Bus creation schema."""

    ppu: str = Field(..., min_length=1, max_length=10)
    alias: Optional[str] = Field(None, max_length=100)


class BusUpdate(BaseModel):
    """Bus update schema."""

    ppu: Optional[str] = Field(None, min_length=1, max_length=10)
    alias: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None


class BusResponse(BaseModel):
    """Bus response schema."""

    id: int
    ppu: str
    alias: Optional[str]
    activo: bool
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
