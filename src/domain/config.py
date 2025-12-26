"""Configuration data classes"""

from dataclasses import dataclass, field
from .enums import MeasureStatus


@dataclass
class DetectionConfig:
    """Configuration for circle detection"""

    pixel_to_mm: float = 0.00644  # mm per pixel (based on FOV calculation)
    min_diameter_mm: float = 1.0
    max_diameter_mm: float = 20.0
    min_circularity: float = 0.85
    blur_kernel: int = 5
    edge_margin: int = 10
    show_contours: bool = True
    show_diameter_line: bool = True
    show_label: bool = True


@dataclass
class ToleranceConfig:
    """Configuration for tolerance checking"""

    enabled: bool = False
    nominal_mm: float = 10.0
    tolerance_mm: float = 0.05

    @property
    def min_mm(self) -> float:
        """Get minimum acceptable diameter"""
        return self.nominal_mm - self.tolerance_mm

    @property
    def max_mm(self) -> float:
        """Get maximum acceptable diameter"""
        return self.nominal_mm + self.tolerance_mm

    def check(self, diameter_mm: float) -> MeasureStatus:
        """
        Check if diameter is within tolerance

        Args:
            diameter_mm: Measured diameter in mm

        Returns:
            MeasureStatus.OK if within tolerance,
            MeasureStatus.NG if outside tolerance,
            MeasureStatus.NONE if tolerance checking disabled
        """
        if not self.enabled:
            return MeasureStatus.NONE

        if self.min_mm <= diameter_mm <= self.max_mm:
            return MeasureStatus.OK
        return MeasureStatus.NG


@dataclass
class CameraConfig:
    """Configuration for camera settings"""

    default_exposure_us: float = 50.0
    trigger_mode: str = "software"
    pixel_format: str = "BGR8"
