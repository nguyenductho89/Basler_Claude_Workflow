"""Event type constants for the application event bus.

This module defines all event types used for communication between
components in the hybrid architecture (Desktop UI + Web Dashboard).
"""


class EventType:
    """Event type constants for the application event bus."""

    # Detection events
    DETECTION_STARTED = "detection_started"
    DETECTION_COMPLETE = "detection_complete"
    DETECTION_ERROR = "detection_error"

    # Camera events
    CAMERA_CONNECTED = "camera_connected"
    CAMERA_DISCONNECTED = "camera_disconnected"
    CAMERA_ERROR = "camera_error"
    FRAME_CAPTURED = "frame_captured"

    # Statistics events
    STATISTICS_UPDATE = "statistics_update"
    STATISTICS_RESET = "statistics_reset"

    # IO events
    IO_STATUS_CHANGED = "io_status_changed"
    IO_TRIGGER_RECEIVED = "io_trigger_received"
    IO_ERROR = "io_error"

    # Recipe events
    RECIPE_LOADED = "recipe_loaded"
    RECIPE_SAVED = "recipe_saved"
    RECIPE_CHANGED = "recipe_changed"

    # Calibration events
    CALIBRATION_UPDATED = "calibration_updated"

    # System events
    SYSTEM_STATUS_CHANGED = "system_status_changed"
    SYSTEM_ERROR = "system_error"
    SYSTEM_SHUTDOWN = "system_shutdown"

    # Web-specific events (for WebSocket broadcast)
    WEB_CLIENT_CONNECTED = "web_client_connected"
    WEB_CLIENT_DISCONNECTED = "web_client_disconnected"
