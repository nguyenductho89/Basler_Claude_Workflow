"""Domain entities"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import MeasureStatus


@dataclass
class CircleResult:
    """Result of a detected circle"""

    hole_id: int
    center_x: float  # pixels
    center_y: float  # pixels
    radius: float  # pixels
    diameter_mm: float
    circularity: float
    area_mm2: float
    status: MeasureStatus = MeasureStatus.OK
    confidence: float = 1.0


@dataclass
class CalibrationData:
    """Calibration data for pixel to mm conversion"""

    pixel_to_mm: float
    calibrated_at: datetime
    reference_size_mm: float
    reference_size_px: float

    @classmethod
    def create(cls, reference_mm: float, reference_px: float) -> "CalibrationData":
        """Create calibration data from reference measurement"""
        return cls(
            pixel_to_mm=reference_mm / reference_px,
            calibrated_at=datetime.now(),
            reference_size_mm=reference_mm,
            reference_size_px=reference_px,
        )
