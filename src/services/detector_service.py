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

        circles = self._find_circles(binary, frame.shape[:2])

        if not circles:
            # Ring-shaped features (boss edge lit by ring/coaxial light) often
            # produce broken arc contours that fail circularity checks even when
            # the ring is clearly visible.  Hough accumulates votes from partial
            # arcs and can find the circle even when only 30-40% of the ring is
            # present.
            logger.info("Contour detection: 0 circles — trying Hough fallback")
            circles = self.detect_with_hough(frame)
            if circles:
                logger.info(f"Hough fallback: found {len(circles)} circle(s)")

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

        if self._config.fill_holes:
            # Flood-fill from (0,0) — always background for a centered part.
            # Background pixels become white; enclosed holes (ring interior) stay
            # black.  OR-ing with NOT(flooded) fills those holes → ring → solid disk.
            h, w = binary.shape[:2]
            temp = binary.copy()
            flood_mask = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(temp, flood_mask, (0, 0), 255)
            binary = cv2.bitwise_or(binary, cv2.bitwise_not(temp))
            logger.debug("Preprocess: filled enclosed holes")

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

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logger.debug(f"Found {len(contours)} contours")

        # Compute all areas once; keep in-range candidates sorted largest first.
        # Boss ring is always the largest in-range contour by a wide margin —
        # pre-sorting enables the dominant-candidate check below.
        all_areas = [(c, cv2.contourArea(c)) for c in contours]
        in_range = sorted(
            [(c, a) for c, a in all_areas if self._min_area_px <= a <= self._max_area_px],
            key=lambda x: x[1],
            reverse=True,
        )
        rejected_area = len(contours) - len(in_range)
        rejected_circularity = 0
        rejected_edge = 0

        # ── Dominant-candidate shortcut ───────────────────────────────────────
        # Ring-light on zinc: the boss ring consistently appears as many arc
        # segments in the binary image (large perimeter → circularity ≈ 0.07,
        # fill_ratio ≈ 0.47 — both fail normal gates).  However, the boss is
        # always 50-100× larger than any specular-noise contour.
        #
        # Measurement: minEnclosingCircle overestimates when noise blobs have
        # merged into the ring and extended its bounding circle (e.g. 13.2mm
        # boss reading as 17mm).  Distance histogram on the contour boundary
        # finds the modal point-to-centroid distance, which peaks at the outer
        # ring edge regardless of protrusions or gaps.
        if self._config.dominant_ratio > 1.0 and in_range:
            top_c, top_a = in_range[0]
            second_a = in_range[1][1] if len(in_range) > 1 else 0.0
            ratio = (top_a / second_a) if second_a > 0 else float("inf")

            if ratio >= self._config.dominant_ratio:
                M = cv2.moments(top_c)
                cx = float(M["m10"] / M["m00"]) if M["m00"] > 0 else width / 2.0
                cy = float(M["m01"] / M["m00"]) if M["m00"] > 0 else height / 2.0

                pts = top_c.reshape(-1, 2).astype(np.float32)
                dists = np.linalg.norm(pts - np.array([[cx, cy]], dtype=np.float32), axis=1)
                n_bins = max(50, int((dists.max() - dists.min()) / 5))
                hist, edges = np.histogram(dists, bins=n_bins)
                peak = int(np.argmax(hist))
                radius = float((edges[peak] + edges[peak + 1]) / 2.0)

                margin = self._config.edge_margin
                if (
                    cx - radius < margin
                    or cx + radius > width - margin
                    or cy - radius < margin
                    or cy + radius > height - margin
                ):
                    logger.debug("Dominant candidate rejected: too close to edge")
                    rejected_edge += 1
                else:
                    diameter_mm = 2.0 * radius * self._config.pixel_to_mm
                    area_mm2 = top_a * self._config.pixel_to_mm**2
                    circles.append(
                        CircleResult(
                            hole_id=1,
                            center_x=cx,
                            center_y=cy,
                            radius=radius,
                            diameter_mm=diameter_mm,
                            circularity=0.0,
                            area_mm2=area_mm2,
                            status=MeasureStatus.OK,
                        )
                    )
                    ratio_tag = f"{ratio:.0f}×" if ratio < float("inf") else "only in range"
                    logger.info(
                        f"Circle #1 [dominant]: D={diameter_mm:.3f}mm (r={radius:.0f}px) | "
                        f"area={top_a:.0f}px² ({ratio_tag} second) | center=({cx:.0f},{cy:.0f})"
                    )
                    logger.info(f"Detected 1 circle(s) from {len(contours)} contours [dominant path]")
                    return circles

        # ── Normal per-contour evaluation ─────────────────────────────────────
        hole_id = 0
        for contour, area in in_range:
            perimeter = cv2.arcLength(contour, True)
            if perimeter < 1:
                continue

            # Perimeter-based circularity: 4πA/P². Sensitive to jagged edges
            # from blur — a blurry circle has ~40% excess perimeter → circularity
            # drops by ~2×. Used as a quality metric but NOT as the primary gate.
            circularity = 4 * math.pi * area / (perimeter**2)

            # fill_ratio = contour_area / area of enclosing circle.
            # A blurry-but-circular blob still fills ~85-95% of its enclosing
            # circle regardless of edge jaggedness, making this blur-resistant.
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            enclosing_area = math.pi * radius**2
            fill_ratio = area / enclosing_area if enclosing_area > 0 else 0.0

            circularity_ok = circularity >= self._config.min_circularity
            fill_ratio_ok = self._config.min_fill_ratio > 0 and fill_ratio >= self._config.min_fill_ratio
            if not circularity_ok and not fill_ratio_ok:
                logger.info(
                    f"Contour rejected: circularity={circularity:.4f} "
                    f"(need >={self._config.min_circularity}), "
                    f"fill_ratio={fill_ratio:.4f} "
                    f"(need >={self._config.min_fill_ratio}) | "
                    f"area={area:.0f}px², perimeter={perimeter:.0f}px"
                )
                rejected_circularity += 1
                continue

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

            hole_id += 1
            diameter_mm = 2 * radius * self._config.pixel_to_mm
            area_mm2 = area * (self._config.pixel_to_mm**2)
            circles.append(
                CircleResult(
                    hole_id=hole_id,
                    center_x=cx,
                    center_y=cy,
                    radius=radius,
                    diameter_mm=diameter_mm,
                    circularity=circularity,
                    area_mm2=area_mm2,
                    status=MeasureStatus.OK,
                )
            )
            logger.info(
                f"Circle #{hole_id}: D={diameter_mm:.3f}mm (r={radius:.0f}px) | "
                f"circularity={circularity:.3f}, fill_ratio={fill_ratio:.3f} | "
                f"center=({cx:.0f},{cy:.0f})"
            )

        if len(circles) == 0 and len(contours) > 0:
            top_areas = sorted([a for _, a in all_areas], reverse=True)[:5]
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

        blur_size = self._config.blur_kernel
        if blur_size % 2 == 0:
            blur_size += 1
        # sigma=0 → OpenCV computes sigma from ksize, giving a proper Gaussian
        blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

        min_radius = int((self._config.min_diameter_mm / 2) / self._config.pixel_to_mm)
        max_radius = int((self._config.max_diameter_mm / 2) / self._config.pixel_to_mm)
        min_radius = max(5, min_radius)
        max_radius = max(min_radius + 10, max_radius)

        logger.debug(
            f"Hough detection: radius range {min_radius}-{max_radius} px, "
            f"diameter range {self._config.min_diameter_mm:.2f}-{self._config.max_diameter_mm:.2f} mm"
        )

        circles: List[CircleResult] = []

        # param1 = Canny high threshold (lower → more edges counted as ring)
        # param2 = accumulator votes needed (lower → easier to detect, more false positives)
        # dp=1 gives full-resolution accumulator — important for large radii (>500px)
        # where dp=1.2 can skip the true radius in the quantised accumulator.
        param_sets = [
            (100, 50),  # Strong edges, high confidence — ideal for clean ring
            (80, 40),  # Medium sensitivity
            (60, 30),  # Permissive — catches fragmented rings
            (40, 20),  # Highly permissive — fallback for broken arcs
        ]

        for param1, param2 in param_sets:
            hough_circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
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

                # Sort by radius descending — boss is the largest circle; noise
                # spots are small and already constrained by minRadius/maxRadius,
                # but among multiple candidates the boss has the biggest radius.
                candidates = sorted(hough_circles[0], key=lambda c: c[2], reverse=True)
                for x, y, r in candidates:
                    if x - r < margin or x + r > width - margin or y - r < margin or y + r > height - margin:
                        logger.debug(f"Hough circle rejected: too close to edge")
                        continue

                    diameter_mm = 2 * r * self._config.pixel_to_mm
                    area_mm2 = math.pi * r**2 * self._config.pixel_to_mm**2
                    circles.append(
                        CircleResult(
                            hole_id=1,
                            center_x=float(x),
                            center_y=float(y),
                            radius=float(r),
                            diameter_mm=diameter_mm,
                            circularity=0.95,
                            area_mm2=area_mm2,
                            status=MeasureStatus.OK,
                        )
                    )
                    logger.info(
                        f"Hough circle: D={diameter_mm:.3f}mm (r={r:.0f}px) | "
                        f"center=({x:.0f},{y:.0f}) | param1={param1}, param2={param2}"
                    )
                    break  # Take only the largest valid circle (boss)

                if circles:
                    break  # Found the boss; stop trying softer param sets

        return circles
