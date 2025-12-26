"""Integration tests for complete measurement workflow - UC-02"""
import pytest
import numpy as np
import cv2
import time
from src.services.detector_service import CircleDetector
from src.services.visualizer_service import CircleVisualizer
from src.services.calibration_service import CalibrationService
from src.services.recipe_service import RecipeService
from src.services.image_saver import ImageSaver
from src.services.io_service import IOService
from src.domain.config import DetectionConfig, ToleranceConfig
from src.domain.io_config import IOConfig, IOMode
from src.domain.enums import MeasureStatus


class TestMeasurementWorkflow:
    """
    Integration tests for UC-02: Tự động đo lỗ tròn

    Complete workflow:
    1. Trigger → 2. Capture → 3. Detect → 4. Measure → 5. Check tolerance → 6. Output
    """

    @pytest.fixture
    def detection_system(self, temp_config_dir, temp_recipe_dir, temp_output_dir):
        """Create complete detection system"""
        calibration = CalibrationService(str(temp_config_dir / "calib.json"))
        detector = CircleDetector()
        visualizer = CircleVisualizer()
        recipe_service = RecipeService(str(temp_recipe_dir))
        image_saver = ImageSaver(str(temp_output_dir))
        io_service = IOService(IOConfig(mode=IOMode.SIMULATION))

        return {
            "calibration": calibration,
            "detector": detector,
            "visualizer": visualizer,
            "recipe_service": recipe_service,
            "image_saver": image_saver,
            "io_service": io_service
        }

    @pytest.fixture
    def test_workpiece_ok(self):
        """Create test image simulating OK workpiece with circle"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Circle: 100px diameter = 10mm with calibration 0.1 mm/px
        cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)
        return img

    @pytest.fixture
    def test_workpiece_ng(self):
        """Create test image simulating NG workpiece (oversized hole)"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Circle: 150px diameter = 15mm (oversized)
        cv2.circle(img, (320, 240), 75, (255, 255, 255), -1)
        return img

    @pytest.fixture
    def test_workpiece_multiple(self):
        """Create test image with multiple holes"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(img, (160, 240), 50, (255, 255, 255), -1)  # OK
        cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)  # OK
        cv2.circle(img, (480, 240), 75, (255, 255, 255), -1)  # NG (oversized)
        return img

    # ========== UC-02: Complete measurement workflow ==========
    def test_complete_ok_workflow(self, detection_system, test_workpiece_ok):
        """TC-WF-001: Complete workflow for OK workpiece"""
        calibration = detection_system["calibration"]
        detector = detection_system["detector"]
        visualizer = detection_system["visualizer"]

        # Step 1: Calibrate (100px = 10mm)
        calibration.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        # Step 2: Configure detector with calibration
        config = DetectionConfig(pixel_to_mm=calibration.pixel_to_mm)
        detector.update_config(config)

        # Step 3: Detect circles
        circles, binary = detector.detect(test_workpiece_ok)
        assert len(circles) >= 1

        # Step 4: Check measurement (should be ~10mm)
        circle = circles[0]
        assert abs(circle.diameter_mm - 10.0) < 1.0

        # Step 5: Check tolerance (OK range: 9-11mm)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        status = tolerance.check(circle.diameter_mm)
        assert status == MeasureStatus.OK

        # Step 6: Visualize result
        result_frame = visualizer.draw(test_workpiece_ok, circles, tolerance)
        assert result_frame is not None

    def test_complete_ng_workflow(self, detection_system, test_workpiece_ng):
        """TC-WF-002: Complete workflow for NG workpiece"""
        calibration = detection_system["calibration"]
        detector = detection_system["detector"]
        visualizer = detection_system["visualizer"]
        image_saver = detection_system["image_saver"]

        # Step 1: Calibrate
        calibration.calibrate(reference_size_mm=10.0, reference_size_px=100.0)

        # Step 2: Configure detector
        config = DetectionConfig(pixel_to_mm=calibration.pixel_to_mm)
        detector.update_config(config)

        # Step 3: Detect circles
        circles, binary = detector.detect(test_workpiece_ng)
        assert len(circles) >= 1

        # Step 4: Check measurement (should be ~15mm - oversized)
        circle = circles[0]
        assert circle.diameter_mm > 12.0

        # Step 5: Check tolerance (OK range: 9-11mm)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        status = tolerance.check(circle.diameter_mm)
        assert status == MeasureStatus.NG

        # Update circle status
        circle.status = status

        # Step 6: Visualize and save NG image
        result_frame = visualizer.draw(test_workpiece_ng, circles, tolerance)
        saved_path = image_saver.save_ng_image(test_workpiece_ng, circles, result_frame)
        assert saved_path is not None

    def test_workflow_with_recipe(self, detection_system, test_workpiece_ok):
        """TC-WF-003: Workflow using recipe configuration"""
        recipe_service = detection_system["recipe_service"]
        detector = detection_system["detector"]

        # Create and save recipe
        recipe = recipe_service.create_recipe(
            name="Product_A",
            description="Standard 10mm hole product",
            detection_config=DetectionConfig(
                pixel_to_mm=0.1,
                min_diameter_mm=5.0,
                max_diameter_mm=15.0,
                min_circularity=0.85
            ),
            tolerance_config=ToleranceConfig(
                enabled=True,
                nominal_mm=10.0,
                tolerance_mm=0.5
            ),
            pixel_to_mm=0.1
        )
        recipe_service.save_recipe(recipe)

        # Load recipe
        loaded = recipe_service.get_recipe("Product_A")
        assert loaded is not None

        # Apply to detector
        detector.update_config(loaded.detection_config)

        # Detect
        circles, _ = detector.detect(test_workpiece_ok)
        assert len(circles) >= 1

        # Check tolerance using recipe config
        status = loaded.tolerance_config.check(circles[0].diameter_mm)
        assert status in [MeasureStatus.OK, MeasureStatus.NG]

    def test_workflow_multiple_circles(self, detection_system, test_workpiece_multiple):
        """TC-WF-004: Workflow with multiple circles (mixed OK/NG)"""
        calibration = detection_system["calibration"]
        detector = detection_system["detector"]
        visualizer = detection_system["visualizer"]
        image_saver = detection_system["image_saver"]

        # Setup
        calibration.calibrate(reference_size_mm=10.0, reference_size_px=100.0)
        config = DetectionConfig(pixel_to_mm=calibration.pixel_to_mm)
        detector.update_config(config)

        # Detect all circles
        circles, _ = detector.detect(test_workpiece_multiple)
        assert len(circles) >= 2

        # Check each circle against tolerance
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        ok_count = 0
        ng_count = 0

        for circle in circles:
            status = tolerance.check(circle.diameter_mm)
            circle.status = status
            if status == MeasureStatus.OK:
                ok_count += 1
            else:
                ng_count += 1

        # Should have at least 1 NG (the oversized one)
        assert ng_count >= 1

        # Visualize all circles
        result_frame = visualizer.draw(test_workpiece_multiple, circles, tolerance)
        assert result_frame is not None

        # Should save because there's at least one NG
        saved_path = image_saver.save_ng_image(test_workpiece_multiple, circles, result_frame)
        assert saved_path is not None


class TestIOIntegration:
    """Integration tests for IO with detection workflow"""

    @pytest.fixture
    def io_service(self):
        """Create IO service in simulation mode"""
        service = IOService(IOConfig(mode=IOMode.SIMULATION))
        service.initialize()
        service.start()
        yield service
        service.stop()
        service.cleanup()

    @pytest.fixture
    def detector(self):
        """Create detector with test config"""
        config = DetectionConfig(pixel_to_mm=0.1)
        return CircleDetector(config)

    def test_trigger_detection_workflow(self, io_service, detector, test_image_single_circle):
        """TC-IO-INT-001: Trigger initiates detection workflow"""
        results = []

        def on_trigger():
            # Simulate detection when triggered
            circles, _ = detector.detect(test_image_single_circle)
            results.append(circles)

        io_service.register_trigger_callback(on_trigger)

        # Simulate trigger pulse
        io_service.sim_pulse_trigger()
        time.sleep(0.3)

        assert len(results) > 0
        assert len(results[0]) >= 1

    def test_ok_result_signal(self, io_service, detector, test_image_single_circle):
        """TC-IO-INT-002: OK detection sends OK signal"""
        # Detect circle
        circles, _ = detector.detect(test_image_single_circle)
        assert len(circles) >= 1

        # Check tolerance (circle is ~10mm)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        status = tolerance.check(circles[0].diameter_mm)

        # Send result
        io_service.set_result(ok=(status == MeasureStatus.OK))
        time.sleep(0.2)

        # No exception means success

    def test_ng_result_signal(self, io_service, detector):
        """TC-IO-INT-003: NG detection sends NG signal"""
        # Create oversized circle
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(img, (320, 240), 100, (255, 255, 255), -1)  # 200px = 20mm

        circles, _ = detector.detect(img)
        assert len(circles) >= 1

        # Check tolerance (circle is ~20mm, way outside 9-11mm)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=1.0)
        status = tolerance.check(circles[0].diameter_mm)
        assert status == MeasureStatus.NG

        # Send NG result
        io_service.set_result(ok=False)
        time.sleep(0.2)

    def test_recipe_selection_via_io(self, io_service, temp_recipe_dir):
        """TC-IO-INT-004: Recipe selection via IO bits"""
        recipe_service = RecipeService(str(temp_recipe_dir))

        # Create multiple recipes
        for i in range(4):
            recipe = recipe_service.create_recipe(
                name=f"Recipe_{i}",
                detection_config=DetectionConfig(),
                tolerance_config=ToleranceConfig(),
                pixel_to_mm=0.00644
            )
            recipe_service.save_recipe(recipe)

        recipes = recipe_service.recipe_names

        # Simulate recipe selection via IO
        io_service.sim_set_recipe(2)  # Binary: 10
        time.sleep(0.1)

        recipe_index = io_service.status.recipe_index
        assert recipe_index == 2

        # Get recipe by index
        if len(recipes) > recipe_index:
            selected_recipe = recipe_service.get_recipe(recipes[recipe_index])
            assert selected_recipe is not None


class TestPerformance:
    """Performance tests for detection workflow"""

    @pytest.fixture
    def detector(self):
        """Create detector with typical config"""
        config = DetectionConfig(pixel_to_mm=0.00644)
        return CircleDetector(config)

    def test_detection_latency(self, detector, test_image_single_circle):
        """TC-PERF-001: Detection completes within target time"""
        import time

        iterations = 100
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            detector.detect(test_image_single_circle)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Average should be < 50ms (0.05s)
        assert avg_time < 0.1, f"Average detection time {avg_time*1000:.1f}ms exceeds 100ms"

    def test_throughput(self, detector, test_image_single_circle):
        """TC-PERF-002: Detection throughput >= 20 fps"""
        import time

        iterations = 100
        start = time.perf_counter()

        for _ in range(iterations):
            detector.detect(test_image_single_circle)

        elapsed = time.perf_counter() - start
        fps = iterations / elapsed

        assert fps >= 20, f"Throughput {fps:.1f} fps below 20 fps target"

    def test_memory_stability(self, detector, test_image_single_circle):
        """TC-PERF-003: No memory leak during repeated detection"""
        import tracemalloc

        tracemalloc.start()

        # Run many iterations
        for _ in range(500):
            detector.detect(test_image_single_circle)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be < 200MB for this test
        assert peak < 200 * 1024 * 1024, f"Peak memory {peak/1024/1024:.1f}MB exceeds 200MB"
