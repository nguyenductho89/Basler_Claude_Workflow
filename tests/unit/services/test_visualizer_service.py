"""Tests for CircleVisualizer - US-03, US-04: Display results and OK/NG colors"""

import pytest
import numpy as np
import cv2
from src.services.visualizer_service import CircleVisualizer
from src.domain.entities import CircleResult
from src.domain.config import DetectionConfig, ToleranceConfig
from src.domain.enums import MeasureStatus


class TestCircleVisualizer:
    """Test CircleVisualizer for US-03 and US-04"""

    @pytest.fixture
    def visualizer(self):
        """Create visualizer with default config"""
        return CircleVisualizer()

    @pytest.fixture
    def test_frame(self):
        """Create test frame"""
        return np.zeros((480, 640, 3), dtype=np.uint8)

    @pytest.fixture
    def sample_circle_ok(self):
        """Create sample OK circle result"""
        return CircleResult(
            hole_id=1,
            center_x=320,
            center_y=240,
            radius=50,  # 100px diameter
            diameter_mm=10.0,
            circularity=0.95,
            area_mm2=78.54,
            status=MeasureStatus.OK,
        )

    @pytest.fixture
    def sample_circle_ng(self):
        """Create sample NG circle result"""
        return CircleResult(
            hole_id=2,
            center_x=480,
            center_y=240,
            radius=40,  # 80px diameter
            diameter_mm=8.0,
            circularity=0.92,
            area_mm2=50.27,
            status=MeasureStatus.NG,
        )

    # ========== US-03: Display measurement results ==========
    def test_draw_returns_valid_frame(self, visualizer, test_frame, sample_circle_ok):
        """TC-VIS-001: Draw returns valid frame with same shape"""
        circles = [sample_circle_ok]
        result = visualizer.draw(test_frame, circles)

        assert result is not None
        assert result.shape == test_frame.shape

    def test_draw_multiple_circles(self, visualizer, test_frame, sample_circle_ok, sample_circle_ng):
        """TC-VIS-002: Draw multiple circles"""
        circles = [sample_circle_ok, sample_circle_ng]
        result = visualizer.draw(test_frame, circles)

        assert result is not None
        # Frame should be modified (not all zeros)
        assert not np.array_equal(result, test_frame)

    def test_draw_empty_circles(self, visualizer, test_frame):
        """TC-VIS-003: Draw with empty circle list"""
        result = visualizer.draw(test_frame, [])

        assert result is not None
        assert result.shape == test_frame.shape

    def test_draw_none_frame(self, visualizer, sample_circle_ok):
        """TC-VIS-004: Handle None frame gracefully"""
        result = visualizer.draw(None, [sample_circle_ok])
        assert result is None

    def test_draw_empty_frame(self, visualizer, sample_circle_ok):
        """TC-VIS-005: Handle empty frame gracefully"""
        empty_frame = np.array([])
        result = visualizer.draw(empty_frame, [sample_circle_ok])
        assert result is not None

    # ========== US-04: OK/NG color display ==========
    def test_ok_circle_color(self, visualizer, test_frame, sample_circle_ok):
        """TC-VIS-006: OK circle displayed in green"""
        circles = [sample_circle_ok]
        result = visualizer.draw(test_frame, circles)

        # Check that green color (0, 255, 0) exists in the result
        green_pixels = np.where((result[:, :, 0] == 0) & (result[:, :, 1] == 255) & (result[:, :, 2] == 0))
        assert len(green_pixels[0]) > 0

    def test_ng_circle_color(self, visualizer, test_frame, sample_circle_ng):
        """TC-VIS-007: NG circle displayed in red"""
        circles = [sample_circle_ng]
        result = visualizer.draw(test_frame, circles)

        # Check that red color (0, 0, 255) exists in the result
        red_pixels = np.where((result[:, :, 0] == 0) & (result[:, :, 1] == 0) & (result[:, :, 2] == 255))
        assert len(red_pixels[0]) > 0

    def test_tolerance_check_updates_color(self, visualizer, test_frame):
        """TC-VIS-008: Tolerance check updates circle color"""
        # Circle with diameter 10mm
        circle = CircleResult(
            hole_id=1,
            center_x=320,
            center_y=240,
            radius=50,  # 100px diameter
            diameter_mm=10.0,
            circularity=0.95,
            area_mm2=78.54,
            status=MeasureStatus.NONE,
        )

        # Tolerance: nominal=10mm, tolerance=0.5mm -> OK range: 9.5-10.5mm
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5)

        result = visualizer.draw(test_frame, [circle], tolerance)

        # Circle should be marked as OK (green) since 10.0 is within tolerance
        green_pixels = np.where((result[:, :, 0] == 0) & (result[:, :, 1] == 255) & (result[:, :, 2] == 0))
        assert len(green_pixels[0]) > 0

    def test_tolerance_ng_color(self, visualizer, test_frame):
        """TC-VIS-009: Circle outside tolerance shown as NG (red)"""
        # Circle with diameter 12mm
        circle = CircleResult(
            hole_id=1,
            center_x=320,
            center_y=240,
            radius=50,
            diameter_mm=12.0,  # Outside tolerance
            circularity=0.95,
            area_mm2=78.54,
            status=MeasureStatus.NONE,
        )

        # Tolerance: nominal=10mm, tolerance=0.5mm -> OK range: 9.5-10.5mm
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5)

        result = visualizer.draw(test_frame, [circle], tolerance)

        # Circle should be marked as NG (red)
        red_pixels = np.where((result[:, :, 0] == 0) & (result[:, :, 1] == 0) & (result[:, :, 2] == 255))
        assert len(red_pixels[0]) > 0

    # ========== Display options ==========
    def test_show_contours_option(self, visualizer, test_frame, sample_circle_ok):
        """TC-VIS-010: Contours display can be toggled"""
        # With contours
        config_with = DetectionConfig(show_contours=True)
        visualizer.update_config(config_with)
        result_with = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Without contours
        config_without = DetectionConfig(show_contours=False)
        visualizer.update_config(config_without)
        result_without = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Results should be different
        assert not np.array_equal(result_with, result_without)

    def test_show_label_option(self, visualizer, test_frame, sample_circle_ok):
        """TC-VIS-011: Label display can be toggled"""
        # With label
        config_with = DetectionConfig(show_label=True)
        visualizer.update_config(config_with)
        result_with = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Without label
        config_without = DetectionConfig(show_label=False)
        visualizer.update_config(config_without)
        result_without = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Results should be different (label adds text)
        assert not np.array_equal(result_with, result_without)

    def test_show_diameter_line_option(self, visualizer, test_frame, sample_circle_ok):
        """TC-VIS-012: Diameter line display can be toggled"""
        # With diameter line
        config_with = DetectionConfig(show_diameter_line=True, show_contours=False, show_label=False)
        visualizer.update_config(config_with)
        result_with = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Without diameter line
        config_without = DetectionConfig(show_diameter_line=False, show_contours=False, show_label=False)
        visualizer.update_config(config_without)
        result_without = visualizer.draw(test_frame.copy(), [sample_circle_ok])

        # Results should be different
        assert not np.array_equal(result_with, result_without)

    # ========== Binary overlay ==========
    def test_draw_binary_overlay(self, visualizer, test_frame):
        """TC-VIS-013: Draw binary overlay"""
        binary = np.zeros((480, 640), dtype=np.uint8)
        cv2.circle(binary, (320, 240), 50, 255, -1)

        result = visualizer.draw_binary_overlay(test_frame, binary, alpha=0.3)

        assert result is not None
        assert result.shape == test_frame.shape
        # Should have green overlay
        assert np.any(result[:, :, 1] > 0)

    def test_draw_binary_overlay_none_inputs(self, visualizer, test_frame):
        """TC-VIS-014: Handle None inputs for binary overlay"""
        result1 = visualizer.draw_binary_overlay(None, np.zeros((480, 640), dtype=np.uint8))
        assert result1 is None

        result2 = visualizer.draw_binary_overlay(test_frame, None)
        assert np.array_equal(result2, test_frame)

    # ========== Statistics overlay ==========
    def test_draw_statistics(self, visualizer, test_frame, sample_circle_ok, sample_circle_ng):
        """TC-VIS-015: Draw statistics on frame"""
        circles = [sample_circle_ok, sample_circle_ng]
        result = visualizer.draw_statistics(test_frame.copy(), circles)

        assert result is not None
        # Frame should be modified (statistics text added)
        assert not np.array_equal(result, test_frame)

    def test_draw_statistics_empty(self, visualizer, test_frame):
        """TC-VIS-016: Draw statistics with empty circles"""
        result = visualizer.draw_statistics(test_frame.copy(), [])
        assert result is not None

    # ========== Edge cases ==========
    def test_circle_near_edge(self, visualizer, test_frame):
        """TC-VIS-017: Handle circle near frame edge"""
        # Circle near top edge
        circle = CircleResult(
            hole_id=1,
            center_x=320,
            center_y=30,  # Near top edge
            radius=25,  # 50px diameter
            diameter_mm=5.0,
            circularity=0.95,
            area_mm2=19.63,
            status=MeasureStatus.OK,
        )

        # Should not raise exception
        result = visualizer.draw(test_frame, [circle])
        assert result is not None

    def test_update_config(self, visualizer):
        """TC-VIS-018: Update visualizer config"""
        new_config = DetectionConfig(show_contours=False, show_diameter_line=False, show_label=True)
        visualizer.update_config(new_config)

        assert visualizer._config.show_contours == False
        assert visualizer._config.show_diameter_line == False
        assert visualizer._config.show_label == True
