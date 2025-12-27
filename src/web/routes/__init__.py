"""Web routes package."""

from .api import router as api_router
from .stream import router as stream_router
from .websocket import router as websocket_router

__all__ = ["api_router", "stream_router", "websocket_router"]
