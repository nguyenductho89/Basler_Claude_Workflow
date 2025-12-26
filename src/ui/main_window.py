"""Main Window - Primary application window"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional

from ..services.camera_service import BaslerGigECamera
from ..utils.constants import (
    APP_NAME, APP_VERSION,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    VIDEO_WIDTH, VIDEO_HEIGHT,
    DEFAULT_EXPOSURE_US, UI_UPDATE_INTERVAL
)
from .panels.video_canvas import VideoCanvas
from .panels.camera_panel import CameraPanel

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window"""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title(f"{APP_NAME} v{APP_VERSION}")
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self._root.minsize(800, 600)

        # Services
        self._camera = BaslerGigECamera()

        # State
        self._is_running = False
        self._update_job: Optional[str] = None

        # Setup UI
        self._setup_ui()
        self._setup_bindings()

        logger.info("MainWindow initialized")

    def _setup_ui(self) -> None:
        """Setup the main window UI layout"""
        # Main container
        main_frame = ttk.Frame(self._root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Video display
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.video_canvas = VideoCanvas(left_frame, VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_canvas.pack(fill=tk.BOTH, expand=True)

        # Right panel - Controls
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        # Camera panel
        self.camera_panel = CameraPanel(
            right_frame,
            on_connect=self._on_camera_connect,
            on_disconnect=self._on_camera_disconnect,
            on_refresh=self._on_camera_refresh
        )
        self.camera_panel.pack(fill=tk.X, pady=(0, 10))

        # Exposure control
        exposure_frame = ttk.LabelFrame(right_frame, text="Exposure Control", padding=10)
        exposure_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(exposure_frame, text="Exposure (us):").pack(anchor=tk.W)

        self.exposure_var = tk.DoubleVar(value=DEFAULT_EXPOSURE_US)
        self.exposure_scale = ttk.Scale(
            exposure_frame,
            from_=10,
            to=10000,
            variable=self.exposure_var,
            orient=tk.HORIZONTAL,
            command=self._on_exposure_change
        )
        self.exposure_scale.pack(fill=tk.X, pady=5)

        self.exposure_label = ttk.Label(
            exposure_frame,
            text=f"{DEFAULT_EXPOSURE_US:.1f} us"
        )
        self.exposure_label.pack(anchor=tk.W)

        # Info panel
        info_frame = ttk.LabelFrame(right_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=8, width=30, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)

        # Status bar
        status_frame = ttk.Frame(self._root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_bar = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            padding=5
        )
        self.status_bar.pack(fill=tk.X)

    def _setup_bindings(self) -> None:
        """Setup keyboard and window bindings"""
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._root.bind("<Escape>", lambda e: self._on_close())

    def _on_camera_refresh(self):
        """Refresh camera device list"""
        self._update_status("Scanning for cameras...")
        devices = BaslerGigECamera.list_devices()
        self._update_status(f"Found {len(devices)} camera(s)")
        return devices

    def _on_camera_connect(self, device_index: int) -> None:
        """Connect to camera"""
        self._update_status("Connecting to camera...")

        exposure = self.exposure_var.get()
        success = self._camera.connect(device_index, exposure)

        if success:
            self.camera_panel.set_connected(True, self._camera.device_info)
            self._start_video_update()
            self._update_status("Camera connected")
            self._update_info()
        else:
            messagebox.showerror("Error", "Failed to connect to camera")
            self._update_status("Connection failed")

    def _on_camera_disconnect(self) -> None:
        """Disconnect from camera"""
        self._stop_video_update()
        self._camera.disconnect()
        self.camera_panel.set_connected(False)
        self.video_canvas.clear()
        self._update_status("Camera disconnected")
        self._update_info()

    def _on_exposure_change(self, value: str) -> None:
        """Handle exposure slider change"""
        exposure = float(value)
        self.exposure_label.config(text=f"{exposure:.1f} us")

        if self._camera.is_connected:
            self._camera.set_exposure(exposure)

    def _start_video_update(self) -> None:
        """Start the video update loop"""
        self._is_running = True
        self._update_video()

    def _stop_video_update(self) -> None:
        """Stop the video update loop"""
        self._is_running = False
        if self._update_job:
            self._root.after_cancel(self._update_job)
            self._update_job = None

    def _update_video(self) -> None:
        """Update video frame"""
        if not self._is_running or not self._camera.is_connected:
            return

        try:
            frame = self._camera.grab_frame()
            if frame is not None:
                self.video_canvas.update_frame(frame)
        except Exception as e:
            logger.error(f"Error updating video: {e}")

        # Schedule next update
        self._update_job = self._root.after(UI_UPDATE_INTERVAL, self._update_video)

    def _update_status(self, message: str) -> None:
        """Update status bar message"""
        self.status_bar.config(text=message)
        logger.info(message)

    def _update_info(self) -> None:
        """Update info panel"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        if self._camera.is_connected:
            info = self._camera.get_info()
            text = f"Model: {info.get('model', 'N/A')}\n"
            text += f"Serial: {info.get('serial', 'N/A')}\n"
            text += f"Exposure: {info.get('exposure_us', 'N/A')} us\n"
        else:
            text = "No camera connected"

        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)

    def _on_close(self) -> None:
        """Handle window close"""
        if self._camera.is_connected:
            self._on_camera_disconnect()

        self._root.destroy()
        logger.info("Application closed")

    def run(self) -> None:
        """Start the application main loop"""
        logger.info("Starting application")
        self._root.mainloop()
