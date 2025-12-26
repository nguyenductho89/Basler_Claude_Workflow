"""Tests for domain config classes"""
import pytest
from src.domain.config import DetectionConfig, ToleranceConfig
from src.domain.enums import MeasureStatus


class TestDetectionConfig:
    """Test DetectionConfig dataclass"""

    def test_default_values(self):
        """TC-DOM-001: Default config values"""
        config = DetectionConfig()
        assert config.pixel_to_mm == 0.00644
        assert config.min_diameter_mm == 1.0
        assert config.max_diameter_mm == 20.0
        assert config.min_circularity == 0.85
        assert config.blur_kernel == 5

    def test_custom_values(self):
        """TC-DOM-002: Custom config values"""
        config = DetectionConfig(
            pixel_to_mm=0.01,
            min_diameter_mm=2.0,
            max_diameter_mm=15.0
        )
        assert config.pixel_to_mm == 0.01
        assert config.min_diameter_mm == 2.0
        assert config.max_diameter_mm == 15.0

    def test_display_options(self):
        """TC-DOM-003: Display options"""
        config = DetectionConfig(
            show_contours=False,
            show_diameter_line=False,
            show_label=False
        )
        assert config.show_contours == False
        assert config.show_diameter_line == False
        assert config.show_label == False


class TestToleranceConfig:
    """Test ToleranceConfig dataclass"""

    def test_default_disabled(self):
        """TC-DOM-004: Tolerance disabled by default"""
        config = ToleranceConfig()
        assert config.enabled == False

    def test_tolerance_range(self):
        """TC-DOM-005: Tolerance range calculation"""
        config = ToleranceConfig(
            enabled=True,
            nominal_mm=10.0,
            tolerance_mm=0.1
        )
        assert config.min_mm == 9.9
        assert config.max_mm == 10.1

    def test_check_ok_within_tolerance(self):
        """TC-DOM-006: Check OK when within tolerance"""
        config = ToleranceConfig(
            enabled=True,
            nominal_mm=10.0,
            tolerance_mm=0.1
        )
        # Exactly nominal
        assert config.check(10.0) == MeasureStatus.OK
        # Within tolerance
        assert config.check(10.05) == MeasureStatus.OK
        assert config.check(9.95) == MeasureStatus.OK
        # At boundary
        assert config.check(10.1) == MeasureStatus.OK
        assert config.check(9.9) == MeasureStatus.OK

    def test_check_ng_outside_tolerance(self):
        """TC-DOM-007: Check NG when outside tolerance"""
        config = ToleranceConfig(
            enabled=True,
            nominal_mm=10.0,
            tolerance_mm=0.1
        )
        # Outside tolerance
        assert config.check(10.2) == MeasureStatus.NG
        assert config.check(9.8) == MeasureStatus.NG

    def test_check_disabled_returns_none(self):
        """TC-DOM-008: Check returns NONE when disabled"""
        config = ToleranceConfig(enabled=False)
        assert config.check(10.0) == MeasureStatus.NONE
