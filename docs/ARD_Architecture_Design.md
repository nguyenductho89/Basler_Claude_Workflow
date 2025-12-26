# Architecture Design Document (ARD)
# Hệ Thống Đo Kích Thước Lỗ Tròn - Circle Measurement System

---

## 1. Tổng Quan Kiến Trúc

### 1.1 Mục Đích Tài Liệu

Tài liệu này mô tả chi tiết kiến trúc phần mềm của hệ thống đo kích thước lỗ tròn sử dụng camera Basler và ống kính Telecentric. Tài liệu này dành cho:
- Software Developers
- System Integrators
- Technical Reviewers

### 1.2 Phạm Vi

| Hạng mục | Phạm vi |
|----------|---------|
| Phần mềm | Vision Application trên PC |
| Giao tiếp | GigE Camera, Digital I/O |
| Ngôn ngữ | Python 3.10+ |
| Platform | Windows 10/11 64-bit |

### 1.3 Tài Liệu Tham Chiếu

| Tài liệu | Version |
|----------|---------|
| PRD_Measurement_System.md | 2.0 |
| Basler Pylon SDK Documentation | 7.x |
| OpenCV Documentation | 4.x |

---

## 2. Kiến Trúc Tổng Thể

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CIRCLE MEASUREMENT SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  Main       │  │  Camera     │  │  Settings   │  │  Results   │  │   │
│  │  │  Window     │  │  View       │  │  Panel      │  │  Panel     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      APPLICATION LAYER                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  App        │  │  Detection  │  │  Measure    │  │  Recipe    │  │   │
│  │  │  Controller │  │  Service    │  │  Service    │  │  Manager   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN LAYER                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  Circle     │  │  Detection  │  │  Calibration│  │  Tolerance │  │   │
│  │  │  Entity     │  │  Config     │  │  Data       │  │  Rule      │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INFRASTRUCTURE LAYER                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  Camera     │  │  Image      │  │  Config     │  │  Logger    │  │   │
│  │  │  Driver     │  │  Processor  │  │  Storage    │  │            │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      EXTERNAL SYSTEMS                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │  Basler     │  │  File       │  │  PLC/IO     │                  │   │
│  │  │  Camera     │  │  System     │  │  Interface  │                  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Trách nhiệm | Ví dụ Components |
|-------|-------------|------------------|
| **Presentation** | UI, User interaction | MainWindow, Panels, Dialogs |
| **Application** | Business logic orchestration | Services, Controllers |
| **Domain** | Core business entities & rules | Entities, Value Objects |
| **Infrastructure** | External system communication | Camera driver, File I/O |

---

## 3. Component Design

### 3.1 Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        GUI Application                                │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     MainWindow                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │  │
│  │  │ CameraPanel  │  │ ControlPanel │  │    VideoCanvas        │ │  │
│  │  │ - Connect    │  │ - Exposure   │  │    - Live view        │ │  │
│  │  │ - Disconnect │  │ - Detection  │  │    - Overlay drawing  │ │  │
│  │  │ - Refresh    │  │ - Tolerance  │  │                       │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘ │  │
│  └─────────┼─────────────────┼──────────────────────┼─────────────┘  │
│            │                 │                      │                │
│            ▼                 ▼                      ▼                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    ApplicationController                         │ │
│  │  - Coordinates all services                                      │ │
│  │  - Manages application state                                     │ │
│  │  - Handles user commands                                         │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                             │                                        │
│         ┌───────────────────┼───────────────────┐                   │
│         ▼                   ▼                   ▼                   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│  │CameraService│     │CircleDetector│    │Visualizer   │            │
│  │- connect()  │     │- detect()   │     │- draw()     │            │
│  │- disconnect()│    │- configure()│     │- overlay()  │            │
│  │- grab()     │     │             │     │             │            │
│  └──────┬──────┘     └──────┬──────┘     └─────────────┘            │
│         │                   │                                        │
│         ▼                   ▼                                        │
│  ┌─────────────┐     ┌─────────────┐                                │
│  │BaslerDriver │     │ImageProcessor                                │
│  │(pypylon)    │     │(OpenCV)     │                                │
│  └─────────────┘     └─────────────┘                                │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Descriptions

#### 3.2.1 CameraService
```
Responsibilities:
  - Quản lý kết nối camera GigE
  - Cấu hình camera (exposure, trigger, etc.)
  - Grab và trả về frame

Dependencies:
  - pypylon (Basler Pylon SDK)

Interface:
  + list_devices() → List[DeviceInfo]
  + connect(device_index, exposure_us) → bool
  + disconnect() → void
  + grab_frame() → ndarray
  + set_exposure(exposure_us) → void
  + is_connected → bool
```

#### 3.2.2 CircleDetector
```
Responsibilities:
  - Xử lý ảnh (pre-processing)
  - Phát hiện hình tròn tự động
  - Tính toán thông số (diameter, circularity)

Dependencies:
  - OpenCV
  - NumPy

Interface:
  + detect(frame) → Tuple[List[CircleResult], binary_image]
  + configure(config: DetectionConfig) → void
```

#### 3.2.3 Visualizer
```
Responsibilities:
  - Vẽ overlay lên frame (edge, diameter line, label)
  - Hiển thị kết quả OK/NG

Dependencies:
  - OpenCV

Interface:
  + draw(frame, circles, tolerance) → frame_with_overlay
```

#### 3.2.4 ApplicationController
```
Responsibilities:
  - Điều phối các services
  - Quản lý application state
  - Xử lý user commands

Dependencies:
  - CameraService
  - CircleDetector
  - Visualizer

Interface:
  + start() → void
  + stop() → void
  + on_connect() → void
  + on_disconnect() → void
  + update_settings(config) → void
```

---

## 4. Class Design

### 4.1 Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Domain Classes                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │   <<dataclass>>     │         │   <<dataclass>>     │                   │
│  │   CircleResult      │         │   DetectionConfig   │                   │
│  ├─────────────────────┤         ├─────────────────────┤                   │
│  │ + hole_id: int      │         │ + pixel_to_mm: float│                   │
│  │ + center_x: float   │         │ + min_diameter: float                   │
│  │ + center_y: float   │         │ + max_diameter: float                   │
│  │ + radius: float     │         │ + min_circularity: float                │
│  │ + diameter_mm: float│         │ + blur_kernel: int  │                   │
│  │ + circularity: float│         │ + edge_margin: int  │                   │
│  │ + area_mm2: float   │         │ + show_contours: bool                   │
│  │ + status: Status    │         │ + show_diameter: bool                   │
│  └─────────────────────┘         │ + show_label: bool  │                   │
│                                  └─────────────────────┘                   │
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │   <<dataclass>>     │         │    <<enum>>         │                   │
│  │   ToleranceConfig   │         │    MeasureStatus    │                   │
│  ├─────────────────────┤         ├─────────────────────┤                   │
│  │ + enabled: bool     │         │ OK                  │                   │
│  │ + nominal_mm: float │         │ NG                  │                   │
│  │ + tolerance_mm: float         │ PARTIAL             │                   │
│  └─────────────────────┘         │ SKIPPED             │                   │
│                                  └─────────────────────┘                   │
│                                                                             │
│  ┌─────────────────────┐         ┌─────────────────────┐                   │
│  │   <<dataclass>>     │         │   <<dataclass>>     │                   │
│  │   CalibrationData   │         │   Recipe            │                   │
│  ├─────────────────────┤         ├─────────────────────┤                   │
│  │ + pixel_to_mm: float│         │ + name: str         │                   │
│  │ + calibrated_at:    │         │ + detection_config  │                   │
│  │     datetime        │         │ + tolerance_config  │                   │
│  │ + reference_size:   │         │ + calibration_data  │                   │
│  │     float           │         │ + created_at: datetime                  │
│  └─────────────────────┘         └─────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Service Classes                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        BaslerGigECamera                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ - camera: pylon.InstantCamera                                        │   │
│  │ - converter: pylon.ImageFormatConverter                              │   │
│  │ - is_connected: bool                                                 │   │
│  │ - is_grabbing: bool                                                  │   │
│  │ - device_info: DeviceInfo                                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ + list_devices() → List[Dict]                                        │   │
│  │ + connect(device_index: int, exposure_us: float) → bool              │   │
│  │ + disconnect() → void                                                │   │
│  │ + start_grabbing() → void                                            │   │
│  │ + stop_grabbing() → void                                             │   │
│  │ + grab_frame() → Optional[ndarray]                                   │   │
│  │ + set_exposure(exposure_us: float) → void                            │   │
│  │ + get_info() → Dict                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         CircleDetector                               │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ - config: DetectionConfig                                            │   │
│  │ - min_area_px: float                                                 │   │
│  │ - max_area_px: float                                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ + __init__(config: DetectionConfig)                                  │   │
│  │ + detect(frame: ndarray) → Tuple[List[CircleResult], ndarray]        │   │
│  │ + update_config(config: DetectionConfig) → void                      │   │
│  │ - _calc_pixel_limits() → void                                        │   │
│  │ - _preprocess(frame: ndarray) → ndarray                              │   │
│  │ - _find_circles(binary: ndarray) → List[CircleResult]                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        CircleVisualizer                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ - config: DetectionConfig                                            │   │
│  │ - colors: Dict[str, Tuple]                                           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ + draw(frame: ndarray, circles: List[CircleResult],                  │   │
│  │        tolerance: Optional[ToleranceConfig]) → ndarray               │   │
│  │ - _draw_circle_edge(frame, circle, color) → void                     │   │
│  │ - _draw_diameter_line(frame, circle) → void                          │   │
│  │ - _draw_label(frame, circle, tolerance) → void                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW DIAGRAM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐      ┌─────────────┐      ┌─────────────┐      ┌──────────┐   │
│  │ Camera  │─────>│ Raw Frame   │─────>│ Grayscale   │─────>│ Blurred  │   │
│  │ (GigE)  │      │ (BGR)       │      │ Frame       │      │ Frame    │   │
│  └─────────┘      └─────────────┘      └─────────────┘      └────┬─────┘   │
│                                                                   │         │
│                                                                   ▼         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Binary Threshold                              │  │
│  │                    (Otsu's Method / Adaptive)                         │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       Find Contours                                   │  │
│  │                  List of all closed contours                          │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Filter Contours                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │ Area Filter    │  │ Circularity    │  │ Edge Margin    │          │  │
│  │  │ min < A < max  │  │ > 0.85         │  │ Check          │          │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Fit Circle (Each Contour)                         │  │
│  │              cv2.minEnclosingCircle() → (center, radius)              │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Calculate Measurements                           │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │ Diameter (mm)  │  │ Area (mm²)     │  │ Circularity    │          │  │
│  │  │ = 2r × px2mm   │  │ = A × px2mm²   │  │ = 4πA/P²       │          │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│  ┌────────────────┐      ┌────────────────┐      ┌────────────────┐       │
│  │ CircleResult   │─────>│ Tolerance      │─────>│ Status         │       │
│  │ List           │      │ Check          │      │ (OK/NG)        │       │
│  └────────────────┘      └────────────────┘      └───────┬────────┘       │
│                                                          │                 │
│                          ┌───────────────────────────────┘                 │
│                          │                                                 │
│                          ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Visualizer                                    │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │ Draw Edge      │  │ Draw Diameter  │  │ Draw Label     │          │  │
│  │  │ (Green/Red)    │  │ Line (Blue)    │  │ D=xx.xxxmm     │          │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│                          ┌────────────────┐                                │
│                          │ Display Frame  │                                │
│                          │ (with Overlay) │                                │
│                          └────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Module Structure

### 5.1 Project Structure

```
circle_measurement_system/
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                      # Entry point
│   │
│   ├── domain/                      # Domain entities
│   │   ├── __init__.py
│   │   ├── entities.py              # CircleResult, Recipe, etc.
│   │   ├── enums.py                 # MeasureStatus, etc.
│   │   └── config.py                # DetectionConfig, ToleranceConfig
│   │
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── camera_service.py        # BaslerGigECamera
│   │   ├── detector_service.py      # CircleDetector
│   │   ├── visualizer_service.py    # CircleVisualizer
│   │   ├── calibration_service.py   # CalibrationManager
│   │   └── recipe_service.py        # RecipeManager
│   │
│   ├── ui/                          # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py           # Main application window
│   │   ├── panels/
│   │   │   ├── __init__.py
│   │   │   ├── camera_panel.py      # Camera connection panel
│   │   │   ├── control_panel.py     # Settings panel
│   │   │   ├── results_panel.py     # Detection results
│   │   │   └── video_canvas.py      # Video display
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── calibration_dialog.py
│   │       └── recipe_dialog.py
│   │
│   ├── infrastructure/              # External interfaces
│   │   ├── __init__.py
│   │   ├── basler_driver.py         # Pylon SDK wrapper
│   │   ├── image_processor.py       # OpenCV operations
│   │   ├── config_storage.py        # JSON/YAML config files
│   │   └── logger.py                # Logging setup
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── constants.py             # Application constants
│       └── helpers.py               # Helper functions
│
├── config/
│   ├── default_config.json          # Default settings
│   └── recipes/                     # Recipe files
│       └── sample_recipe.json
│
├── logs/                            # Log files
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_detector.py
│   ├── test_camera.py
│   └── test_visualizer.py
│
├── docs/                            # Documentation
│   ├── PRD_Measurement_System.md
│   └── ARD_Architecture_Design.md
│
├── requirements.txt
├── setup.py
└── README.md
```

### 5.2 Module Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODULE DEPENDENCY GRAPH                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌──────────┐                                   │
│                              │  main.py │                                   │
│                              └────┬─────┘                                   │
│                                   │                                         │
│                                   ▼                                         │
│                         ┌─────────────────┐                                 │
│                         │  main_window.py │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│           ┌──────────────────────┼──────────────────────┐                  │
│           │                      │                      │                  │
│           ▼                      ▼                      ▼                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│  │  camera_panel   │   │  control_panel  │   │  video_canvas   │          │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘          │
│           │                     │                     │                    │
│           └──────────────┬──────┴─────────────────────┘                    │
│                          │                                                  │
│                          ▼                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         SERVICES LAYER                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │ │
│  │  │camera_service│  │detector_     │  │visualizer_   │  │calibration│  │ │
│  │  │              │  │service       │  │service       │  │_service   │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘  │ │
│  └─────────┼─────────────────┼─────────────────┼────────────────┼────────┘ │
│            │                 │                 │                │          │
│            ▼                 ▼                 ▼                ▼          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        DOMAIN LAYER                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │ │
│  │  │  entities    │  │   config     │  │    enums     │                  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│            │                 │                                              │
│            ▼                 ▼                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     INFRASTRUCTURE LAYER                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │ │
│  │  │basler_driver │  │image_processor│ │config_storage│                  │ │
│  │  │  (pypylon)   │  │  (OpenCV)    │  │  (JSON)      │                  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Interface Design

### 6.1 Camera Service Interface

```python
class ICameraService(Protocol):
    """Interface for camera operations"""

    @staticmethod
    def list_devices() -> List[Dict[str, Any]]:
        """List all available camera devices"""
        ...

    def connect(self, device_index: int, exposure_us: float = 50.0) -> bool:
        """Connect to camera by index"""
        ...

    def disconnect(self) -> None:
        """Disconnect from camera"""
        ...

    def grab_frame(self) -> Optional[np.ndarray]:
        """Grab a single frame"""
        ...

    def set_exposure(self, exposure_us: float) -> None:
        """Set exposure time in microseconds"""
        ...

    @property
    def is_connected(self) -> bool:
        """Check if camera is connected"""
        ...
```

### 6.2 Detector Service Interface

```python
class IDetectorService(Protocol):
    """Interface for circle detection"""

    def detect(self, frame: np.ndarray) -> Tuple[List[CircleResult], np.ndarray]:
        """
        Detect circles in frame
        Returns: (list of circles, binary image)
        """
        ...

    def configure(self, config: DetectionConfig) -> None:
        """Update detection configuration"""
        ...
```

### 6.3 Visualizer Service Interface

```python
class IVisualizerService(Protocol):
    """Interface for visualization"""

    def draw(
        self,
        frame: np.ndarray,
        circles: List[CircleResult],
        tolerance: Optional[ToleranceConfig] = None
    ) -> np.ndarray:
        """Draw detection results on frame"""
        ...
```

---

## 7. Configuration Management

### 7.1 Configuration Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Application Configuration",
  "type": "object",
  "properties": {
    "camera": {
      "type": "object",
      "properties": {
        "default_exposure_us": {"type": "number", "default": 50.0},
        "trigger_mode": {"type": "string", "enum": ["software", "hardware"]},
        "pixel_format": {"type": "string", "default": "BGR8"}
      }
    },
    "detection": {
      "type": "object",
      "properties": {
        "pixel_to_mm": {"type": "number", "default": 0.00644},
        "min_diameter_mm": {"type": "number", "default": 1.0},
        "max_diameter_mm": {"type": "number", "default": 20.0},
        "min_circularity": {"type": "number", "default": 0.85},
        "blur_kernel": {"type": "integer", "default": 5},
        "edge_margin": {"type": "integer", "default": 10}
      }
    },
    "tolerance": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean", "default": false},
        "nominal_mm": {"type": "number", "default": 10.0},
        "tolerance_mm": {"type": "number", "default": 0.05}
      }
    },
    "display": {
      "type": "object",
      "properties": {
        "show_contours": {"type": "boolean", "default": true},
        "show_diameter_line": {"type": "boolean", "default": true},
        "show_labels": {"type": "boolean", "default": true}
      }
    }
  }
}
```

### 7.2 Recipe Schema

```json
{
  "name": "Product_A_10mm_Holes",
  "version": "1.0",
  "created_at": "2025-12-26T10:00:00Z",
  "detection": {
    "min_diameter_mm": 8.0,
    "max_diameter_mm": 12.0,
    "min_circularity": 0.90
  },
  "tolerance": {
    "enabled": true,
    "nominal_mm": 10.0,
    "tolerance_mm": 0.05
  },
  "calibration": {
    "pixel_to_mm": 0.00644,
    "calibrated_at": "2025-12-26T09:00:00Z"
  }
}
```

---

## 8. Error Handling Strategy

### 8.1 Exception Hierarchy

```
BaseApplicationError
├── CameraError
│   ├── CameraNotFoundError
│   ├── CameraConnectionError
│   └── CameraGrabError
├── DetectionError
│   ├── InvalidImageError
│   └── ProcessingError
├── ConfigurationError
│   ├── InvalidConfigError
│   └── ConfigNotFoundError
└── CalibrationError
    └── InvalidCalibrationError
```

### 8.2 Error Handling Matrix

| Error Type | Severity | User Action | System Action |
|------------|----------|-------------|---------------|
| CameraNotFound | High | Check connection | Show dialog, retry option |
| CameraGrabError | Medium | - | Retry grab, log warning |
| InvalidImage | Low | - | Skip frame, log |
| ConfigNotFound | Medium | Select config | Use defaults |
| CalibrationInvalid | High | Re-calibrate | Block measurement |

---

## 9. Performance Considerations

### 9.1 Performance Requirements

| Metric | Requirement | Target |
|--------|-------------|--------|
| Frame processing time | < 200ms | < 100ms |
| UI responsiveness | < 100ms | < 50ms |
| Memory usage | < 500MB | < 300MB |
| Camera latency | < 50ms | < 30ms |

### 9.2 Optimization Strategies

1. **Image Processing**
   - Sử dụng ROI để giảm vùng xử lý
   - Resize ảnh trước khi hiển thị
   - Sử dụng NumPy vectorized operations

2. **Threading**
   - Camera grab thread riêng
   - UI thread không bị block
   - Processing có thể parallel

3. **Memory Management**
   - Reuse frame buffers
   - Clear old frames kịp thời
   - Limit history/log size

---

## 10. Testing Strategy

### 10.1 Test Levels

| Level | Scope | Tools |
|-------|-------|-------|
| Unit Test | Individual classes | pytest |
| Integration Test | Service interactions | pytest |
| System Test | Full application | Manual + Automated |
| Performance Test | Speed, memory | pytest-benchmark |

### 10.2 Test Coverage Targets

| Module | Coverage Target |
|--------|-----------------|
| Domain | 95% |
| Services | 90% |
| Infrastructure | 80% |
| UI | 70% |

---

## 11. Deployment

### 11.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| CPU | Intel i5 | Intel i7 |
| RAM | 8 GB | 16 GB |
| Storage | 10 GB free | 50 GB SSD |
| Network | GigE port | Dedicated GigE |
| Display | 1920×1080 | 1920×1080 |

### 11.2 Dependencies

```
# Python 3.10+
numpy>=1.21.0
opencv-python>=4.5.0
Pillow>=9.0.0
pypylon>=1.9.0

# Development
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
mypy>=0.950
```

### 11.3 Installation Steps

```bash
# 1. Install Basler Pylon SDK
# Download from: https://www.baslerweb.com/en/downloads/software-downloads/

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python src/main.py
```

---

**Document Version:** 1.0
**Created Date:** 2025-12-26
**Author:** Claude AI Assistant
**Status:** Draft

---

**Revision History:**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-26 | Initial architecture design |
