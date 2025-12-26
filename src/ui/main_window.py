"""Main Window - Primary application window with multi-threading support"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, List

from ..services.camera_service import BaslerGigECamera
from ..services.detector_service import CircleDetector
from ..services.visualizer_service import CircleVisualizer
from ..services.calibration_service import CalibrationService
from ..services.thread_manager import ThreadManager, ProcessResult
from ..services.recipe_service import RecipeService
from ..services.image_saver import ImageSaver
from ..services.io_service import IOService
from ..domain.config import DetectionConfig, ToleranceConfig
from ..domain.io_config import IOConfig, IOMode
from ..domain.entities import CircleResult, CalibrationData
from ..domain.enums import MeasureStatus
from ..domain.recipe import Recipe
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
from .panels.history_panel import HistoryPanel
from .panels.statistics_panel import StatisticsPanel
from .panels.io_panel import IOPanel
from .dialogs.calibration_dialog import CalibrationDialog
from .dialogs.recipe_dialog import RecipeDialog

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window with multi-threaded processing"""

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
        self._recipe_service = RecipeService()
        self._image_saver = ImageSaver()
        self._io_service = IOService()

        # Thread manager
        self._thread_manager = ThreadManager(
            self._camera,
            self._detector,
            self._visualizer
        )

        # Apply calibration to detector
        self._apply_calibration()

        # State
        self._is_running = False
        self._update_job: Optional[str] = None
        self._detection_enabled = True
        self._tolerance_config = ToleranceConfig()
        self._last_circles: List[CircleResult] = []
        self._last_frame = None
        self._last_display_frame = None
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_recipe: Optional[Recipe] = None
        self._save_ng_images = False

        # Setup UI
        self._setup_menu()
        self._setup_ui()
        self._setup_bindings()

        logger.info("MainWindow initialized with multi-threading support")

    def _setup_menu(self) -> None:
        """Setup menu bar"""
        menubar = tk.Menu(self._root)
        self._root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export History...", command=self._export_history)
        file_menu.add_command(label="Export Statistics...", command=self._export_statistics)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Esc")

        # Recipe menu
        recipe_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Recipe", menu=recipe_menu)
        recipe_menu.add_command(label="Manage Recipes...", command=self._open_recipe_dialog)
        recipe_menu.add_separator()
        self._recipe_submenu = tk.Menu(recipe_menu, tearoff=0)
        recipe_menu.add_cascade(label="Load Recipe", menu=self._recipe_submenu)
        recipe_menu.add_command(label="Save Current as Recipe...", command=self._save_current_as_recipe)
        self._update_recipe_submenu()

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calibration...", command=self._open_calibration_dialog)
        tools_menu.add_separator()
        tools_menu.add_command(label="Toggle Detection", command=self._toggle_detection, accelerator="Space")
        tools_menu.add_command(label="Clear History", command=self._clear_history)
        tools_menu.add_command(label="Reset Statistics", command=self._reset_statistics)
        tools_menu.add_separator()
        self._save_ng_var = tk.BooleanVar(value=False)
        tools_menu.add_checkbutton(
            label="Save NG Images",
            variable=self._save_ng_var,
            command=self._toggle_save_ng
        )

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

        # History panel
        self.history_panel = HistoryPanel(right_frame)
        self.history_panel.pack(fill=tk.X, pady=(0, 10))

        # Statistics panel
        self.statistics_panel = StatisticsPanel(right_frame)
        self.statistics_panel.pack(fill=tk.X, pady=(0, 10))

        # IO Panel
        self.io_panel = IOPanel(
            right_frame,
            self._io_service,
            on_trigger=self._on_io_trigger
        )
        self.io_panel.pack(fill=tk.X, pady=(0, 10))

        # Status bar with FPS
        status_frame = ttk.Frame(self._root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_bar = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            padding=5
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.fps_label = ttk.Label(
            status_frame,
            text="FPS: --",
            relief=tk.SUNKEN,
            padding=5,
            width=15
        )
        self.fps_label.pack(side=tk.RIGHT)

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
            self._start_processing()
            self._update_status("Camera connected - Multi-threaded processing active")
        else:
            messagebox.showerror("Error", "Failed to connect to camera")
            self._update_status("Connection failed")

    def _on_camera_disconnect(self) -> None:
        """Disconnect from camera"""
        self._stop_processing()
        self._camera.disconnect()
        self.camera_panel.set_connected(False)
        self.video_canvas.clear()
        self.results_panel.clear()
        self._last_frame = None
        self._update_status("Camera disconnected")
        self.fps_label.config(text="FPS: --")

    def _on_exposure_change(self, value: str) -> None:
        """Handle exposure slider change"""
        exposure = float(value)
        self.exposure_label.config(text=f"{exposure:.1f} us")

        if self._camera.is_connected:
            self._camera.set_exposure(exposure)

    def _on_detection_toggle(self) -> None:
        """Handle detection enable/disable"""
        self._detection_enabled = self.detection_var.get()
        self._thread_manager.set_detection_enabled(self._detection_enabled)

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
        config.pixel_to_mm = self._calibration.pixel_to_mm
        self._detector.update_config(config)
        self._visualizer.update_config(config)
        logger.debug("Detection config updated")

    def _on_tolerance_change(self, tolerance: ToleranceConfig) -> None:
        """Handle tolerance config change"""
        self._tolerance_config = tolerance
        self._thread_manager.set_tolerance_config(tolerance)
        logger.debug(f"Tolerance config updated: enabled={tolerance.enabled}")

    def _start_processing(self) -> None:
        """Start multi-threaded processing"""
        self._thread_manager.set_tolerance_config(self._tolerance_config)
        self._thread_manager.set_detection_enabled(self._detection_enabled)
        self._thread_manager.start()

        self._is_running = True
        self._frame_count = 0
        self._last_fps_time = 0
        self._update_ui()

    def _stop_processing(self) -> None:
        """Stop multi-threaded processing"""
        self._is_running = False
        self._thread_manager.stop()

        if self._update_job:
            self._root.after_cancel(self._update_job)
            self._update_job = None

    def _update_ui(self) -> None:
        """Update UI from processing results"""
        if not self._is_running:
            return

        try:
            # Get result from queue (non-blocking)
            result = self._thread_manager.get_result(timeout=0.01)

            if result is not None:
                self._last_frame = result.frame.copy()
                self._last_display_frame = result.display_frame.copy()
                self._last_circles = result.circles

                # Update video display
                self.video_canvas.update_frame(result.display_frame)

                # Update results panel
                self.results_panel.update_results(result.circles)

                # Add to history and statistics (only if circles detected)
                if result.circles:
                    self.history_panel.add_measurement(result.circles)

                    # Update statistics
                    ok_count = sum(1 for c in result.circles if c.status == MeasureStatus.OK)
                    ng_count = sum(1 for c in result.circles if c.status == MeasureStatus.NG)
                    self.statistics_panel.add_inspection(ok_count, ng_count)

                    # Save NG images if enabled
                    if self._save_ng_images and ng_count > 0:
                        ng_circles = [c for c in result.circles if c.status == MeasureStatus.NG]
                        self._image_saver.save_ng_image(
                            result.frame,
                            ng_circles,
                            result.display_frame
                        )

                    # Send IO result to PLC
                    overall_ok = ng_count == 0
                    self._send_io_result(overall_ok)

                # Update FPS counter
                self._frame_count += 1
                import time
                current_time = time.time()
                if self._last_fps_time == 0:
                    self._last_fps_time = current_time
                elif current_time - self._last_fps_time >= 1.0:
                    fps = self._frame_count / (current_time - self._last_fps_time)
                    self.fps_label.config(text=f"FPS: {fps:.1f}")
                    self._frame_count = 0
                    self._last_fps_time = current_time

        except Exception as e:
            logger.error(f"Error updating UI: {e}")

        # Schedule next update
        self._update_job = self._root.after(UI_UPDATE_INTERVAL, self._update_ui)

    def _export_history(self) -> None:
        """Export history via history panel"""
        self.history_panel._export_csv()

    def _clear_history(self) -> None:
        """Clear history"""
        if messagebox.askyesno("Confirm", "Clear all measurement history?"):
            self.history_panel.clear()

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
            "Features:\n"
            "- Multi-threaded processing\n"
            "- Real-time circle detection\n"
            "- Calibration support\n"
            "- Measurement history\n"
            "- Recipe management\n"
            "- Production statistics\n"
            "- PLC/IO integration\n\n"
            "Camera: Basler acA4600-7gc\n"
            "Lens: Telecentric HK-YC10-80H"
        )

    def _update_recipe_submenu(self) -> None:
        """Update the recipe submenu with available recipes"""
        self._recipe_submenu.delete(0, tk.END)
        recipes = self._recipe_service.recipe_names

        if not recipes:
            self._recipe_submenu.add_command(label="(No recipes)", state=tk.DISABLED)
        else:
            for recipe_name in recipes:
                self._recipe_submenu.add_command(
                    label=recipe_name,
                    command=lambda name=recipe_name: self._load_recipe(name)
                )

    def _open_recipe_dialog(self) -> None:
        """Open recipe management dialog"""
        RecipeDialog(
            self._root,
            self._recipe_service,
            self._on_recipe_load
        )
        self._update_recipe_submenu()

    def _on_recipe_load(self, recipe: Recipe) -> None:
        """Handle recipe load from dialog"""
        self._apply_recipe(recipe)

    def _load_recipe(self, name: str) -> None:
        """Load a recipe by name"""
        recipe = self._recipe_service.get_recipe(name)
        if recipe:
            self._apply_recipe(recipe)
        else:
            messagebox.showerror("Error", f"Failed to load recipe: {name}")

    def _apply_recipe(self, recipe: Recipe) -> None:
        """Apply a recipe to current settings"""
        self._current_recipe = recipe

        # Apply detection config
        self._detector.update_config(recipe.detection_config)
        self._visualizer.update_config(recipe.detection_config)

        # Apply tolerance config
        self._tolerance_config = recipe.tolerance_config
        self._thread_manager.set_tolerance_config(recipe.tolerance_config)

        # Apply calibration
        self._calibration.set_pixel_to_mm(recipe.pixel_to_mm)
        self._apply_calibration()
        self._update_calibration_label()

        # Update UI controls
        self.control_panel.set_config(recipe.detection_config)
        self.control_panel.set_tolerance(recipe.tolerance_config)

        self._root.title(f"{APP_NAME} v{APP_VERSION} - {recipe.name}")
        self._update_status(f"Recipe loaded: {recipe.name}")
        logger.info(f"Recipe applied: {recipe.name}")

    def _save_current_as_recipe(self) -> None:
        """Save current settings as a new recipe"""
        from tkinter import simpledialog
        name = simpledialog.askstring(
            "Save Recipe",
            "Enter recipe name:",
            parent=self._root
        )
        if not name:
            return

        description = simpledialog.askstring(
            "Save Recipe",
            "Enter recipe description (optional):",
            parent=self._root
        ) or ""

        recipe = self._recipe_service.create_recipe(
            name=name,
            description=description,
            detection_config=self._detector.config,
            tolerance_config=self._tolerance_config,
            pixel_to_mm=self._calibration.pixel_to_mm
        )

        if self._recipe_service.save_recipe(recipe):
            self._current_recipe = recipe
            self._root.title(f"{APP_NAME} v{APP_VERSION} - {recipe.name}")
            self._update_recipe_submenu()
            self._update_status(f"Recipe saved: {recipe.name}")
        else:
            messagebox.showerror("Error", "Failed to save recipe")

    def _reset_statistics(self) -> None:
        """Reset production statistics"""
        if messagebox.askyesno("Confirm", "Reset all production statistics?"):
            self.statistics_panel.reset()
            self._update_status("Statistics reset")

    def _export_statistics(self) -> None:
        """Export statistics to CSV"""
        from tkinter import filedialog
        import csv
        from datetime import datetime

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not filepath:
            return

        try:
            stats = self.statistics_panel.get_statistics()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Inspections", stats["total_inspections"]])
                writer.writerow(["Total Circles", stats["total_circles"]])
                writer.writerow(["OK Count", stats["ok_count"]])
                writer.writerow(["NG Count", stats["ng_count"]])
                writer.writerow(["OK Rate (%)", f"{stats['ok_rate']:.2f}"])
                writer.writerow(["Runtime (seconds)", f"{stats['runtime_seconds']:.0f}"])

                if self._current_recipe:
                    writer.writerow(["Recipe", self._current_recipe.name])

            self._update_status(f"Statistics exported to {filepath}")
            logger.info(f"Statistics exported: {filepath}")
        except Exception as e:
            logger.error(f"Failed to export statistics: {e}")
            messagebox.showerror("Error", f"Failed to export statistics: {e}")

    def _toggle_save_ng(self) -> None:
        """Toggle NG image saving"""
        self._save_ng_images = self._save_ng_var.get()
        if self._save_ng_images:
            self._update_status("NG image saving enabled")
        else:
            self._update_status("NG image saving disabled")

    def _on_io_trigger(self) -> None:
        """Handle IO trigger signal"""
        logger.info("IO trigger received")
        # If camera is connected and running, the next frame will be processed
        # This is useful for hardware trigger mode
        if self._camera.is_connected and self._is_running:
            self._update_status("Trigger received - processing...")

    def _send_io_result(self, ok: bool) -> None:
        """Send inspection result to PLC"""
        if self._io_service.is_running:
            self._io_service.set_result(ok)
            logger.debug(f"IO result sent: {'OK' if ok else 'NG'}")

    def _on_close(self) -> None:
        """Handle window close"""
        if self._camera.is_connected:
            self._on_camera_disconnect()

        # Cleanup IO service
        if self._io_service.is_running:
            self._io_service.cleanup()

        self._root.destroy()
        logger.info("Application closed")

    def run(self) -> None:
        """Start the application main loop"""
        logger.info("Starting application")
        self._root.mainloop()
