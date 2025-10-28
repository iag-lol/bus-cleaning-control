"""User model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "ADMIN"
    SUPERVISOR = "SUP"
    OPERATOR = "OPER"


class User(SQLModel, table=True):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    rol: UserRole = Field(default=UserRole.OPERATOR)
    hashed_password: str = Field(max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        """SQLModel configuration."""
        use_enum_values = True
