"""Circle Visualizer Service - Draw detection results on images"""

import logging
from typing import List, Optional, Tuple

import cv2
import numpy as np

from ..domain.entities import CircleResult
from ..domain.enums import MeasureStatus
from ..domain.config import DetectionConfig, ToleranceConfig

logger = logging.getLogger(__name__)


class CircleVisualizer:
    """Service for visualizing circle detection results"""

    # Color definitions (BGR)
    COLOR_OK = (0, 255, 0)  # Green
    COLOR_NG = (0, 0, 255)  # Red
    COLOR_PARTIAL = (0, 165, 255)  # Orange
    COLOR_EDGE = (255, 255, 0)  # Cyan
    COLOR_DIAMETER = (255, 0, 0)  # Blue
    COLOR_LABEL_BG = (0, 0, 0)  # Black
    COLOR_LABEL_TEXT = (255, 255, 255)  # White

    def __init__(self, config: Optional[DetectionConfig] = None):
        self._config = config or DetectionConfig()

    def update_config(self, config: DetectionConfig) -> None:
        """Update visualization configuration"""
        self._config = config

    def draw(
        self, frame: np.ndarray, circles: List[CircleResult], tolerance: Optional[ToleranceConfig] = None
    ) -> np.ndarray:
        """
        Draw detection results on frame

        Args:
            frame: BGR image
            circles: List of detected circles
            tolerance: Optional tolerance config for OK/NG coloring

        Returns:
            Frame with overlay drawn
        """
        if frame is None or frame.size == 0:
            return frame

        output = frame.copy()

        for circle in circles:
            # Determine status color
            color = self._get_status_color(circle, tolerance)

            # Update circle status based on tolerance
            if tolerance and tolerance.enabled:
                circle.status = self._check_tolerance(circle, tolerance)

            # Draw circle edge
            if self._config.show_contours:
                self._draw_circle_edge(output, circle, color)

            # Draw diameter line
            if self._config.show_diameter_line:
                self._draw_diameter_line(output, circle)

            # Draw label
            if self._config.show_label:
                self._draw_label(output, circle, color)

        return output

    def _get_status_color(self, circle: CircleResult, tolerance: Optional[ToleranceConfig]) -> Tuple[int, int, int]:
        """Get color based on circle status and tolerance"""
        if tolerance and tolerance.enabled:
            status = self._check_tolerance(circle, tolerance)
            if status == MeasureStatus.OK:
                return self.COLOR_OK
            elif status == MeasureStatus.NG:
                return self.COLOR_NG
            elif status == MeasureStatus.PARTIAL:
                return self.COLOR_PARTIAL

        # Default based on existing status
        if circle.status == MeasureStatus.OK:
            return self.COLOR_OK
        elif circle.status == MeasureStatus.NG:
            return self.COLOR_NG
        elif circle.status == MeasureStatus.PARTIAL:
            return self.COLOR_PARTIAL

        return self.COLOR_EDGE

    def _check_tolerance(self, circle: CircleResult, tolerance: ToleranceConfig) -> MeasureStatus:
        """Check if circle is within tolerance"""
        if not tolerance.enabled:
            return MeasureStatus.OK

        lower = tolerance.nominal_mm - tolerance.tolerance_mm
        upper = tolerance.nominal_mm + tolerance.tolerance_mm

        if lower <= circle.diameter_mm <= upper:
            return MeasureStatus.OK
        else:
            return MeasureStatus.NG

    def _draw_circle_edge(self, frame: np.ndarray, circle: CircleResult, color: Tuple[int, int, int]) -> None:
        """Draw circle edge"""
        center = (int(circle.center_x), int(circle.center_y))
        radius = int(circle.radius)
        # Thickness 8px: at 0.17× display scale this renders as ~1.4px — visible
        cv2.circle(frame, center, radius, color, 8)

    def _draw_diameter_line(self, frame: np.ndarray, circle: CircleResult) -> None:
        """Draw diameter line through center"""
        cx, cy = int(circle.center_x), int(circle.center_y)
        r = int(circle.radius)

        cv2.line(frame, (cx - r, cy), (cx + r, cy), self.COLOR_DIAMETER, 5)
        cv2.line(frame, (cx, cy - r), (cx, cy + r), self.COLOR_DIAMETER, 5)
        cv2.circle(frame, (cx, cy), 15, self.COLOR_DIAMETER, -1)

    def _draw_label(self, frame: np.ndarray, circle: CircleResult, color: Tuple[int, int, int]) -> None:
        """Draw measurement label"""
        label = f"D={circle.diameter_mm:.3f}mm"

        label_x = int(circle.center_x - circle.radius)
        label_y = int(circle.center_y - circle.radius - 40)

        if label_y < 80:
            label_y = int(circle.center_y + circle.radius + 100)

        # Font sized for 14MP source image displayed at ~0.17× scale.
        # scale=4.0 → ~80px source height → ~14px on 800px display (readable).
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 4.0
        thickness = 5
        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

        padding = 15
        cv2.rectangle(
            frame,
            (label_x - padding, label_y - text_h - padding),
            (label_x + text_w + padding, label_y + baseline + padding),
            self.COLOR_LABEL_BG,
            -1,
        )
        cv2.putText(frame, label, (label_x, label_y), font, font_scale, color, thickness)

        id_label = f"#{circle.hole_id}"
        id_x = int(circle.center_x - 30)
        id_y = int(circle.center_y + 10)
        cv2.putText(frame, id_label, (id_x, id_y), font, 3.0, self.COLOR_LABEL_TEXT, 4)

    def draw_binary_overlay(self, frame: np.ndarray, binary: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Draw semi-transparent binary overlay

        Args:
            frame: Original BGR image
            binary: Binary image
            alpha: Transparency (0-1)

        Returns:
            Frame with binary overlay
        """
        if frame is None or binary is None:
            return frame

        # Create colored overlay from binary
        overlay = np.zeros_like(frame)
        overlay[binary > 0] = [0, 255, 0]  # Green for detected areas

        # Blend with original
        output = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)

        return output

    def draw_statistics(
        self, frame: np.ndarray, circles: List[CircleResult], position: Tuple[int, int] = (10, 30)
    ) -> np.ndarray:
        """
        Draw statistics on frame

        Args:
            frame: BGR image
            circles: List of circles
            position: (x, y) position for text

        Returns:
            Frame with statistics
        """
        if frame is None:
            return frame

        output = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        thickness = 4
        line_height = 80

        x, y = position

        ok_count = sum(1 for c in circles if c.status == MeasureStatus.OK)
        ng_count = sum(1 for c in circles if c.status == MeasureStatus.NG)

        lines = [f"Detected: {len(circles)}", f"OK: {ok_count}", f"NG: {ng_count}"]

        for i, line in enumerate(lines):
            cv2.putText(output, line, (x, y + i * line_height), font, font_scale, self.COLOR_LABEL_TEXT, thickness)

        return output
