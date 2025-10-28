"""Cleaning events endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.bus import Bus
from app.models.cleaning_event import CleaningEvent, CleaningState
from app.models.user import User
from app.schemas.cleaning_event import (
    CleaningEventCreate,
    CleaningEventResponse,
    AnalysisRequest,
    AnalysisResponse,
)
from app.services.ml_service import ml_service
from app.services.alert_service import alert_service

router = APIRouter(prefix="/events", tags=["Cleaning Events"])


@router.post("", response_model=CleaningEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: CleaningEventCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> CleaningEvent:
    """
    Create a new cleaning event.

    Args:
        event_data: Event creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created event

    Raises:
        HTTPException: If bus not found
    """
    # Verify bus exists
    bus_result = await session.execute(
        select(Bus).where(Bus.id == event_data.bus_id)
    )
    bus = bus_result.scalar_one_or_none()

    if not bus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    # Create event
    event = CleaningEvent(
        bus_id=event_data.bus_id,
        user_id=current_user.id,
        estado=event_data.estado,
        confidence=event_data.confidence,
        observaciones=event_data.observaciones,
        imagen_thumb_url=event_data.imagen_thumb_url,
        origen=event_data.origen,
        issues=event_data.issues,
    )

    session.add(event)
    await session.commit()
    await session.refresh(event)

    # Trigger WebSocket notification
    try:
        from app.main import get_websocket_manager
        manager = get_websocket_manager()
        await manager.broadcast({
            "type": "event.created",
            "data": {
                "id": event.id,
                "bus_id": event.bus_id,
                "bus_ppu": bus.ppu,
                "user_nombre": current_user.nombre,
                "estado": event.estado.value,
                "confidence": event.confidence,
                "created_at": event.created_at.isoformat(),
            }
        })
    except Exception as e:
        # Don't fail the request if WebSocket fails
        print(f"Error broadcasting event: {e}")

    # Check and create alerts if needed
    try:
        alerts = await alert_service.check_and_create_alerts(session, bus.id, event)
        if alerts:
            # Broadcast alert notifications
            for alert in alerts:
                await manager.broadcast({
                    "type": "alert.created",
                    "data": {
                        "id": alert.id,
                        "bus_id": alert.bus_id,
                        "bus_ppu": bus.ppu,
                        "tipo": alert.tipo.value,
                        "nivel": alert.nivel.value,
                        "detalle": alert.detalle,
                    }
                })
    except Exception as e:
        # Don't fail the request if alert check fails
        print(f"Error checking alerts: {e}")

    return event


@router.get("", response_model=List[CleaningEventResponse])
async def list_events(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    ppu: Optional[str] = Query(None, description="Filter by bus PPU"),
    estado: Optional[CleaningState] = Query(None, description="Filter by state"),
    operario_id: Optional[int] = Query(None, alias="operario", description="Filter by operator ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """
    List cleaning events with optional filters.

    Args:
        from_date: Start date filter
        to_date: End date filter
        ppu: Bus PPU filter
        estado: State filter
        operario_id: Operator ID filter
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of events
    """
    query = select(CleaningEvent, Bus, User).join(
        Bus, CleaningEvent.bus_id == Bus.id
    ).join(
        User, CleaningEvent.user_id == User.id
    )

    # Apply filters
    if from_date:
        query = query.where(CleaningEvent.created_at >= from_date)
    if to_date:
        query = query.where(CleaningEvent.created_at <= to_date)
    if ppu:
        query = query.where(Bus.ppu.ilike(f"%{ppu}%"))
    if estado:
        query = query.where(CleaningEvent.estado == estado)
    if operario_id:
        query = query.where(CleaningEvent.user_id == operario_id)

    # Order and paginate
    query = query.order_by(CleaningEvent.created_at.desc()).offset(skip).limit(limit)

    result = await session.execute(query)
    rows = result.all()

    # Build response with joined data
    events = []
    for event, bus, user in rows:
        event_dict = {
            **event.__dict__,
            "bus_ppu": bus.ppu,
            "user_nombre": user.nombre,
        }
        events.append(event_dict)

    return events


@router.get("/{event_id}", response_model=CleaningEventResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get event by ID.

    Args:
        event_id: Event ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        Event with related data

    Raises:
        HTTPException: If event not found
    """
    result = await session.execute(
        select(CleaningEvent, Bus, User)
        .join(Bus, CleaningEvent.bus_id == Bus.id)
        .join(User, CleaningEvent.user_id == User.id)
        .where(CleaningEvent.id == event_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    event, bus, user = row
    event_dict = {
        **event.__dict__,
        "bus_ppu": bus.ppu,
        "user_nombre": user.nombre,
    }

    return event_dict


# AI Analysis endpoint
ai_router = APIRouter(prefix="/ai", tags=["AI Analysis"])


@ai_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    """
    Analyze image to detect cleaning state.

    Args:
        request: Image analysis request
        current_user: Current authenticated user

    Returns:
        Analysis result with state, confidence, and issues
    """
    try:
        # Analyze image
        state, confidence, issues = ml_service.analyze_image(request.image_base64)

        # Generate suggestions based on issues
        suggestions = _generate_suggestions(issues)

        return AnalysisResponse(
            estado=state,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}",
        )


def _generate_suggestions(issues: List[str]) -> List[str]:
    """
    Generate actionable suggestions based on detected issues.

    Args:
        issues: List of detected issues

    Returns:
        List of suggestions
    """
    suggestions = []

    for issue in issues:
        if "papel" in issue.lower() or "basura" in issue.lower():
            suggestions.append("Recoger y desechar basura del piso y asientos")
        elif "ventana" in issue.lower() or "cristal" in issue.lower():
            suggestions.append("Limpiar ventanas con paño y limpiador de cristales")
        elif "mancha" in issue.lower():
            suggestions.append("Aplicar limpiador y frotar manchas con paño")
        elif "polvo" in issue.lower():
            suggestions.append("Pasar paño seco o aspirar superficies con polvo")
        elif "pasamano" in issue.lower():
            suggestions.append("Limpiar pasamanos con desinfectante")
        else:
            suggestions.append("Revisar y limpiar área afectada")

    # Add general suggestion if no specific ones
    if not suggestions:
        suggestions.append("Realizar limpieza general del bus")

    return suggestions
