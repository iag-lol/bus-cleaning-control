"""Initial data helpers for the application."""

import logging

from sqlmodel import select

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def ensure_default_admin() -> bool:
    """
    Ensure that the default admin user exists.

    Returns:
        True if the admin was created during this call, False otherwise.
    """
    default_email = settings.DEFAULT_ADMIN_EMAIL
    default_password = settings.DEFAULT_ADMIN_PASSWORD

    if not default_email or not default_password:
        logger.warning(
            "Skipping default admin creation because credentials are not configured."
        )
        return False

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == default_email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return False

        admin = User(
            nombre=settings.DEFAULT_ADMIN_NAME,
            email=default_email,
            hashed_password=get_password_hash(default_password),
            rol=UserRole.ADMIN,
            activo=True,
        )

        session.add(admin)
        await session.commit()

        logger.info("Created default admin user with email %s", default_email)
        return True
