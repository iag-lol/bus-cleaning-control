"""Cleaning event model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Column, JSON


class CleaningState(str, Enum):
    """Cleaning state enumeration."""

    CLEAN = "clean"
    DIRTY = "dirty"
    UNCERTAIN = "uncertain"


class InferenceOrigin(str, Enum):
    """Origin of ML inference."""

    EDGE = "edge"  # Client-side inference
    SERVER = "server"  # Server-side inference
    MANUAL = "manual"  # Manual classification


class CleaningEvent(SQLModel, table=True):
    """Cleaning event model for tracking bus cleaning inspections."""

    __tablename__ = "cleaning_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    bus_id: int = Field(foreign_key="buses.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    estado: CleaningState = Field(index=True)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    observaciones: Optional[str] = Field(default=None, max_length=1000)
    imagen_thumb_url: Optional[str] = Field(default=None, max_length=500)
    origen: InferenceOrigin = Field(default=InferenceOrigin.EDGE)

    # JSON field for AI-generated issues/suggestions
    issues: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        """SQLModel configuration."""
        use_enum_values = True
