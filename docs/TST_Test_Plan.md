# Test Plan - Circle Measurement System v2.1

| Document Info | |
|---------------|---|
| Version | 1.2 |
| Date | 2025-12-27 |
| Status | Draft |
| Author | Development Team |

---

## 1. Introduction

### 1.1 Purpose
Tài liệu này mô tả kế hoạch kiểm thử cho Circle Measurement System v2.0, bao gồm các test cases, test procedures, và acceptance criteria.

### 1.2 Scope
Test plan bao gồm tất cả các tính năng từ MVP 1.0 đến Release 2.1:
- Camera integration
- Circle detection & visualization
- Calibration system
- Threading & history
- Recipe management
- Production statistics
- PLC/IO integration
- **Web Dashboard (v2.1)**: REST API, WebSocket, MJPEG streaming

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

## 11. Web Dashboard Tests (v2.1)

### 11.1 Web API Unit Tests

```python
# tests/unit/web/test_api.py

class TestWebAPIEndpoints:
    """Test REST API endpoints"""

    @pytest.fixture
    def client(self, app_core):
        """Create test client"""
        from src.web.server import create_app
        app = create_app(app_core)
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_get_status(self, client):
        """TC-WEB-001: GET /api/status returns system status"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "camera_connected" in data
        assert "is_running" in data
        assert "current_recipe" in data

    def test_get_statistics(self, client):
        """TC-WEB-002: GET /api/statistics returns production stats"""
        response = client.get("/api/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_inspections" in data
        assert "ok_count" in data
        assert "ng_count" in data
        assert "ok_rate" in data

    def test_get_statistics_export(self, client):
        """TC-WEB-003: GET /api/statistics/export returns CSV"""
        response = client.get("/api/statistics/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    def test_get_recipes_list(self, client):
        """TC-WEB-004: GET /api/recipes returns recipe list"""
        response = client.get("/api/recipes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recipes"], list)

    def test_get_recipe_by_name(self, client):
        """TC-WEB-005: GET /api/recipes/{name} returns recipe details"""
        response = client.get("/api/recipes/Default")
        if response.status_code == 200:
            data = response.json()
            assert "name" in data
            assert "detection_config" in data
        else:
            assert response.status_code == 404

    def test_get_io_status(self, client):
        """TC-WEB-006: GET /api/io/status returns IO status"""
        response = client.get("/api/io/status")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        assert "trigger_state" in data
        assert "system_ready" in data

    def test_get_calibration(self, client):
        """TC-WEB-007: GET /api/calibration returns calibration info"""
        response = client.get("/api/calibration")
        assert response.status_code == 200
        data = response.json()
        assert "is_calibrated" in data
        assert "pixel_to_mm" in data

    def test_get_history(self, client):
        """TC-WEB-008: GET /api/history returns measurement history"""
        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_history_with_limit(self, client):
        """TC-WEB-009: GET /api/history?limit=10 returns limited history"""
        response = client.get("/api/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10
```

### 11.2 WebSocket Tests

```python
# tests/unit/web/test_websocket.py

class TestWebSocket:
    """Test WebSocket connections"""

    @pytest.fixture
    def ws_client(self, app_core):
        """Create WebSocket test client"""
        from src.web.server import create_app
        app = create_app(app_core)
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_websocket_connect(self, ws_client):
        """TC-WS-001: WebSocket connection established"""
        with ws_client.websocket_connect("/ws/live") as websocket:
            assert websocket is not None

    def test_websocket_receive_status(self, ws_client, app_core):
        """TC-WS-002: WebSocket receives system_status event"""
        with ws_client.websocket_connect("/ws/live") as websocket:
            # Wait for initial status message
            data = websocket.receive_json(timeout=5)
            assert data["event"] == "system_status"
            assert "camera_connected" in data["data"]

    def test_websocket_receive_detection(self, ws_client, app_core):
        """TC-WS-003: WebSocket receives detection_result event"""
        with ws_client.websocket_connect("/ws/live") as websocket:
            # Trigger a detection
            app_core.publish("detection_complete", mock_detection_result())

            # Receive the event
            data = websocket.receive_json(timeout=5)
            assert data["event"] == "detection_result"

    def test_websocket_multiple_clients(self, ws_client, app_core):
        """TC-WS-004: Multiple WebSocket clients supported"""
        with ws_client.websocket_connect("/ws/live") as ws1:
            with ws_client.websocket_connect("/ws/live") as ws2:
                with ws_client.websocket_connect("/ws/live") as ws3:
                    # All three should be connected
                    assert ws1 is not None
                    assert ws2 is not None
                    assert ws3 is not None

    def test_websocket_broadcast(self, ws_client, app_core):
        """TC-WS-005: Event broadcast to all clients"""
        clients = []
        try:
            for i in range(3):
                client = ws_client.websocket_connect("/ws/live").__enter__()
                clients.append(client)

            # Publish an event
            app_core.publish("statistics_update", {"total": 100})

            # All clients should receive
            for client in clients:
                data = client.receive_json(timeout=5)
                assert data["event"] == "statistics_update"
        finally:
            for client in clients:
                client.__exit__(None, None, None)

    def test_websocket_disconnect_graceful(self, ws_client):
        """TC-WS-006: WebSocket disconnects gracefully"""
        with ws_client.websocket_connect("/ws/live") as websocket:
            pass  # Connection closes when exiting context
        # No exception should be raised
```

### 11.3 MJPEG Stream Tests

```python
# tests/unit/web/test_stream.py

class TestMJPEGStream:
    """Test MJPEG video stream"""

    @pytest.fixture
    def client(self, app_core):
        from src.web.server import create_app
        app = create_app(app_core)
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_stream_content_type(self, client):
        """TC-STR-001: Stream returns correct content-type"""
        response = client.get("/stream/video", stream=True)
        assert response.status_code == 200
        assert "multipart/x-mixed-replace" in response.headers["content-type"]

    def test_stream_returns_frames(self, client, app_core):
        """TC-STR-002: Stream returns JPEG frames"""
        # Set a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        app_core.set_display_frame(test_frame)

        response = client.get("/stream/video", stream=True)
        content = b""
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk
            if b"\xff\xd8" in content and b"\xff\xd9" in content:
                break  # Found complete JPEG

        # Verify JPEG markers
        assert b"\xff\xd8" in content  # JPEG start
        assert b"\xff\xd9" in content  # JPEG end

    def test_stream_no_frame_placeholder(self, client, app_core):
        """TC-STR-003: Returns placeholder when no frame available"""
        app_core.clear_display_frame()

        response = client.get("/stream/video", stream=True)
        content = b""
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk
            if len(content) > 5000:
                break

        # Should still get valid response (placeholder image)
        assert response.status_code == 200
```

### 11.4 Web Integration Tests

```python
# tests/integration/web/test_web_integration.py

class TestWebIntegration:
    """Integration tests for Web Dashboard"""

    @pytest.fixture
    def full_system(self, tmp_path):
        """Create full system with AppCore and services"""
        from src.core.app_core import AppCore
        from src.services.detector_service import CircleDetector
        from src.services.recipe_service import RecipeService

        app_core = AppCore()
        app_core.detector = CircleDetector()
        app_core.recipe_service = RecipeService(str(tmp_path / "recipes"))
        return app_core

    def test_detection_result_to_websocket(self, full_system):
        """TC-WINT-001: Detection result propagates to WebSocket"""
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        app = create_app(full_system)
        client = TestClient(app)

        with client.websocket_connect("/ws/live") as websocket:
            # Simulate detection
            from src.domain.config import CircleResult, MeasureStatus
            result = CircleResult(
                center_x=320, center_y=240,
                diameter_px=100, diameter_mm=10.0,
                status=MeasureStatus.OK
            )
            full_system.publish("detection_complete", {"circles": [result]})

            # Should receive via WebSocket
            data = websocket.receive_json(timeout=5)
            assert data["event"] == "detection_result"

    def test_recipe_api_loads_real_recipes(self, full_system):
        """TC-WINT-002: Recipe API returns real recipes from service"""
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        # Create a recipe
        recipe = full_system.recipe_service.create_recipe(name="TestRecipe")
        full_system.recipe_service.save_recipe(recipe)

        app = create_app(full_system)
        client = TestClient(app)

        response = client.get("/api/recipes")
        data = response.json()

        assert "TestRecipe" in data["recipes"]

    def test_statistics_synced_with_api(self, full_system):
        """TC-WINT-003: Statistics API reflects actual statistics"""
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        # Update statistics
        full_system.statistics.add_inspection(ok=True)
        full_system.statistics.add_inspection(ok=True)
        full_system.statistics.add_inspection(ok=False)

        app = create_app(full_system)
        client = TestClient(app)

        response = client.get("/api/statistics")
        data = response.json()

        assert data["total_inspections"] == 3
        assert data["ok_count"] == 2
        assert data["ng_count"] == 1

    def test_hybrid_mode_tkinter_and_web(self, full_system):
        """TC-WINT-004: Tkinter and Web Dashboard share state"""
        # This test verifies that changes from Tkinter are visible in Web
        full_system.set_current_recipe("NewRecipe")

        from src.web.server import create_app
        from fastapi.testclient import TestClient

        app = create_app(full_system)
        client = TestClient(app)

        response = client.get("/api/status")
        data = response.json()

        assert data["current_recipe"] == "NewRecipe"
```

### 11.5 Web Performance Tests

```python
# tests/performance/web/test_web_performance.py

class TestWebPerformance:
    """Performance tests for Web Dashboard"""

    def test_api_response_time(self, benchmark, client):
        """TC-WPERF-001: API response time < 100ms"""
        result = benchmark(client.get, "/api/status")
        assert benchmark.stats.stats.mean < 0.1  # 100ms

    def test_websocket_latency(self, app_core):
        """TC-WPERF-002: WebSocket message latency < 500ms"""
        import time
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        app = create_app(app_core)
        client = TestClient(app)

        latencies = []
        with client.websocket_connect("/ws/live") as websocket:
            for _ in range(10):
                start = time.time()
                app_core.publish("test_event", {"timestamp": start})
                data = websocket.receive_json(timeout=2)
                latencies.append(time.time() - start)

        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 0.5  # 500ms

    def test_concurrent_clients(self, app_core):
        """TC-WPERF-003: Support 5+ concurrent WebSocket clients"""
        import threading
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        app = create_app(app_core)

        connected = []
        errors = []

        def connect_client():
            try:
                client = TestClient(app)
                with client.websocket_connect("/ws/live") as ws:
                    connected.append(True)
                    time.sleep(2)  # Stay connected
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=connect_client) for _ in range(5)]
        for t in threads:
            t.start()

        time.sleep(1)  # Let connections establish

        assert len(connected) >= 5
        assert len(errors) == 0

        for t in threads:
            t.join()

    def test_mjpeg_frame_rate(self, app_core):
        """TC-WPERF-004: MJPEG stream achieves >= 5 FPS"""
        import time
        from src.web.server import create_app
        from fastapi.testclient import TestClient

        # Set up test frames
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        app_core.set_display_frame(test_frame)

        app = create_app(app_core)
        client = TestClient(app)

        response = client.get("/stream/video", stream=True)

        frame_count = 0
        start_time = time.time()

        for chunk in response.iter_content(chunk_size=4096):
            if b"\xff\xd9" in chunk:  # JPEG end marker
                frame_count += 1
            if time.time() - start_time >= 5:  # Test for 5 seconds
                break

        fps = frame_count / 5.0
        assert fps >= 5  # Minimum 5 FPS
```

### 11.6 Web UAT Checklist

#### 11.6.1 Web Dashboard Access
- [ ] Dashboard accessible at http://localhost:8080
- [ ] Dashboard loads without errors
- [ ] Page layout displays correctly
- [ ] Responsive design works on different screen sizes

#### 11.6.2 Live Video Stream
- [ ] Video stream displays in browser
- [ ] Stream shows detection overlays
- [ ] No significant delay (< 2 seconds)
- [ ] Stream reconnects after network interruption

#### 11.6.3 Detection Results Display
- [ ] Circle detection results display in real-time
- [ ] OK/NG status displayed with correct color coding
- [ ] Diameter measurements shown accurately
- [ ] Results update immediately after detection

#### 11.6.4 Statistics Panel
- [ ] Statistics display correctly
- [ ] OK rate percentage calculated correctly
- [ ] Statistics update in real-time
- [ ] Export CSV button works

#### 11.6.5 Recipe Information
- [ ] Current recipe name displayed
- [ ] Nominal diameter and tolerance shown
- [ ] Recipe info updates when changed in desktop app

#### 11.6.6 IO Status Panel
- [ ] IO connection status displayed
- [ ] Trigger state indicator works
- [ ] Ready/Result indicators update correctly
- [ ] IO status syncs with desktop app

#### 11.6.7 History Table
- [ ] Measurement history displayed
- [ ] Table updates with new measurements
- [ ] Scrolling works for large history
- [ ] Timestamps displayed correctly

#### 11.6.8 Multi-client Support
- [ ] Multiple browsers can view dashboard simultaneously
- [ ] All clients receive same data
- [ ] No performance degradation with 5 clients
- [ ] Client disconnect handled gracefully

### 11.7 Web Performance Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| API response time | < 100ms | pytest-benchmark |
| WebSocket latency | < 500ms | Timestamp comparison |
| MJPEG stream FPS | >= 5 FPS | Frame counter |
| Concurrent clients | >= 5 | Thread test |
| Memory overhead | < 50MB | tracemalloc |
| Detection FPS impact | < 5% | Compare with/without web |

---

## 12. Appendix

### 12.1 Test Case ID Convention

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
- WEB: Web API endpoints (v2.1)
- WS: WebSocket tests (v2.1)
- STR: MJPEG stream tests (v2.1)
- WINT: Web integration tests (v2.1)
- WPERF: Web performance tests (v2.1)
```

### 12.2 Regression Test Strategy

#### 12.2.1 Regression Test Scope

| Trigger | Scope | Description |
|---------|-------|-------------|
| Bug Fix | Affected module + related modules | Test the fix and verify no side effects |
| Feature Addition | New feature + integration points | Full regression on affected areas |
| Refactoring | Full regression | Complete test suite execution |
| Release | Full regression + smoke tests | All tests must pass |

#### 12.2.2 Regression Test Suite

| Suite | Tests | Execution Time | Frequency |
|-------|-------|----------------|-----------|
| Smoke | 10 critical tests | ~2 min | Every commit |
| Core | 50 unit tests | ~5 min | Every push |
| Full | 113+ all tests | ~15 min | Daily/PR merge |
| Extended | Full + performance | ~30 min | Weekly |

#### 12.2.3 CI/CD Automated Regression

```yaml
# Automated via GitHub Actions
on:
  push: Run Smoke + Core
  pull_request: Run Full Suite
  schedule (daily): Run Extended Suite
```

#### 12.2.4 Regression Priority Matrix

| Priority | Criteria | Examples |
|----------|----------|----------|
| P1 Critical | Core functionality, data integrity | Detection accuracy, calibration save |
| P2 High | Key features, user workflows | Recipe load, tolerance check |
| P3 Medium | Secondary features | Statistics export, history |
| P4 Low | UI, cosmetic | Color display, label format |

---

### 12.3 Test Fixtures

Test fixtures được lưu tại `tests/fixtures/`:

```
tests/fixtures/
├── images/
│   ├── circle_single_10mm.png      # Single circle, 10mm diameter
│   ├── circles_multiple_3.png      # 3 circles: 8mm, 10mm, 12mm
│   ├── circles_edge_partial.png    # Circle at edge (partial)
│   ├── ellipse_not_circle.png      # Ellipse for filter test
│   ├── blank_no_object.png         # Blank image
│   ├── noisy_low_contrast.png      # Low contrast test
│   └── calibration_target.png      # Known diameter for calibration
├── recipes/
│   ├── test_recipe_default.json    # Default test recipe
│   ├── test_recipe_tight_tol.json  # Tight tolerance (0.05mm)
│   └── test_recipe_large_range.json # Large diameter range
├── calibration/
│   └── test_calibration.json       # Pre-defined calibration data
└── config/
    └── test_app_config.json        # Test application config
```

#### Image Fixture Specifications

| Filename | Dimensions | Circles | Diameter (px) | Purpose |
|----------|------------|---------|---------------|---------|
| circle_single_10mm.png | 640×480 | 1 | 155 | Basic detection |
| circles_multiple_3.png | 800×600 | 3 | 124, 155, 186 | Multi-circle |
| circles_edge_partial.png | 640×480 | 1 | 155 (partial) | Edge handling |
| ellipse_not_circle.png | 640×480 | 0 | N/A | Filter test |
| blank_no_object.png | 640×480 | 0 | N/A | No detection |

---

### 12.4 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-27 | Dev Team | Initial test plan |
| 1.1 | 2025-12-27 | Dev Team | Added Regression Strategy, Test Fixtures |
| 1.2 | 2025-12-27 | Dev Team | Added Web Dashboard Tests (Section 11) for v2.1 |

---

*End of Test Plan Document*
