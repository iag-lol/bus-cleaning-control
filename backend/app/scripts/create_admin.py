"""Script to create initial admin user."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import init_db
from app.core.config import settings
from app.core.initial_data import ensure_default_admin


async def create_admin_user():
    """Create initial admin user if it doesn't exist."""
    # Initialize database
    await init_db()

    created = await ensure_default_admin()
    if created:
        print("✓ Admin user created successfully!")
        print(f"  Email: {settings.DEFAULT_ADMIN_EMAIL}")
        print(f"  Password: {settings.DEFAULT_ADMIN_PASSWORD}")
        print("\n⚠️  IMPORTANT: Change the password immediately in production!")
    else:
        print("Admin user already exists!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
