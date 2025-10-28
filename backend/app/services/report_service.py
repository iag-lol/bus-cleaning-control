"""Report service for generating summaries and exports."""

import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.models.bus import Bus
from app.models.cleaning_event import CleaningEvent, CleaningState
from app.models.user import User


class ReportService:
    """Service for generating reports and analytics."""

    async def get_summary(
        self,
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Get summary statistics.

        Args:
            session: Database session
            from_date: Start date filter
            to_date: End date filter

        Returns:
            Dictionary with summary statistics
        """
        # Default to last 30 days if not specified
        if not from_date:
            from_date = datetime.utcnow() - timedelta(days=30)
        if not to_date:
            to_date = datetime.utcnow()

        # Total events
        total_result = await session.execute(
            select(func.count(CleaningEvent.id))
            .where(CleaningEvent.created_at >= from_date)
            .where(CleaningEvent.created_at <= to_date)
        )
        total_events = total_result.scalar_one()

        # Events by state
        state_result = await session.execute(
            select(
                CleaningEvent.estado,
                func.count(CleaningEvent.id)
            )
            .where(CleaningEvent.created_at >= from_date)
            .where(CleaningEvent.created_at <= to_date)
            .group_by(CleaningEvent.estado)
        )
        state_counts = {state: count for state, count in state_result.all()}

        # Percentages
        clean_count = state_counts.get(CleaningState.CLEAN, 0)
        dirty_count = state_counts.get(CleaningState.DIRTY, 0)
        uncertain_count = state_counts.get(CleaningState.UNCERTAIN, 0)

        clean_pct = (clean_count / total_events * 100) if total_events > 0 else 0
        dirty_pct = (dirty_count / total_events * 100) if total_events > 0 else 0
        uncertain_pct = (uncertain_count / total_events * 100) if total_events > 0 else 0

        # Buses with most issues (most dirty events)
        buses_result = await session.execute(
            select(
                Bus.ppu,
                func.count(CleaningEvent.id).label("dirty_count")
            )
            .join(CleaningEvent, Bus.id == CleaningEvent.bus_id)
            .where(CleaningEvent.estado == CleaningState.DIRTY)
            .where(CleaningEvent.created_at >= from_date)
            .where(CleaningEvent.created_at <= to_date)
            .group_by(Bus.id, Bus.ppu)
            .order_by(func.count(CleaningEvent.id).desc())
            .limit(10)
        )
        top_dirty_buses = [
            {"ppu": ppu, "dirty_count": count}
            for ppu, count in buses_result.all()
        ]

        # Operator performance
        operator_result = await session.execute(
            select(
                User.nombre,
                func.count(CleaningEvent.id).label("total"),
                func.sum(
                    func.case(
                        (CleaningEvent.estado == CleaningState.CLEAN, 1),
                        else_=0
                    )
                ).label("clean_count")
            )
            .join(CleaningEvent, User.id == CleaningEvent.user_id)
            .where(CleaningEvent.created_at >= from_date)
            .where(CleaningEvent.created_at <= to_date)
            .group_by(User.id, User.nombre)
        )
        operator_stats = []
        for nombre, total, clean in operator_result.all():
            clean_rate = (clean / total * 100) if total > 0 else 0
            operator_stats.append({
                "nombre": nombre,
                "total_inspecciones": total,
                "clean_count": clean or 0,
                "clean_rate": round(clean_rate, 1),
            })

        return {
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
            },
            "total_events": total_events,
            "by_state": {
                "clean": {"count": clean_count, "percentage": round(clean_pct, 1)},
                "dirty": {"count": dirty_count, "percentage": round(dirty_pct, 1)},
                "uncertain": {"count": uncertain_count, "percentage": round(uncertain_pct, 1)},
            },
            "top_dirty_buses": top_dirty_buses,
            "operator_performance": operator_stats,
        }

    async def export_csv(
        self,
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        ppu: Optional[str] = None,
        estado: Optional[CleaningState] = None,
    ) -> bytes:
        """
        Export events to CSV.

        Args:
            session: Database session
            from_date: Start date filter
            to_date: End date filter
            ppu: Bus PPU filter
            estado: State filter

        Returns:
            CSV file as bytes
        """
        # Build query
        query = select(
            CleaningEvent,
            Bus.ppu,
            User.nombre
        ).join(
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

        # Order by date
        query = query.order_by(CleaningEvent.created_at.desc())

        result = await session.execute(query)
        rows = result.all()

        # Build DataFrame
        data = []
        for event, ppu, nombre in rows:
            data.append({
                "ID": event.id,
                "PPU": ppu,
                "Operario": nombre,
                "Estado": event.estado.value,
                "Confianza": event.confidence,
                "Observaciones": event.observaciones or "",
                "Origen": event.origen.value,
                "Fecha": event.created_at.strftime("%d-%m-%Y %H:%M"),
            })

        df = pd.DataFrame(data)

        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")

        return csv_buffer.getvalue().encode("utf-8")

    async def export_pdf(
        self,
        session: AsyncSession,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> bytes:
        """
        Export summary report to PDF.

        Args:
            session: Database session
            from_date: Start date filter
            to_date: End date filter

        Returns:
            PDF file as bytes
        """
        # Get summary data
        summary = await self.get_summary(session, from_date, to_date)

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title = Paragraph(
            "<b>Reporte de Control de Aseo de Buses</b>",
            styles["Title"]
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Period
        period_text = f"Período: {summary['period']['from'][:10]} a {summary['period']['to'][:10]}"
        story.append(Paragraph(period_text, styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

        # Summary stats
        summary_data = [
            ["Métrica", "Valor"],
            ["Total Inspecciones", str(summary["total_events"])],
            ["Limpios", f"{summary['by_state']['clean']['count']} ({summary['by_state']['clean']['percentage']}%)"],
            ["Sucios", f"{summary['by_state']['dirty']['count']} ({summary['by_state']['dirty']['percentage']}%)"],
            ["Dudosos", f"{summary['by_state']['uncertain']['count']} ({summary['by_state']['uncertain']['percentage']}%)"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))

        # Top dirty buses
        if summary["top_dirty_buses"]:
            story.append(Paragraph("<b>Buses con Más Rechazos</b>", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            buses_data = [["PPU", "Rechazos"]]
            for bus in summary["top_dirty_buses"][:5]:
                buses_data.append([bus["ppu"], str(bus["dirty_count"])])

            buses_table = Table(buses_data, colWidths=[2 * inch, 1.5 * inch])
            buses_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

            story.append(buses_table)

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


# Global report service instance
report_service = ReportService()
