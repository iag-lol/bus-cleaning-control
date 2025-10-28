"""Reports endpoints."""

from datetime import datetime
from typing import Optional, Dict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, require_supervisor
from app.models.cleaning_event import CleaningState
from app.models.user import User
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=Dict)
async def get_summary(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> Dict:
    """
    Get summary statistics (supervisor+ only).

    Args:
        from_date: Start date filter
        to_date: End date filter
        session: Database session
        current_user: Current authenticated user

    Returns:
        Summary statistics
    """
    summary = await report_service.get_summary(session, from_date, to_date)
    return summary


@router.get("/export.csv")
async def export_csv(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    ppu: Optional[str] = Query(None),
    estado: Optional[CleaningState] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> Response:
    """
    Export events to CSV (supervisor+ only).

    Args:
        from_date: Start date filter
        to_date: End date filter
        ppu: Bus PPU filter
        estado: State filter
        session: Database session
        current_user: Current authenticated user

    Returns:
        CSV file
    """
    csv_bytes = await report_service.export_csv(
        session,
        from_date,
        to_date,
        ppu,
        estado,
    )

    filename = f"eventos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export.pdf")
async def export_pdf(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_supervisor),
) -> Response:
    """
    Export summary report to PDF (supervisor+ only).

    Args:
        from_date: Start date filter
        to_date: End date filter
        session: Database session
        current_user: Current authenticated user

    Returns:
        PDF file
    """
    pdf_bytes = await report_service.export_pdf(session, from_date, to_date)

    filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
