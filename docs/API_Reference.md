# API Reference - Circle Measurement System

## Version: 2.0.0

---

## Table of Contents
1. [Domain Layer](#1-domain-layer)
2. [Service Layer](#2-service-layer)
3. [Error Codes](#3-error-codes)
4. [Data Types](#4-data-types)

---

## 1. Domain Layer

### 1.1 CircleResult

Kết quả phát hiện một vòng tròn.

```python
@dataclass
class CircleResult:
    center_x: float      # Tọa độ X tâm (pixels)
    center_y: float      # Tọa độ Y tâm (pixels)
    radius: float        # Bán kính (pixels)
    diameter_mm: float   # Đường kính (mm)
    circularity: float   # Độ tròn (0.0 - 1.0)
    area_mm2: float      # Diện tích (mm²)
    status: MeasureStatus  # Trạng thái OK/NG
```

| Property | Type | Description | Range |
|----------|------|-------------|-------|
| `center_x` | float | Tọa độ X tâm vòng tròn | 0 - image_width |
| `center_y` | float | Tọa độ Y tâm vòng tròn | 0 - image_height |
| `radius` | float | Bán kính tính bằng pixels | > 0 |
| `diameter_mm` | float | Đường kính đã convert sang mm | > 0 |
| `circularity` | float | Độ tròn (1.0 = tròn hoàn hảo) | 0.0 - 1.0 |
| `area_mm2` | float | Diện tích vòng tròn | > 0 |
| `status` | MeasureStatus | Kết quả so sánh tolerance | OK, NG, NONE |

---

### 1.2 DetectionConfig

Cấu hình tham số phát hiện vòng tròn.

```python
@dataclass
class DetectionConfig:
    pixel_to_mm: float = 0.00644
    min_diameter_mm: float = 1.0
    max_diameter_mm: float = 20.0
    min_circularity: float = 0.85
    blur_kernel: int = 5
    edge_margin: int = 10
    binary_threshold: int = 0  # 0 = Otsu auto
    show_contours: bool = True
    show_diameter_line: bool = True
    show_label: bool = True
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pixel_to_mm` | float | 0.00644 | Tỷ lệ chuyển đổi pixel → mm |
| `min_diameter_mm` | float | 1.0 | Đường kính tối thiểu (mm) |
| `max_diameter_mm` | float | 20.0 | Đường kính tối đa (mm) |
| `min_circularity` | float | 0.85 | Độ tròn tối thiểu |
| `blur_kernel` | int | 5 | Kích thước kernel Gaussian blur |
| `edge_margin` | int | 10 | Margin từ biên ảnh (pixels) |
| `binary_threshold` | int | 0 | Ngưỡng binary (0 = Otsu) |
| `show_contours` | bool | True | Hiển thị contours |
| `show_diameter_line` | bool | True | Hiển thị đường kính |
| `show_label` | bool | True | Hiển thị label |

---

### 1.3 ToleranceConfig

Cấu hình dung sai đo lường.

```python
@dataclass
class ToleranceConfig:
    enabled: bool = False
    nominal_mm: float = 10.0
    tolerance_mm: float = 0.1
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | False | Bật/tắt kiểm tra dung sai |
| `nominal_mm` | float | 10.0 | Giá trị danh định (mm) |
| `tolerance_mm` | float | 0.1 | Dung sai cho phép ± (mm) |

**Methods:**

```python
def check(self, value: float) -> MeasureStatus:
    """
    Kiểm tra giá trị có nằm trong dung sai không.

    Args:
        value: Giá trị đo được (mm)

    Returns:
        MeasureStatus.OK nếu trong dung sai
        MeasureStatus.NG nếu ngoài dung sai
        MeasureStatus.NONE nếu tolerance disabled
    """
```

---

### 1.4 CalibrationData

Dữ liệu calibration.

```python
@dataclass
class CalibrationData:
    pixel_to_mm: float
    calibrated_at: datetime
    reference_size_mm: float
    reference_size_px: float
```

| Property | Type | Description |
|----------|------|-------------|
| `pixel_to_mm` | float | Tỷ lệ chuyển đổi |
| `calibrated_at` | datetime | Thời điểm calibration |
| `reference_size_mm` | float | Kích thước mẫu chuẩn (mm) |
| `reference_size_px` | float | Kích thước mẫu chuẩn (pixels) |

---

### 1.5 Recipe

Công thức sản phẩm.

```python
@dataclass
class Recipe:
    name: str
    description: str = ""
    detection_config: DetectionConfig
    tolerance_config: ToleranceConfig
    pixel_to_mm: float = 0.00644
    created_at: datetime
    updated_at: datetime
```

**Methods:**

```python
def to_dict(self) -> dict:
    """Convert recipe to dictionary."""

@classmethod
def from_dict(cls, data: dict) -> 'Recipe':
    """Create recipe from dictionary."""

def to_json(self) -> str:
    """Serialize recipe to JSON string."""

@classmethod
def from_json(cls, json_str: str) -> 'Recipe':
    """Deserialize recipe from JSON string."""
```

---

### 1.6 IOConfig

Cấu hình IO/PLC.

```python
@dataclass
class IOConfig:
    mode: IOMode = IOMode.SIMULATION
    device_name: str = "Dev1"
    trigger_channel: int = 0
    enable_channel: int = 1
    ok_channel: int = 0
    ng_channel: int = 1
    ready_channel: int = 2
    error_channel: int = 3
    busy_channel: int = 4
    trigger_debounce_ms: int = 50
    result_pulse_ms: int = 100
    polling_interval_ms: int = 10
```

---

### 1.7 IOStatus

Trạng thái IO hiện tại.

```python
@dataclass
class IOStatus:
    connected: bool = False
    trigger: bool = False
    system_enable: bool = True
    recipe_bit0: bool = False
    recipe_bit1: bool = False
    result_ok: bool = False
    result_ng: bool = False
    system_ready: bool = False
    system_error: bool = False
    busy: bool = False
    error_message: str = ""
```

---

### 1.8 Enums

```python
class MeasureStatus(Enum):
    OK = "ok"           # Trong dung sai
    NG = "ng"           # Ngoài dung sai
    NONE = "none"       # Không kiểm tra
    PARTIAL = "partial" # Vòng tròn bị cắt

class IOMode(Enum):
    SIMULATION = "simulation"  # Mô phỏng
    NI_DAQMX = "ni_daqmx"     # National Instruments
    ADVANTECH = "advantech"    # Advantech USB

class TriggerMode(Enum):
    SOFTWARE = "software"  # Trigger từ phần mềm
    HARDWARE = "hardware"  # Trigger từ PLC
```

---

## 2. Service Layer

### 2.1 CameraService

Quản lý kết nối và điều khiển camera.

```python
class BaslerGigECamera:
    """Service for Basler GigE camera operations."""
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `list_devices()` | - | `List[Dict]` | Liệt kê camera có sẵn |
| `connect(device_index, exposure_us)` | `int`, `float` | `bool` | Kết nối camera |
| `disconnect()` | - | `None` | Ngắt kết nối |
| `start_grabbing()` | - | `None` | Bắt đầu grab liên tục |
| `stop_grabbing()` | - | `None` | Dừng grab |
| `grab_frame()` | - | `Optional[ndarray]` | Lấy 1 frame |
| `set_exposure(exposure_us)` | `float` | `None` | Đặt exposure time |
| `get_info()` | - | `Dict` | Thông tin camera |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_connected` | bool | Trạng thái kết nối |
| `is_grabbing` | bool | Đang grab hay không |
| `device_info` | Dict | Thông tin thiết bị |

#### Example

```python
from src.services.camera_service import BaslerGigECamera

# List available cameras
devices = BaslerGigECamera.list_devices()
print(f"Found {len(devices)} cameras")

# Connect to first camera
camera = BaslerGigECamera()
if camera.connect(device_index=0, exposure_us=50.0):
    print("Connected!")

    # Grab a frame
    frame = camera.grab_frame()
    if frame is not None:
        print(f"Frame shape: {frame.shape}")

    # Disconnect
    camera.disconnect()
```

---

### 2.2 DetectorService

Phát hiện và đo vòng tròn.

```python
class CircleDetector:
    """Service for circle detection and measurement."""

    def __init__(self, config: Optional[DetectionConfig] = None):
        ...
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `detect(frame)` | `ndarray` | `List[CircleResult]` | Phát hiện circles |
| `update_config(config)` | `DetectionConfig` | `None` | Cập nhật config |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `config` | DetectionConfig | Cấu hình hiện tại |

#### Example

```python
from src.services.detector_service import CircleDetector
from src.domain.config import DetectionConfig
import cv2

# Create detector with custom config
config = DetectionConfig(
    min_diameter_mm=5.0,
    max_diameter_mm=15.0,
    min_circularity=0.9
)
detector = CircleDetector(config)

# Load and process image
image = cv2.imread("test_image.png")
circles = detector.detect(image)

for circle in circles:
    print(f"Diameter: {circle.diameter_mm:.3f} mm")
    print(f"Status: {circle.status}")
```

---

### 2.3 VisualizerService

Vẽ overlay kết quả lên ảnh.

```python
class CircleVisualizer:
    """Service for drawing detection results."""
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `draw(frame, circles, tolerance)` | `ndarray`, `List[CircleResult]`, `Optional[ToleranceConfig]` | `ndarray` | Vẽ overlay |

#### Example

```python
from src.services.visualizer_service import CircleVisualizer
from src.domain.config import ToleranceConfig

visualizer = CircleVisualizer()

# Draw results with tolerance checking
tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5)
result_frame = visualizer.draw(frame, circles, tolerance)

cv2.imshow("Result", result_frame)
```

---

### 2.4 CalibrationService

Quản lý calibration pixel-to-mm.

```python
class CalibrationService:
    """Service for camera calibration management."""

    def __init__(self, config_path: Optional[str] = None):
        ...
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `calibrate(reference_size_mm, reference_size_px)` | `float`, `float` | `CalibrationData` | Thực hiện calibration |
| `calibrate_from_circle(frame, known_diameter_mm)` | `ndarray`, `float` | `Optional[CalibrationData]` | Auto-calibrate từ ảnh |
| `set_pixel_to_mm(value)` | `float` | `None` | Set tỷ lệ trực tiếp |
| `reset_calibration()` | - | `None` | Reset về mặc định |
| `get_info()` | - | `Dict` | Thông tin calibration |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `pixel_to_mm` | float | Tỷ lệ chuyển đổi |
| `is_calibrated` | bool | Đã calibrate chưa |
| `calibration_data` | CalibrationData | Dữ liệu calibration |

#### Example

```python
from src.services.calibration_service import CalibrationService

calib = CalibrationService()

# Manual calibration
# Known: 10mm circle measures 1550 pixels
calib_data = calib.calibrate(
    reference_size_mm=10.0,
    reference_size_px=1550.0
)
print(f"Pixel to mm: {calib_data.pixel_to_mm:.6f}")

# Auto-calibration from image
# calib_data = calib.calibrate_from_circle(frame, known_diameter_mm=10.0)
```

---

### 2.5 RecipeService

Quản lý recipe sản phẩm.

```python
class RecipeService:
    """Service for recipe management."""

    def __init__(self, recipe_dir: Optional[str] = None):
        ...
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_recipe(name, description, ...)` | `str`, `str`, ... | `Recipe` | Tạo recipe mới |
| `save_recipe(recipe)` | `Recipe` | `bool` | Lưu recipe |
| `get_recipe(name)` | `str` | `Optional[Recipe]` | Load recipe |
| `delete_recipe(name)` | `str` | `bool` | Xóa recipe |
| `export_recipe(name, path)` | `str`, `str` | `bool` | Export ra file |
| `import_recipe(path)` | `str` | `Optional[Recipe]` | Import từ file |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `recipe_names` | List[str] | Danh sách tên recipe |
| `current_recipe` | Optional[Recipe] | Recipe đang active |

---

### 2.6 IOService

Giao tiếp với PLC/IO.

```python
class IOService:
    """Service for PLC/IO communication."""

    def __init__(self, config: Optional[IOConfig] = None):
        ...
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `initialize(config)` | `Optional[IOConfig]` | `bool` | Khởi tạo IO |
| `start()` | - | `bool` | Bắt đầu polling |
| `stop()` | - | `None` | Dừng polling |
| `cleanup()` | - | `None` | Giải phóng resources |
| `set_ready(ready)` | `bool` | `None` | Set tín hiệu Ready |
| `set_busy(busy)` | `bool` | `None` | Set tín hiệu Busy |
| `set_error(error)` | `bool` | `None` | Set tín hiệu Error |
| `set_result(ok)` | `bool` | `None` | Set kết quả OK/NG |
| `register_trigger_callback(callback)` | `Callable` | `None` | Đăng ký callback |
| `register_status_callback(callback)` | `Callable` | `None` | Đăng ký status callback |

#### Simulation Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `sim_set_trigger(value)` | `bool` | Set trigger input |
| `sim_set_enable(value)` | `bool` | Set enable input |
| `sim_set_recipe(index)` | `int` | Set recipe bits (0-3) |
| `sim_pulse_trigger()` | - | Generate trigger pulse |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `config` | IOConfig | Cấu hình IO |
| `status` | IOStatus | Trạng thái IO |
| `is_running` | bool | Đang chạy hay không |

---

### 2.7 ImageSaver

Lưu ảnh NG.

```python
class ImageSaver:
    """Service for saving NG images."""

    def __init__(self, save_dir: str = "output/ng_images"):
        ...
```

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `save_ng_image(frame, circles, processed_frame)` | `ndarray`, `List[CircleResult]`, `ndarray` | `Optional[str]` | Lưu ảnh NG |
| `set_save_directory(path)` | `str` | `None` | Đổi thư mục lưu |

---

## 3. Error Codes

### 3.1 Camera Errors (E1xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E100 | CAMERA_NOT_FOUND | Không tìm thấy camera | Kiểm tra kết nối, cài driver |
| E101 | CAMERA_CONNECTION_FAILED | Kết nối thất bại | Kiểm tra IP, firewall |
| E102 | CAMERA_GRAB_FAILED | Grab frame thất bại | Kiểm tra exposure, trigger |
| E103 | CAMERA_TIMEOUT | Timeout khi grab | Giảm exposure hoặc tăng timeout |
| E104 | CAMERA_ALREADY_CONNECTED | Camera đã kết nối | Disconnect trước |
| E105 | CAMERA_NOT_CONNECTED | Camera chưa kết nối | Connect trước |

### 3.2 Detection Errors (E2xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E200 | DETECTION_NO_CIRCLES | Không phát hiện circle | Điều chỉnh threshold, lighting |
| E201 | DETECTION_INVALID_IMAGE | Ảnh không hợp lệ | Kiểm tra camera output |
| E202 | DETECTION_CONFIG_INVALID | Config không hợp lệ | Kiểm tra parameters |

### 3.3 Calibration Errors (E3xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E300 | CALIBRATION_INVALID_REFERENCE | Reference size không hợp lệ | Nhập giá trị > 0 |
| E301 | CALIBRATION_NO_CIRCLE_FOUND | Không tìm thấy circle để calibrate | Đặt mẫu chuẩn đúng vị trí |
| E302 | CALIBRATION_FILE_ERROR | Lỗi đọc/ghi file calibration | Kiểm tra quyền file |

### 3.4 Recipe Errors (E4xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E400 | RECIPE_NOT_FOUND | Recipe không tồn tại | Kiểm tra tên recipe |
| E401 | RECIPE_INVALID_FORMAT | Format file không đúng | Kiểm tra JSON syntax |
| E402 | RECIPE_SAVE_FAILED | Lưu recipe thất bại | Kiểm tra quyền thư mục |
| E403 | RECIPE_NAME_EXISTS | Tên recipe đã tồn tại | Đổi tên khác |

### 3.5 IO Errors (E5xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E500 | IO_DEVICE_NOT_FOUND | Không tìm thấy IO device | Kiểm tra kết nối, driver |
| E501 | IO_CONNECTION_FAILED | Kết nối IO thất bại | Kiểm tra device name |
| E502 | IO_READ_ERROR | Lỗi đọc input | Kiểm tra wiring |
| E503 | IO_WRITE_ERROR | Lỗi ghi output | Kiểm tra wiring |
| E504 | IO_DRIVER_NOT_INSTALLED | Driver chưa cài | Cài NI-DAQmx hoặc Advantech driver |

---

## 4. Data Types

### 4.1 Type Aliases

```python
from typing import List, Dict, Tuple, Optional, Callable
import numpy as np

# Image types
Frame = np.ndarray  # Shape: (H, W, 3) for color, (H, W) for gray
BinaryImage = np.ndarray  # Shape: (H, W), dtype: uint8

# Callback types
TriggerCallback = Callable[[], None]
StatusCallback = Callable[[IOStatus], None]
FrameCallback = Callable[[Frame], None]

# Result types
DetectionResult = Tuple[List[CircleResult], BinaryImage]
```

### 4.2 JSON Schemas

#### Recipe JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "detection_config", "tolerance_config"],
  "properties": {
    "name": {"type": "string", "minLength": 1},
    "description": {"type": "string"},
    "detection_config": {
      "type": "object",
      "properties": {
        "pixel_to_mm": {"type": "number", "minimum": 0},
        "min_diameter_mm": {"type": "number", "minimum": 0},
        "max_diameter_mm": {"type": "number", "minimum": 0},
        "min_circularity": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "tolerance_config": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "nominal_mm": {"type": "number", "minimum": 0},
        "tolerance_mm": {"type": "number", "minimum": 0}
      }
    },
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"}
  }
}
```

#### Calibration JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["pixel_to_mm", "calibrated_at"],
  "properties": {
    "pixel_to_mm": {"type": "number", "minimum": 0},
    "calibrated_at": {"type": "string", "format": "date-time"},
    "reference_size_mm": {"type": "number", "minimum": 0},
    "reference_size_px": {"type": "number", "minimum": 0}
  }
}
```

---

## Appendix A: Quick Reference

### Service Creation

```python
# Camera
from src.services.camera_service import BaslerGigECamera
camera = BaslerGigECamera()

# Detector
from src.services.detector_service import CircleDetector
detector = CircleDetector()

# Visualizer
from src.services.visualizer_service import CircleVisualizer
visualizer = CircleVisualizer()

# Calibration
from src.services.calibration_service import CalibrationService
calibration = CalibrationService()

# Recipe
from src.services.recipe_service import RecipeService
recipe_service = RecipeService()

# IO
from src.services.io_service import IOService
io_service = IOService()

# Image Saver
from src.services.image_saver import ImageSaver
saver = ImageSaver()
```

### Common Workflows

```python
# 1. Basic detection
camera.connect(0)
frame = camera.grab_frame()
circles = detector.detect(frame)
result = visualizer.draw(frame, circles)
camera.disconnect()

# 2. With calibration
calibration.calibrate(10.0, 1550.0)
detector.update_config(DetectionConfig(
    pixel_to_mm=calibration.pixel_to_mm
))

# 3. With tolerance
tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0, tolerance_mm=0.5)
for circle in circles:
    status = tolerance.check(circle.diameter_mm)
    print(f"{circle.diameter_mm:.3f}mm - {status.value}")

# 4. With IO
io_service.initialize()
io_service.start()
io_service.register_trigger_callback(lambda: print("Triggered!"))
```

---

*Document Version: 2.0.0*
*Last Updated: December 2024*
