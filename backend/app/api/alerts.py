"""Alerts endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.deps import get_current_user, require_supervisor
from app.models.alert import Alert, AlertType, AlertLevel
from app.models.bus import Bus
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertResolve

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    tipo: Optional[AlertType] = Query(None, description="Filter by alert type"),
    nivel: Optional[AlertLevel] = Query(None, description="Filter by alert level"),
    bus_id: Optional[int] = Query(None, description="Filter by bus ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """
    List alerts with optional filters.

    Args:
        resolved: Filter by resolution status (True=resolved, False=unresolved, None=all)
        tipo: Filter by alert type
        nivel: Filter by alert level
        bus_id: Filter by bus ID
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of alerts
    """
    query = select(Alert, Bus).join(Bus, Alert.bus_id == Bus.id)

    # Apply filters
    if resolved is not None:
        if resolved:
            query = query.where(Alert.resolved_at.is_not(None))
        else:
            query = query.where(Alert.resolved_at.is_(None))

    if tipo:
        query = query.where(Alert.tipo == tipo)
    if nivel:
        query = query.where(Alert.nivel == nivel)
    if bus_id:
        query = query.where(Alert.bus_id == bus_id)

    # Order by creation date (newest first)
    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

    result = await session.execute(query)
    rows = result.all()

    # Build response with joined data
    alerts = []
    for alert, bus in rows:
        alert_dict = {
            **alert.__dict__,
            "bus_ppu": bus.ppu,
        }
        alerts.append(alert_dict)

    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get alert by ID.

    Args:
        alert_id: Alert ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Alert with related data

    Raises:
        HTTPException: If alert not found
    """
    result = await session.execute(
        select(Alert, Bus)
        .join(Bus, Alert.bus_id == Bus.id)
        .where(Alert.id == alert_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert, bus = row
    alert_dict = {
        **alert.__dict__,
        "bus_ppu": bus.ppu,
    }

    return alert_dict


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    resolve_data: AlertResolve,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> dict:
    """
    Resolve an alert (supervisor+ only).

    Args:
        alert_id: Alert ID
        resolve_data: Resolution data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Resolved alert

    Raises:
        HTTPException: If alert not found or already resolved
    """
    result = await session.execute(
        select(Alert, Bus)
        .join(Bus, Alert.bus_id == Bus.id)
        .where(Alert.id == alert_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert, bus = row

    if alert.resolved_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert already resolved",
        )

    # Mark as resolved
    alert.resolved_by = current_user.id
    alert.resolved_at = datetime.utcnow()

    session.add(alert)
    await session.commit()
    await session.refresh(alert)

    alert_dict = {
        **alert.__dict__,
        "bus_ppu": bus.ppu,
    }

    return alert_dict
