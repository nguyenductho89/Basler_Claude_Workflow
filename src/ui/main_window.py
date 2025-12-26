"""Main Window - Primary application window"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, List

from ..services.camera_service import BaslerGigECamera
from ..services.detector_service import CircleDetector
from ..services.visualizer_service import CircleVisualizer
from ..services.calibration_service import CalibrationService
from ..domain.config import DetectionConfig, ToleranceConfig
from ..domain.entities import CircleResult, CalibrationData
from ..utils.constants import (
    APP_NAME, APP_VERSION,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    VIDEO_WIDTH, VIDEO_HEIGHT,
    DEFAULT_EXPOSURE_US, UI_UPDATE_INTERVAL
)
from .panels.video_canvas import VideoCanvas
from .panels.camera_panel import CameraPanel
from .panels.control_panel import ControlPanel
from .panels.results_panel import ResultsPanel
from .dialogs.calibration_dialog import CalibrationDialog

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window"""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title(f"{APP_NAME} v{APP_VERSION}")
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self._root.minsize(1000, 700)

        # Services
        self._camera = BaslerGigECamera()
        self._calibration = CalibrationService()
        self._detector = CircleDetector()
        self._visualizer = CircleVisualizer()

        # Apply calibration to detector
        self._apply_calibration()

        # State
        self._is_running = False
        self._update_job: Optional[str] = None
        self._detection_enabled = True
        self._tolerance_config = ToleranceConfig()
        self._last_circles: List[CircleResult] = []
        self._last_frame = None

        # Setup UI
        self._setup_menu()
        self._setup_ui()
        self._setup_bindings()

        logger.info("MainWindow initialized")

    def _setup_menu(self) -> None:
        """Setup menu bar"""
        menubar = tk.Menu(self._root)
        self._root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Esc")

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calibration...", command=self._open_calibration_dialog)
        tools_menu.add_separator()
        tools_menu.add_command(label="Toggle Detection", command=self._toggle_detection, accelerator="Space")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

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

        # Right panel - Controls (scrollable)
        right_outer = ttk.Frame(main_frame, width=320)
        right_outer.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_outer.pack_propagate(False)

        # Create canvas for scrolling
        canvas = tk.Canvas(right_outer, width=300, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_outer, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        right_frame = scrollable_frame

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

        # Calibration info
        calib_frame = ttk.LabelFrame(right_frame, text="Calibration", padding=10)
        calib_frame.pack(fill=tk.X, pady=(0, 10))

        self.calib_label = ttk.Label(calib_frame, text="")
        self.calib_label.pack(anchor=tk.W)

        self.calib_btn = ttk.Button(
            calib_frame,
            text="Open Calibration...",
            command=self._open_calibration_dialog
        )
        self.calib_btn.pack(anchor=tk.W, pady=(5, 0))

        self._update_calibration_label()

        # Detection toggle
        detect_toggle_frame = ttk.Frame(right_frame)
        detect_toggle_frame.pack(fill=tk.X, pady=(0, 10))

        self.detection_var = tk.BooleanVar(value=True)
        self.detection_check = ttk.Checkbutton(
            detect_toggle_frame,
            text="Enable Circle Detection",
            variable=self.detection_var,
            command=self._on_detection_toggle
        )
        self.detection_check.pack(anchor=tk.W)

        # Control panel (Detection settings)
        self.control_panel = ControlPanel(
            right_frame,
            on_config_change=self._on_config_change,
            on_tolerance_change=self._on_tolerance_change
        )
        self.control_panel.pack(fill=tk.X, pady=(0, 10))

        # Results panel
        self.results_panel = ResultsPanel(right_frame)
        self.results_panel.pack(fill=tk.X, pady=(0, 10))

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
        self._root.bind("<space>", lambda e: self._toggle_detection())

    def _apply_calibration(self) -> None:
        """Apply calibration data to detector"""
        config = self._detector.config
        config.pixel_to_mm = self._calibration.pixel_to_mm
        self._detector.update_config(config)
        logger.info(f"Applied calibration: {config.pixel_to_mm:.6f} mm/px")

    def _update_calibration_label(self) -> None:
        """Update calibration info label"""
        info = self._calibration.get_info()
        if info["calibrated"]:
            text = f"Calibrated: {info['pixel_to_mm']:.6f} mm/px"
        else:
            text = f"Default: {info['pixel_to_mm']:.6f} mm/px"
        self.calib_label.config(text=text)

    def _open_calibration_dialog(self) -> None:
        """Open calibration dialog"""
        CalibrationDialog(
            self._root,
            self._calibration,
            self._get_current_frame,
            self._on_calibration_complete
        )

    def _get_current_frame(self):
        """Get current frame for calibration"""
        return self._last_frame

    def _on_calibration_complete(self, calibration: CalibrationData) -> None:
        """Handle calibration complete"""
        self._apply_calibration()
        self._update_calibration_label()
        self._update_status(f"Calibration applied: {calibration.pixel_to_mm:.6f} mm/px")

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
            self._update_status("Camera connected - Circle detection active")
        else:
            messagebox.showerror("Error", "Failed to connect to camera")
            self._update_status("Connection failed")

    def _on_camera_disconnect(self) -> None:
        """Disconnect from camera"""
        self._stop_video_update()
        self._camera.disconnect()
        self.camera_panel.set_connected(False)
        self.video_canvas.clear()
        self.results_panel.clear()
        self._last_frame = None
        self._update_status("Camera disconnected")

    def _on_exposure_change(self, value: str) -> None:
        """Handle exposure slider change"""
        exposure = float(value)
        self.exposure_label.config(text=f"{exposure:.1f} us")

        if self._camera.is_connected:
            self._camera.set_exposure(exposure)

    def _on_detection_toggle(self) -> None:
        """Handle detection enable/disable"""
        self._detection_enabled = self.detection_var.get()
        if self._detection_enabled:
            self._update_status("Circle detection enabled")
        else:
            self._update_status("Circle detection disabled")
            self.results_panel.clear()

    def _toggle_detection(self) -> None:
        """Toggle detection with spacebar"""
        self.detection_var.set(not self.detection_var.get())
        self._on_detection_toggle()

    def _on_config_change(self, config: DetectionConfig) -> None:
        """Handle detection config change"""
        # Preserve calibration when config changes
        config.pixel_to_mm = self._calibration.pixel_to_mm
        self._detector.update_config(config)
        self._visualizer.update_config(config)
        logger.debug("Detection config updated")

    def _on_tolerance_change(self, tolerance: ToleranceConfig) -> None:
        """Handle tolerance config change"""
        self._tolerance_config = tolerance
        logger.debug(f"Tolerance config updated: enabled={tolerance.enabled}")

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
        """Update video frame with circle detection"""
        if not self._is_running or not self._camera.is_connected:
            return

        try:
            frame = self._camera.grab_frame()
            if frame is not None:
                self._last_frame = frame.copy()

                if self._detection_enabled:
                    # Detect circles
                    circles, binary = self._detector.detect(frame)
                    self._last_circles = circles

                    # Draw visualization
                    display_frame = self._visualizer.draw(
                        frame,
                        circles,
                        self._tolerance_config
                    )

                    # Update results panel
                    self.results_panel.update_results(circles)

                    # Display
                    self.video_canvas.update_frame(display_frame)
                else:
                    # Just display raw frame
                    self.video_canvas.update_frame(frame)

        except Exception as e:
            logger.error(f"Error updating video: {e}")

        # Schedule next update
        self._update_job = self._root.after(UI_UPDATE_INTERVAL, self._update_video)

    def _update_status(self, message: str) -> None:
        """Update status bar message"""
        self.status_bar.config(text=message)
        logger.info(message)

    def _show_about(self) -> None:
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            f"{APP_NAME}\nVersion {APP_VERSION}\n\n"
            "Automated Quality Inspection System\n"
            "for measuring circular hole dimensions\n"
            "on metal parts using Machine Vision.\n\n"
            "Camera: Basler acA4600-7gc\n"
            "Lens: Telecentric HK-YC10-80H"
        )

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
