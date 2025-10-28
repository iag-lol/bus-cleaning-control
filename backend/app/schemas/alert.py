"""Alert schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.alert import AlertType, AlertLevel


class AlertResponse(BaseModel):
    """Alert response schema."""

    id: int
    bus_id: int
    tipo: AlertType
    nivel: AlertLevel
    detalle: str
    created_at: datetime
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]

    # Populated in joins
    bus_ppu: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class AlertResolve(BaseModel):
    """Alert resolution schema."""

    notes: Optional[str] = None
