"""Calibration Dialog - UI for camera calibration"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import logging

import numpy as np

from ...services.calibration_service import CalibrationService
from ...domain.entities import CalibrationData

logger = logging.getLogger(__name__)


class CalibrationDialog(tk.Toplevel):
    """Dialog for performing camera calibration"""

    def __init__(
        self,
        parent,
        calibration_service: CalibrationService,
        get_frame_callback: Callable[[], Optional[np.ndarray]],
        on_calibration_complete: Optional[Callable[[CalibrationData], None]] = None
    ):
        super().__init__(parent)

        self.title("Camera Calibration")
        self.geometry("450x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._calibration_service = calibration_service
        self._get_frame = get_frame_callback
        self._on_complete = on_calibration_complete
        self._current_frame: Optional[np.ndarray] = None
        self._measured_diameter_px: Optional[float] = None

        self._setup_ui()
        self._update_info()

    def _setup_ui(self) -> None:
        """Setup dialog UI"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Current calibration info
        info_frame = ttk.LabelFrame(main_frame, text="Current Calibration", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        self.info_text = tk.Text(info_frame, height=5, width=45, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)

        # Calibration method
        method_frame = ttk.LabelFrame(main_frame, text="Calibration Method", padding=10)
        method_frame.pack(fill=tk.X, pady=(0, 15))

        # Option 1: Manual entry
        manual_frame = ttk.Frame(method_frame)
        manual_frame.pack(fill=tk.X, pady=5)

        ttk.Label(manual_frame, text="Manual Entry:").pack(anchor=tk.W)

        entry_frame = ttk.Frame(manual_frame)
        entry_frame.pack(fill=tk.X, pady=5)

        ttk.Label(entry_frame, text="Reference size (mm):").pack(side=tk.LEFT)
        self.ref_mm_var = tk.DoubleVar(value=10.0)
        self.ref_mm_entry = ttk.Entry(entry_frame, textvariable=self.ref_mm_var, width=10)
        self.ref_mm_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(entry_frame, text="Measured (px):").pack(side=tk.LEFT)
        self.ref_px_var = tk.DoubleVar(value=1550.0)
        self.ref_px_entry = ttk.Entry(entry_frame, textvariable=self.ref_px_var, width=10)
        self.ref_px_entry.pack(side=tk.LEFT, padx=5)

        self.manual_btn = ttk.Button(
            manual_frame,
            text="Calibrate (Manual)",
            command=self._on_manual_calibrate
        )
        self.manual_btn.pack(anchor=tk.W, pady=5)

        ttk.Separator(method_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Option 2: Auto-detect from frame
        auto_frame = ttk.Frame(method_frame)
        auto_frame.pack(fill=tk.X, pady=5)

        ttk.Label(auto_frame, text="Auto-Detect from Camera:").pack(anchor=tk.W)

        auto_entry_frame = ttk.Frame(auto_frame)
        auto_entry_frame.pack(fill=tk.X, pady=5)

        ttk.Label(auto_entry_frame, text="Known diameter (mm):").pack(side=tk.LEFT)
        self.known_mm_var = tk.DoubleVar(value=10.0)
        self.known_mm_entry = ttk.Entry(auto_entry_frame, textvariable=self.known_mm_var, width=10)
        self.known_mm_entry.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(auto_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.capture_btn = ttk.Button(
            btn_frame,
            text="Capture Frame",
            command=self._on_capture_frame
        )
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.auto_btn = ttk.Button(
            btn_frame,
            text="Detect & Calibrate",
            command=self._on_auto_calibrate,
            state=tk.DISABLED
        )
        self.auto_btn.pack(side=tk.LEFT)

        self.capture_status = ttk.Label(auto_frame, text="No frame captured")
        self.capture_status.pack(anchor=tk.W)

        # Bottom buttons
        btn_bottom = ttk.Frame(main_frame)
        btn_bottom.pack(fill=tk.X, pady=(15, 0))

        self.reset_btn = ttk.Button(
            btn_bottom,
            text="Reset to Default",
            command=self._on_reset
        )
        self.reset_btn.pack(side=tk.LEFT)

        self.close_btn = ttk.Button(
            btn_bottom,
            text="Close",
            command=self.destroy
        )
        self.close_btn.pack(side=tk.RIGHT)

    def _update_info(self) -> None:
        """Update calibration info display"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = self._calibration_service.get_info()

        if info["calibrated"]:
            text = f"Status: Calibrated\n"
            text += f"Pixel to mm: {info['pixel_to_mm']:.6f} mm/px\n"
            text += f"Calibrated at: {info['calibrated_at']}\n"
            text += f"Reference: {info['reference_mm']:.3f} mm = {info['reference_px']:.1f} px"
        else:
            text = f"Status: Using defaults\n"
            text += f"Pixel to mm: {info['pixel_to_mm']:.6f} mm/px\n"
            text += f"(Based on theoretical FOV calculation)"

        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)

    def _on_manual_calibrate(self) -> None:
        """Handle manual calibration"""
        try:
            ref_mm = self.ref_mm_var.get()
            ref_px = self.ref_px_var.get()

            if ref_mm <= 0 or ref_px <= 0:
                messagebox.showerror("Error", "Values must be positive")
                return

            calibration = self._calibration_service.calibrate(ref_mm, ref_px)
            self._update_info()

            messagebox.showinfo(
                "Success",
                f"Calibration complete!\nPixel to mm: {calibration.pixel_to_mm:.6f}"
            )

            if self._on_complete:
                self._on_complete(calibration)

        except Exception as e:
            logger.error(f"Calibration error: {e}")
            messagebox.showerror("Error", f"Calibration failed: {e}")

    def _on_capture_frame(self) -> None:
        """Capture current frame for auto-calibration"""
        frame = self._get_frame()

        if frame is None:
            messagebox.showwarning("Warning", "No frame available. Is camera connected?")
            return

        self._current_frame = frame.copy()
        self.capture_status.config(text=f"Frame captured: {frame.shape[1]}x{frame.shape[0]}")
        self.auto_btn.config(state=tk.NORMAL)
        logger.info("Calibration frame captured")

    def _on_auto_calibrate(self) -> None:
        """Auto-detect circle and calibrate"""
        if self._current_frame is None:
            messagebox.showwarning("Warning", "Please capture a frame first")
            return

        try:
            known_mm = self.known_mm_var.get()

            if known_mm <= 0:
                messagebox.showerror("Error", "Known diameter must be positive")
                return

            calibration = self._calibration_service.calibrate_from_circle(
                self._current_frame,
                known_mm
            )

            if calibration is None:
                messagebox.showwarning(
                    "Warning",
                    "Could not detect a circle in the captured frame.\n"
                    "Please ensure a circular reference object is clearly visible."
                )
                return

            self._update_info()

            messagebox.showinfo(
                "Success",
                f"Auto-calibration complete!\nPixel to mm: {calibration.pixel_to_mm:.6f}"
            )

            if self._on_complete:
                self._on_complete(calibration)

        except Exception as e:
            logger.error(f"Auto-calibration error: {e}")
            messagebox.showerror("Error", f"Auto-calibration failed: {e}")

    def _on_reset(self) -> None:
        """Reset calibration to defaults"""
        if messagebox.askyesno("Confirm", "Reset calibration to default values?"):
            self._calibration_service.reset_calibration()
            self._update_info()
            logger.info("Calibration reset to defaults")
