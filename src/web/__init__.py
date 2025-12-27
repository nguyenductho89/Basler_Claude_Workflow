"""Web module for the Web Dashboard.

This module provides REST API and WebSocket endpoints for
remote monitoring via web browser.

Usage:
    from src.web import start_web_server, stop_web_server

    # Start server in background
    server = start_web_server(port=8080)

    # ... application runs ...

    # Stop server on shutdown
    stop_web_server()
"""

from .server import (
    create_app,
    WebServer,
    get_web_server,
    start_web_server,
    stop_web_server,
)
from .schemas import (
    SystemStatusSchema,
    StatisticsSchema,
    RecipeListSchema,
    RecipeDetailSchema,
    IOStatusSchema,
    CalibrationSchema,
    HistoryResponseSchema,
    CircleResultSchema,
    MeasureStatusEnum,
)

__all__ = [
    # Server
    "create_app",
    "WebServer",
    "get_web_server",
    "start_web_server",
    "stop_web_server",
    # Schemas
    "SystemStatusSchema",
    "StatisticsSchema",
    "RecipeListSchema",
    "RecipeDetailSchema",
    "IOStatusSchema",
    "CalibrationSchema",
    "HistoryResponseSchema",
    "CircleResultSchema",
    "MeasureStatusEnum",
]
