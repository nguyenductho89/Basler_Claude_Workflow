"""Configuration data classes"""

from dataclasses import dataclass, field
from .enums import MeasureStatus


@dataclass
class DetectionConfig:
    """Configuration for circle detection"""

    pixel_to_mm: float = 0.00644  # mm per pixel (based on FOV calculation)
    min_diameter_mm: float = 3.0
    max_diameter_mm: float = 20.0
    min_circularity: float = 0.75
    # fill_ratio = contour_area / enclosing_circle_area. Unlike perimeter-based
    # circularity, this is immune to jagged edges caused by blur or noise —
    # a blurry-but-circular blob still fills ~90% of its enclosing circle.
    # Set to 0.0 to disable (use circularity only).
    min_fill_ratio: float = 0.65
    blur_kernel: int = 31
    edge_margin: int = 10
    # Thresholding method:
    #   "otsu"     – bright features on dark background (backlit through-holes)
    #   "otsu_inv" – dark features on bright background (reflected coaxial/ring
    #                light on shiny metal; boss/countersink detection)
    #   "adaptive" – uneven lighting across FOV
    threshold_method: str = "otsu"
    # Morphological closing kernel (px) applied after threshold to smooth
    # contour boundaries. 0 = disabled.
    morph_close_kernel: int = 15
    # After morph-close, flood-fill from the image border to find all background
    # pixels, then fill enclosed holes in white regions.  Converts a closed ring
    # (annulus) into a solid disk so contour-circularity → ~1.0.  Has no effect
    # when the ring has un-bridged gaps (background still reaches the interior).
    fill_holes: bool = True
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
    # Image quality parameters
    gain_db: float = 0.0  # Lower = less noise = sharper
    gamma: float = 1.0  # 1.0 = no correction
    sharpness: float = 0.0  # Higher = sharper edges (if supported)
