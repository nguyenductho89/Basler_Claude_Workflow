"""Configuration data classes"""
from dataclasses import dataclass, field


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


@dataclass
class CameraConfig:
    """Configuration for camera settings"""
    default_exposure_us: float = 50.0
    trigger_mode: str = "software"
    pixel_format: str = "BGR8"
