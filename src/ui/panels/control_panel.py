"""Control Panel - Detection and display settings"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import logging

from ...domain.config import DetectionConfig, ToleranceConfig

logger = logging.getLogger(__name__)


class ControlPanel(ttk.LabelFrame):
    """Panel for detection and display controls"""

    def __init__(
        self,
        parent,
        on_config_change: Optional[Callable[[DetectionConfig], None]] = None,
        on_tolerance_change: Optional[Callable[[ToleranceConfig], None]] = None
    ):
        super().__init__(parent, text="Detection Settings", padding=10)

        self._on_config_change = on_config_change
        self._on_tolerance_change = on_tolerance_change

        self._config = DetectionConfig()
        self._tolerance = ToleranceConfig()

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Detection parameters section
        detect_frame = ttk.LabelFrame(self, text="Detection Parameters", padding=5)
        detect_frame.pack(fill=tk.X, pady=(0, 10))

        # Min diameter
        self._create_slider(
            detect_frame,
            "Min Diameter (mm):",
            0.5, 20.0,
            self._config.min_diameter_mm,
            self._on_min_diameter_change,
            "min_diameter"
        )

        # Max diameter
        self._create_slider(
            detect_frame,
            "Max Diameter (mm):",
            1.0, 50.0,
            self._config.max_diameter_mm,
            self._on_max_diameter_change,
            "max_diameter"
        )

        # Min circularity
        self._create_slider(
            detect_frame,
            "Min Circularity:",
            0.5, 1.0,
            self._config.min_circularity,
            self._on_circularity_change,
            "circularity"
        )

        # Blur kernel
        ttk.Label(detect_frame, text="Blur Kernel:").pack(anchor=tk.W)
        self.blur_var = tk.IntVar(value=self._config.blur_kernel)
        blur_frame = ttk.Frame(detect_frame)
        blur_frame.pack(fill=tk.X, pady=2)
        for val in [3, 5, 7, 9]:
            ttk.Radiobutton(
                blur_frame,
                text=str(val),
                value=val,
                variable=self.blur_var,
                command=self._on_blur_change
            ).pack(side=tk.LEFT, padx=5)

        # Display options section
        display_frame = ttk.LabelFrame(self, text="Display Options", padding=5)
        display_frame.pack(fill=tk.X, pady=(0, 10))

        self.show_contours_var = tk.BooleanVar(value=self._config.show_contours)
        ttk.Checkbutton(
            display_frame,
            text="Show Contours",
            variable=self.show_contours_var,
            command=self._on_display_change
        ).pack(anchor=tk.W)

        self.show_diameter_var = tk.BooleanVar(value=self._config.show_diameter_line)
        ttk.Checkbutton(
            display_frame,
            text="Show Diameter Line",
            variable=self.show_diameter_var,
            command=self._on_display_change
        ).pack(anchor=tk.W)

        self.show_label_var = tk.BooleanVar(value=self._config.show_label)
        ttk.Checkbutton(
            display_frame,
            text="Show Labels",
            variable=self.show_label_var,
            command=self._on_display_change
        ).pack(anchor=tk.W)

        # Tolerance section
        tolerance_frame = ttk.LabelFrame(self, text="Tolerance Settings", padding=5)
        tolerance_frame.pack(fill=tk.X)

        self.tolerance_enabled_var = tk.BooleanVar(value=self._tolerance.enabled)
        ttk.Checkbutton(
            tolerance_frame,
            text="Enable Tolerance Check",
            variable=self.tolerance_enabled_var,
            command=self._on_tolerance_enable_change
        ).pack(anchor=tk.W)

        # Nominal diameter
        nominal_frame = ttk.Frame(tolerance_frame)
        nominal_frame.pack(fill=tk.X, pady=2)
        ttk.Label(nominal_frame, text="Nominal (mm):").pack(side=tk.LEFT)
        self.nominal_var = tk.DoubleVar(value=self._tolerance.nominal_mm)
        self.nominal_spinbox = ttk.Spinbox(
            nominal_frame,
            from_=0.1,
            to=100.0,
            increment=0.1,
            textvariable=self.nominal_var,
            width=10,
            command=self._on_tolerance_value_change
        )
        self.nominal_spinbox.pack(side=tk.RIGHT)

        # Tolerance +/-
        tol_frame = ttk.Frame(tolerance_frame)
        tol_frame.pack(fill=tk.X, pady=2)
        ttk.Label(tol_frame, text="Tolerance +/- (mm):").pack(side=tk.LEFT)
        self.tolerance_var = tk.DoubleVar(value=self._tolerance.tolerance_mm)
        self.tolerance_spinbox = ttk.Spinbox(
            tol_frame,
            from_=0.001,
            to=10.0,
            increment=0.01,
            textvariable=self.tolerance_var,
            width=10,
            command=self._on_tolerance_value_change
        )
        self.tolerance_spinbox.pack(side=tk.RIGHT)

    def _create_slider(
        self,
        parent,
        label: str,
        from_: float,
        to: float,
        initial: float,
        command: Callable,
        name: str
    ) -> None:
        """Create a labeled slider"""
        ttk.Label(parent, text=label).pack(anchor=tk.W)

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        var = tk.DoubleVar(value=initial)
        setattr(self, f"{name}_var", var)

        scale = ttk.Scale(
            frame,
            from_=from_,
            to=to,
            variable=var,
            orient=tk.HORIZONTAL,
            command=lambda v, cmd=command: cmd(float(v))
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        label_widget = ttk.Label(frame, text=f"{initial:.2f}", width=6)
        label_widget.pack(side=tk.RIGHT)
        setattr(self, f"{name}_label", label_widget)

    def _on_min_diameter_change(self, value: float) -> None:
        """Handle min diameter change"""
        self._config.min_diameter_mm = value
        self.min_diameter_label.config(text=f"{value:.2f}")
        self._notify_config_change()

    def _on_max_diameter_change(self, value: float) -> None:
        """Handle max diameter change"""
        self._config.max_diameter_mm = value
        self.max_diameter_label.config(text=f"{value:.2f}")
        self._notify_config_change()

    def _on_circularity_change(self, value: float) -> None:
        """Handle circularity change"""
        self._config.min_circularity = value
        self.circularity_label.config(text=f"{value:.2f}")
        self._notify_config_change()

    def _on_blur_change(self) -> None:
        """Handle blur kernel change"""
        self._config.blur_kernel = self.blur_var.get()
        self._notify_config_change()

    def _on_display_change(self) -> None:
        """Handle display option change"""
        self._config.show_contours = self.show_contours_var.get()
        self._config.show_diameter_line = self.show_diameter_var.get()
        self._config.show_label = self.show_label_var.get()
        self._notify_config_change()

    def _on_tolerance_enable_change(self) -> None:
        """Handle tolerance enable/disable"""
        self._tolerance.enabled = self.tolerance_enabled_var.get()
        self._notify_tolerance_change()

    def _on_tolerance_value_change(self) -> None:
        """Handle tolerance value change"""
        self._tolerance.nominal_mm = self.nominal_var.get()
        self._tolerance.tolerance_mm = self.tolerance_var.get()
        self._notify_tolerance_change()

    def _notify_config_change(self) -> None:
        """Notify config change callback"""
        if self._on_config_change:
            self._on_config_change(self._config)

    def _notify_tolerance_change(self) -> None:
        """Notify tolerance change callback"""
        if self._on_tolerance_change:
            self._on_tolerance_change(self._tolerance)

    def get_config(self) -> DetectionConfig:
        """Get current detection config"""
        return self._config

    def get_tolerance(self) -> ToleranceConfig:
        """Get current tolerance config"""
        return self._tolerance

    def set_config(self, config: DetectionConfig) -> None:
        """Set detection config"""
        self._config = config
        self.min_diameter_var.set(config.min_diameter_mm)
        self.max_diameter_var.set(config.max_diameter_mm)
        self.circularity_var.set(config.min_circularity)
        self.blur_var.set(config.blur_kernel)
        self.show_contours_var.set(config.show_contours)
        self.show_diameter_var.set(config.show_diameter_line)
        self.show_label_var.set(config.show_label)

    def set_tolerance(self, tolerance: ToleranceConfig) -> None:
        """Set tolerance config"""
        self._tolerance = tolerance
        self.tolerance_enabled_var.set(tolerance.enabled)
        self.nominal_var.set(tolerance.nominal_mm)
        self.tolerance_var.set(tolerance.tolerance_mm)
