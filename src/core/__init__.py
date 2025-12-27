"""Core module for shared application state and event bus.

This module provides the central infrastructure for the hybrid
architecture (Desktop UI + Web Dashboard).

Usage:
    from src.core import AppCore, EventType

    app_core = AppCore()  # Get singleton
    app_core.subscribe(EventType.DETECTION_COMPLETE, my_handler)
    app_core.publish(EventType.DETECTION_COMPLETE, data)
"""

from .app_core import AppCore, FrameBuffer, SystemState
from .events import EventType

__all__ = [
    "AppCore",
    "EventType",
    "FrameBuffer",
    "SystemState",
]
