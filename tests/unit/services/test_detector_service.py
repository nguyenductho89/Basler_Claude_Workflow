"""Tests for CircleDetector service"""

import pytest
import numpy as np
import cv2
from src.services.detector_service import CircleDetector
from src.domain.config import DetectionConfig, ToleranceConfig
from src.domain.enums import MeasureStatus


class TestCircleDetector:
    """Test CircleDetector service"""

    @pytest.fixture
    def detector(self):
        """Create detector instance with config suitable for test images"""
        # Test images have circles with ~100px diameter
        # With pixel_to_mm=0.1, diameter_mm = 10mm (within default range)
        config = DetectionConfig(pixel_to_mm=0.1)
        return CircleDetector(config)

    def test_default_config(self, detector):
        """TC-DET-001: Default configuration"""
        assert detector.config is not None
        assert detector.config.min_circularity == 0.85

    def test_detect_single_circle(self, detector, test_image_single_circle):
        """TC-DET-002: Detect single circle"""
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1
        # Check center is approximately at (320, 240)
        circle = circles[0]
        assert abs(circle.center_x - 320) < 10
        assert abs(circle.center_y - 240) < 10

    def test_detect_no_circles(self, detector, test_image_no_circles):
        """TC-DET-003: No circles in blank image"""
        circles, binary = detector.detect(test_image_no_circles)
        assert len(circles) == 0

    def test_detect_multiple_circles(self, detector, test_image_multiple_circles):
        """TC-DET-004: Detect multiple circles"""
        circles, binary = detector.detect(test_image_multiple_circles)
        assert len(circles) >= 2

    def test_filter_non_circular(self, detector, test_image_ellipse):
        """TC-DET-005: Filter non-circular shapes (ellipse)"""
        circles, binary = detector.detect(test_image_ellipse)
        # Ellipse should be filtered due to low circularity
        assert len(circles) == 0

    def test_update_config(self, detector):
        """TC-DET-006: Update detection config"""
        new_config = DetectionConfig(min_diameter_mm=5.0, max_diameter_mm=15.0, min_circularity=0.9)
        detector.update_config(new_config)
        assert detector.config.min_diameter_mm == 5.0
        assert detector.config.max_diameter_mm == 15.0
        assert detector.config.min_circularity == 0.9

    def test_circle_diameter_calculation(self, detector, test_image_single_circle):
        """TC-DET-007: Circle diameter calculation"""
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1
        # Radius was 50px, so diameter should be ~100px (~0.644mm with default pixel_to_mm)
        circle = circles[0]
        # diameter_mm = diameter_px * pixel_to_mm = ~100 * 0.00644 = ~0.644mm
        assert circle.diameter_mm > 0

    def test_grayscale_input(self, detector):
        """TC-DET-008: Handle grayscale input"""
        gray_img = np.zeros((480, 640), dtype=np.uint8)
        cv2.circle(gray_img, (320, 240), 50, 255, -1)
        circles, binary = detector.detect(gray_img)
        assert len(circles) >= 1

    def test_detect_returns_binary(self, detector, test_image_single_circle):
        """TC-DET-009: Detection returns binary image"""
        circles, binary = detector.detect(test_image_single_circle)
        assert binary is not None
        assert len(binary.shape) == 2  # Binary is grayscale

    def test_tolerance_check_method(self):
        """TC-DET-010: Tolerance check using ToleranceConfig"""
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5)
        # Test OK case
        assert tolerance.check(10.0) == MeasureStatus.OK
        assert tolerance.check(10.4) == MeasureStatus.OK
        # Test NG case
        assert tolerance.check(11.0) == MeasureStatus.NG
        assert tolerance.check(9.0) == MeasureStatus.NG
