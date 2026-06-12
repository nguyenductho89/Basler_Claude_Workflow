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

        self._min_area_px = math.pi * (min_radius_px**2)
        self._max_area_px = math.pi * (max_radius_px**2)

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

        # Find and filter circles using the contour method. The circularity
        # filter here is the system's defined gate for rejecting non-circular
        # shapes, so we do not auto-fall back to the more lenient Hough method
        # (which would accept ellipses). Call detect_with_hough() explicitly
        # when ring/annulus detection is required.
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

        # Apply Gaussian blur to reduce noise
        kernel_size = self._config.blur_kernel
        if kernel_size % 2 == 0:
            kernel_size += 1
        blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

        # Threshold to separate the target feature from background.
        if self._config.threshold_method == "adaptive":
            # Adaptive handles uneven lighting across the FOV. Block size scales
            # with the image so large features stay within a single neighbourhood.
            block_size = max(51, (min(frame.shape[:2]) // 10) | 1)  # ensure odd
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 2
            )
            logger.debug(f"Preprocess: adaptive threshold, block_size={block_size}")
        elif self._config.threshold_method == "otsu_inv":
            # Inverted Otsu: dark features (boss/countersink) on bright background
            # (reflected coaxial or ring light on shiny metal plate).
            # The dark boss interior becomes white (foreground) for contour finding.
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            logger.debug("Preprocess: Otsu-INV threshold (reflected light mode)")
        else:
            # Standard Otsu: bright features on dark background (backlit through-holes).
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            logger.debug("Preprocess: Otsu threshold (backlit mode)")

        # Morphological closing: fills small gaps on the bright hole boundary
        # caused by surface texture / partial occlusion, improving circularity.
        if self._config.morph_close_kernel > 0:
            k = self._config.morph_close_kernel
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            logger.debug(f"Preprocess: morphological close, kernel={k}")

        return binary

    def _find_circles(self, binary: np.ndarray, image_shape: Tuple[int, int]) -> List[CircleResult]:
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

        # Find outer contours of the thresholded holes
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        logger.debug(f"Found {len(contours)} contours")

        hole_id = 0
        rejected_area = 0
        rejected_circularity = 0
        rejected_edge = 0
        for contour in contours:
            # Calculate contour properties
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            # Skip if perimeter is too small
            if perimeter < 1:
                continue

            # Skip if area is out of range
            if area < self._min_area_px or area > self._max_area_px:
                logger.debug(
                    f"Contour rejected: area={area:.0f}px² " f"(range: {self._min_area_px:.0f}-{self._max_area_px:.0f})"
                )
                rejected_area += 1
                continue

            # Calculate circularity
            circularity = 4 * math.pi * area / (perimeter**2)

            # Skip if not circular enough
            if circularity < self._config.min_circularity:
                logger.info(
                    f"Contour rejected circularity={circularity:.4f} "
                    f"(need >={self._config.min_circularity}) | area={area:.0f}px², "
                    f"perimeter={perimeter:.0f}px"
                )
                rejected_circularity += 1
                continue

            # Fit minimum enclosing circle
            (cx, cy), radius = cv2.minEnclosingCircle(contour)

            # Check edge margin
            margin = self._config.edge_margin
            if (
                cx - radius < margin
                or cx + radius > width - margin
                or cy - radius < margin
                or cy + radius > height - margin
            ):
                logger.debug(f"Contour rejected: too close to edge (center=({cx:.0f},{cy:.0f}), r={radius:.0f})")
                rejected_edge += 1
                continue

            # Calculate measurements
            hole_id += 1
            diameter_px = 2 * radius
            diameter_mm = diameter_px * self._config.pixel_to_mm
            area_mm2 = area * (self._config.pixel_to_mm**2)

            circle = CircleResult(
                hole_id=hole_id,
                center_x=cx,
                center_y=cy,
                radius=radius,
                diameter_mm=diameter_mm,
                circularity=circularity,
                area_mm2=area_mm2,
                status=MeasureStatus.OK,
            )
            circles.append(circle)
            logger.debug(f"Circle detected: id={hole_id}, diameter={diameter_mm:.3f}mm, circularity={circularity:.3f}")

        if len(circles) == 0 and len(contours) > 0:
            top_areas = sorted([cv2.contourArea(c) for c in contours], reverse=True)[:5]
            logger.info(
                f"Detected 0 circle(s) from {len(contours)} contours "
                f"[rejected: area={rejected_area}, circularity={rejected_circularity}, edge={rejected_edge}] "
                f"| area_range={self._min_area_px:.0f}-{self._max_area_px:.0f}px² "
                f"| top5_areas={[f'{a:.0f}' for a in top_areas]} "
                f"| circularity_threshold={self._config.min_circularity}, method={self._config.threshold_method}"
            )
        else:
            logger.info(f"Detected {len(circles)} circle(s) from {len(contours)} contours")
        return circles

    def detect_with_hough(self, frame: np.ndarray) -> List[CircleResult]:
        """
        Alternative detection using Hough Circle Transform
        Better for detecting ring/annulus shapes

        Args:
            frame: BGR image

        Returns:
            List of CircleResult
        """
        if frame is None or frame.size == 0:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame.copy()

        # Use larger blur for Hough to reduce noise
        blur_size = self._config.blur_kernel
        if blur_size % 2 == 0:
            blur_size += 1
        blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 2)

        # Calculate radius range in pixels
        min_radius = int((self._config.min_diameter_mm / 2) / self._config.pixel_to_mm)
        max_radius = int((self._config.max_diameter_mm / 2) / self._config.pixel_to_mm)

        # Ensure valid range
        min_radius = max(5, min_radius)
        max_radius = max(min_radius + 10, max_radius)

        logger.debug(
            f"Hough detection: radius range {min_radius}-{max_radius} px, "
            f"diameter range {self._config.min_diameter_mm:.2f}-{self._config.max_diameter_mm:.2f} mm"
        )

        circles: List[CircleResult] = []

        # Try multiple parameter combinations for better detection
        param_sets = [
            (50, 30),  # Default
            (100, 30),  # Higher edge threshold
            (50, 20),  # Lower accumulator threshold (more sensitive)
            (80, 25),  # Balanced
        ]

        for param1, param2 in param_sets:
            hough_circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1.2,  # Slightly lower resolution for speed
                minDist=min_radius * 2,
                param1=param1,
                param2=param2,
                minRadius=min_radius,
                maxRadius=max_radius,
            )

            if hough_circles is not None:
                logger.debug(f"Hough found {len(hough_circles[0])} circles with param1={param1}, param2={param2}")
                height, width = frame.shape[:2]
                margin = self._config.edge_margin

                for i, (x, y, r) in enumerate(hough_circles[0]):
                    # Check edge margin
                    if x - r < margin or x + r > width - margin or y - r < margin or y + r > height - margin:
                        logger.debug(f"Hough circle rejected: too close to edge")
                        continue

                    diameter_mm = 2 * r * self._config.pixel_to_mm
                    area_mm2 = math.pi * (r**2) * (self._config.pixel_to_mm**2)

                    circle = CircleResult(
                        hole_id=len(circles) + 1,
                        center_x=float(x),
                        center_y=float(y),
                        radius=float(r),
                        diameter_mm=diameter_mm,
                        circularity=0.95,  # Hough assumes good circularity
                        area_mm2=area_mm2,
                        status=MeasureStatus.OK,
                    )
                    circles.append(circle)
                    logger.debug(f"Hough circle detected: center=({x:.0f},{y:.0f}), r={r:.0f}px, d={diameter_mm:.3f}mm")

                if circles:
                    break  # Found circles, stop trying other params

        return circles
