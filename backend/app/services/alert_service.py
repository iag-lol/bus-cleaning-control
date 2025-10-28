"""Alert service for detecting and creating alerts."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.core.config import settings
from app.models.alert import Alert, AlertType, AlertLevel
from app.models.cleaning_event import CleaningEvent, CleaningState


class AlertService:
    """Service for managing and creating alerts."""

    async def check_and_create_alerts(
        self,
        session: AsyncSession,
        bus_id: int,
        latest_event: CleaningEvent,
    ) -> List[Alert]:
        """
        Check if new alerts should be created based on latest event.

        Args:
            session: Database session
            bus_id: Bus ID
            latest_event: Latest cleaning event

        Returns:
            List of newly created alerts
        """
        alerts = []

        # Check for repeated dirty events
        if latest_event.estado == CleaningState.DIRTY:
            dirty_alert = await self._check_repeated_dirty(session, bus_id)
            if dirty_alert:
                alerts.append(dirty_alert)

        # Check for recurring uncertain events
        if latest_event.estado == CleaningState.UNCERTAIN:
            uncertain_alert = await self._check_recurring_uncertain(session, bus_id)
            if uncertain_alert:
                alerts.append(uncertain_alert)

        # Check for very dirty (low confidence or specific issues)
        if latest_event.estado == CleaningState.DIRTY and latest_event.confidence and latest_event.confidence > 0.85:
            muy_sucio_alert = await self._check_muy_sucio(session, bus_id, latest_event)
            if muy_sucio_alert:
                alerts.append(muy_sucio_alert)

        return alerts

    async def _check_repeated_dirty(
        self,
        session: AsyncSession,
        bus_id: int,
    ) -> Optional[Alert]:
        """
        Check for repeated dirty events within window.

        Args:
            session: Database session
            bus_id: Bus ID

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        window_start = datetime.utcnow() - timedelta(
            hours=settings.ALERT_DIRTY_WINDOW_HOURS
        )

        # Count dirty events in window
        result = await session.execute(
            select(func.count(CleaningEvent.id))
            .where(CleaningEvent.bus_id == bus_id)
            .where(CleaningEvent.estado == CleaningState.DIRTY)
            .where(CleaningEvent.created_at >= window_start)
        )
        dirty_count = result.scalar_one()

        if dirty_count >= settings.ALERT_DIRTY_THRESHOLD:
            # Check if alert already exists for recent period
            existing_alert = await session.execute(
                select(Alert)
                .where(Alert.bus_id == bus_id)
                .where(Alert.tipo == AlertType.REPETIDO)
                .where(Alert.resolved_at.is_(None))
                .where(Alert.created_at >= window_start)
            )
            if existing_alert.scalar_one_or_none():
                return None

            # Create new alert
            alert = Alert(
                bus_id=bus_id,
                tipo=AlertType.REPETIDO,
                nivel=AlertLevel.WARNING,
                detalle=f"Bus marcado como sucio {dirty_count} veces en las últimas {settings.ALERT_DIRTY_WINDOW_HOURS}h",
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)

            return alert

        return None

    async def _check_recurring_uncertain(
        self,
        session: AsyncSession,
        bus_id: int,
    ) -> Optional[Alert]:
        """
        Check for recurring uncertain events.

        Args:
            session: Database session
            bus_id: Bus ID

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        window_start = datetime.utcnow() - timedelta(
            hours=settings.ALERT_DIRTY_WINDOW_HOURS
        )

        # Count uncertain events
        result = await session.execute(
            select(func.count(CleaningEvent.id))
            .where(CleaningEvent.bus_id == bus_id)
            .where(CleaningEvent.estado == CleaningState.UNCERTAIN)
            .where(CleaningEvent.created_at >= window_start)
        )
        uncertain_count = result.scalar_one()

        if uncertain_count >= settings.ALERT_UNCERTAIN_THRESHOLD:
            # Check if alert already exists
            existing_alert = await session.execute(
                select(Alert)
                .where(Alert.bus_id == bus_id)
                .where(Alert.tipo == AlertType.DUDOSO_RECURRENTE)
                .where(Alert.resolved_at.is_(None))
                .where(Alert.created_at >= window_start)
            )
            if existing_alert.scalar_one_or_none():
                return None

            # Create alert
            alert = Alert(
                bus_id=bus_id,
                tipo=AlertType.DUDOSO_RECURRENTE,
                nivel=AlertLevel.INFO,
                detalle=f"Bus con estado dudoso {uncertain_count} veces en las últimas {settings.ALERT_DIRTY_WINDOW_HOURS}h - requiere revisión manual",
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)

            return alert

        return None

    async def _check_muy_sucio(
        self,
        session: AsyncSession,
        bus_id: int,
        event: CleaningEvent,
    ) -> Optional[Alert]:
        """
        Check if event indicates very dirty bus.

        Args:
            session: Database session
            bus_id: Bus ID
            event: Cleaning event

        Returns:
            Alert if very dirty, None otherwise
        """
        # High confidence dirty + multiple issues
        if event.issues and len(event.issues.get("issues", [])) >= 3:
            alert = Alert(
                bus_id=bus_id,
                tipo=AlertType.MUY_SUCIO,
                nivel=AlertLevel.CRITICAL,
                detalle=f"Bus muy sucio detectado con {len(event.issues.get('issues', []))} problemas",
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)

            return alert

        return None


# Global alert service instance
alert_service = AlertService()
