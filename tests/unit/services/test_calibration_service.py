"""Tests for CalibrationService - UC-04: Calibration"""

import pytest
import json
import numpy as np
import cv2
from src.services.calibration_service import CalibrationService
from src.domain.config import DetectionConfig


class TestCalibrationService:
    """Test CalibrationService for UC-04: Calibration workflow"""

    @pytest.fixture
    def calib_service(self, temp_config_dir):
        """Create calibration service with temp directory"""
        return CalibrationService(config_path=str(temp_config_dir / "calib.json"))

    @pytest.fixture
    def calibration_image(self):
        """Create test image with known circle for calibration"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Circle with radius 100px (diameter 200px)
        cv2.circle(img, (320, 240), 100, (255, 255, 255), -1)
        return img

    # ========== UC-04 Step 1: Initial state ==========
    def test_default_pixel_to_mm(self, calib_service):
        """TC-CAL-001: Default calibration value when no calibration exists"""
        assert calib_service.pixel_to_mm == DetectionConfig().pixel_to_mm
        assert calib_service.is_calibrated == False

    def test_calibration_info_uncalibrated(self, calib_service):
        """TC-CAL-002: Get info when not calibrated"""
        info = calib_service.get_info()
        assert info["calibrated"] == False
        assert info["source"] == "default"

    # ========== UC-04 Step 2: Perform calibration with known reference ==========
    def test_calibrate_with_reference(self, calib_service):
        """TC-CAL-003: Calibrate with known reference size"""
        # Reference: 100px = 10mm -> pixel_to_mm = 0.1
        result = calib_service.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        assert result is not None
        assert result.pixel_to_mm == 0.1
        assert calib_service.is_calibrated == True
        assert calib_service.pixel_to_mm == 0.1

    def test_calibrate_precision(self, calib_service):
        """TC-CAL-004: Calibration precision calculation"""
        # Reference: 1550px = 10mm -> pixel_to_mm = 0.00645161...
        result = calib_service.calibrate(reference_size_mm=10.0, reference_size_px=1550.0)

        expected = 10.0 / 1550.0
        assert abs(result.pixel_to_mm - expected) < 1e-10

    # ========== UC-04 Step 3: Validation - reject invalid values ==========
    def test_calibrate_invalid_zero_px(self, calib_service):
        """TC-CAL-005: Reject zero pixel reference"""
        with pytest.raises(ValueError, match="positive"):
            calib_service.calibrate(reference_size_mm=10.0, reference_size_px=0)

    def test_calibrate_invalid_negative_px(self, calib_service):
        """TC-CAL-006: Reject negative pixel reference"""
        with pytest.raises(ValueError, match="positive"):
            calib_service.calibrate(reference_size_mm=10.0, reference_size_px=-100)

    def test_calibrate_invalid_zero_mm(self, calib_service):
        """TC-CAL-007: Reject zero mm reference"""
        with pytest.raises(ValueError, match="positive"):
            calib_service.calibrate(reference_size_mm=0, reference_size_px=100)

    def test_calibrate_invalid_negative_mm(self, calib_service):
        """TC-CAL-008: Reject negative mm reference"""
        with pytest.raises(ValueError, match="positive"):
            calib_service.calibrate(reference_size_mm=-10.0, reference_size_px=100)

    # ========== UC-04 Step 4: Auto-calibration from circle ==========
    def test_calibrate_from_circle(self, calib_service, calibration_image):
        """TC-CAL-009: Auto-calibrate from detected circle"""
        # Circle in image has diameter 200px
        # If we say it's 20mm, then pixel_to_mm = 0.1
        result = calib_service.calibrate_from_circle(frame=calibration_image, known_diameter_mm=20.0)

        assert result is not None
        # Diameter is ~200px, so pixel_to_mm should be ~0.1
        assert 0.08 < result.pixel_to_mm < 0.12

    def test_calibrate_from_circle_no_circle(self, calib_service, test_image_no_circles):
        """TC-CAL-010: Auto-calibrate fails when no circle detected"""
        result = calib_service.calibrate_from_circle(frame=test_image_no_circles, known_diameter_mm=10.0)

        assert result is None

    # ========== UC-04 Step 5: Persistence - save/load calibration ==========
    def test_save_and_load_calibration(self, temp_config_dir):
        """TC-CAL-011: Persist calibration data across instances"""
        config_path = str(temp_config_dir / "calib.json")

        # Create and calibrate
        service1 = CalibrationService(config_path=config_path)
        service1.calibrate(reference_size_mm=10.0, reference_size_px=500.0)
        expected_ratio = 10.0 / 500.0

        # Create new instance - should load saved data
        service2 = CalibrationService(config_path=config_path)
        assert service2.is_calibrated == True
        assert abs(service2.pixel_to_mm - expected_ratio) < 1e-10

    def test_calibration_file_format(self, calib_service, temp_config_dir):
        """TC-CAL-012: Verify saved calibration file format"""
        calib_service.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        config_path = temp_config_dir / "calib.json"
        assert config_path.exists()

        with open(config_path) as f:
            data = json.load(f)

        assert "pixel_to_mm" in data
        assert "calibrated_at" in data
        assert "reference_size_mm" in data
        assert "reference_size_px" in data

    # ========== UC-04 Step 6: Reset calibration ==========
    def test_reset_calibration(self, calib_service, temp_config_dir):
        """TC-CAL-013: Reset calibration to default"""
        calib_service.calibrate(reference_size_mm=10.0, reference_size_px=100.0)
        assert calib_service.is_calibrated == True

        calib_service.reset_calibration()

        assert calib_service.is_calibrated == False
        assert calib_service.pixel_to_mm == DetectionConfig().pixel_to_mm

        # File should be deleted
        config_path = temp_config_dir / "calib.json"
        assert not config_path.exists()

    # ========== Direct value setting ==========
    def test_set_pixel_to_mm_directly(self, calib_service):
        """TC-CAL-014: Set pixel_to_mm directly (for recipe loading)"""
        calib_service.set_pixel_to_mm(0.05)

        assert calib_service.pixel_to_mm == 0.05
        assert calib_service.is_calibrated == True

    def test_set_pixel_to_mm_invalid(self, calib_service):
        """TC-CAL-015: Reject invalid direct pixel_to_mm value"""
        with pytest.raises(ValueError):
            calib_service.set_pixel_to_mm(0)

        with pytest.raises(ValueError):
            calib_service.set_pixel_to_mm(-0.01)

    # ========== Calibration info ==========
    def test_calibration_info_calibrated(self, calib_service):
        """TC-CAL-016: Get complete calibration info after calibration"""
        calib_service.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        info = calib_service.get_info()

        assert info["calibrated"] == True
        assert info["pixel_to_mm"] == 0.1
        assert info["reference_mm"] == 10.0
        assert info["reference_px"] == 100.0
        assert "calibrated_at" in info
