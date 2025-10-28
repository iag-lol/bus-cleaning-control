"""Alert model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class AlertType(str, Enum):
    """Alert type enumeration."""

    REPETIDO = "repetido"  # Repeated dirty events
    MUY_SUCIO = "muy_sucio"  # Very dirty
    DUDOSO_RECURRENTE = "dudoso_recurrente"  # Recurring uncertain


class AlertLevel(str, Enum):
    """Alert level enumeration."""

    INFO = "info"
    WARNING = "warn"
    CRITICAL = "critical"


class Alert(SQLModel, table=True):
    """Alert model for tracking cleaning issues."""

    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    bus_id: int = Field(foreign_key="buses.id", index=True)
    tipo: AlertType = Field(index=True)
    nivel: AlertLevel = Field(default=AlertLevel.WARNING)
    detalle: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    resolved_by: Optional[int] = Field(default=None, foreign_key="users.id")
    resolved_at: Optional[datetime] = None

    class Config:
        """SQLModel configuration."""
        use_enum_values = True
