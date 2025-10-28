"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, buses, events, alerts, reports
from app.api.events import ai_router
from app.core.config import settings
from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Connect a new WebSocket client.

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
        """
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de control de aseo de buses con IA",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}


# Include routers
app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(events.router)
app.include_router(ai_router)
app.include_router(alerts.router)
app.include_router(reports.router)


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.

    Args:
        websocket: WebSocket connection
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        }
    )


# Export manager for use in other modules
def get_websocket_manager() -> ConnectionManager:
    """
    Get WebSocket connection manager.

    Returns:
        Connection manager instance
    """
    return manager
