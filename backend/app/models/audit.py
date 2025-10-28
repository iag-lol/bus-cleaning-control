"""Audit log model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column, JSON


class AuditLog(SQLModel, table=True):
    """Audit log model for tracking user actions."""

    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    accion: str = Field(max_length=100, index=True)
    entidad: str = Field(max_length=50, index=True)  # e.g., "bus", "user", "event"
    entidad_id: Optional[int] = Field(default=None)
    diff_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
