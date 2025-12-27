# API Reference - Circle Measurement System

## Version: 2.1.0

---

## Table of Contents
1. [Domain Layer](#1-domain-layer)
2. [Service Layer](#2-service-layer)
3. [Error Codes](#3-error-codes)
4. [Data Types](#4-data-types)
5. [Web API (v2.1)](#5-web-api-v21)

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

## 5. Web API (v2.1)

### 5.1 Overview

Web Dashboard API cung cấp REST endpoints và WebSocket cho remote monitoring. Server chạy trên port **8080**.

**Base URL:** `http://localhost:8080`

### 5.2 REST API Endpoints

#### 5.2.1 System Status

```http
GET /api/status
```

**Response:**
```json
{
  "camera_connected": true,
  "is_running": true,
  "current_recipe": "Product_A",
  "fps": 28.5,
  "web_clients": 2,
  "timestamp": "2024-12-27T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `camera_connected` | bool | Camera connection status |
| `is_running` | bool | Detection loop running |
| `current_recipe` | string | Active recipe name |
| `fps` | float | Current detection FPS |
| `web_clients` | int | Connected WebSocket clients |
| `timestamp` | string | ISO 8601 timestamp |

---

#### 5.2.2 Production Statistics

```http
GET /api/statistics
```

**Response:**
```json
{
  "total_inspections": 1234,
  "ok_count": 1200,
  "ng_count": 34,
  "ok_rate": 97.24,
  "throughput_per_minute": 15.5,
  "runtime_seconds": 4800,
  "last_result": "OK",
  "session_start": "2024-12-27T08:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `total_inspections` | int | Total inspections count |
| `ok_count` | int | OK count |
| `ng_count` | int | NG count |
| `ok_rate` | float | OK percentage (0-100) |
| `throughput_per_minute` | float | Inspections per minute |
| `runtime_seconds` | int | Runtime in seconds |
| `last_result` | string | Last result: "OK", "NG", "NONE" |
| `session_start` | string | Session start timestamp |

---

#### 5.2.3 Export Statistics

```http
GET /api/statistics/export
```

**Response:** CSV file download

```csv
timestamp,total,ok,ng,ok_rate
2024-12-27T10:30:00Z,1234,1200,34,97.24
```

**Headers:**
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="statistics_20241227_103000.csv"
```

---

#### 5.2.4 Recipe List

```http
GET /api/recipes
```

**Response:**
```json
{
  "recipes": ["Default", "Product_A", "Product_B"],
  "current": "Product_A",
  "count": 3
}
```

---

#### 5.2.5 Recipe Details

```http
GET /api/recipes/{name}
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `name` | string | Recipe name |

**Response:**
```json
{
  "name": "Product_A",
  "description": "Standard product configuration",
  "detection_config": {
    "pixel_to_mm": 0.00644,
    "min_diameter_mm": 8.0,
    "max_diameter_mm": 12.0,
    "min_circularity": 0.85
  },
  "tolerance_config": {
    "enabled": true,
    "nominal_mm": 10.0,
    "tolerance_mm": 0.05
  },
  "created_at": "2024-12-01T00:00:00Z",
  "updated_at": "2024-12-27T10:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Recipe not found: Product_X"
}
```

---

#### 5.2.6 IO Status

```http
GET /api/io/status
```

**Response:**
```json
{
  "connected": true,
  "mode": "simulation",
  "trigger_state": false,
  "system_enable": true,
  "system_ready": true,
  "result_ok": false,
  "result_ng": false,
  "busy": false,
  "error": false,
  "recipe_index": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| `connected` | bool | IO connection status |
| `mode` | string | "simulation", "ni_daqmx", "advantech" |
| `trigger_state` | bool | Trigger input state |
| `system_enable` | bool | System enable input |
| `system_ready` | bool | Ready output state |
| `result_ok` | bool | OK output state |
| `result_ng` | bool | NG output state |
| `busy` | bool | Busy output state |
| `error` | bool | Error output state |
| `recipe_index` | int | Recipe selection (0-3) |

---

#### 5.2.7 Calibration Info

```http
GET /api/calibration
```

**Response:**
```json
{
  "is_calibrated": true,
  "pixel_to_mm": 0.00644,
  "reference_size_mm": 10.0,
  "reference_size_px": 1552.8,
  "calibrated_at": "2024-12-27T08:00:00Z"
}
```

---

#### 5.2.8 Measurement History

```http
GET /api/history
GET /api/history?limit=50&offset=0
```

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | int | 100 | Maximum items to return |
| `offset` | int | 0 | Skip first N items |

**Response:**
```json
{
  "items": [
    {
      "timestamp": "2024-12-27T10:30:00.123Z",
      "circles": [
        {
          "diameter_mm": 10.02,
          "status": "OK",
          "center_x": 320,
          "center_y": 240
        }
      ],
      "overall_status": "OK"
    }
  ],
  "total": 1234,
  "limit": 100,
  "offset": 0
}
```

---

### 5.3 Video Stream

#### 5.3.1 MJPEG Stream

```http
GET /stream/video
```

**Response:** Multipart MJPEG stream

**Headers:**
```
Content-Type: multipart/x-mixed-replace; boundary=frame
```

**Stream Format:**
```
--frame
Content-Type: image/jpeg

<JPEG binary data>
--frame
Content-Type: image/jpeg

<JPEG binary data>
...
```

**Usage in HTML:**
```html
<img src="http://localhost:8080/stream/video" />
```

**Stream Parameters:**
- Target FPS: 10 fps
- JPEG Quality: 85%
- Resolution: Same as camera (with overlays)

---

### 5.4 WebSocket API

#### 5.4.1 Connection

```
WebSocket: ws://localhost:8080/ws/live
```

**Connection Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/live');

ws.onopen = () => {
  console.log('Connected to Web Dashboard');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.event, data.data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

---

#### 5.4.2 Event Types

##### detection_result

Gửi khi phát hiện vòng tròn mới.

```json
{
  "event": "detection_result",
  "data": {
    "timestamp": "2024-12-27T10:30:00.123Z",
    "circles": [
      {
        "center_x": 320.5,
        "center_y": 240.2,
        "diameter_mm": 10.02,
        "circularity": 0.98,
        "status": "OK"
      }
    ],
    "overall_status": "OK",
    "detection_time_ms": 15.2
  }
}
```

##### statistics_update

Gửi mỗi 5 giây hoặc khi có thay đổi.

```json
{
  "event": "statistics_update",
  "data": {
    "total_inspections": 1234,
    "ok_count": 1200,
    "ng_count": 34,
    "ok_rate": 97.24,
    "throughput_per_minute": 15.5
  }
}
```

##### io_status

Gửi mỗi 500ms hoặc khi có thay đổi IO.

```json
{
  "event": "io_status",
  "data": {
    "trigger_state": false,
    "system_ready": true,
    "result_ok": false,
    "result_ng": false,
    "recipe_index": 0
  }
}
```

##### system_status

Gửi khi kết nối và mỗi 10 giây.

```json
{
  "event": "system_status",
  "data": {
    "camera_connected": true,
    "is_running": true,
    "current_recipe": "Product_A",
    "fps": 28.5,
    "web_clients": 2
  }
}
```

##### recipe_changed

Gửi khi recipe được thay đổi.

```json
{
  "event": "recipe_changed",
  "data": {
    "name": "Product_B",
    "nominal_mm": 15.0,
    "tolerance_mm": 0.1
  }
}
```

---

### 5.5 Pydantic Schemas

```python
# src/web/schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MeasureStatusEnum(str, Enum):
    OK = "OK"
    NG = "NG"
    NONE = "NONE"

class CircleResultSchema(BaseModel):
    center_x: float
    center_y: float
    diameter_mm: float
    circularity: float
    status: MeasureStatusEnum

class DetectionResultSchema(BaseModel):
    timestamp: datetime
    circles: List[CircleResultSchema]
    overall_status: MeasureStatusEnum
    detection_time_ms: float

class SystemStatusSchema(BaseModel):
    camera_connected: bool
    is_running: bool
    current_recipe: Optional[str]
    fps: float
    web_clients: int
    timestamp: datetime

class StatisticsSchema(BaseModel):
    total_inspections: int
    ok_count: int
    ng_count: int
    ok_rate: float
    throughput_per_minute: float
    runtime_seconds: int
    last_result: MeasureStatusEnum
    session_start: datetime

class IOStatusSchema(BaseModel):
    connected: bool
    mode: str
    trigger_state: bool
    system_enable: bool
    system_ready: bool
    result_ok: bool
    result_ng: bool
    busy: bool
    error: bool
    recipe_index: int

class CalibrationSchema(BaseModel):
    is_calibrated: bool
    pixel_to_mm: float
    reference_size_mm: Optional[float]
    reference_size_px: Optional[float]
    calibrated_at: Optional[datetime]

class RecipeListSchema(BaseModel):
    recipes: List[str]
    current: Optional[str]
    count: int

class DetectionConfigSchema(BaseModel):
    pixel_to_mm: float
    min_diameter_mm: float
    max_diameter_mm: float
    min_circularity: float

class ToleranceConfigSchema(BaseModel):
    enabled: bool
    nominal_mm: float
    tolerance_mm: float

class RecipeDetailSchema(BaseModel):
    name: str
    description: str
    detection_config: DetectionConfigSchema
    tolerance_config: ToleranceConfigSchema
    created_at: datetime
    updated_at: datetime

class HistoryItemSchema(BaseModel):
    timestamp: datetime
    circles: List[CircleResultSchema]
    overall_status: MeasureStatusEnum

class HistoryResponseSchema(BaseModel):
    items: List[HistoryItemSchema]
    total: int
    limit: int
    offset: int

class WebSocketEventSchema(BaseModel):
    event: str
    data: dict
```

---

### 5.6 Error Responses

#### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Camera not connected |

#### Error Response Format

```json
{
  "detail": "Error message here",
  "error_code": "E6XX"
}
```

#### Web API Error Codes (E6xx)

| Code | Name | Description |
|------|------|-------------|
| E600 | WEB_SERVER_ERROR | Internal server error |
| E601 | WEB_STREAM_ERROR | Video stream error |
| E602 | WEB_WEBSOCKET_ERROR | WebSocket connection error |
| E603 | WEB_CAMERA_NOT_READY | Camera not connected for stream |
| E604 | WEB_RECIPE_NOT_FOUND | Recipe not found |
| E605 | WEB_INVALID_PARAMS | Invalid query parameters |

---

### 5.7 CORS Configuration

Web API cho phép CORS từ tất cả origins để hỗ trợ development:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Recommendation:** Giới hạn `allow_origins` cho các domain cụ thể.

---

### 5.8 Rate Limiting

| Endpoint | Rate Limit |
|----------|------------|
| `/api/*` | 100 requests/minute |
| `/stream/video` | 1 connection/client |
| `/ws/live` | 5 connections/IP |

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

*Document Version: 2.1.0*
*Last Updated: December 2024*
