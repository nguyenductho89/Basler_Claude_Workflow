"""WebSocket handler for real-time updates.

This module provides WebSocket endpoint for pushing real-time
events to connected web clients.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Set, Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core import AppCore, EventType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections and broadcasts.

    This class handles:
    - Connection lifecycle (connect/disconnect)
    - Message broadcasting to all clients
    - Event subscription from AppCore
    """

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self._app_core: AppCore = None
        self._broadcast_task: asyncio.Task = None
        self._event_queue: asyncio.Queue = None
        self._running = False

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.add(websocket)

        # Update client count in AppCore
        if self._app_core:
            self._app_core.web_clients = len(self.active_connections)

        logger.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")

        # Send initial status
        await self._send_initial_status(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Handle WebSocket disconnection.

        Args:
            websocket: WebSocket connection that disconnected
        """
        self.active_connections.discard(websocket)

        # Update client count in AppCore
        if self._app_core:
            self._app_core.web_clients = len(self.active_connections)

        logger.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")

    async def _send_initial_status(self, websocket: WebSocket) -> None:
        """Send initial status to a newly connected client.

        Args:
            websocket: WebSocket connection
        """
        try:
            if self._app_core:
                status = self._app_core.get_status()
                await self._send_event(websocket, "system_status", status)
        except Exception as e:
            logger.error(f"Error sending initial status: {e}")

    async def _send_event(self, websocket: WebSocket, event_type: str, data: Any) -> None:
        """Send an event to a single client.

        Args:
            websocket: Target WebSocket connection
            event_type: Event type string
            data: Event data
        """
        try:
            message = {"event": event_type, "data": self._serialize_data(data)}
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending event: {e}")

    async def broadcast(self, event_type: str, data: Any) -> None:
        """Broadcast an event to all connected clients.

        Args:
            event_type: Event type string
            data: Event data
        """
        if not self.active_connections:
            return

        message = {"event": event_type, "data": self._serialize_data(data)}

        # Send to all connections
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    def _serialize_data(self, data: Any) -> Any:
        """Serialize data for JSON transmission.

        Args:
            data: Data to serialize

        Returns:
            JSON-serializable data
        """
        if data is None:
            return None

        if isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self._serialize_data(item) for item in data]

        if isinstance(data, datetime):
            return data.isoformat()

        if hasattr(data, "__dict__"):
            # Convert objects to dict
            result = {}
            for key, value in data.__dict__.items():
                if not key.startswith("_"):
                    result[key] = self._serialize_data(value)
            return result

        if hasattr(data, "value"):
            # Handle enums
            return data.value

        return data

    def setup_event_handlers(self, app_core: AppCore) -> None:
        """Set up event handlers to receive events from AppCore.

        Args:
            app_core: AppCore instance to subscribe to
        """
        self._app_core = app_core
        self._event_queue = asyncio.Queue()

        # Subscribe to events
        def queue_event(event_type: str):
            def handler(data):
                try:
                    # Put event in queue for async processing
                    asyncio.get_event_loop().call_soon_threadsafe(self._event_queue.put_nowait, (event_type, data))
                except Exception:
                    pass

            return handler

        app_core.subscribe(EventType.DETECTION_COMPLETE, queue_event("detection_result"))
        app_core.subscribe(EventType.STATISTICS_UPDATE, queue_event("statistics_update"))
        app_core.subscribe(EventType.IO_STATUS_CHANGED, queue_event("io_status"))
        app_core.subscribe(EventType.SYSTEM_STATUS_CHANGED, queue_event("system_status"))
        app_core.subscribe(EventType.RECIPE_CHANGED, queue_event("recipe_changed"))

    async def start_broadcast_loop(self) -> None:
        """Start the broadcast loop that processes queued events."""
        self._running = True

        while self._running:
            try:
                # Wait for events with timeout
                try:
                    event_type, data = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                    await self.broadcast(event_type, data)
                except asyncio.TimeoutError:
                    pass

            except Exception as e:
                logger.error(f"Broadcast loop error: {e}")
                await asyncio.sleep(0.1)

    def stop_broadcast_loop(self) -> None:
        """Stop the broadcast loop."""
        self._running = False


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates.

    This endpoint provides real-time events to connected clients:
    - detection_result: Circle detection results
    - statistics_update: Production statistics (every 5s)
    - io_status: IO status changes (every 500ms)
    - system_status: System status changes (every 10s)
    - recipe_changed: Recipe change notifications

    Usage (JavaScript):
    ```javascript
    const ws = new WebSocket('ws://localhost:8080/ws/live');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Event:', data.event, data.data);
    };
    ```
    """
    # Initialize manager with AppCore if not already done
    if manager._app_core is None:
        from src.core import AppCore

        manager.setup_event_handlers(AppCore())

    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive by receiving messages
            # (clients may send ping/pong or other messages)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Handle any client messages if needed
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await websocket.send_json({"event": "ping", "data": {}})
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager."""
    return manager
