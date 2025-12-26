"""Integration tests for detection pipeline"""

import pytest
import numpy as np
import cv2
from src.services.detector_service import CircleDetector
from src.services.visualizer_service import CircleVisualizer
from src.services.calibration_service import CalibrationService
from src.services.recipe_service import RecipeService
from src.domain.config import DetectionConfig, ToleranceConfig
from src.domain.enums import MeasureStatus


class TestDetectionPipeline:
    """Integration tests for detection pipeline"""

    @pytest.fixture
    def pipeline(self):
        """Create detection pipeline components"""
        # Use pixel_to_mm=0.1 so 100px circles = 10mm (within default range)
        detector = CircleDetector(DetectionConfig(pixel_to_mm=0.1))
        visualizer = CircleVisualizer()
        return detector, visualizer

    def test_detect_and_visualize(self, pipeline, test_image_single_circle):
        """TC-INT-001: Detect circle and visualize result"""
        detector, visualizer = pipeline

        # Detect circles (returns tuple of circles and binary)
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1

        # Visualize - result shape should match input
        result = visualizer.draw(test_image_single_circle, circles)
        assert result.shape == test_image_single_circle.shape
        # Result should not be None
        assert result is not None

    def test_detect_with_calibration(self, test_image_single_circle, temp_config_dir):
        """TC-INT-002: Detection with calibration applied"""
        detector = CircleDetector()
        calibration = CalibrationService(config_path=str(temp_config_dir / "calib.json"))

        # Calibrate: 100px = 10mm
        calibration.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        # Apply calibration to detector
        config = DetectionConfig(pixel_to_mm=calibration.pixel_to_mm)
        detector.update_config(config)

        # Detect - circle has radius 50px, diameter 100px = 10mm
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1
        assert abs(circles[0].diameter_mm - 10.0) < 1.0

    def test_tolerance_check_ok(self, test_image_single_circle, temp_config_dir):
        """TC-INT-003: Tolerance check - OK result"""
        detector = CircleDetector()

        # Calibrate: 100px = 10mm
        config = DetectionConfig(pixel_to_mm=0.1)  # 100px = 10mm
        detector.update_config(config)

        # Detect
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1

        # Check tolerance
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        status = tolerance.check(circles[0].diameter_mm)
        assert status == MeasureStatus.OK

    def test_tolerance_check_ng(self, test_image_single_circle, temp_config_dir):
        """TC-INT-004: Tolerance check - NG result"""
        detector = CircleDetector()

        # Calibrate: 100px = 10mm
        config = DetectionConfig(pixel_to_mm=0.1)
        detector.update_config(config)

        # Detect
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1

        # Check with tight tolerance (circle is ~10mm, tolerance around 5mm)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=5.0, tolerance_mm=0.1)
        status = tolerance.check(circles[0].diameter_mm)
        assert status == MeasureStatus.NG


class TestRecipeIntegration:
    """Integration tests for recipe with detection"""

    def test_apply_recipe_to_detector(self, temp_recipe_dir):
        """TC-INT-005: Apply recipe config to detector"""
        recipe_service = RecipeService(str(temp_recipe_dir))
        detector = CircleDetector()

        # Create recipe with custom config
        recipe = recipe_service.create_recipe(
            name="CustomConfig",
            detection_config=DetectionConfig(min_diameter_mm=5.0, max_diameter_mm=15.0, min_circularity=0.9),
            tolerance_config=ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5),
            pixel_to_mm=0.01,
        )

        # Apply to detector
        detector.update_config(recipe.detection_config)

        assert detector.config.min_diameter_mm == 5.0
        assert detector.config.max_diameter_mm == 15.0
        assert detector.config.min_circularity == 0.9

    def test_save_load_apply_recipe(self, temp_recipe_dir, test_image_single_circle):
        """TC-INT-006: Save, load, and apply recipe"""
        recipe_service = RecipeService(str(temp_recipe_dir))
        detector = CircleDetector()

        # Create and save recipe
        recipe = recipe_service.create_recipe(
            name="TestRecipe",
            detection_config=DetectionConfig(
                pixel_to_mm=0.1,  # 100px = 10mm
                min_diameter_mm=5.0,
                max_diameter_mm=15.0,
            ),
            tolerance_config=ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5),
            pixel_to_mm=0.1,
        )
        recipe_service.save_recipe(recipe)

        # Load recipe
        loaded = recipe_service.get_recipe("TestRecipe")
        assert loaded is not None

        # Apply to detector
        detector.update_config(loaded.detection_config)

        # Detect
        circles, binary = detector.detect(test_image_single_circle)
        assert len(circles) >= 1

        # Check tolerance
        status = loaded.tolerance_config.check(circles[0].diameter_mm)
        assert status in [MeasureStatus.OK, MeasureStatus.NG]
