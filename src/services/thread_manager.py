"""Thread Manager - Multi-threaded camera and processing management"""

import logging
import threading
from queue import Queue, Empty, Full
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from .camera_service import BaslerGigECamera
from .detector_service import CircleDetector
from .visualizer_service import CircleVisualizer
from ..domain.entities import CircleResult
from ..domain.config import ToleranceConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """Result from processing thread"""

    frame: np.ndarray
    display_frame: np.ndarray
    circles: list
    timestamp: datetime
    processing_time_ms: float


class ThreadManager:
    """Manages camera and processing threads"""

    def __init__(self, camera: BaslerGigECamera, detector: CircleDetector, visualizer: CircleVisualizer):
        self._camera = camera
        self._detector = detector
        self._visualizer = visualizer

        # Queues for inter-thread communication
        self._frame_queue: Queue = Queue(maxsize=2)
        self._result_queue: Queue = Queue(maxsize=5)

        # Threads
        self._camera_thread: Optional[threading.Thread] = None
        self._processing_thread: Optional[threading.Thread] = None

        # Control events
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

        # State
        self._is_running = False
        self._detection_enabled = True
        self._tolerance_config = ToleranceConfig()

        # Callbacks
        self._on_result: Optional[Callable[[ProcessResult], None]] = None

    @property
    def is_running(self) -> bool:
        """Check if threads are running"""
        return self._is_running

    def set_detection_enabled(self, enabled: bool) -> None:
        """Enable/disable detection processing"""
        self._detection_enabled = enabled

    def set_tolerance_config(self, config: ToleranceConfig) -> None:
        """Update tolerance config"""
        self._tolerance_config = config

    def set_result_callback(self, callback: Callable[[ProcessResult], None]) -> None:
        """Set callback for processing results"""
        self._on_result = callback

    def start(self) -> None:
        """Start all worker threads"""
        if self._is_running:
            logger.warning("Threads already running")
            return

        self._stop_event.clear()
        self._pause_event.clear()
        self._is_running = True

        # Clear queues
        self._clear_queues()

        # Start camera thread
        self._camera_thread = threading.Thread(target=self._camera_loop, daemon=True, name="CameraThread")
        self._camera_thread.start()

        # Start processing thread
        self._processing_thread = threading.Thread(target=self._processing_loop, daemon=True, name="ProcessingThread")
        self._processing_thread.start()

        logger.info("Worker threads started")

    def stop(self) -> None:
        """Stop all worker threads gracefully"""
        if not self._is_running:
            return

        self._stop_event.set()
        self._is_running = False

        # Wait for threads to finish
        if self._camera_thread and self._camera_thread.is_alive():
            self._camera_thread.join(timeout=2.0)

        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=2.0)

        self._clear_queues()
        logger.info("Worker threads stopped")

    def pause(self) -> None:
        """Pause processing"""
        self._pause_event.set()

    def resume(self) -> None:
        """Resume processing"""
        self._pause_event.clear()

    def get_result(self, timeout: float = 0.1) -> Optional[ProcessResult]:
        """Get latest processing result from queue"""
        try:
            return self._result_queue.get(timeout=timeout)
        except Empty:
            return None

    def _clear_queues(self) -> None:
        """Clear all queues"""
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break

        while not self._result_queue.empty():
            try:
                self._result_queue.get_nowait()
            except Empty:
                break

    def _camera_loop(self) -> None:
        """Camera grab loop - runs in separate thread"""
        logger.info("Camera thread started")

        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                self._stop_event.wait(0.1)
                continue

            if not self._camera.is_connected:
                self._stop_event.wait(0.1)
                continue

            try:
                frame = self._camera.grab_frame(timeout_ms=500)
                if frame is not None:
                    # Try to put frame in queue, drop if full
                    try:
                        self._frame_queue.put(frame, timeout=0.05)
                    except Full:
                        pass  # Drop frame if queue is full

            except Exception as e:
                logger.error(f"Camera thread error: {e}")
                self._stop_event.wait(0.1)

        logger.info("Camera thread stopped")

    def _processing_loop(self) -> None:
        """Image processing loop - runs in separate thread"""
        logger.info("Processing thread started")

        while not self._stop_event.is_set():
            try:
                # Get frame from queue
                frame = self._frame_queue.get(timeout=0.1)
            except Empty:
                continue

            if self._pause_event.is_set():
                continue

            try:
                start_time = datetime.now()

                if self._detection_enabled:
                    # Detect circles
                    circles, binary = self._detector.detect(frame)

                    # Draw visualization
                    display_frame = self._visualizer.draw(frame, circles, self._tolerance_config)
                else:
                    circles = []
                    display_frame = frame.copy()

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                # Create result
                result = ProcessResult(
                    frame=frame,
                    display_frame=display_frame,
                    circles=circles,
                    timestamp=start_time,
                    processing_time_ms=processing_time,
                )

                # Put result in queue
                try:
                    self._result_queue.put(result, timeout=0.05)
                except Full:
                    # Replace oldest result
                    try:
                        self._result_queue.get_nowait()
                        self._result_queue.put(result, timeout=0.05)
                    except (Empty, Full):
                        pass

                # Call callback if set
                if self._on_result:
                    self._on_result(result)

            except Exception as e:
                logger.error(f"Processing thread error: {e}")

        logger.info("Processing thread stopped")
