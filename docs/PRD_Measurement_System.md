# Product Requirements Document (PRD)
# Hệ Thống Đo Kích Thước Lỗ Tròn Trên Vật Thể Kim Loại

---

## 1. Tổng Quan Dự Án

### 1.1 Mô Tả Dự Án
Xây dựng hệ thống kiểm tra chất lượng tự động (Automated Quality Inspection System) sử dụng công nghệ thị giác máy (Machine Vision) để đo kích thước lỗ tròn trên các chi tiết kim loại di chuyển trên băng tải công nghiệp.

### 1.2 Mục Tiêu
- Đo chính xác đường kính lỗ tròn trên vật thể kim loại
- Phát hiện lỗi kích thước nằm ngoài dung sai cho phép
- Hoạt động liên tục 24/7 trong môi trường nhà máy
- Tích hợp với hệ thống điều khiển sản xuất (PLC/SCADA)

### 1.3 Phạm Vi Dự Án
| Hạng mục | Mô tả |
|----------|-------|
| Loại sản phẩm | Speed nut / Spring nut (đai ốc lò xo dập, mạ kẽm). Tấm kim loại chữ nhật ~22×16mm có vành boss tròn dập (drawn boss) đường kính ~4–15mm chứa cơ cấu lò xo bên trong. |
| Vị trí lắp đặt | Trên dây chuyền băng tải |
| Chế độ hoạt động | Thời gian thực (Real-time) |
| Môi trường | Nhà máy sản xuất công nghiệp |

---

## 2. Thông Số Kỹ Thuật Thiết Bị

### 2.1 Camera: Basler acA4600-7gc

| Thông số | Giá trị |
|----------|---------|
| **Cảm biến** | ON Semiconductor MT9F002 CMOS |
| **Độ phân giải** | 4608 × 3288 pixels (14 Megapixels) |
| **Tốc độ khung hình** | 7 fps @ full resolution |
| **Kích thước cảm biến** | 1/2.3" |
| **Giao tiếp** | GigE Vision (Gigabit Ethernet) |
| **Loại** | Color (Màu) |
| **Kiểu màn trập** | Rolling Shutter |
| **Độ sâu bit** | 8-bit hoặc 12-bit |
| **Kích thước** | 29 × 29 mm (Tiêu chuẩn Ace) |
| **Nguồn điện** | Power over Ethernet (PoE) hoặc 12V DC |

**Tính năng nổi bật:**
- Hỗ trợ Area of Interest (AOI) để tăng tốc độ
- Auto Exposure Control
- Pixel Binning
- Trigger Input/Output
- GigE Vision & GenICam compliant
- Tương thích Pylon SDK

### 2.2 Ống Kính: Telecentric Lens HK-YC10-80H

| Thông số | Giá trị |
|----------|---------|
| **Loại** | Object-Space Telecentric |
| **Độ phóng đại (Magnification) β** | 0.208x |
| **Khoảng cách làm việc (WD)** | 228 ±4 mm |
| **Hỗ trợ CCD tối đa** | φ16.6mm (1") |
| **Khẩu độ phía ảnh (Image F/#)** | 6.5 |
| **Độ méo (Distortion)** | < 0.1% |
| **Độ lệch telecentric** | < 0.1° |
| **Trường nhìn tối đa (FOV max)** | φ80mm |
| **MTF30 (lp/mm)** | > 135 |
| **Độ sâu trường ảnh (DoF)** | ±14.8mm @F16 |
| **Khoảng cách vật-ảnh (I/O)** | 446 ±4 mm |
| **Bước sóng hoạt động** | 420 ~ 660nm |
| **Mount** | C-Mount |
| **Chiều dài ống kính** | 200.5mm |

**Bảng FOV theo loại cảm biến:**

| Cảm biến | Kích thước (mm) | FOV (mm × mm) |
|----------|-----------------|---------------|
| 1" PYTHON 5000 | 12.43 × 9.83 | 59.8 × 47.3 |
| 1" IMX255 | 14.19 × 7.51 | 68.2 × 36.1 |
| 1" IMX183 | 13.13 × 8.76 | 63.1 × 42.1 |
| **1/2.3" MT9F002 (acA4600-7gc)** | **6.17 × 4.55** | **29.7 × 21.9** |

*Nguồn: Datasheet HK-YC10-80H*

### 2.3 Lý Do Chọn Ống Kính Telecentric

| Ưu điểm | Giải thích |
|---------|------------|
| **Không méo phối cảnh** | Đo chính xác kích thước bất kể vị trí vật trong FOV |
| **Độ phóng đại không đổi** | Magnification không thay đổi theo khoảng cách Z |
| **Phù hợp đo lường** | Thiết kế chuyên cho ứng dụng đo kích thước |
| **Giảm sai số** | Loại bỏ lỗi do góc nhìn gây ra |

---

## 3. User Stories & Use Cases

### 3.1 User Stories

| ID | Role | Story | Priority |
|----|------|-------|----------|
| US-01 | Operator | Tôi muốn xem hình ảnh live từ camera để giám sát quá trình đo | High |
| US-02 | Operator | Tôi muốn hệ thống tự động phát hiện và đo tất cả lỗ tròn mà không cần cấu hình vị trí | High |
| US-03 | Operator | Tôi muốn thấy kết quả đo (đường kính) hiển thị trực tiếp trên hình ảnh | High |
| US-04 | Operator | Tôi muốn biết ngay sản phẩm OK hay NG qua màu sắc hiển thị | High |
| US-05 | Operator | Tôi muốn kết nối/ngắt kết nối camera dễ dàng qua nút bấm | High |
| US-06 | Technician | Tôi muốn điều chỉnh exposure time khi điều kiện ánh sáng thay đổi | Medium |
| US-07 | Technician | Tôi muốn thay đổi dung sai đo cho từng loại sản phẩm khác nhau | Medium |
| US-08 | Technician | Tôi muốn calibrate hệ thống với mẫu chuẩn | Medium |
| US-09 | Engineer | Tôi muốn lưu/tải recipe cho các loại sản phẩm khác nhau | Medium |
| US-10 | Engineer | Tôi muốn xem thống kê OK/NG theo thời gian | Low |
| US-11 | Manager | Tôi muốn xuất báo cáo đo lường theo ca/ngày | Low |
| US-12 | Supervisor | Tôi muốn giám sát sản xuất từ xa qua trình duyệt web mà không cần cài phần mềm | Medium |

### 3.2 Acceptance Criteria

#### US-01: Live Camera View
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-01.1 | GIVEN camera connected, WHEN app starts, THEN live view displays at ≥10 FPS | ✅ Pass |
| AC-01.2 | GIVEN live view running, WHEN exposure changes, THEN image brightness updates immediately | ✅ Pass |
| AC-01.3 | GIVEN live view, WHEN frame rate < 5 FPS, THEN warning displayed | ✅ Pass |

#### US-02: Auto Circle Detection
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-02.1 | GIVEN image with circles, WHEN detect runs, THEN all circles within size range found | ✅ Pass |
| AC-02.2 | GIVEN non-circular shapes, WHEN detect runs, THEN shapes with circularity < 0.85 rejected | ✅ Pass |
| AC-02.3 | GIVEN circle at edge, WHEN detect runs, THEN partial circles marked as PARTIAL status | ✅ Pass |

#### US-03: Visual Measurement Display
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-03.1 | GIVEN detected circle, WHEN visualize, THEN edge highlighted with visible color | ✅ Pass |
| AC-03.2 | GIVEN detected circle, WHEN visualize, THEN diameter line drawn through center | ✅ Pass |
| AC-03.3 | GIVEN detected circle, WHEN visualize, THEN label shows "D=X.XXXmm" format | ✅ Pass |

#### US-04: OK/NG Color Indication
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-04.1 | GIVEN tolerance enabled AND diameter in range, WHEN display, THEN show GREEN color | ✅ Pass |
| AC-04.2 | GIVEN tolerance enabled AND diameter out of range, WHEN display, THEN show RED color | ✅ Pass |
| AC-04.3 | GIVEN tolerance disabled, WHEN display, THEN show GRAY color | ✅ Pass |

#### US-05: Easy Camera Connection
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-05.1 | GIVEN cameras available, WHEN refresh clicked, THEN device list updates | ✅ Pass |
| AC-05.2 | GIVEN camera selected, WHEN connect clicked, THEN connection established in < 3 seconds | ✅ Pass |
| AC-05.3 | GIVEN camera connected, WHEN disconnect clicked, THEN camera released properly | ✅ Pass |

#### US-06: Exposure Control
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-06.1 | GIVEN camera connected, WHEN exposure slider moved, THEN camera exposure updates | ✅ Pass |
| AC-06.2 | GIVEN exposure range 10µs-1000ms, WHEN value outside range, THEN clamp to valid range | ✅ Pass |

#### US-07: Tolerance Configuration
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-07.1 | GIVEN tolerance panel, WHEN nominal entered, THEN value stored correctly | ✅ Pass |
| AC-07.2 | GIVEN tolerance panel, WHEN tolerance entered, THEN OK range = nominal ± tolerance | ✅ Pass |
| AC-07.3 | GIVEN tolerance disabled, WHEN measurement taken, THEN no OK/NG judgment | ✅ Pass |

#### US-08: Calibration
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-08.1 | GIVEN calibration dialog, WHEN reference size entered, THEN pixel-to-mm calculated | ✅ Pass |
| AC-08.2 | GIVEN calibration complete, WHEN app restarts, THEN calibration data loaded | ✅ Pass |
| AC-08.3 | GIVEN calibration, WHEN measurement accuracy checked, THEN error < 0.01mm | ✅ Pass |

#### US-09: Recipe Management
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-09.1 | GIVEN recipe dialog, WHEN save clicked, THEN recipe file created in recipes/ | ✅ Pass |
| AC-09.2 | GIVEN saved recipe, WHEN load clicked, THEN all settings applied | ✅ Pass |
| AC-09.3 | GIVEN recipe, WHEN export clicked, THEN JSON file saved to selected path | ✅ Pass |

#### US-10: Statistics Tracking
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-10.1 | GIVEN measurements running, WHEN OK detected, THEN OK count increments | ✅ Pass |
| AC-10.2 | GIVEN statistics panel, WHEN displayed, THEN shows OK rate = OK/(OK+NG)×100% | ✅ Pass |
| AC-10.3 | GIVEN statistics, WHEN reset clicked, THEN all counters reset to zero | ✅ Pass |

#### US-11: Report Export
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-11.1 | GIVEN history data, WHEN export CSV clicked, THEN file with timestamp created | ✅ Pass |
| AC-11.2 | GIVEN CSV file, WHEN opened, THEN contains: time, diameter, status, recipe columns | ✅ Pass |

#### US-12: Web Dashboard Remote Monitoring
| AC ID | Acceptance Criteria | Status |
|-------|---------------------|--------|
| AC-12.1 | GIVEN web server running, WHEN browser accesses http://[ip]:8080, THEN dashboard displays | ✅ Pass |
| AC-12.2 | GIVEN dashboard open, WHEN camera streaming, THEN live video shows at ≥5 FPS | ✅ Pass |
| AC-12.3 | GIVEN dashboard open, WHEN circles detected, THEN results update within 500ms | ✅ Pass |
| AC-12.4 | GIVEN dashboard open, WHEN statistics change, THEN values update every 5 seconds | ✅ Pass |
| AC-12.5 | GIVEN dashboard, WHEN export clicked, THEN CSV downloads to browser | ✅ Pass |
| AC-12.6 | GIVEN multiple browsers connected, WHEN system running, THEN all receive updates | ✅ Pass |

### 3.3 Use Cases

#### UC-01: Kết Nối Camera
```
Actor: Operator
Precondition: Camera đã được kết nối vật lý qua GigE
Flow:
  1. Operator nhấn nút "Refresh Devices"
  2. Hệ thống quét và hiển thị danh sách camera có sẵn
  3. Operator chọn camera từ dropdown
  4. Operator nhấn nút "Connect"
  5. Hệ thống kết nối và bắt đầu hiển thị live stream
Postcondition: Camera connected, live stream hiển thị
Exception:
  - Không tìm thấy camera → Hiển thị thông báo lỗi
  - Kết nối thất bại → Hiển thị chi tiết lỗi
```

#### UC-02: Tự Động Đo Lỗ Tròn
```
Actor: System (Automatic)
Precondition: Camera connected, vật thể trong FOV
Flow:
  1. Trigger sensor phát hiện vật thể đi qua
  2. Camera chụp ảnh
  3. Hệ thống tự động phát hiện tất cả hình tròn
  4. Hệ thống đo đường kính từng lỗ
  5. Hệ thống so sánh với dung sai
  6. Hệ thống hiển thị kết quả (vẽ edge, đường kính, label)
  7. Hệ thống gửi tín hiệu OK/NG ra PLC
Postcondition: Kết quả đo được hiển thị và ghi log
```

#### UC-03: Thay Đổi Dung Sai
```
Actor: Technician
Precondition: Có quyền truy cập cài đặt
Flow:
  1. Technician mở panel "Tolerance Settings"
  2. Technician nhập Nominal diameter (mm)
  3. Technician nhập Tolerance ± (mm)
  4. Technician bật "Enable OK/NG Check"
  5. Hệ thống áp dụng dung sai mới ngay lập tức
Postcondition: Dung sai mới được áp dụng
```

#### UC-04: Calibration
```
Actor: Technician
Precondition: Có mẫu chuẩn với kích thước đã biết
Flow:
  1. Technician đặt mẫu chuẩn vào vùng FOV
  2. Technician nhấn "Calibrate"
  3. Hệ thống đo kích thước mẫu (pixels)
  4. Technician nhập kích thước thực (mm)
  5. Hệ thống tính toán tỷ lệ pixel/mm
  6. Hệ thống lưu thông số calibration
Postcondition: Hệ thống đã được calibrate
```

### 3.3 Sequence Diagram - Quy Trình Đo Tự Động

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Trigger │  │ Camera  │  │ Vision  │  │ Measure │  │ Display │  │   PLC   │
│ Sensor  │  │         │  │ Process │  │ Engine  │  │   UI    │  │         │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │            │            │
     │ Detect     │            │            │            │            │
     │ Object     │            │            │            │            │
     │───────────>│            │            │            │            │
     │            │ Trigger    │            │            │            │
     │            │───────────>│            │            │            │
     │            │            │ Grab Frame │            │            │
     │            │<───────────│            │            │            │
     │            │  Image     │            │            │            │
     │            │───────────>│            │            │            │
     │            │            │ Pre-process│            │            │
     │            │            │───────────>│            │            │
     │            │            │            │ Detect     │            │
     │            │            │            │ Circles    │            │
     │            │            │            │──────┐     │            │
     │            │            │            │      │     │            │
     │            │            │            │<─────┘     │            │
     │            │            │            │ Measure    │            │
     │            │            │            │ Diameter   │            │
     │            │            │            │──────┐     │            │
     │            │            │            │      │     │            │
     │            │            │            │<─────┘     │            │
     │            │            │            │ Results    │            │
     │            │            │            │───────────>│            │
     │            │            │            │            │ Draw       │
     │            │            │            │            │ Overlay    │
     │            │            │            │            │──────┐     │
     │            │            │            │            │      │     │
     │            │            │            │            │<─────┘     │
     │            │            │            │ OK/NG      │            │
     │            │            │            │────────────────────────>│
     │            │            │            │            │            │
```

---

## 4. Yêu Cầu Chức Năng

### 4.1 Chức Năng Chính

#### F01: Thu Nhận Hình Ảnh
- **Mô tả**: Chụp ảnh chi tiết kim loại khi di chuyển qua vùng kiểm tra
- **Yêu cầu**:
  - Trigger từ cảm biến quang (Photoelectric Sensor)
  - Thời gian phơi sáng có thể điều chỉnh: **2000–5000µs** (reflected light)
  - **Reflected coaxial light hoặc ring light chiếu từ trên xuống (Continuous Mode)**
  - Exposure time đủ để thu đủ ánh sáng phản xạ từ bề mặt kim loại

#### F02: Tự Động Phát Hiện Hình Tròn
- **Mô tả**: Tự động phát hiện tất cả các lỗ tròn trên vật thể khi chạy qua camera
- **Yêu cầu**:
  - **Tự động phát hiện** - Không cần định nghĩa trước vị trí ROI
  - Phát hiện **nhiều lỗ tròn** trong một ảnh (số lượng không giới hạn)
  - Phân biệt lỗ tròn với các hình dạng khác (oval, rectangle, noise)
  - Lọc theo kích thước (min/max diameter) để loại bỏ nhiễu
  - Xử lý các trường hợp lỗ bị che khuất một phần (partial occlusion)
  - Hoạt động với các vật thể có vị trí/góc xoay khác nhau trên băng tải

**Thuật toán phát hiện tự động:**
```
1. Threshold/Binarization → Tách vật thể khỏi nền (backlight)
2. Contour Detection    → Tìm tất cả các đường viền
3. Contour Filtering    → Lọc theo diện tích, circularity
4. Circle Fitting       → Fit vòng tròn cho mỗi contour hợp lệ
5. Validation           → Kiểm tra độ tròn (circularity > 0.85)
```

#### F03: Đo Kích Thước Lỗ
- **Mô tả**: Tính toán đường kính lỗ tròn
- **Yêu cầu**:
  - Thuật toán Circle Fitting (Least Squares, Hough Transform)
  - Đo đường kính theo pixel và chuyển đổi sang mm
  - Độ chính xác: ±0.01mm (tùy thuộc calibration)

#### F04: Đánh Giá Chất Lượng
- **Mô tả**: So sánh kết quả đo với dung sai cho phép
- **Yêu cầu**:
  - Thiết lập giá trị Nominal (danh định)
  - Thiết lập dung sai trên/dưới (Upper/Lower Tolerance)
  - Phân loại: OK / NG (Not Good)

#### F05: Xuất Kết Quả
- **Mô tả**: Gửi tín hiệu kết quả ra ngoài
- **Yêu cầu**:
  - Digital I/O cho PLC (OK/NG signal)
  - Lưu log kết quả đo
  - Lưu ảnh NG để truy vết

### 4.2 Chức Năng Phụ Trợ

#### F06: Calibration (Hiệu Chuẩn)
- Calibration tỷ lệ pixel/mm sử dụng mẫu chuẩn
- Lưu trữ và tải thông số calibration
- Hỗ trợ re-calibration định kỳ

#### F07: Quản Lý Recipe
- Lưu/Tải các cấu hình sản phẩm khác nhau
- Chuyển đổi nhanh giữa các loại sản phẩm
- Export/Import recipe

#### F08: Giao Diện Người Dùng (HMI)
- Hiển thị ảnh live từ camera
- Hiển thị kết quả đo thời gian thực
- Cấu hình thông số hệ thống
- Biểu đồ thống kê (SPC Charts)

#### F09: Báo Cáo & Thống Kê
- Thống kê số lượng OK/NG theo ca/ngày
- Xuất báo cáo Excel/PDF
- Tích hợp MES (Manufacturing Execution System)

#### F10: Web Dashboard (Remote Monitoring)
- **Mô tả**: Giao diện web cho phép giám sát từ xa qua trình duyệt
- **Yêu cầu**:
  - Web server chạy background trên port 8080
  - Hiển thị live video stream (MJPEG, 10 FPS)
  - Hiển thị kết quả đo real-time qua WebSocket
  - Hiển thị thống kê sản xuất
  - Hiển thị trạng thái IO/PLC
  - Hỗ trợ nhiều client đồng thời
  - Responsive design cho mobile/tablet
  - Không yêu cầu cài đặt phần mềm (chỉ cần browser)

**Giới hạn:**
- Read-only (chỉ giám sát, không điều khiển)
- Không thay đổi được parameters
- Không thực hiện calibration

---

## 5. Yêu Cầu Phi Chức Năng

### 5.1 Hiệu Năng

| Yêu cầu | Giá trị |
|---------|---------|
| **Thời gian xử lý/ảnh** | < 200ms |
| **Tốc độ băng tải tối đa** | Phụ thuộc FOV và kích thước sản phẩm |
| **Số lượng sản phẩm/phút** | ≥ 20 pcs/min (tùy cấu hình) |
| **Thời gian khởi động** | < 30 giây |

### 5.2 Độ Chính Xác

| Yêu cầu | Giá trị |
|---------|---------|
| **Độ phân giải đo** | 0.01mm |
| **Độ lặp lại (Repeatability)** | ≤ 0.02mm (3σ) |
| **Độ chính xác tuyệt đối** | ≤ ±0.05mm |
| **Gauge R&R** | ≤ 10% |

### 5.3 Độ Tin Cậy

| Yêu cầu | Giá trị |
|---------|---------|
| **Thời gian hoạt động (Uptime)** | ≥ 99.5% |
| **MTBF** | ≥ 10,000 giờ |
| **MTTR** | ≤ 30 phút |
| **Tỷ lệ phát hiện đúng** | ≥ 99.9% |
| **Tỷ lệ báo sai (False Rejection)** | ≤ 0.1% |

### 5.4 Môi Trường Hoạt Động

| Yêu cầu | Giá trị |
|---------|---------|
| **Nhiệt độ** | 0°C ~ 45°C |
| **Độ ẩm** | 20% ~ 80% RH (không ngưng tụ) |
| **Rung động** | Chịu được rung động công nghiệp thông thường |
| **Bụi/Dầu** | Cần vỏ bảo vệ IP65 cho camera và đèn |

### 5.5 Web Dashboard Performance

| Yêu cầu | Giá trị |
|---------|---------|
| **Video Stream FPS** | ≥ 5 FPS (target: 10 FPS) |
| **WebSocket Latency** | < 500ms |
| **Page Load Time** | < 3 giây |
| **Concurrent Clients** | ≥ 5 browsers đồng thời |
| **Browser Support** | Chrome, Edge, Firefox (latest) |
| **Mobile Support** | Responsive design |
| **CPU Overhead** | < 5% thêm khi có web clients |
| **Memory Overhead** | < 100MB thêm cho web server |

---

## 6. Kiến Trúc Hệ Thống

### 6.1 Sơ Đồ Khối Hệ Thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HỆ THỐNG ĐO LỖ TRÒN                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  Trigger │───>│    Camera    │───>│   PC Xử Lý Ảnh          │  │
│  │  Sensor  │    │ acA4600-7gc  │    │  (Vision Controller)     │  │
│  └──────────┘    │ + Telecentric│    │                          │  │
│                  │    Lens      │    │  ┌─────────────────────┐ │  │
│                  └──────────────┘    │  │ Vision Software     │ │  │
│                         │            │  │ - Image Acquisition │ │  │
│                         │            │  │ - Image Processing  │ │  │
│  ┌──────────┐                        │  │ - Measurement       │ │  │
│  │  LED     │  (Continuous Mode)     │  │ - Decision Making   │ │  │
│  │ Backlight│  24V DC Always ON      │  └─────────────────────┘ │  │
│  │ 50×50mm  │                        │            │             │  │
│  └──────────┘                        └────────────┼─────────────┘  │
│                                                   │                │
│                                                   ▼                │
│                                      ┌──────────────────────────┐  │
│                                      │      PLC/SCADA          │  │
│                                      │   (Factory Control)      │  │
│                                      │  - OK/NG Signal          │  │
│                                      │  - Reject Mechanism      │  │
│                                      │  - Production Count      │  │
│                                      └──────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Cấu Hình Phần Cứng

#### A. Hệ Thống Camera
| Thành phần | Model/Specs |
|------------|-------------|
| Camera | Basler acA4600-7gc |
| Lens | HK-YC10-80H Telecentric |
| Mount | C-Mount Adapter |
| Filter | IR Cut Filter (nếu cần) |

#### B. Hệ Thống Chiếu Sáng
| Thành phần | Khuyến nghị |
|------------|-------------|
| Loại đèn | **Coaxial Diffuse LED hoặc Low-angle Ring Light** |
| Hướng chiếu | **Từ trên xuống (reflected light)** — KHÔNG dùng backlight |
| Kích thước ring | Đường kính 150–200mm (phù hợp WD=228mm, góc 30–45°) |
| Màu sắc | White LED hoặc Red LED (620nm) |
| **Chế độ hoạt động** | **Sáng liên tục (Continuous Mode)** |
| Nguồn cấp | 24V DC với Dimmer điều chỉnh độ sáng |
| Bước sóng | Trong dải 420–660nm (theo spec lens) |

**⚠️ LÝ DO KHÔNG DÙNG BACKLIGHT:**
Speed nut / spring nut có cấu trúc:
1. Tấm kim loại phẳng (đặc, không xuyên sáng)
2. Vành boss tròn dập vào tấm — **đây là feature cần đo** (kim loại đặc)
3. Lỗ spring bên trong (irregular butterfly shape) — backlight CHỈ soi được qua đây

Backlight sẽ chiếu qua lỗ spring (hình bất quy tắc), tạo blob sáng không tròn → circularity luôn < 0.5 → không detect được.
Reflected light chiếu lên bề mặt → flat plate = sáng, boss edge = tối → detect được vành tròn cần đo.

**Kết quả mong đợi với reflected coaxial light:**
- Flat plate (bề mặt phẳng phản xạ) → **trắng sáng**
- Thành boss (bề mặt nghiêng) → **xám gradient**
- **Biên ngoài boss = vòng tối rõ nét** trên nền sáng

#### B1. Bố Trí Lắp Đặt (Khoảng Cách)
```
                    ┌─────────────┐
                    │   Camera    │
                    │ acA4600-7gc │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │    Lens     │
                    │ HK-YC10-80H │
                    │  (200.5mm)  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │    Ring Light / Coaxial  │
              │    LED (30–45°)          │
              │    Ø150–200mm            │
              └────────────┬────────────┘
                           │
                      WD = 228mm
                           │
                           ▼
    ════════════════[ VẬT THỂ ]════════════════  ← Băng tải

Tổng chiều cao từ băng tải đến camera: ~430mm
(Không cần backlight — bỏ hẳn)
```

#### C. PC Xử Lý Ảnh
| Thông số | Yêu cầu tối thiểu |
|----------|-------------------|
| CPU | Intel Core i7 hoặc tương đương |
| RAM | 16GB DDR4 |
| Storage | 512GB SSD |
| GPU | Integrated hoặc NVIDIA (cho acceleration) |
| Network | Gigabit Ethernet (GigE) |
| OS | Windows 10/11 Pro 64-bit |

#### D. Phụ Kiện
| Thành phần | Mô tả |
|------------|-------|
| Trigger Sensor | Photoelectric Sensor (NPN/PNP) |
| I/O Card | Digital I/O cho PLC interface |
| Power Supply | 24V DC Industrial |
| Enclosure | IP65 cho camera và đèn |
| Mounting Bracket | Giá đỡ điều chỉnh được |

### 6.3 Cấu Hình Phần Mềm

| Thành phần | Lựa chọn |
|------------|----------|
| Camera SDK | Basler Pylon SDK |
| Vision Library | OpenCV / Halcon / Cognex VisionPro |
| Programming Language | C++ / C# / Python |
| Database | SQLite / SQL Server |
| UI Framework | Qt / WPF / WinForms |

---

## 7. Quy Trình Xử Lý Ảnh - Tự Động Phát Hiện Hình Tròn

### 7.1 Pipeline Xử Lý

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Trigger  │───>│ 2. Acquire  │───>│ 3. Pre-     │───>│ 4. Binary   │
│   (Sensor)  │    │    Image    │    │  Process    │    │  Threshold  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 8. Output   │<───│ 7. Decision │<───│ 6. Measure  │<───│ 5. Auto     │
│   Results   │    │   (OK/NG)   │    │  All Holes  │    │  Detect     │
└─────────────┘    └─────────────┘    └─────────────┘    │  Circles    │
                                                         └─────────────┘
```

### 7.2 Chi Tiết Thuật Toán Tự Động Phát Hiện

```
┌────────────────────────────────────────────────────────────────────────┐
│                    AUTO CIRCLE DETECTION PIPELINE                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐                                                      │
│  │ Input Image  │  (Grayscale from camera)                             │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Gaussian     │  Kernel: 5×5, σ=1.5                                  │
│  │ Blur         │  → Giảm nhiễu                                        │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Binary       │  Otsu's Method (otsu / otsu_inv / adaptive)          │
│  │ Threshold    │  • otsu_inv (mặc định): Flat plate = Trắng,          │
│  │              │    Boss/lỗ tối = Đen → Invert → Boss = Trắng         │
│  │              │  • otsu: Backlit silhouette (lỗ sáng trên nền tối)   │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Find         │  cv2.findContours()                                  │
│  │ Contours     │  → Tìm tất cả đường viền kín                         │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐  Điều kiện lọc:                                      │
│  │ Filter       │  • Area: min_area < A < max_area                     │
│  │ Contours     │  • Circularity: 4π×Area/Perimeter² > 0.85            │
│  │              │  • Không chạm biên ảnh                               │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Fit Circle   │  cv2.minEnclosingCircle() hoặc                       │
│  │ (Each)       │  Least Squares Circle Fit                            │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Sub-pixel    │  Edge refinement cho độ chính xác cao                │
│  │ Refinement   │  → Độ chính xác ~0.1 pixel                           │
│  └──────┬───────┘                                                      │
│         │                                                              │
│         ▼                                                              │
│  ┌──────────────┐                                                      │
│  │ Output List  │  [(x1,y1,d1), (x2,y2,d2), ...]                       │
│  │ of Circles   │  → Tọa độ tâm + đường kính (mm)                      │
│  └──────────────┘                                                      │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Tham Số Cấu Hình Phát Hiện Tự Động

| Tham số | Mô tả | Giá trị hiện tại | Phạm vi |
|---------|-------|------------------|---------|
| `min_diameter_mm` | Đường kính tối thiểu (mm) | **5.0** | 1.0 ~ 50 |
| `max_diameter_mm` | Đường kính tối đa (mm) | **25.0** | 5.0 ~ 80 |
| `min_circularity` | Độ tròn tối thiểu | **0.75** | 0.5 ~ 1.0 |
| `blur_kernel` | Kích thước kernel blur | **11** | 3, 5, 7, 11, 15 |
| `threshold_method` | Phương pháp threshold | **otsu_inv** | otsu / otsu_inv / adaptive |
| `morph_close_kernel` | Kernel morphological closing (px) | **5** | 0 (tắt) ~ 21 |
| `edge_margin` | Khoảng cách tối thiểu từ biên ảnh (px) | 10 | 5 ~ 50 |

**Giải thích threshold_method:**
| Giá trị | Khi dùng |
|---------|----------|
| `otsu_inv` | **Mặc định** — Reflected coaxial/ring light. Boss tối trên nền sáng. |
| `otsu` | Backlit — Lỗ thông sáng trên nền tối (không áp dụng cho speed nut). |
| `adaptive` | Ánh sáng không đều trên FOV. |

### 7.4 Công Thức Tính Circularity (Độ Tròn)

```
Circularity = 4π × Area / Perimeter²

Trong đó:
- Area = Diện tích contour (pixels²)
- Perimeter = Chu vi contour (pixels)

Giá trị:
- Hình tròn hoàn hảo: Circularity = 1.0
- Hình vuông: Circularity ≈ 0.785
- Hình elip: Circularity < 1.0 (phụ thuộc tỷ lệ)

➜ Ngưỡng khuyến nghị: Circularity ≥ 0.85 để xác định là hình tròn
```

### 7.5 Xử Lý Các Trường Hợp Đặc Biệt

| Trường hợp | Xử lý |
|------------|-------|
| Lỗ chạm biên ảnh | Bỏ qua (không đo được chính xác) |
| Lỗ bị che một phần | Fit circle từ phần visible, đánh dấu "partial" |
| Nhiều lỗ chồng lên nhau | Watershed segmentation hoặc bỏ qua |
| Lỗ quá nhỏ (< min_diameter) | Lọc bỏ, coi là nhiễu |
| Lỗ quá lớn (> max_diameter) | Lọc bỏ, có thể là outline vật thể |
| Hình không tròn | Lọc bỏ dựa trên circularity < 0.85 |

### 7.6 Output Cho Mỗi Lỗ Phát Hiện

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `hole_id` | int | ID của lỗ trong ảnh (1, 2, 3...) |
| `center_x` | float | Tọa độ X tâm lỗ (mm) |
| `center_y` | float | Tọa độ Y tâm lỗ (mm) |
| `diameter` | float | Đường kính lỗ (mm) |
| `circularity` | float | Độ tròn (0~1) |
| `area` | float | Diện tích (mm²) |
| `status` | enum | OK / NG / PARTIAL |
| `confidence` | float | Độ tin cậy phát hiện (0~1) |

---

## 8. Tính Toán Hệ Thống

### 8.1 Tính Toán FOV và Độ Phân Giải

**Thông số đầu vào:**
- Camera: Basler acA4600-7gc (4608 × 3288 pixels, sensor 1/2.3")
- Lens: HK-YC10-80H (Magnification = 0.208x)
- Kích thước lỗ cần đo: 0.5mm ~ 20mm
- Dung sai đo yêu cầu: ±0.05mm

**Tính toán FOV thực tế:**

```
Sensor Size: 6.17mm × 4.55mm (1/2.3")
Magnification: 0.208x

FOV = Sensor Size / Magnification
├── FOV Width  = 6.17mm / 0.208 = 29.66mm ≈ 29.7mm
└── FOV Height = 4.55mm / 0.208 = 21.88mm ≈ 21.9mm

➜ FOV thực tế: 29.7mm × 21.9mm
```

**Tính toán độ phân giải pixel:**

```
Camera Resolution: 4608 × 3288 pixels
FOV: 29.7mm × 21.9mm

Pixel Resolution:
├── Horizontal = 29.7mm / 4608px = 0.00644 mm/pixel = 6.44 µm/pixel
└── Vertical   = 21.9mm / 3288px = 0.00666 mm/pixel = 6.66 µm/pixel

➜ Độ phân giải: ~6.5 µm/pixel
```

**Đánh giá độ chính xác đo:**

```
Với Sub-pixel Edge Detection (độ chính xác 0.1 pixel):
- Độ chính xác lý thuyết = 6.5 µm × 0.1 = 0.65 µm

Với 1 pixel accuracy:
- Sai số = 6.5 µm = 0.0065mm

Để đạt ±0.05mm với 3σ:
- Cần: 0.05mm / 6.5µm = 7.7 pixels
- Với Sub-pixel: 0.05mm / 0.65µm = 77 sub-pixels ✓

➜ KẾT LUẬN: Hệ thống ĐẠT YÊU CẦU độ chính xác ±0.05mm
```

**Kiểm tra kích thước lỗ:**

```
FOV: 29.7mm × 21.9mm
Kích thước lỗ tối đa có thể đo: ~20mm (để có margin)
Kích thước lỗ tối thiểu: ~0.5mm (cần ~77 pixels với sub-pixel)

➜ Phù hợp đo lỗ từ 0.5mm đến 20mm
```

### 8.2 Tính Toán Tốc Độ Xử Lý

```
Camera Frame Rate: 7 fps @ Full Resolution
Processing Time: ~150ms/frame
Total Cycle Time: ~143ms + 150ms ≈ 300ms/product

Throughput: 60s / 0.3s = 200 pcs/min (max theoretical)
Practical Throughput: ~100-150 pcs/min (với margin an toàn)
```

### 8.3 Tính Toán Băng Tải

```
Nếu kích thước sản phẩm: 50mm
Khoảng cách giữa sản phẩm: 50mm
Tổng khoảng cách: 100mm/product

Với throughput 100 pcs/min:
Tốc độ băng tải = 100 × 100mm/min = 10,000 mm/min = 10 m/min
```

---

## 9. Tiêu Chuẩn Nghiệm Thu

### 9.1 Factory Acceptance Test (FAT)

| Test ID | Mô tả | Tiêu chí đạt |
|---------|-------|--------------|
| FAT-01 | Kiểm tra kết nối camera | Ảnh sống hiển thị ổn định |
| FAT-02 | Calibration độ chính xác | Sai số ≤ 0.5% so với mẫu chuẩn |
| FAT-03 | Đo 100 mẫu chuẩn | Repeatability ≤ 0.02mm |
| FAT-04 | Kiểm tra False Rejection | ≤ 0.1% trên 1000 mẫu |
| FAT-05 | Kiểm tra Detection Rate | ≥ 99.9% phát hiện NG |

### 9.2 Site Acceptance Test (SAT)

| Test ID | Mô tả | Tiêu chí đạt |
|---------|-------|--------------|
| SAT-01 | Hoạt động với băng tải thực | Không miss trigger |
| SAT-02 | Tích hợp PLC | Tín hiệu OK/NG chính xác |
| SAT-03 | Chạy liên tục 8 giờ | Không lỗi, không treo |
| SAT-04 | Gauge R&R Study | ≤ 10% |
| SAT-05 | Training nhân viên | Vận hành độc lập |

---

## 10. Rủi Ro và Giải Pháp

| Rủi Ro | Mức độ | Giải pháp |
|--------|--------|-----------|
| Phản xạ bề mặt kim loại | Cao | Sử dụng Backlight + Polarizer |
| Chiếu sáng sai loại (backlight cho solid part) | Cao | **Dùng reflected coaxial/ring light; backlight chỉ cho lỗ thông** |
| Overexposure với reflected light | Trung bình | Giảm exposure xuống 2000–5000µs; dùng dimmer |
| Motion blur (với continuous light) | Trung bình | Giảm exposure time ≤50µs, hoặc nâng cấp Strobe |
| Rung động băng tải | Trung bình | Giảm exposure time, cố định camera chắc chắn |
| Bụi bám lens | Trung bình | Vỏ bảo vệ IP65 + Air purge |
| Thay đổi nhiệt độ | Thấp | Re-calibration định kỳ |
| Lỗ không tròn hoàn hảo | Trung bình | Thuật toán Ellipse Fitting bổ sung |
| Nhiều loại sản phẩm | Trung bình | Hệ thống Recipe management |
| LED backlight giảm độ sáng | Thấp | Kiểm tra định kỳ, có LED dự phòng |

---

## 11. Sprint Plan & Release Roadmap

### 11.1 Tổng Quan Release

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RELEASE ROADMAP                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   MVP 1.0   │──►│ Release 1.1 │──►│ Release 1.2 │──►│ Release 2.0 │     │
│  │  Sprint 1-2 │   │  Sprint 3-4 │   │  Sprint 5   │   │  Sprint 6-7 │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│        │                 │                 │                 │              │
│        ▼                 ▼                 ▼                 ▼              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐         │
│  │ Camera    │    │ Calibrate │    │ Recipe    │    │ PLC/IO    │         │
│  │ + Detect  │    │ + Tolerance│   │ + Reports │    │ + Full    │         │
│  │ + Display │    │ + History │    │ + Export  │    │ Production│         │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 MVP 1.0 - Core Functionality (Sprint 1-2)

**Mục tiêu:** Hệ thống cơ bản hoạt động được, demo cho stakeholders

#### Sprint 1: Camera & Live View

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S1-01 | Project setup (structure, dependencies) | High | 2 |
| S1-02 | Camera Service - connect/disconnect | High | 5 |
| S1-03 | Camera Service - grab frame | High | 3 |
| S1-04 | Main Window UI layout (Tkinter) | High | 5 |
| S1-05 | Video Canvas - live display | High | 5 |
| S1-06 | Camera Panel - device list, buttons | High | 3 |
| S1-07 | Basic error handling | Medium | 3 |
| **Total** | | | **26 SP** |

**Deliverables Sprint 1:**
- [x] Kết nối camera Basler qua GigE
- [x] Hiển thị live stream
- [x] Nút Connect/Disconnect hoạt động
- [x] Chọn camera từ danh sách

#### Sprint 2: Circle Detection & Visualization

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S2-01 | Circle Detector - preprocessing | High | 3 |
| S2-02 | Circle Detector - contour detection | High | 5 |
| S2-03 | Circle Detector - circularity filter | High | 3 |
| S2-04 | Circle Detector - measurement calc | High | 5 |
| S2-05 | Visualizer - draw edge | High | 3 |
| S2-06 | Visualizer - draw diameter line | Medium | 2 |
| S2-07 | Visualizer - draw label | Medium | 3 |
| S2-08 | Control Panel - detection params | Medium | 3 |
| S2-09 | Results Panel - basic display | Medium | 3 |
| **Total** | | | **30 SP** |

**Deliverables Sprint 2 (MVP 1.0):**
- [x] Tự động phát hiện hình tròn
- [x] Hiển thị edge detection overlay
- [x] Hiển thị đường kính + label
- [x] Điều chỉnh tham số detection cơ bản

```
MVP 1.0 Features:
✅ Camera GigE connection
✅ Live streaming
✅ Auto circle detection
✅ Diameter measurement display
✅ Basic parameter adjustment
```

---

### 11.3 Release 1.1 - Measurement Quality (Sprint 3-4)

**Mục tiêu:** Đo lường chính xác, có thể dùng cho testing

#### Sprint 3: Calibration & Tolerance

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S3-01 | Calibration Service | High | 5 |
| S3-02 | Calibration Dialog UI | High | 5 |
| S3-03 | Pixel-to-mm conversion accurate | High | 3 |
| S3-04 | Tolerance Config model | High | 3 |
| S3-05 | Tolerance checking logic | High | 3 |
| S3-06 | OK/NG color display (green/red) | High | 2 |
| S3-07 | Exposure time control | Medium | 3 |
| S3-08 | Save/Load calibration data | Medium | 3 |
| **Total** | | | **27 SP** |

#### Sprint 4: History & Threading

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S4-01 | Threading - Camera thread | High | 5 |
| S4-02 | Threading - Processing thread | High | 5 |
| S4-03 | Queue-based communication | High | 3 |
| S4-04 | Measurement history list | Medium | 3 |
| S4-05 | History Panel UI | Medium | 3 |
| S4-06 | Clear history function | Low | 1 |
| S4-07 | Performance optimization | Medium | 5 |
| S4-08 | Unit tests - Detector | Medium | 3 |
| **Total** | | | **28 SP** |

**Deliverables Release 1.1:**
- [x] Calibration với mẫu chuẩn
- [x] Kiểm tra dung sai OK/NG
- [x] Lưu lịch sử đo
- [x] Multi-threading ổn định
- [x] Điều chỉnh exposure time

```
Release 1.1 Features:
✅ Everything in MVP 1.0
✅ Calibration system
✅ Tolerance checking (OK/NG)
✅ Measurement history
✅ Multi-threaded processing
✅ Exposure control
```

---

### 11.4 Release 1.2 - Production Ready (Sprint 5)

**Mục tiêu:** Sẵn sàng cho môi trường sản xuất (không có PLC)

#### Sprint 5: Recipe & Reporting

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S5-01 | Recipe model & service | High | 5 |
| S5-02 | Recipe Dialog - save/load | High | 5 |
| S5-03 | Recipe selection dropdown | High | 3 |
| S5-04 | Statistics calculation | Medium | 3 |
| S5-05 | Statistics Panel UI | Medium | 3 |
| S5-06 | Export to CSV | Medium | 3 |
| S5-07 | Log file system | Medium | 3 |
| S5-08 | NG image saving | Medium | 3 |
| S5-09 | Configuration file (JSON) | Medium | 2 |
| **Total** | | | **30 SP** |

**Deliverables Release 1.2:**
- [x] Recipe management (save/load/switch)
- [x] Thống kê OK/NG
- [x] Export CSV report
- [x] Lưu ảnh NG
- [x] Logging system

```
Release 1.2 Features:
✅ Everything in Release 1.1
✅ Recipe management
✅ Statistics display
✅ CSV export
✅ NG image archive
✅ Comprehensive logging
```

---

### 11.5 Release 2.0 - Full Production (Sprint 6-7) 🎯

**Mục tiêu:** Tích hợp PLC, sẵn sàng triển khai nhà máy

#### Sprint 6: PLC/IO Integration

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S6-01 | IO Service - NI-DAQmx driver | High | 8 |
| S6-02 | IO Configuration model | High | 3 |
| S6-03 | Digital Input reading | High | 3 |
| S6-04 | Digital Output control | High | 3 |
| S6-05 | Trigger signal handling | High | 5 |
| S6-06 | OK/NG output signals | High | 3 |
| S6-07 | IO Thread implementation | High | 5 |
| S6-08 | IO Panel UI | Medium | 3 |
| S6-09 | IO status indicators | Medium | 2 |
| **Total** | | | **35 SP** |

#### Sprint 7: Integration & Testing

| ID | Task | Priority | Story Points |
|----|------|----------|--------------|
| S7-01 | Hardware trigger mode | High | 5 |
| S7-02 | Full system integration | High | 5 |
| S7-03 | Error recovery mechanisms | High | 5 |
| S7-04 | Integration tests | High | 5 |
| S7-05 | Performance testing | Medium | 3 |
| S7-06 | Documentation update | Medium | 3 |
| S7-07 | FAT preparation | Medium | 3 |
| S7-08 | Bug fixes & polish | Medium | 5 |
| **Total** | | | **34 SP** |

**Deliverables Release 2.0:**
- [x] PLC Digital I/O interface
- [x] External trigger support
- [x] OK/NG signal output
- [x] System Ready/Error signals
- [x] Full production mode

```
Release 2.0 Features (FINAL):
✅ Everything in Release 1.2
✅ PLC/IO integration
✅ Hardware trigger mode
✅ Digital output signals (OK/NG/Ready/Error)
✅ Recipe selection via DI
✅ Production-ready reliability
```

---

### 11.6 Sprint Summary

| Sprint | Release | Focus | Story Points | Status |
|--------|---------|-------|--------------|--------|
| Sprint 1 | MVP 1.0 | Camera & Live View | 26 | ✅ Done |
| Sprint 2 | MVP 1.0 | Detection & Display | 30 | ✅ Done |
| Sprint 3 | Release 1.1 | Calibration & Tolerance | 27 | ✅ Done |
| Sprint 4 | Release 1.1 | Threading & History | 28 | ✅ Done |
| Sprint 5 | Release 1.2 | Recipe & Reporting | 30 | ✅ Done |
| Sprint 6 | Release 2.0 | PLC/IO Integration | 35 | ✅ Done |
| Sprint 7 | Release 2.0 | Integration & Testing | 34 | ✅ Done |
| Sprint 8 | Release 2.0 | Documentation & CI/CD | 15 | ✅ Done |
| Sprint 9 | Release 2.1 | Web Dashboard Backend | 30 | ✅ Done |
| Sprint 10 | Release 2.1 | Web Dashboard Frontend | 25 | ✅ Done |
| **Total** | | | **280 SP** |

### 11.7 Feature Matrix by Release

| Feature | MVP 1.0 | Rel 1.1 | Rel 1.2 | Rel 2.0 | Rel 2.1 |
|---------|:-------:|:-------:|:-------:|:-------:|:-------:|
| Camera Connection | ✅ | ✅ | ✅ | ✅ | ✅ |
| Live Streaming | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auto Circle Detection | ✅ | ✅ | ✅ | ✅ | ✅ |
| Diameter Display | ✅ | ✅ | ✅ | ✅ | ✅ |
| Calibration | ❌ | ✅ | ✅ | ✅ | ✅ |
| Tolerance Check | ❌ | ✅ | ✅ | ✅ | ✅ |
| Multi-threading | ❌ | ✅ | ✅ | ✅ | ✅ |
| Measurement History | ❌ | ✅ | ✅ | ✅ | ✅ |
| Recipe Management | ❌ | ❌ | ✅ | ✅ | ✅ |
| Statistics | ❌ | ❌ | ✅ | ✅ | ✅ |
| CSV Export | ❌ | ❌ | ✅ | ✅ | ✅ |
| NG Image Save | ❌ | ❌ | ✅ | ✅ | ✅ |
| PLC/IO Interface | ❌ | ❌ | ❌ | ✅ | ✅ |
| Hardware Trigger | ❌ | ❌ | ❌ | ✅ | ✅ |
| OK/NG Signals | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Web Dashboard** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Live Video Stream (Web)** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **WebSocket Updates** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Remote Monitoring** | ❌ | ❌ | ❌ | ❌ | ✅ |

### 11.8 Risk per Sprint

| Sprint | Risk Level | Main Risks | Mitigation |
|--------|------------|------------|------------|
| Sprint 1 | 🟢 Low | Camera driver issues | Test với Pylon Viewer trước |
| Sprint 2 | 🟡 Medium | Detection accuracy | Tune parameters, test images |
| Sprint 3 | 🟡 Medium | Calibration precision | Sử dụng mẫu chuẩn certified |
| Sprint 4 | 🟡 Medium | Threading bugs | Careful queue management |
| Sprint 5 | 🟢 Low | Standard features | Well-defined requirements |
| Sprint 6 | 🔴 High | Hardware compatibility | Test I/O card sớm |
| Sprint 7 | 🟡 Medium | Integration issues | Thorough testing |

---

## 12. Deliverables

1. **Phần cứng**
   - Hệ thống camera hoàn chỉnh
   - Hệ thống chiếu sáng
   - PC công nghiệp
   - Tủ điện điều khiển

2. **Phần mềm**
   - Phần mềm Vision chính
   - Tài liệu Source code
   - Hướng dẫn sử dụng

3. **Tài liệu**
   - Bản vẽ lắp đặt
   - Sơ đồ điện
   - Hướng dẫn vận hành
   - Hướng dẫn bảo trì
   - Báo cáo FAT/SAT

4. **Đào tạo**
   - Đào tạo vận hành
   - Đào tạo bảo trì cơ bản

---

## 13. Phụ Lục

### A. Tham Khảo Thông Số Camera

**Nguồn:** [Basler acA4600-7gc Official Page](https://www.baslerweb.com/en/products/cameras/area-scan-cameras/ace/aca4600-7gc/)

### B. Tiêu Chuẩn Áp Dụng

- ISO 9001:2015 - Quality Management
- IEC 61131 - PLC Programming
- GigE Vision Standard
- GenICam Standard

### C. Từ Viết Tắt

| Từ viết tắt | Ý nghĩa |
|-------------|---------|
| FOV | Field of View |
| DOF | Depth of Field |
| WD | Working Distance |
| NG | Not Good |
| PLC | Programmable Logic Controller |
| HMI | Human Machine Interface |
| SPC | Statistical Process Control |
| FAT | Factory Acceptance Test |
| SAT | Site Acceptance Test |
| MTBF | Mean Time Between Failures |
| MTTR | Mean Time To Repair |

---

## 14. Lưu Ý Kỹ Thuật Quan Trọng

### 14.1 Khuyến Nghị Về Cảm Biến Camera

⚠️ **LƯU Ý:** Ống kính HK-YC10-80H được thiết kế tối ưu cho cảm biến 1" (φ16.6mm). Camera Basler acA4600-7gc sử dụng cảm biến 1/2.3" (φ7.7mm) nhỏ hơn nhiều.

**Ưu điểm khi dùng cảm biến nhỏ hơn:**
- Chỉ sử dụng vùng trung tâm của lens (chất lượng quang học tốt nhất)
- Độ méo thấp hơn (vùng trung tâm có distortion thấp nhất)

**Nhược điểm:**
- Không tận dụng hết FOV tối đa của lens (80mm → chỉ dùng 29.7mm)
- Nếu cần FOV lớn hơn, cân nhắc camera với cảm biến 1" (ví dụ: Basler acA4112-30um)

### 14.2 Độ Sâu Trường Ảnh (DoF)

```
DoF của lens: ±14.8mm @F16

Với F/6.5 (mặc định):
- DoF ước tính: ±14.8 × (6.5/16)² ≈ ±2.4mm

➜ Vật thể cần nằm trong khoảng ±2.4mm quanh mặt phẳng tiêu cự
```

### 14.4 Phân Tích Vật Thể & Lựa Chọn Chiếu Sáng

#### Cấu Trúc Speed Nut / Spring Nut
```
┌─────────────────────────────────────────┐
│  Flat plate (zinc-plated ~22×16mm)      │
│    ┌───────────────┐                    │
│    │  Drawn boss   │  ← Feature cần đo  │
│    │  (circular)   │    Ø ~8–15mm        │
│    │  ┌─────────┐  │                    │
│    │  │ Spring  │  │                    │
│    │  │ opening │  │  ← Butterfly shape │
│    │  │(không   │  │    (KHÔNG phải     │
│    │  │ tròn)   │  │     lỗ cần đo)     │
│    │  └─────────┘  │                    │
│    └───────────────┘                    │
└─────────────────────────────────────────┘
```

#### Tại Sao Backlight Không Hoạt Động
- Backlight chiếu từ dưới lên → ánh sáng chỉ xuyên qua **lỗ spring** (hình butterfly)
- Boss tròn cần đo là **kim loại đặc** → không xuyên sáng
- Kết quả: Otsu binary chỉ thấy blob butterfly không tròn → circularity ~0.3–0.5 → reject

#### Tại Sao Reflected Light Hoạt Động
- Reflected light từ trên → **flat plate** phản xạ mạnh (sáng)
- **Boss edge** (bề mặt nghiêng ~90°) phản xạ yếu → tối
- Binary (otsu_inv): Boss interior = white (foreground), plate = black
- `RETR_EXTERNAL` tìm contour của boss = **đường tròn cần đo** ✓

#### Camera Settings Theo Loại Ánh Sáng
| Chế độ | Exposure | Gain | Gamma | Ghi chú |
|--------|----------|------|-------|---------|
| Reflected coaxial | 2000–5000µs | 0dB | 0.8–1.0 | Tăng dần đến khi boss rõ |
| Ring light 45° | 1000–3000µs | 0dB | 1.0 | Tuỳ cường độ đèn |
| Backlit (KHÔNG dùng) | 50µs | 0dB | 1.0 | Chỉ dùng nếu part có lỗ thông sáng |

### 14.3 Checklist Trước Khi Triển Khai

**Phần cứng:**
- [ ] Đèn reflected coaxial hoặc ring light đã lắp đặt (KHÔNG dùng backlight)
- [ ] WD = 228mm tính từ mặt trước lens đến bề mặt part
- [ ] Ring light đặt góc 30–45° từ ngang, đường kính ~150–200mm
- [ ] Kiểm tra kích thước boss thực tế nằm trong FOV (29.7×21.9mm)
- [ ] Độ dày part < DoF (±2.4mm @ F/6.5, ±14.8mm @ F/16)
- [ ] Bề mặt part vuông góc với trục quang (±1°)

**Phần mềm:**
- [ ] `threshold_method = "otsu_inv"` (reflected light)
- [ ] `blur_kernel = 11` (phù hợp camera 14MP)
- [ ] `morph_close_kernel = 5`
- [ ] `min_circularity = 0.75` (tinh chỉnh sau khi có ảnh thực)
- [ ] Calibration với mẫu chuẩn đã biết kích thước
- [ ] Exposure: bắt đầu 2000µs, chỉnh đến khi boss edge rõ nét

**Validation:**
- [ ] Log hiển thị `Detected 1 circle(s)` với circularity > 0.75
- [ ] Đường kính đo được xấp xỉ kích thước boss đã biết
- [ ] Repeatability: đo 10 lần cùng 1 part, std dev < 0.02mm

---

## 15. Error Codes

Bảng mã lỗi chuẩn hóa cho hệ thống.

### 15.1 Camera Errors (E1xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E100 | CAMERA_NOT_FOUND | Không tìm thấy camera | Kiểm tra kết nối cable, cài driver Pylon |
| E101 | CAMERA_CONNECTION_FAILED | Kết nối camera thất bại | Kiểm tra IP, firewall, camera đã được dùng bởi app khác |
| E102 | CAMERA_GRAB_FAILED | Grab frame thất bại | Kiểm tra exposure, trigger mode |
| E103 | CAMERA_TIMEOUT | Timeout khi grab | Giảm exposure hoặc tăng timeout |
| E104 | CAMERA_ALREADY_CONNECTED | Camera đã kết nối | Disconnect trước khi connect lại |
| E105 | CAMERA_NOT_CONNECTED | Camera chưa kết nối | Connect camera trước |

### 15.2 Detection Errors (E2xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E200 | DETECTION_NO_CIRCLES | Không phát hiện circle | Điều chỉnh threshold, kiểm tra ánh sáng |
| E201 | DETECTION_INVALID_IMAGE | Ảnh không hợp lệ | Kiểm tra camera output format |
| E202 | DETECTION_CONFIG_INVALID | Config không hợp lệ | Kiểm tra parameters (min < max, etc.) |
| E203 | DETECTION_PARTIAL_CIRCLE | Circle bị cắt tại biên | Di chuyển vật hoặc mở rộng FOV |

### 15.3 Calibration Errors (E3xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E300 | CALIBRATION_INVALID_REFERENCE | Reference size không hợp lệ | Nhập giá trị > 0 |
| E301 | CALIBRATION_NO_CIRCLE_FOUND | Không tìm thấy circle để calibrate | Đặt mẫu chuẩn đúng vị trí, điều chỉnh ánh sáng |
| E302 | CALIBRATION_FILE_ERROR | Lỗi đọc/ghi file calibration | Kiểm tra quyền file/folder |
| E303 | CALIBRATION_EXPIRED | Calibration quá hạn | Re-calibrate (khuyến nghị < 7 ngày) |

### 15.4 Recipe Errors (E4xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E400 | RECIPE_NOT_FOUND | Recipe không tồn tại | Kiểm tra tên recipe, đường dẫn |
| E401 | RECIPE_INVALID_FORMAT | Format file không đúng | Kiểm tra JSON syntax |
| E402 | RECIPE_SAVE_FAILED | Lưu recipe thất bại | Kiểm tra quyền thư mục recipes/ |
| E403 | RECIPE_NAME_EXISTS | Tên recipe đã tồn tại | Đổi tên khác hoặc overwrite |
| E404 | RECIPE_IMPORT_FAILED | Import recipe thất bại | Kiểm tra file format, version |

### 15.5 IO/PLC Errors (E5xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E500 | IO_DEVICE_NOT_FOUND | Không tìm thấy IO device | Kiểm tra kết nối, cài driver |
| E501 | IO_CONNECTION_FAILED | Kết nối IO thất bại | Kiểm tra device name, port |
| E502 | IO_READ_ERROR | Lỗi đọc input | Kiểm tra wiring, signal level |
| E503 | IO_WRITE_ERROR | Lỗi ghi output | Kiểm tra wiring, load |
| E504 | IO_DRIVER_NOT_INSTALLED | Driver chưa cài | Cài NI-DAQmx hoặc Advantech driver |
| E505 | IO_TRIGGER_TIMEOUT | Timeout chờ trigger | Kiểm tra sensor, PLC program |

### 15.6 System Errors (E9xx)

| Code | Name | Description | Resolution |
|------|------|-------------|------------|
| E900 | SYSTEM_MEMORY_LOW | Bộ nhớ thấp | Đóng ứng dụng khác, tăng RAM |
| E901 | SYSTEM_DISK_FULL | Đĩa đầy | Xóa logs/images cũ |
| E902 | SYSTEM_THREAD_ERROR | Lỗi thread | Restart ứng dụng |
| E903 | SYSTEM_CONFIG_ERROR | Lỗi config file | Kiểm tra JSON syntax |

---

**Document Version:** 2.6
**Created Date:** 2025-12-26
**Last Updated:** 2026-06-12
**Author:** Development Team
**Status:** Approved

---

**Revision History:**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-26 | Initial draft |
| 1.1 | 2025-12-26 | Updated with confirmed HK-YC10-80H lens specifications from datasheet |
| 1.2 | 2025-12-26 | Changed lighting mode to Continuous (non-strobe), added motion blur calculations |
| 1.3 | 2025-12-26 | Added automatic circle detection algorithm, detailed processing pipeline |
| 2.0 | 2025-12-26 | Added User Stories, Use Cases, Sequence Diagram - PRD Complete |
| 2.1 | 2025-12-26 | Fixed section numbering (Section 4 duplicate), unified FOV range (0.5mm~20mm) |
| 2.2 | 2025-12-26 | Added Sprint Plan & Release Roadmap (MVP → Release 2.0 with PLC) |
| 2.3 | 2025-12-27 | Added Acceptance Criteria, Sprint Status, Error Codes |
| 2.4 | 2025-12-27 | Added US-12 Web Dashboard, F10 Web Dashboard, NFR 5.5 Web Performance, Sprint 9-10 |
| 2.5 | 2026-06-12 | Synced status with code: Sprint 9-10 (Web Dashboard) ✅ Done, US-12 AC-12.1~12.6 ✅ Pass (Release 2.1 implemented) |
| 2.6 | 2026-06-12 | Cập nhật hệ thống chiếu sáng: backlight → reflected coaxial/ring light sau khi phân tích cấu trúc speed nut. Thêm section 14.4 phân tích vật thể. Cập nhật tham số detection (otsu_inv, blur_kernel=11, morph_close_kernel=5, min_circularity=0.75). |
