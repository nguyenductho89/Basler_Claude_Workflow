# Requirements Traceability Matrix (RTM)
# Circle Measurement System v2.0

---

## 1. Overview

Ma trận truy xuất yêu cầu (RTM) liên kết các User Stories với thiết kế, code implementation và test cases.

## 2. User Story → Design → Implementation → Test

### 2.1 US-01: Live Camera View

| Item | Reference |
|------|-----------|
| **User Story** | US-01: Tôi muốn xem hình ảnh live từ camera để giám sát quá trình đo |
| **Priority** | High |
| **Design** | ARD Section 3.2.1 - CameraService |
| **Components** | `camera_service.py`, `video_canvas.py` |
| **Classes** | `BaslerGigECamera`, `VideoCanvas` |
| **Methods** | `grab_frame()`, `start_grabbing()` |
| **Test Cases** | TC-CAM-001, TC-CAM-002, TC-SYS-002 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-01.1: Camera list hiển thị sau khi nhấn Refresh
- [x] AC-01.2: Live view hiển thị ≥ 10 FPS
- [x] AC-01.3: Frame rate hiển thị trên status bar
- [x] AC-01.4: Live view dừng khi disconnect

---

### 2.2 US-02: Auto Circle Detection

| Item | Reference |
|------|-----------|
| **User Story** | US-02: Tôi muốn hệ thống tự động phát hiện và đo tất cả lỗ tròn |
| **Priority** | High |
| **Design** | ARD Section 3.2.2 - CircleDetector |
| **Components** | `detector_service.py` |
| **Classes** | `CircleDetector` |
| **Methods** | `detect()`, `_preprocess()`, `_find_circles()` |
| **Test Cases** | TC-DET-001 to TC-DET-005, TC-SYS-003 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-02.1: Phát hiện tất cả circles trong FOV
- [x] AC-02.2: Lọc theo min/max diameter
- [x] AC-02.3: Lọc theo circularity
- [x] AC-02.4: Đo chính xác ±0.01mm sau calibration

---

### 2.3 US-03: Visual Measurement Display

| Item | Reference |
|------|-----------|
| **User Story** | US-03: Tôi muốn thấy kết quả đo hiển thị trực tiếp trên hình ảnh |
| **Priority** | High |
| **Design** | ARD Section 3.2.3 - Visualizer |
| **Components** | `visualizer_service.py` |
| **Classes** | `CircleVisualizer` |
| **Methods** | `draw()`, `_draw_circle_edge()`, `_draw_label()` |
| **Test Cases** | TC-VIS-001 to TC-VIS-006, TC-SYS-003 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-03.1: Edge của circle được highlight
- [x] AC-03.2: Đường kính hiển thị với độ chính xác 0.001mm
- [x] AC-03.3: Label hiển thị đầy đủ thông tin
- [x] AC-03.4: Có thể bật/tắt từng loại overlay

---

### 2.4 US-04: OK/NG Color Indication

| Item | Reference |
|------|-----------|
| **User Story** | US-04: Tôi muốn biết ngay sản phẩm OK hay NG qua màu sắc |
| **Priority** | High |
| **Design** | ARD Section 4.1 - ToleranceConfig |
| **Components** | `visualizer_service.py`, `config.py` |
| **Classes** | `ToleranceConfig`, `CircleVisualizer` |
| **Methods** | `check()`, `draw()` |
| **Test Cases** | TC-DOM-003, TC-DOM-004, TC-VIS-003, TC-SYS-005 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-04.1: OK = Green, NG = Red, None = Gray
- [x] AC-04.2: Màu hiển thị rõ ràng trên mọi background
- [x] AC-04.3: Status text hiển thị cùng màu
- [x] AC-04.4: Panel kết quả cập nhật real-time

---

### 2.5 US-05: Easy Camera Connection

| Item | Reference |
|------|-----------|
| **User Story** | US-05: Tôi muốn kết nối/ngắt kết nối camera dễ dàng |
| **Priority** | High |
| **Design** | ARD Section 6.1 - Camera Service Interface |
| **Components** | `camera_service.py`, `camera_panel.py` |
| **Classes** | `BaslerGigECamera`, `CameraPanel` |
| **Methods** | `connect()`, `disconnect()`, `list_devices()` |
| **Test Cases** | TC-CAM-001 to TC-CAM-005, TC-SYS-001, TC-SYS-002 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-05.1: Connect button rõ ràng
- [x] AC-05.2: Status hiển thị Connected/Disconnected
- [x] AC-05.3: Auto-disconnect khi đóng app
- [x] AC-05.4: Error message khi kết nối thất bại

---

### 2.6 US-06: Exposure Control

| Item | Reference |
|------|-----------|
| **User Story** | US-06: Tôi muốn điều chỉnh exposure time |
| **Priority** | Medium |
| **Design** | ARD Section 6.1 - Camera Service |
| **Components** | `camera_service.py`, `control_panel.py` |
| **Classes** | `BaslerGigECamera` |
| **Methods** | `set_exposure()` |
| **Test Cases** | TC-CAM-006, TC-SYS-002 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-06.1: Slider hoặc input box cho exposure
- [x] AC-06.2: Range: 10µs - 1000ms
- [x] AC-06.3: Thay đổi có hiệu lực ngay lập tức
- [x] AC-06.4: Giá trị được lưu vào recipe

---

### 2.7 US-07: Tolerance Configuration

| Item | Reference |
|------|-----------|
| **User Story** | US-07: Tôi muốn thay đổi dung sai cho từng loại sản phẩm |
| **Priority** | Medium |
| **Design** | ARD Section 4.1 - ToleranceConfig |
| **Components** | `config.py`, `control_panel.py` |
| **Classes** | `ToleranceConfig` |
| **Methods** | `check()` |
| **Test Cases** | TC-DOM-003, TC-DOM-004, TC-SYS-005 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-07.1: Input cho Nominal và Tolerance
- [x] AC-07.2: Enable/Disable checkbox
- [x] AC-07.3: Hiển thị range (min-max)
- [x] AC-07.4: Lưu vào recipe

---

### 2.8 US-08: Calibration

| Item | Reference |
|------|-----------|
| **User Story** | US-08: Tôi muốn calibrate hệ thống với mẫu chuẩn |
| **Priority** | Medium |
| **Design** | ARD Section 3.2 - CalibrationService |
| **Components** | `calibration_service.py`, `calibration_dialog.py` |
| **Classes** | `CalibrationService`, `CalibrationDialog` |
| **Methods** | `calibrate()`, `calibrate_from_circle()` |
| **Test Cases** | TC-CAL-001 to TC-CAL-005, TC-SYS-004 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-08.1: Dialog cho calibration
- [x] AC-08.2: Nhập kích thước mẫu chuẩn (mm)
- [x] AC-08.3: Auto-detect circle option
- [x] AC-08.4: Lưu calibration data
- [x] AC-08.5: Hiển thị pixel-to-mm ratio

---

### 2.9 US-09: Recipe Management

| Item | Reference |
|------|-----------|
| **User Story** | US-09: Tôi muốn lưu/tải recipe cho các loại sản phẩm khác nhau |
| **Priority** | Medium |
| **Design** | ARD Section 4.1 - Recipe |
| **Components** | `recipe_service.py`, `recipe_dialog.py` |
| **Classes** | `RecipeService`, `Recipe` |
| **Methods** | `save_recipe()`, `get_recipe()`, `delete_recipe()` |
| **Test Cases** | TC-RCP-001 to TC-RCP-005, TC-SYS-006 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-09.1: Save recipe với tên
- [x] AC-09.2: Load recipe từ danh sách
- [x] AC-09.3: Delete recipe
- [x] AC-09.4: Export/Import JSON
- [x] AC-09.5: Apply settings ngay lập tức

---

### 2.10 US-10: Statistics Tracking

| Item | Reference |
|------|-----------|
| **User Story** | US-10: Tôi muốn xem thống kê OK/NG theo thời gian |
| **Priority** | Low |
| **Design** | ARD Section 3.1 - Statistics |
| **Components** | `statistics_panel.py`, `history_service.py` |
| **Classes** | `StatisticsPanel`, `InspectionHistory` |
| **Methods** | `update_stats()`, `export_csv()` |
| **Test Cases** | TC-SYS-007, TC-SYS-008 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-10.1: Hiển thị Total, OK, NG counts
- [x] AC-10.2: Hiển thị OK rate %
- [x] AC-10.3: Hiển thị throughput (pcs/min)
- [x] AC-10.4: Reset statistics button
- [x] AC-10.5: Export to CSV

---

### 2.11 US-11: Report Export

| Item | Reference |
|------|-----------|
| **User Story** | US-11: Tôi muốn xuất báo cáo đo lường theo ca/ngày |
| **Priority** | Low |
| **Design** | ARD Section 3.1 - Export |
| **Components** | `history_service.py` |
| **Classes** | `InspectionHistory` |
| **Methods** | `export_csv()`, `export_report()` |
| **Test Cases** | TC-SYS-008 |
| **Status** | ✅ Implemented |

**Acceptance Criteria:**
- [x] AC-11.1: Export CSV với timestamp
- [x] AC-11.2: Include: time, diameter, status, recipe
- [x] AC-11.3: Filter by date range
- [x] AC-11.4: Save dialog cho file location

---

## 3. Use Case → Test Case Mapping

| Use Case | Description | Test Cases |
|----------|-------------|------------|
| UC-01 | Kết nối camera | TC-CAM-001, TC-CAM-002, TC-SYS-002 |
| UC-02 | Tự động đo lỗ tròn | TC-DET-001 to TC-DET-005, TC-INT-001, TC-SYS-003 |
| UC-03 | Thay đổi dung sai | TC-DOM-003, TC-DOM-004, TC-SYS-005 |
| UC-04 | Calibration | TC-CAL-001 to TC-CAL-005, TC-SYS-004 |
| UC-05 | Recipe management | TC-RCP-001 to TC-RCP-005, TC-SYS-006 |
| UC-06 | IO/PLC Integration | TC-IO-001 to TC-IO-006, TC-INT-003, TC-INT-004 |

---

## 4. Component → Test Coverage

| Component | Source File | Test File | Coverage |
|-----------|-------------|-----------|----------|
| Domain Entities | `domain/entities.py` | `test_entities.py` | 95% |
| Domain Config | `domain/config.py` | `test_config.py` | 92% |
| Camera Service | `services/camera_service.py` | `test_camera_service.py` | 68% |
| Detector Service | `services/detector_service.py` | `test_detector_service.py` | 94% |
| Visualizer Service | `services/visualizer_service.py` | `test_visualizer_service.py` | 85% |
| Calibration Service | `services/calibration_service.py` | `test_calibration_service.py` | 90% |
| Recipe Service | `services/recipe_service.py` | `test_recipe_service.py` | 88% |
| IO Service | `services/io_service.py` | `test_io_service.py` | 82% |
| Image Saver | `services/image_saver.py` | `test_image_saver.py` | 85% |

---

## 5. Sprint → Feature Mapping

| Sprint | Features | User Stories | Status |
|--------|----------|--------------|--------|
| Sprint 1 | Camera connection, Live view | US-01, US-05 | ✅ Done |
| Sprint 2 | Circle detection, Visualization | US-02, US-03 | ✅ Done |
| Sprint 3 | Tolerance checking, OK/NG | US-04, US-07 | ✅ Done |
| Sprint 4 | Calibration | US-08 | ✅ Done |
| Sprint 5 | Recipe management | US-09 | ✅ Done |
| Sprint 6 | Statistics, Export | US-10, US-11 | ✅ Done |
| Sprint 7 | IO/PLC Integration | - | ✅ Done |
| Sprint 8 | Testing, Documentation | - | 🔄 In Progress |

---

## 6. Risk Traceability

| Risk ID | Description | Mitigation | Related US |
|---------|-------------|------------|------------|
| R-001 | Camera không ổn định | Retry mechanism, error handling | US-01, US-05 |
| R-002 | Detection không chính xác | Tunable parameters, preview | US-02 |
| R-003 | Calibration drift | Periodic re-calibration reminder | US-08 |
| R-004 | IO timing issues | Debounce, pulse duration config | - |
| R-005 | Memory leak long-run | History limit, garbage collection | US-10 |

---

## 7. Change Log

| Date | Change | Affected Items |
|------|--------|----------------|
| 2024-12-26 | Initial PRD created | All US |
| 2024-12-26 | Added IO/PLC features | US-new |
| 2024-12-27 | Added test cases | All TC |
| 2024-12-27 | Updated AC for all US | AC-* |

---

*Document Version: 1.0*
*Last Updated: December 2024*
