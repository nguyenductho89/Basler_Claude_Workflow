# Test Plan - Circle Measurement System v2.0

| Document Info | |
|---------------|---|
| Version | 1.0 |
| Date | 2025-12-27 |
| Status | Draft |
| Author | Development Team |

---

## 1. Introduction

### 1.1 Purpose
Tài liệu này mô tả kế hoạch kiểm thử cho Circle Measurement System v2.0, bao gồm các test cases, test procedures, và acceptance criteria.

### 1.2 Scope
Test plan bao gồm tất cả các tính năng từ MVP 1.0 đến Release 2.0:
- Camera integration
- Circle detection & visualization
- Calibration system
- Threading & history
- Recipe management
- Production statistics
- PLC/IO integration

### 1.3 Test Environment

| Component | Specification |
|-----------|---------------|
| OS | Windows 10/11 64-bit |
| Python | 3.10+ |
| Camera | Basler acA4600-7gc (hoặc simulation mode) |
| I/O Card | NI USB-6001 (hoặc simulation mode) |
| Test Images | Chuẩn bị sẵn trong `tests/fixtures/` |

---

## 2. Test Strategy

### 2.1 Test Levels

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST PYRAMID                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                      ┌─────────┐                            │
│                     /   UAT    \                            │
│                    /  (Manual)  \                           │
│                   ┌─────────────┐                           │
│                  /  System Tests \                          │
│                 /    (E2E Auto)   \                         │
│                ┌───────────────────┐                        │
│               /  Integration Tests  \                       │
│              /      (Automated)      \                      │
│             ┌─────────────────────────┐                     │
│            /       Unit Tests          \                    │
│           /        (Automated)          \                   │
│          └───────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Test Types

| Type | Description | Tool |
|------|-------------|------|
| Unit Test | Test individual functions/classes | pytest |
| Integration Test | Test component interactions | pytest |
| System Test | End-to-end functionality | pytest + Manual |
| Performance Test | Speed, memory, throughput | pytest-benchmark |
| UAT | User acceptance | Manual checklist |

---

## 3. Unit Tests

### 3.1 Domain Layer Tests

#### 3.1.1 Test: DetectionConfig
```python
# tests/unit/domain/test_config.py

class TestDetectionConfig:
    """Test DetectionConfig dataclass"""

    def test_default_values(self):
        """TC-DOM-001: Default config values"""
        config = DetectionConfig()
        assert config.pixel_to_mm == 0.00644
        assert config.min_diameter_mm == 1.0
        assert config.max_diameter_mm == 20.0
        assert config.min_circularity == 0.85

    def test_custom_values(self):
        """TC-DOM-002: Custom config values"""
        config = DetectionConfig(
            pixel_to_mm=0.01,
            min_diameter_mm=2.0
        )
        assert config.pixel_to_mm == 0.01
        assert config.min_diameter_mm == 2.0
```

#### 3.1.2 Test: ToleranceConfig
```python
class TestToleranceConfig:
    """Test ToleranceConfig dataclass"""

    def test_tolerance_check_ok(self):
        """TC-DOM-003: Tolerance check passes"""
        config = ToleranceConfig(
            enabled=True,
            nominal_mm=10.0,
            tolerance_mm=0.1
        )
        assert config.check(10.05) == MeasureStatus.OK

    def test_tolerance_check_ng(self):
        """TC-DOM-004: Tolerance check fails"""
        config = ToleranceConfig(
            enabled=True,
            nominal_mm=10.0,
            tolerance_mm=0.1
        )
        assert config.check(10.2) == MeasureStatus.NG
```

#### 3.1.3 Test: Recipe
```python
class TestRecipe:
    """Test Recipe model"""

    def test_to_json_from_json(self):
        """TC-DOM-005: Recipe serialization"""
        recipe = Recipe(name="Test", description="Test recipe")
        json_str = recipe.to_json()
        loaded = Recipe.from_json(json_str)
        assert loaded.name == recipe.name
        assert loaded.description == recipe.description

    def test_to_dict_from_dict(self):
        """TC-DOM-006: Recipe dict conversion"""
        recipe = Recipe(name="Test")
        data = recipe.to_dict()
        loaded = Recipe.from_dict(data)
        assert loaded.name == recipe.name
```

#### 3.1.4 Test: IOConfig
```python
class TestIOConfig:
    """Test IOConfig model"""

    def test_default_channels(self):
        """TC-DOM-007: Default IO channel mapping"""
        config = IOConfig()
        assert config.trigger_channel == 0
        assert config.ok_channel == 0
        assert config.ng_channel == 1

    def test_mode_enum(self):
        """TC-DOM-008: IO mode enumeration"""
        assert IOMode.SIMULATION.value == "simulation"
        assert IOMode.NI_DAQMX.value == "ni_daqmx"
```

---

### 3.2 Service Layer Tests

#### 3.2.1 Test: CircleDetector
```python
# tests/unit/services/test_detector_service.py

class TestCircleDetector:
    """Test CircleDetector service"""

    @pytest.fixture
    def detector(self):
        return CircleDetector()

    @pytest.fixture
    def test_image_with_circle(self):
        """Create test image with known circle"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)
        return img

    def test_detect_single_circle(self, detector, test_image_with_circle):
        """TC-DET-001: Detect single circle"""
        circles = detector.detect(test_image_with_circle)
        assert len(circles) == 1
        assert abs(circles[0].center_x - 320) < 5
        assert abs(circles[0].center_y - 240) < 5

    def test_detect_no_circles(self, detector):
        """TC-DET-002: No circles in blank image"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        circles = detector.detect(img)
        assert len(circles) == 0

    def test_detect_multiple_circles(self, detector):
        """TC-DET-003: Detect multiple circles"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(img, (160, 240), 40, (255, 255, 255), -1)
        cv2.circle(img, (480, 240), 40, (255, 255, 255), -1)
        circles = detector.detect(img)
        assert len(circles) == 2

    def test_filter_by_diameter(self, detector):
        """TC-DET-004: Filter circles by diameter"""
        detector.update_config(DetectionConfig(
            min_diameter_mm=5.0,
            max_diameter_mm=10.0
        ))
        # Small circle should be filtered out
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(img, (320, 240), 10, (255, 255, 255), -1)  # Too small
        circles = detector.detect(img)
        assert len(circles) == 0

    def test_filter_by_circularity(self, detector):
        """TC-DET-005: Filter non-circular shapes"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.ellipse(img, (320, 240), (80, 40), 0, 0, 360, (255, 255, 255), -1)
        circles = detector.detect(img)
        assert len(circles) == 0  # Ellipse should be filtered
```

#### 3.2.2 Test: CalibrationService
```python
# tests/unit/services/test_calibration_service.py

class TestCalibrationService:
    """Test CalibrationService"""

    @pytest.fixture
    def calib_service(self, tmp_path):
        return CalibrationService(config_path=str(tmp_path / "calib.json"))

    def test_default_pixel_to_mm(self, calib_service):
        """TC-CAL-001: Default calibration value"""
        assert calib_service.pixel_to_mm == 0.00644

    def test_calibrate_with_reference(self, calib_service):
        """TC-CAL-002: Calibrate with known reference"""
        calib_data = calib_service.calibrate(
            reference_size_mm=10.0,
            reference_size_px=1000.0
        )
        assert calib_data.pixel_to_mm == 0.01
        assert calib_service.is_calibrated

    def test_calibrate_invalid_values(self, calib_service):
        """TC-CAL-003: Reject invalid calibration values"""
        with pytest.raises(ValueError):
            calib_service.calibrate(reference_size_mm=-1.0, reference_size_px=100)
        with pytest.raises(ValueError):
            calib_service.calibrate(reference_size_mm=10.0, reference_size_px=0)

    def test_save_load_calibration(self, calib_service):
        """TC-CAL-004: Persist calibration data"""
        calib_service.calibrate(reference_size_mm=10.0, reference_size_px=500.0)

        # Create new instance - should load saved data
        new_service = CalibrationService(config_path=calib_service._config_path)
        assert new_service.pixel_to_mm == 0.02

    def test_reset_calibration(self, calib_service):
        """TC-CAL-005: Reset calibration to default"""
        calib_service.calibrate(reference_size_mm=10.0, reference_size_px=500.0)
        calib_service.reset_calibration()
        assert not calib_service.is_calibrated
```

#### 3.2.3 Test: RecipeService
```python
# tests/unit/services/test_recipe_service.py

class TestRecipeService:
    """Test RecipeService"""

    @pytest.fixture
    def recipe_service(self, tmp_path):
        return RecipeService(recipe_dir=str(tmp_path / "recipes"))

    def test_create_recipe(self, recipe_service):
        """TC-RCP-001: Create new recipe"""
        recipe = recipe_service.create_recipe(
            name="Test Recipe",
            description="Test description"
        )
        assert recipe.name == "Test Recipe"
        assert recipe.description == "Test description"

    def test_save_and_load_recipe(self, recipe_service):
        """TC-RCP-002: Save and load recipe"""
        recipe = recipe_service.create_recipe(name="SaveTest")
        recipe_service.save_recipe(recipe)

        loaded = recipe_service.get_recipe("SaveTest")
        assert loaded is not None
        assert loaded.name == "SaveTest"

    def test_list_recipes(self, recipe_service):
        """TC-RCP-003: List all recipes"""
        recipe_service.save_recipe(recipe_service.create_recipe(name="Recipe1"))
        recipe_service.save_recipe(recipe_service.create_recipe(name="Recipe2"))

        recipes = recipe_service.list_recipes()
        assert "Recipe1" in recipes
        assert "Recipe2" in recipes

    def test_delete_recipe(self, recipe_service):
        """TC-RCP-004: Delete recipe"""
        recipe_service.save_recipe(recipe_service.create_recipe(name="ToDelete"))
        assert recipe_service.delete_recipe("ToDelete")
        assert recipe_service.get_recipe("ToDelete") is None

    def test_export_import_recipe(self, recipe_service, tmp_path):
        """TC-RCP-005: Export and import recipe"""
        recipe = recipe_service.create_recipe(name="ExportTest")
        recipe_service.save_recipe(recipe)

        export_path = tmp_path / "exported.json"
        recipe_service.export_recipe("ExportTest", str(export_path))

        recipe_service.delete_recipe("ExportTest")
        recipe_service.import_recipe(str(export_path))

        loaded = recipe_service.get_recipe("ExportTest")
        assert loaded is not None
```

#### 3.2.4 Test: IOService
```python
# tests/unit/services/test_io_service.py

class TestIOService:
    """Test IOService"""

    @pytest.fixture
    def io_service(self):
        service = IOService(IOConfig(mode=IOMode.SIMULATION))
        yield service
        service.cleanup()

    def test_initialize_simulation(self, io_service):
        """TC-IO-001: Initialize in simulation mode"""
        assert io_service.initialize()
        assert io_service.status.connected

    def test_start_stop(self, io_service):
        """TC-IO-002: Start and stop IO service"""
        io_service.initialize()
        assert io_service.start()
        assert io_service.is_running
        io_service.stop()
        assert not io_service.is_running

    def test_set_ready_signal(self, io_service):
        """TC-IO-003: Set ready signal"""
        io_service.initialize()
        io_service.start()
        io_service.set_ready(True)
        time.sleep(0.1)
        assert io_service.status.system_ready

    def test_set_result_ok(self, io_service):
        """TC-IO-004: Set OK result"""
        io_service.initialize()
        io_service.start()
        io_service.set_result(ok=True)
        time.sleep(0.2)  # Wait for pulse
        # OK pulse should have completed

    def test_trigger_callback(self, io_service):
        """TC-IO-005: Trigger callback invocation"""
        triggered = []

        def on_trigger():
            triggered.append(True)

        io_service.register_trigger_callback(on_trigger)
        io_service.initialize()
        io_service.start()
        io_service.sim_pulse_trigger()
        time.sleep(0.1)

        assert len(triggered) > 0

    def test_sim_recipe_selection(self, io_service):
        """TC-IO-006: Simulation recipe selection"""
        io_service.initialize()
        io_service.start()
        io_service.sim_set_recipe(2)  # Binary: 10
        time.sleep(0.1)
        assert io_service.status.recipe_index == 2
```

#### 3.2.5 Test: ImageSaver
```python
# tests/unit/services/test_image_saver.py

class TestImageSaver:
    """Test ImageSaver service"""

    @pytest.fixture
    def image_saver(self, tmp_path):
        return ImageSaver(save_dir=str(tmp_path / "output"))

    @pytest.fixture
    def test_frame(self):
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def test_save_ng_image(self, image_saver, test_frame):
        """TC-IMG-001: Save NG image"""
        circles = [CircleResult(
            center_x=320, center_y=240,
            diameter_px=100, diameter_mm=10.0,
            status=MeasureStatus.NG
        )]

        path = image_saver.save_ng_image(test_frame, circles, test_frame)
        assert path is not None
        assert os.path.exists(path)

    def test_save_creates_directory(self, image_saver, test_frame):
        """TC-IMG-002: Auto-create output directory"""
        circles = [CircleResult(
            center_x=320, center_y=240,
            diameter_px=100, diameter_mm=10.0,
            status=MeasureStatus.NG
        )]

        path = image_saver.save_ng_image(test_frame, circles, test_frame)
        assert os.path.exists(os.path.dirname(path))
```

---

### 3.3 Camera Service Tests

```python
# tests/unit/services/test_camera_service.py

class TestBaslerGigECamera:
    """Test BaslerGigECamera service"""

    def test_trigger_mode_constants(self):
        """TC-CAM-001: Trigger mode constants"""
        assert TriggerMode.SOFTWARE == "software"
        assert TriggerMode.HARDWARE == "hardware"

    def test_list_devices_no_camera(self):
        """TC-CAM-002: List devices when no camera connected"""
        devices = BaslerGigECamera.list_devices()
        assert isinstance(devices, list)

    def test_connect_invalid_index(self):
        """TC-CAM-003: Connect with invalid device index"""
        camera = BaslerGigECamera()
        result = camera.connect(device_index=999)
        assert result == False

    def test_disconnect_not_connected(self):
        """TC-CAM-004: Disconnect when not connected"""
        camera = BaslerGigECamera()
        camera.disconnect()  # Should not raise

    def test_grab_frame_not_connected(self):
        """TC-CAM-005: Grab frame when not connected"""
        camera = BaslerGigECamera()
        frame = camera.grab_frame()
        assert frame is None
```

---

## 4. Integration Tests

### 4.1 Camera + Detection Integration
```python
# tests/integration/test_camera_detection.py

class TestCameraDetectionIntegration:
    """Integration tests for camera + detection pipeline"""

    @pytest.fixture
    def pipeline(self):
        camera = BaslerGigECamera()
        detector = CircleDetector()
        visualizer = CircleVisualizer()
        return camera, detector, visualizer

    def test_detection_pipeline_with_test_image(self, pipeline):
        """TC-INT-001: Full detection pipeline with test image"""
        _, detector, visualizer = pipeline

        # Load test image
        img = cv2.imread("tests/fixtures/circles_3.png")

        # Detect circles
        circles = detector.detect(img)

        # Visualize
        result = visualizer.draw(img, circles)

        assert len(circles) == 3
        assert result.shape == img.shape
```

### 4.2 Recipe + Config Integration
```python
# tests/integration/test_recipe_config.py

class TestRecipeConfigIntegration:
    """Integration tests for recipe + config"""

    def test_apply_recipe_to_detector(self, tmp_path):
        """TC-INT-002: Apply recipe config to detector"""
        recipe_service = RecipeService(str(tmp_path))
        detector = CircleDetector()

        # Create recipe with custom config
        recipe = recipe_service.create_recipe(
            name="CustomConfig",
            detection_config=DetectionConfig(
                min_diameter_mm=5.0,
                max_diameter_mm=15.0
            )
        )

        # Apply to detector
        detector.update_config(recipe.detection_config)

        assert detector.config.min_diameter_mm == 5.0
        assert detector.config.max_diameter_mm == 15.0
```

### 4.3 IO + Detection Integration
```python
# tests/integration/test_io_detection.py

class TestIODetectionIntegration:
    """Integration tests for IO + detection result"""

    def test_ok_result_triggers_ok_signal(self):
        """TC-INT-003: OK detection triggers OK signal"""
        io_service = IOService(IOConfig(mode=IOMode.SIMULATION))
        io_service.initialize()
        io_service.start()

        # Simulate OK result
        io_service.set_result(ok=True)
        time.sleep(0.2)

        io_service.stop()

    def test_ng_result_triggers_ng_signal(self):
        """TC-INT-004: NG detection triggers NG signal"""
        io_service = IOService(IOConfig(mode=IOMode.SIMULATION))
        io_service.initialize()
        io_service.start()

        # Simulate NG result
        io_service.set_result(ok=False)
        time.sleep(0.2)

        io_service.stop()
```

---

## 5. System Tests (E2E)

### 5.1 Complete Workflow Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|-----------------|
| TC-SYS-001 | Application startup | 1. Run main.py | Window opens, no errors |
| TC-SYS-002 | Camera connection | 1. Click Refresh 2. Select camera 3. Click Connect | Live view displayed |
| TC-SYS-003 | Circle detection | 1. Connect camera 2. Place circle object 3. Observe detection | Circles detected and displayed |
| TC-SYS-004 | Calibration workflow | 1. Menu → Tools → Calibration 2. Enter known diameter 3. Apply | Calibration saved |
| TC-SYS-005 | Tolerance check | 1. Enable tolerance 2. Set nominal=10mm, tol=0.1mm 3. Detect | OK/NG status displayed |
| TC-SYS-006 | Recipe save/load | 1. Configure settings 2. Recipe → Save 3. Load different recipe | Settings applied |
| TC-SYS-007 | Statistics tracking | 1. Run detections 2. View statistics panel | Counts updated correctly |
| TC-SYS-008 | Export history | 1. Run detections 2. File → Export History | CSV file created |
| TC-SYS-009 | IO simulation | 1. Start IO 2. Click Simulate Trigger | Trigger callback fired |
| TC-SYS-010 | NG image saving | 1. Enable Save NG Images 2. Detect NG circle | Image saved to output/ |

### 5.2 Error Handling Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|-----------------|
| TC-ERR-001 | Camera disconnect during operation | 1. Connect 2. Unplug camera | Graceful handling, error message |
| TC-ERR-002 | Invalid recipe file | 1. Corrupt recipe JSON 2. Load recipe | Error message, no crash |
| TC-ERR-003 | Export to invalid path | 1. Export to non-existent drive | Error message shown |
| TC-ERR-004 | Missing dependencies | 1. Uninstall opencv 2. Run app | Clear error message |

---

## 6. Performance Tests

### 6.1 Detection Speed

```python
# tests/performance/test_detection_speed.py

class TestDetectionPerformance:
    """Performance tests for detection"""

    def test_detection_latency(self, benchmark):
        """TC-PERF-001: Single frame detection time"""
        detector = CircleDetector()
        img = cv2.imread("tests/fixtures/circles_3.png")

        result = benchmark(detector.detect, img)

        # Should complete in < 50ms
        assert benchmark.stats.stats.mean < 0.05

    def test_throughput(self):
        """TC-PERF-002: Detection throughput"""
        detector = CircleDetector()
        img = cv2.imread("tests/fixtures/circles_3.png")

        start = time.time()
        for _ in range(100):
            detector.detect(img)
        elapsed = time.time() - start

        fps = 100 / elapsed
        assert fps >= 20  # Minimum 20 fps
```

### 6.2 Memory Usage

```python
class TestMemoryUsage:
    """Memory usage tests"""

    def test_no_memory_leak(self):
        """TC-PERF-003: No memory leak during extended operation"""
        import tracemalloc

        tracemalloc.start()
        detector = CircleDetector()
        img = cv2.imread("tests/fixtures/circles_3.png")

        # Run many iterations
        for _ in range(1000):
            detector.detect(img)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (< 500MB)
        assert peak < 500 * 1024 * 1024
```

### 6.3 Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Detection latency | < 50ms | pytest-benchmark |
| UI update rate | 30 fps | FPS counter |
| Memory usage | < 500MB | tracemalloc |
| Startup time | < 5s | Manual timing |
| IO response time | < 10ms | Oscilloscope |

---

## 7. User Acceptance Tests (UAT)

### 7.1 UAT Checklist

#### 7.1.1 Camera Functions
- [ ] Camera list refreshes correctly
- [ ] Can connect to camera
- [ ] Live view displays smoothly
- [ ] Exposure control works
- [ ] Can disconnect cleanly

#### 7.1.2 Detection Functions
- [ ] Circles are detected accurately
- [ ] Detection parameters adjustable
- [ ] Tolerance check works (OK/NG)
- [ ] Results displayed correctly
- [ ] Overlay visualization clear

#### 7.1.3 Calibration
- [ ] Calibration dialog opens
- [ ] Can enter reference diameter
- [ ] Auto-detect calibration circle works
- [ ] Calibration saved/loaded correctly
- [ ] Measurements in mm are accurate

#### 7.1.4 Recipe Management
- [ ] Can create new recipe
- [ ] Can save recipe
- [ ] Can load recipe
- [ ] Can delete recipe
- [ ] Export/Import works
- [ ] Settings applied correctly

#### 7.1.5 Statistics
- [ ] Inspection count accurate
- [ ] OK/NG counts accurate
- [ ] OK rate calculated correctly
- [ ] Runtime displayed
- [ ] Throughput calculated
- [ ] Reset statistics works
- [ ] Export to CSV works

#### 7.1.6 PLC/IO (Simulation)
- [ ] IO panel displays correctly
- [ ] Start/Stop IO works
- [ ] LED indicators update
- [ ] Simulate trigger works
- [ ] Enable toggle works
- [ ] Recipe bits work

#### 7.1.7 NG Image Saving
- [ ] Enable/disable works
- [ ] Images saved to correct folder
- [ ] Filename includes timestamp
- [ ] Image quality acceptable

### 7.2 UAT Sign-off

| Tester | Date | Result | Signature |
|--------|------|--------|-----------|
| | | Pass / Fail | |
| | | Pass / Fail | |
| | | Pass / Fail | |

---

## 8. Test Data

### 8.1 Test Images

| Filename | Description | Circles | Sizes (mm) |
|----------|-------------|---------|------------|
| circles_1.png | Single circle | 1 | 10.0 |
| circles_3.png | Three circles | 3 | 8.0, 10.0, 12.0 |
| circles_10.png | Ten circles | 10 | Various |
| no_circles.png | Blank image | 0 | N/A |
| ellipse.png | Ellipse (non-circle) | 0 | N/A |
| low_contrast.png | Low contrast circles | 2 | 10.0, 15.0 |
| noisy.png | Noisy image | 2 | 10.0, 12.0 |

### 8.2 Test Fixtures Location
```
tests/
├── fixtures/
│   ├── images/
│   │   ├── circles_1.png
│   │   ├── circles_3.png
│   │   └── ...
│   ├── recipes/
│   │   ├── test_recipe.json
│   │   └── ...
│   └── calibration/
│       └── test_calibration.json
├── unit/
├── integration/
├── performance/
└── conftest.py
```

---

## 9. Test Execution

### 9.1 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/ -v --benchmark-only

# Run specific test
pytest tests/unit/services/test_detector_service.py -v
```

### 9.2 CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src
```

---

## 10. Test Reports

### 10.1 Test Summary Template

| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Unit Tests | | | | |
| Integration Tests | | | | |
| System Tests | | | | |
| Performance Tests | | | | |
| **Total** | | | | |

### 10.2 Defect Tracking

| ID | Description | Severity | Status | Assigned |
|----|-------------|----------|--------|----------|
| | | | | |

---

## 11. Appendix

### 11.1 Test Case ID Convention

```
TC-[Category]-[Number]

Categories:
- DOM: Domain layer
- DET: Detection service
- CAL: Calibration service
- RCP: Recipe service
- IO: IO service
- CAM: Camera service
- IMG: Image saver
- INT: Integration tests
- SYS: System tests
- PERF: Performance tests
- ERR: Error handling
```

### 11.2 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-27 | Dev Team | Initial test plan |

---

*End of Test Plan Document*
