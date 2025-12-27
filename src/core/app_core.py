"""AppCore - Central application state and event bus.

This module provides the AppCore singleton that manages:
- Shared state between Desktop UI and Web Dashboard
- Event bus for decoupled component communication
- Service container for dependency injection
- Thread-safe frame buffer access
"""

import threading
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from .events import EventType

logger = logging.getLogger(__name__)


@dataclass
class FrameBuffer:
    """Thread-safe frame buffer for sharing images between components."""

    raw_frame: Optional[np.ndarray] = None
    display_frame: Optional[np.ndarray] = None
    binary_frame: Optional[np.ndarray] = None
    timestamp: Optional[datetime] = None


@dataclass
class SystemState:
    """Current system state."""

    camera_connected: bool = False
    is_running: bool = False
    current_recipe: Optional[str] = None
    fps: float = 0.0
    web_clients: int = 0


class AppCore:
    """Singleton application core for shared state and event bus.

    This class provides:
    - Centralized state management
    - Event bus for publish/subscribe communication
    - Thread-safe frame buffer access
    - Service container for dependency injection

    Usage:
        app_core = AppCore()  # Get singleton instance
        app_core.subscribe(EventType.DETECTION_COMPLETE, handler)
        app_core.publish(EventType.DETECTION_COMPLETE, data)
    """

    _instance: Optional["AppCore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "AppCore":
        """Create or return singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialize()
                    cls._instance = instance
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the AppCore instance."""
        # Event bus
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_lock = threading.Lock()

        # Frame buffer with lock
        self._frame_buffer = FrameBuffer()
        self._frame_lock = threading.Lock()

        # System state
        self._state = SystemState()
        self._state_lock = threading.Lock()

        # Services container (lazy initialization)
        self._services: Dict[str, Any] = {}

        # Latest detection result
        self._latest_result: Optional[Any] = None
        self._result_lock = threading.Lock()

        # Statistics reference
        self._statistics: Optional[Any] = None

        # IO status reference
        self._io_status: Optional[Any] = None

        # Calibration service reference
        self._calibration_service: Optional[Any] = None

        # Recipe service reference
        self._recipe_service: Optional[Any] = None

        # Measurement history
        self._history: List[Dict] = []
        self._history_lock = threading.Lock()
        self._max_history = 1000

        logger.info("AppCore initialized")

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    # ========== Event Bus ==========

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: The event type to subscribe to (from EventType)
            callback: Function to call when event is published
        """
        with self._event_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logger.debug(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
        """
        with self._event_lock:
            if event_type in self._subscribers:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    logger.debug(f"Unsubscribed from {event_type}")

    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event to all subscribers.

        Args:
            event_type: The event type to publish
            data: Optional data to pass to subscribers
        """
        with self._event_lock:
            subscribers = self._subscribers.get(event_type, []).copy()

        for callback in subscribers:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")

    # ========== Frame Buffer ==========

    def set_raw_frame(self, frame: np.ndarray) -> None:
        """Set the raw camera frame (thread-safe).

        Args:
            frame: Raw frame from camera
        """
        with self._frame_lock:
            self._frame_buffer.raw_frame = frame.copy() if frame is not None else None
            self._frame_buffer.timestamp = datetime.now()

    def set_display_frame(self, frame: np.ndarray) -> None:
        """Set the display frame with overlays (thread-safe).

        Args:
            frame: Frame with detection overlays
        """
        with self._frame_lock:
            self._frame_buffer.display_frame = frame.copy() if frame is not None else None

    def set_binary_frame(self, frame: np.ndarray) -> None:
        """Set the binary threshold frame (thread-safe).

        Args:
            frame: Binary image from thresholding
        """
        with self._frame_lock:
            self._frame_buffer.binary_frame = frame.copy() if frame is not None else None

    def get_raw_frame(self) -> Optional[np.ndarray]:
        """Get a copy of the raw camera frame (thread-safe).

        Returns:
            Copy of raw frame or None
        """
        with self._frame_lock:
            if self._frame_buffer.raw_frame is not None:
                return self._frame_buffer.raw_frame.copy()
            return None

    def get_display_frame(self) -> Optional[np.ndarray]:
        """Get a copy of the display frame (thread-safe).

        Returns:
            Copy of display frame or None
        """
        with self._frame_lock:
            if self._frame_buffer.display_frame is not None:
                return self._frame_buffer.display_frame.copy()
            return None

    def get_binary_frame(self) -> Optional[np.ndarray]:
        """Get a copy of the binary frame (thread-safe).

        Returns:
            Copy of binary frame or None
        """
        with self._frame_lock:
            if self._frame_buffer.binary_frame is not None:
                return self._frame_buffer.binary_frame.copy()
            return None

    def clear_frames(self) -> None:
        """Clear all frame buffers."""
        with self._frame_lock:
            self._frame_buffer = FrameBuffer()

    # ========== System State ==========

    @property
    def camera_connected(self) -> bool:
        """Get camera connection status."""
        with self._state_lock:
            return self._state.camera_connected

    @camera_connected.setter
    def camera_connected(self, value: bool) -> None:
        """Set camera connection status."""
        with self._state_lock:
            self._state.camera_connected = value
        self.publish(EventType.SYSTEM_STATUS_CHANGED, self.get_status())

    @property
    def is_running(self) -> bool:
        """Get running status."""
        with self._state_lock:
            return self._state.is_running

    @is_running.setter
    def is_running(self, value: bool) -> None:
        """Set running status."""
        with self._state_lock:
            self._state.is_running = value
        self.publish(EventType.SYSTEM_STATUS_CHANGED, self.get_status())

    @property
    def current_recipe(self) -> Optional[str]:
        """Get current recipe name."""
        with self._state_lock:
            return self._state.current_recipe

    @current_recipe.setter
    def current_recipe(self, value: Optional[str]) -> None:
        """Set current recipe name."""
        with self._state_lock:
            self._state.current_recipe = value
        self.publish(EventType.RECIPE_CHANGED, {"name": value})

    @property
    def fps(self) -> float:
        """Get current FPS."""
        with self._state_lock:
            return self._state.fps

    @fps.setter
    def fps(self, value: float) -> None:
        """Set current FPS."""
        with self._state_lock:
            self._state.fps = value

    @property
    def web_clients(self) -> int:
        """Get number of connected web clients."""
        with self._state_lock:
            return self._state.web_clients

    @web_clients.setter
    def web_clients(self, value: int) -> None:
        """Set number of connected web clients."""
        with self._state_lock:
            self._state.web_clients = value

    def get_status(self) -> Dict:
        """Get current system status as dictionary."""
        with self._state_lock:
            return {
                "camera_connected": self._state.camera_connected,
                "is_running": self._state.is_running,
                "current_recipe": self._state.current_recipe,
                "fps": self._state.fps,
                "web_clients": self._state.web_clients,
                "timestamp": datetime.now().isoformat(),
            }

    # ========== Detection Results ==========

    def set_latest_result(self, result: Any) -> None:
        """Set the latest detection result.

        Args:
            result: Detection result (list of CircleResult)
        """
        with self._result_lock:
            self._latest_result = result

        # Add to history
        self._add_to_history(result)

        # Publish event
        self.publish(EventType.DETECTION_COMPLETE, result)

    def get_latest_result(self) -> Optional[Any]:
        """Get the latest detection result."""
        with self._result_lock:
            return self._latest_result

    # ========== History ==========

    def _add_to_history(self, result: Any) -> None:
        """Add detection result to history."""
        if result is None:
            return

        with self._history_lock:
            history_item = {
                "timestamp": datetime.now().isoformat(),
                "result": result,
            }
            self._history.insert(0, history_item)

            # Trim to max size
            if len(self._history) > self._max_history:
                self._history = self._history[: self._max_history]

    def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get measurement history.

        Args:
            limit: Maximum items to return
            offset: Skip first N items

        Returns:
            List of history items
        """
        with self._history_lock:
            return self._history[offset : offset + limit]

    def get_history_count(self) -> int:
        """Get total history count."""
        with self._history_lock:
            return len(self._history)

    def clear_history(self) -> None:
        """Clear measurement history."""
        with self._history_lock:
            self._history.clear()

    # ========== Services ==========

    def register_service(self, name: str, service: Any) -> None:
        """Register a service for dependency injection.

        Args:
            name: Service name
            service: Service instance
        """
        self._services[name] = service
        logger.debug(f"Registered service: {name}")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service.

        Args:
            name: Service name

        Returns:
            Service instance or None
        """
        return self._services.get(name)

    # ========== Convenience Properties ==========

    @property
    def statistics(self) -> Optional[Any]:
        """Get statistics service."""
        return self._statistics

    @statistics.setter
    def statistics(self, value: Any) -> None:
        """Set statistics service."""
        self._statistics = value

    @property
    def io_status(self) -> Optional[Any]:
        """Get IO status."""
        return self._io_status

    @io_status.setter
    def io_status(self, value: Any) -> None:
        """Set IO status."""
        self._io_status = value

    @property
    def calibration_service(self) -> Optional[Any]:
        """Get calibration service."""
        return self._calibration_service

    @calibration_service.setter
    def calibration_service(self, value: Any) -> None:
        """Set calibration service."""
        self._calibration_service = value

    @property
    def recipe_service(self) -> Optional[Any]:
        """Get recipe service."""
        return self._recipe_service

    @recipe_service.setter
    def recipe_service(self, value: Any) -> None:
        """Set recipe service."""
        self._recipe_service = value
