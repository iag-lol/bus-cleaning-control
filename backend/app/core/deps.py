"""FastAPI dependencies."""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_session
from app.models.user import User, UserRole

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        session: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    result = await session.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None or not user.activo:
        raise credentials_exception

    return user


def require_role(required_role: UserRole):
    """
    Dependency factory to require specific user role.

    Args:
        required_role: Required user role

    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Check if user has required role."""
        # Role hierarchy: ADMIN > SUPERVISOR > OPERATOR
        role_hierarchy = {
            UserRole.OPERATOR: 0,
            UserRole.SUPERVISOR: 1,
            UserRole.ADMIN: 2,
        }

        if role_hierarchy[current_user.rol] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker


# Convenience dependencies
require_admin = require_role(UserRole.ADMIN)
require_supervisor = require_role(UserRole.SUPERVISOR)
