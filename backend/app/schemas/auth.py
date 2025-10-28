"""Authentication schemas."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str
    type: str
    exp: int
