"""Calibration Service - Pixel to mm calibration management"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from ..domain.entities import CalibrationData
from ..domain.config import DetectionConfig

logger = logging.getLogger(__name__)


class CalibrationService:
    """Service for managing camera calibration"""

    DEFAULT_CALIBRATION_FILE = "config/calibration.json"

    def __init__(self, config_path: Optional[str] = None):
        self._config_path = Path(config_path or self.DEFAULT_CALIBRATION_FILE)
        self._calibration_data: Optional[CalibrationData] = None
        self._load_calibration()

    @property
    def calibration_data(self) -> Optional[CalibrationData]:
        """Get current calibration data"""
        return self._calibration_data

    @property
    def pixel_to_mm(self) -> float:
        """Get pixel to mm ratio"""
        if self._calibration_data:
            return self._calibration_data.pixel_to_mm
        return DetectionConfig().pixel_to_mm  # Default value

    @property
    def is_calibrated(self) -> bool:
        """Check if calibration data exists"""
        return self._calibration_data is not None

    def set_pixel_to_mm(self, value: float) -> None:
        """Set pixel to mm ratio directly (used when loading recipes)"""
        if value <= 0:
            raise ValueError("Pixel to mm ratio must be positive")

        self._calibration_data = CalibrationData(
            pixel_to_mm=value,
            calibrated_at=datetime.now(),
            reference_size_mm=0,
            reference_size_px=0
        )
        logger.info(f"Pixel to mm ratio set to: {value:.6f}")

    def calibrate(
        self,
        reference_size_mm: float,
        reference_size_px: float
    ) -> CalibrationData:
        """
        Perform calibration using reference measurement

        Args:
            reference_size_mm: Known size in millimeters
            reference_size_px: Measured size in pixels

        Returns:
            CalibrationData object
        """
        if reference_size_px <= 0:
            raise ValueError("Reference size in pixels must be positive")
        if reference_size_mm <= 0:
            raise ValueError("Reference size in mm must be positive")

        self._calibration_data = CalibrationData.create(
            reference_mm=reference_size_mm,
            reference_px=reference_size_px
        )

        self._save_calibration()
        logger.info(
            f"Calibration complete: {self._calibration_data.pixel_to_mm:.6f} mm/px"
        )

        return self._calibration_data

    def calibrate_from_circle(
        self,
        frame: np.ndarray,
        known_diameter_mm: float
    ) -> Optional[CalibrationData]:
        """
        Auto-calibrate from a detected circle

        Args:
            frame: BGR image containing calibration circle
            known_diameter_mm: Known diameter of the circle in mm

        Returns:
            CalibrationData if successful, None otherwise
        """
        # Detect circle in frame
        circle_px = self._detect_calibration_circle(frame)

        if circle_px is None:
            logger.warning("No calibration circle detected")
            return None

        diameter_px = circle_px[2] * 2  # radius to diameter

        return self.calibrate(
            reference_size_mm=known_diameter_mm,
            reference_size_px=diameter_px
        )

    def _detect_calibration_circle(
        self,
        frame: np.ndarray
    ) -> Optional[Tuple[float, float, float]]:
        """
        Detect the largest circle in frame for calibration

        Args:
            frame: BGR image

        Returns:
            (center_x, center_y, radius) if found, None otherwise
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

        # Apply blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Binary threshold
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Find the largest circular contour
        best_circle = None
        best_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if perimeter < 1:
                continue

            # Check circularity
            circularity = 4 * np.pi * area / (perimeter ** 2)

            if circularity > 0.8 and area > best_area:
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                best_circle = (cx, cy, radius)
                best_area = area

        return best_circle

    def _save_calibration(self) -> None:
        """Save calibration data to file"""
        if not self._calibration_data:
            return

        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "pixel_to_mm": self._calibration_data.pixel_to_mm,
                "calibrated_at": self._calibration_data.calibrated_at.isoformat(),
                "reference_size_mm": self._calibration_data.reference_size_mm,
                "reference_size_px": self._calibration_data.reference_size_px
            }

            with open(self._config_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Calibration saved to {self._config_path}")

        except Exception as e:
            logger.error(f"Failed to save calibration: {e}")

    def _load_calibration(self) -> None:
        """Load calibration data from file"""
        if not self._config_path.exists():
            logger.info("No calibration file found, using defaults")
            return

        try:
            with open(self._config_path, 'r') as f:
                data = json.load(f)

            self._calibration_data = CalibrationData(
                pixel_to_mm=data["pixel_to_mm"],
                calibrated_at=datetime.fromisoformat(data["calibrated_at"]),
                reference_size_mm=data["reference_size_mm"],
                reference_size_px=data["reference_size_px"]
            )

            logger.info(
                f"Calibration loaded: {self._calibration_data.pixel_to_mm:.6f} mm/px"
            )

        except Exception as e:
            logger.error(f"Failed to load calibration: {e}")
            self._calibration_data = None

    def reset_calibration(self) -> None:
        """Reset to default calibration"""
        self._calibration_data = None
        if self._config_path.exists():
            try:
                self._config_path.unlink()
                logger.info("Calibration reset to defaults")
            except Exception as e:
                logger.error(f"Failed to delete calibration file: {e}")

    def get_info(self) -> dict:
        """Get calibration information"""
        if not self._calibration_data:
            return {
                "calibrated": False,
                "pixel_to_mm": DetectionConfig().pixel_to_mm,
                "source": "default"
            }

        return {
            "calibrated": True,
            "pixel_to_mm": self._calibration_data.pixel_to_mm,
            "calibrated_at": self._calibration_data.calibrated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "reference_mm": self._calibration_data.reference_size_mm,
            "reference_px": self._calibration_data.reference_size_px,
            "source": str(self._config_path)
        }
