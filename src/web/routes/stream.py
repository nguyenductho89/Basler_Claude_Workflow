"""MJPEG video stream endpoint.

This module provides the MJPEG streaming endpoint for live video
display in web browsers.
"""

import asyncio
import logging
import time
from typing import AsyncGenerator

import cv2
import numpy as np
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.core import AppCore
from src.web.dependencies import get_app_core

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["stream"])

# Stream configuration
STREAM_FPS = 10  # Target FPS for web streaming
JPEG_QUALITY = 85  # JPEG quality (0-100)
FRAME_INTERVAL = 1.0 / STREAM_FPS  # Time between frames


def create_placeholder_frame() -> np.ndarray:
    """Create a placeholder frame when no camera image is available.

    Returns:
        Placeholder frame with "No Camera" text
    """
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (40, 40, 40)  # Dark gray background

    # Add text
    text = "No Camera Connected"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2

    # Get text size for centering
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (frame.shape[1] - text_width) // 2
    y = (frame.shape[0] + text_height) // 2

    cv2.putText(frame, text, (x, y), font, font_scale, (128, 128, 128), thickness)

    return frame


def encode_frame_to_jpeg(frame: np.ndarray) -> bytes:
    """Encode a frame to JPEG bytes.

    Args:
        frame: OpenCV frame (BGR format)

    Returns:
        JPEG encoded bytes
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    _, buffer = cv2.imencode(".jpg", frame, encode_param)
    return buffer.tobytes()


async def generate_mjpeg_stream(
    app_core: AppCore,
) -> AsyncGenerator[bytes, None]:
    """Generate MJPEG stream frames.

    This generator yields MJPEG frame data in the format expected
    by browsers for multipart streaming.

    Args:
        app_core: AppCore instance for accessing frames

    Yields:
        MJPEG frame bytes with boundary markers
    """
    boundary = b"--frame\r\n"
    content_type = b"Content-Type: image/jpeg\r\n\r\n"

    last_frame_time = 0.0
    placeholder = None

    while True:
        # Throttle to target FPS
        current_time = time.time()
        elapsed = current_time - last_frame_time

        if elapsed < FRAME_INTERVAL:
            await asyncio.sleep(FRAME_INTERVAL - elapsed)

        last_frame_time = time.time()

        try:
            # Get the display frame (with overlays)
            frame = app_core.get_display_frame()

            if frame is None:
                # Try raw frame
                frame = app_core.get_raw_frame()

            if frame is None:
                # Use placeholder
                if placeholder is None:
                    placeholder = create_placeholder_frame()
                frame = placeholder

            # Encode to JPEG
            jpeg_bytes = encode_frame_to_jpeg(frame)

            # Yield MJPEG frame
            yield boundary + content_type + jpeg_bytes + b"\r\n"

        except Exception as e:
            logger.error(f"Error generating stream frame: {e}")
            await asyncio.sleep(0.1)


@router.get("/video")
async def video_stream(app_core: AppCore = Depends(get_app_core)):
    """Get MJPEG video stream.

    This endpoint returns a multipart MJPEG stream that can be
    displayed in an HTML <img> tag:

    ```html
    <img src="http://localhost:8080/stream/video" />
    ```

    The stream runs at approximately 10 FPS to minimize bandwidth
    while providing smooth video playback.
    """
    return StreamingResponse(
        generate_mjpeg_stream(app_core),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
