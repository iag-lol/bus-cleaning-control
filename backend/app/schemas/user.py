"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """User creation schema."""

    nombre: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    rol: UserRole = UserRole.OPERATOR


class UserUpdate(BaseModel):
    """User update schema."""

    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    rol: Optional[UserRole] = None
    activo: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    nombre: str
    email: str
    rol: UserRole
    activo: bool
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True
