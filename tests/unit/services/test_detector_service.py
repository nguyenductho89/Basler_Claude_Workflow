"""Tests for CircleDetector service"""
import pytest
import numpy as np
import cv2
from src.services.detector_service import CircleDetector
from src.domain.config import DetectionConfig


class TestCircleDetector:
    """Test CircleDetector service"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return CircleDetector()

    def test_default_config(self, detector):
        """TC-DET-001: Default configuration"""
        assert detector.config is not None
        assert detector.config.min_circularity == 0.85

    def test_detect_single_circle(self, detector, test_image_single_circle):
        """TC-DET-002: Detect single circle"""
        circles = detector.detect(test_image_single_circle)
        assert len(circles) >= 1
        # Check center is approximately at (320, 240)
        circle = circles[0]
        assert abs(circle.center_x - 320) < 10
        assert abs(circle.center_y - 240) < 10

    def test_detect_no_circles(self, detector, test_image_no_circles):
        """TC-DET-003: No circles in blank image"""
        circles = detector.detect(test_image_no_circles)
        assert len(circles) == 0

    def test_detect_multiple_circles(self, detector, test_image_multiple_circles):
        """TC-DET-004: Detect multiple circles"""
        circles = detector.detect(test_image_multiple_circles)
        assert len(circles) >= 2

    def test_filter_non_circular(self, detector, test_image_ellipse):
        """TC-DET-005: Filter non-circular shapes (ellipse)"""
        circles = detector.detect(test_image_ellipse)
        # Ellipse should be filtered due to low circularity
        assert len(circles) == 0

    def test_update_config(self, detector):
        """TC-DET-006: Update detection config"""
        new_config = DetectionConfig(
            min_diameter_mm=5.0,
            max_diameter_mm=15.0,
            min_circularity=0.9
        )
        detector.update_config(new_config)
        assert detector.config.min_diameter_mm == 5.0
        assert detector.config.max_diameter_mm == 15.0
        assert detector.config.min_circularity == 0.9

    def test_circle_diameter_calculation(self, detector, test_image_single_circle):
        """TC-DET-007: Circle diameter calculation"""
        circles = detector.detect(test_image_single_circle)
        assert len(circles) >= 1
        # Radius was 50px, so diameter should be ~100px
        circle = circles[0]
        assert abs(circle.diameter_px - 100) < 10

    def test_grayscale_input(self, detector):
        """TC-DET-008: Handle grayscale input"""
        gray_img = np.zeros((480, 640), dtype=np.uint8)
        cv2.circle(gray_img, (320, 240), 50, 255, -1)
        circles = detector.detect(gray_img)
        assert len(circles) >= 1

    def test_detect_with_tolerance(self, detector, test_image_single_circle):
        """TC-DET-009: Detection with tolerance checking"""
        from src.domain.config import ToleranceConfig

        tolerance = ToleranceConfig(
            enabled=True,
            nominal_mm=0.644,  # ~100px * 0.00644
            tolerance_mm=0.1
        )
        circles = detector.detect(test_image_single_circle, tolerance)
        assert len(circles) >= 1
        # Check that status is set
        assert circles[0].status is not None
