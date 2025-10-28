"""Cleaning event schemas."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.cleaning_event import CleaningState, InferenceOrigin


class CleaningEventCreate(BaseModel):
    """Cleaning event creation schema."""

    bus_id: int
    estado: CleaningState
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    observaciones: Optional[str] = Field(None, max_length=1000)
    imagen_thumb_url: Optional[str] = None
    origen: InferenceOrigin = InferenceOrigin.EDGE
    issues: Optional[dict] = None


class CleaningEventResponse(BaseModel):
    """Cleaning event response schema."""

    id: int
    bus_id: int
    user_id: int
    estado: CleaningState
    confidence: Optional[float]
    observaciones: Optional[str]
    imagen_thumb_url: Optional[str]
    origen: InferenceOrigin
    issues: Optional[dict]
    created_at: datetime

    # Populated in joins
    bus_ppu: Optional[str] = None
    user_nombre: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Image analysis request schema."""

    image_base64: str = Field(..., description="Base64-encoded image")


class AnalysisResponse(BaseModel):
    """Image analysis response schema."""

    estado: CleaningState
    confidence: float
    issues: List[str] = []
    suggestions: List[str] = []
