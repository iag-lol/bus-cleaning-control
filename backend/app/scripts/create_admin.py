"""Script to create initial admin user."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole


async def create_admin_user():
    """Create initial admin user if it doesn't exist."""
    # Initialize database
    await init_db()

    async with async_session_maker() as session:
        # Check if admin user already exists
        result = await session.execute(
            select(User).where(User.email == "admin@buses.cl")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            nombre="Administrador",
            email="admin@buses.cl",
            hashed_password=get_password_hash("Admin123!"),
            rol=UserRole.ADMIN,
            activo=True,
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print(f"✓ Admin user created successfully!")
        print(f"  Email: admin@buses.cl")
        print(f"  Password: Admin123!")
        print(f"\n⚠️  IMPORTANT: Change the password immediately in production!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
