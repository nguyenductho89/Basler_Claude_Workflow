"""Circle Detector Service - Automatic circle detection and measurement"""
import logging
import math
from typing import List, Tuple, Optional

import cv2
import numpy as np

from ..domain.entities import CircleResult
from ..domain.enums import MeasureStatus
from ..domain.config import DetectionConfig

logger = logging.getLogger(__name__)


class CircleDetector:
    """Service for automatic circle detection in images"""

    def __init__(self, config: Optional[DetectionConfig] = None):
        self._config = config or DetectionConfig()
        self._min_area_px: float = 0
        self._max_area_px: float = 0
        self._calc_pixel_limits()

    @property
    def config(self) -> DetectionConfig:
        """Get current detection config"""
        return self._config

    def update_config(self, config: DetectionConfig) -> None:
        """Update detection configuration"""
        self._config = config
        self._calc_pixel_limits()

    def _calc_pixel_limits(self) -> None:
        """Calculate pixel area limits from mm diameter limits"""
        px_per_mm = 1.0 / self._config.pixel_to_mm

        # Calculate area limits (pi * r^2)
        min_radius_px = (self._config.min_diameter_mm / 2) * px_per_mm
        max_radius_px = (self._config.max_diameter_mm / 2) * px_per_mm

        self._min_area_px = math.pi * (min_radius_px ** 2)
        self._max_area_px = math.pi * (max_radius_px ** 2)

        logger.debug(f"Pixel limits: area {self._min_area_px:.0f} - {self._max_area_px:.0f} px²")

    def detect(self, frame: np.ndarray) -> Tuple[List[CircleResult], np.ndarray]:
        """
        Detect circles in frame

        Args:
            frame: BGR image as numpy array

        Returns:
            Tuple of (list of CircleResult, binary image)
        """
        if frame is None or frame.size == 0:
            return [], np.array([])

        # Preprocessing
        binary = self._preprocess(frame)

        # Find and filter circles
        circles = self._find_circles(binary, frame.shape[:2])

        return circles, binary

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess image for circle detection

        Args:
            frame: BGR image

        Returns:
            Binary image
        """
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        # Apply Gaussian blur
        kernel_size = self._config.blur_kernel
        if kernel_size % 2 == 0:
            kernel_size += 1
        blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

        # Binary threshold using Otsu's method
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    def _find_circles(
        self,
        binary: np.ndarray,
        image_shape: Tuple[int, int]
    ) -> List[CircleResult]:
        """
        Find circles in binary image

        Args:
            binary: Binary image
            image_shape: (height, width) of original image

        Returns:
            List of CircleResult
        """
        height, width = image_shape
        circles: List[CircleResult] = []

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        hole_id = 0
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # Skip if area is out of range
            if area < self._min_area_px or area > self._max_area_px:
                continue

            # Skip if perimeter is too small
            if perimeter < 1:
                continue

            # Calculate circularity
            circularity = 4 * math.pi * area / (perimeter ** 2)

            # Skip if not circular enough
            if circularity < self._config.min_circularity:
                continue

            # Fit minimum enclosing circle
            (cx, cy), radius = cv2.minEnclosingCircle(contour)

            # Check edge margin
            margin = self._config.edge_margin
            if (cx - radius < margin or cx + radius > width - margin or
                cy - radius < margin or cy + radius > height - margin):
                continue

            # Calculate measurements
            hole_id += 1
            diameter_px = 2 * radius
            diameter_mm = diameter_px * self._config.pixel_to_mm
            area_mm2 = area * (self._config.pixel_to_mm ** 2)

            circle = CircleResult(
                hole_id=hole_id,
                center_x=cx,
                center_y=cy,
                radius=radius,
                diameter_mm=diameter_mm,
                circularity=circularity,
                area_mm2=area_mm2,
                status=MeasureStatus.OK
            )
            circles.append(circle)

        logger.debug(f"Detected {len(circles)} circle(s)")
        return circles

    def detect_with_hough(self, frame: np.ndarray) -> List[CircleResult]:
        """
        Alternative detection using Hough Circle Transform

        Args:
            frame: BGR image

        Returns:
            List of CircleResult
        """
        if frame is None or frame.size == 0:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame.copy()
        blurred = cv2.GaussianBlur(gray, (self._config.blur_kernel, self._config.blur_kernel), 0)

        # Hough Circle detection
        min_radius = int((self._config.min_diameter_mm / 2) / self._config.pixel_to_mm)
        max_radius = int((self._config.max_diameter_mm / 2) / self._config.pixel_to_mm)

        hough_circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=min_radius * 2,
            param1=50,
            param2=30,
            minRadius=min_radius,
            maxRadius=max_radius
        )

        circles: List[CircleResult] = []
        if hough_circles is not None:
            for i, (x, y, r) in enumerate(hough_circles[0]):
                diameter_mm = 2 * r * self._config.pixel_to_mm
                area_mm2 = math.pi * (r ** 2) * (self._config.pixel_to_mm ** 2)

                circle = CircleResult(
                    hole_id=i + 1,
                    center_x=float(x),
                    center_y=float(y),
                    radius=float(r),
                    diameter_mm=diameter_mm,
                    circularity=1.0,  # Assumed for Hough
                    area_mm2=area_mm2,
                    status=MeasureStatus.OK
                )
                circles.append(circle)

        return circles
