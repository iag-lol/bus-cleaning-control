"""Bus endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.deps import get_current_user, require_supervisor
from app.models.bus import Bus
from app.models.user import User
from app.schemas.bus import BusCreate, BusUpdate, BusResponse

router = APIRouter(prefix="/buses", tags=["Buses"])


@router.get("", response_model=List[BusResponse])
async def list_buses(
    search: Optional[str] = Query(None, description="Search by PPU or alias"),
    activo: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Bus]:
    """
    List buses with optional filters.

    Args:
        search: Search term for PPU or alias
        activo: Filter by active status
        skip: Number of records to skip
        limit: Maximum number of records to return
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of buses
    """
    query = select(Bus)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Bus.ppu.ilike(search_pattern)) | (Bus.alias.ilike(search_pattern))
        )

    if activo is not None:
        query = query.where(Bus.activo == activo)

    # Order and paginate
    query = query.order_by(Bus.ppu).offset(skip).limit(limit)

    result = await session.execute(query)
    buses = result.scalars().all()

    return buses


@router.post("", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def create_bus(
    bus_data: BusCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Bus:
    """
    Create a new bus.

    Args:
        bus_data: Bus creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created bus

    Raises:
        HTTPException: If PPU already exists
    """
    # Check if PPU already exists
    existing = await session.execute(
        select(Bus).where(Bus.ppu == bus_data.ppu.upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bus with PPU '{bus_data.ppu}' already exists",
        )

    # Create bus
    bus = Bus(
        ppu=bus_data.ppu.upper(),
        alias=bus_data.alias,
    )

    session.add(bus)
    await session.commit()
    await session.refresh(bus)

    return bus


@router.get("/{bus_id}", response_model=BusResponse)
async def get_bus(
    bus_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Bus:
    """
    Get bus by ID.

    Args:
        bus_id: Bus ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Bus

    Raises:
        HTTPException: If bus not found
    """
    result = await session.execute(
        select(Bus).where(Bus.id == bus_id)
    )
    bus = result.scalar_one_or_none()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return bus


@router.put("/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> Bus:
    """
    Update bus (supervisor+ only).

    Args:
        bus_id: Bus ID
        bus_data: Bus update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated bus

    Raises:
        HTTPException: If bus not found or PPU already exists
    """
    # Get bus
    result = await session.execute(
        select(Bus).where(Bus.id == bus_id)
    )
    bus = result.scalar_one_or_none()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    # Check if new PPU already exists
    if bus_data.ppu and bus_data.ppu.upper() != bus.ppu:
        existing = await session.execute(
            select(Bus).where(Bus.ppu == bus_data.ppu.upper())
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bus with PPU '{bus_data.ppu}' already exists",
            )

    # Update fields
    update_data = bus_data.model_dump(exclude_unset=True)
    if "ppu" in update_data:
        update_data["ppu"] = update_data["ppu"].upper()

    for field, value in update_data.items():
        setattr(bus, field, value)

    session.add(bus)
    await session.commit()
    await session.refresh(bus)

    return bus


@router.delete("/{bus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bus(
    bus_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> None:
    """
    Delete bus (soft delete - set inactive, supervisor+ only).

    Args:
        bus_id: Bus ID
        session: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If bus not found
    """
    result = await session.execute(
        select(Bus).where(Bus.id == bus_id)
    )
    bus = result.scalar_one_or_none()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    # Soft delete
    bus.activo = False
    session.add(bus)
    await session.commit()
