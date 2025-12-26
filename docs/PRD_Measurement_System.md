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
| Loại sản phẩm | Chi tiết kim loại có lỗ tròn |
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

### 3.2 Use Cases

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
  - Thời gian phơi sáng có thể điều chỉnh (Exposure Time)
  - Backlight sáng liên tục (Continuous Lighting)
  - Exposure time ngắn để tránh motion blur (khuyến nghị ≤50µs @10m/min)

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

---

## 4. Yêu Cầu Phi Chức Năng

### 4.1 Hiệu Năng

| Yêu cầu | Giá trị |
|---------|---------|
| **Thời gian xử lý/ảnh** | < 200ms |
| **Tốc độ băng tải tối đa** | Phụ thuộc FOV và kích thước sản phẩm |
| **Số lượng sản phẩm/phút** | ≥ 20 pcs/min (tùy cấu hình) |
| **Thời gian khởi động** | < 30 giây |

### 4.2 Độ Chính Xác

| Yêu cầu | Giá trị |
|---------|---------|
| **Độ phân giải đo** | 0.01mm |
| **Độ lặp lại (Repeatability)** | ≤ 0.02mm (3σ) |
| **Độ chính xác tuyệt đối** | ≤ ±0.05mm |
| **Gauge R&R** | ≤ 10% |

### 4.3 Độ Tin Cậy

| Yêu cầu | Giá trị |
|---------|---------|
| **Thời gian hoạt động (Uptime)** | ≥ 99.5% |
| **MTBF** | ≥ 10,000 giờ |
| **MTTR** | ≤ 30 phút |
| **Tỷ lệ phát hiện đúng** | ≥ 99.9% |
| **Tỷ lệ báo sai (False Rejection)** | ≤ 0.1% |

### 4.4 Môi Trường Hoạt Động

| Yêu cầu | Giá trị |
|---------|---------|
| **Nhiệt độ** | 0°C ~ 45°C |
| **Độ ẩm** | 20% ~ 80% RH (không ngưng tụ) |
| **Rung động** | Chịu được rung động công nghiệp thông thường |
| **Bụi/Dầu** | Cần vỏ bảo vệ IP65 cho camera và đèn |

---

## 5. Kiến Trúc Hệ Thống

### 5.1 Sơ Đồ Khối Hệ Thống

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

### 5.2 Cấu Hình Phần Cứng

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
| Loại đèn | LED Backlight (chiếu ngược) |
| Kích thước | 50mm × 50mm (lớn hơn FOV 29.7×21.9mm) |
| Màu sắc | Red LED (620nm) hoặc Green LED (520nm) |
| **Chế độ hoạt động** | **Sáng liên tục (Continuous Mode)** |
| Nguồn cấp | 24V DC với Dimmer điều chỉnh độ sáng |
| Bước sóng | Trong dải 420~660nm (theo spec lens) |
| Lý do | Backlight tạo silhouette rõ nét cho đo lường |

**Lưu ý chế độ sáng liên tục:**
| Ưu điểm | Nhược điểm |
|---------|------------|
| Đơn giản, không cần đồng bộ trigger | Cần giảm exposure time để tránh motion blur |
| Chi phí thấp hơn (không cần strobe controller) | Tiêu thụ điện liên tục |
| Dễ cài đặt và bảo trì | Tuổi thọ LED có thể ngắn hơn |
| Phù hợp cho tốc độ băng tải thấp-trung bình | Nếu cần tốc độ cao, nâng cấp lên Strobe |

**Tính toán Exposure Time tối đa (tránh motion blur):**
```
Giả sử tốc độ băng tải: 10 m/min = 166.7 mm/s
Độ phân giải: 6.5 µm/pixel
Motion blur cho phép: 1 pixel

Exposure Time max = 6.5 µm / 166.7 mm/s = 0.039 ms ≈ 39 µs

➜ Khuyến nghị: Exposure ≤ 50 µs với tốc độ 10 m/min
➜ Nếu băng tải chậm hơn, có thể tăng exposure time
```

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
                      WD = 228mm
                           │
                           ▼
    ════════════════[ VẬT THỂ ]════════════════  ← Băng tải
                           │
                      ~50-100mm
                           │
                    ┌──────┴──────┐
                    │  Backlight  │
                    │  50×50mm    │
                    └─────────────┘

Tổng chiều cao từ backlight đến camera: ~480mm
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

### 5.3 Cấu Hình Phần Mềm

| Thành phần | Lựa chọn |
|------------|----------|
| Camera SDK | Basler Pylon SDK |
| Vision Library | OpenCV / Halcon / Cognex VisionPro |
| Programming Language | C++ / C# / Python |
| Database | SQLite / SQL Server |
| UI Framework | Qt / WPF / WinForms |

---

## 6. Quy Trình Xử Lý Ảnh - Tự Động Phát Hiện Hình Tròn

### 6.1 Pipeline Xử Lý

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

### 6.2 Chi Tiết Thuật Toán Tự Động Phát Hiện

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
│  │ Binary       │  Otsu's Method hoặc Adaptive Threshold               │
│  │ Threshold    │  → Backlight: Lỗ = Trắng, Vật = Đen                  │
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

### 6.3 Tham Số Cấu Hình Phát Hiện Tự Động

| Tham số | Mô tả | Giá trị mặc định | Phạm vi |
|---------|-------|------------------|---------|
| `min_diameter` | Đường kính lỗ nhỏ nhất (mm) | 1.0 | 0.5 ~ 50 |
| `max_diameter` | Đường kính lỗ lớn nhất (mm) | 20.0 | 1.0 ~ 80 |
| `min_circularity` | Độ tròn tối thiểu | 0.85 | 0.7 ~ 1.0 |
| `blur_kernel` | Kích thước kernel blur | 5 | 3, 5, 7 |
| `threshold_method` | Phương pháp threshold | Otsu | Otsu/Adaptive |
| `edge_margin` | Khoảng cách tối thiểu từ biên ảnh (px) | 10 | 5 ~ 50 |

### 6.4 Công Thức Tính Circularity (Độ Tròn)

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

### 6.5 Xử Lý Các Trường Hợp Đặc Biệt

| Trường hợp | Xử lý |
|------------|-------|
| Lỗ chạm biên ảnh | Bỏ qua (không đo được chính xác) |
| Lỗ bị che một phần | Fit circle từ phần visible, đánh dấu "partial" |
| Nhiều lỗ chồng lên nhau | Watershed segmentation hoặc bỏ qua |
| Lỗ quá nhỏ (< min_diameter) | Lọc bỏ, coi là nhiễu |
| Lỗ quá lớn (> max_diameter) | Lọc bỏ, có thể là outline vật thể |
| Hình không tròn | Lọc bỏ dựa trên circularity < 0.85 |

### 6.6 Output Cho Mỗi Lỗ Phát Hiện

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

## 7. Tính Toán Hệ Thống

### 7.1 Tính Toán FOV và Độ Phân Giải

**Thông số đầu vào:**
- Camera: Basler acA4600-7gc (4608 × 3288 pixels, sensor 1/2.3")
- Lens: HK-YC10-80H (Magnification = 0.208x)
- Kích thước lỗ cần đo: 5mm ~ 25mm
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

### 7.2 Tính Toán Tốc Độ Xử Lý

```
Camera Frame Rate: 7 fps @ Full Resolution
Processing Time: ~150ms/frame
Total Cycle Time: ~143ms + 150ms ≈ 300ms/product

Throughput: 60s / 0.3s = 200 pcs/min (max theoretical)
Practical Throughput: ~100-150 pcs/min (với margin an toàn)
```

### 7.3 Tính Toán Băng Tải

```
Nếu kích thước sản phẩm: 50mm
Khoảng cách giữa sản phẩm: 50mm
Tổng khoảng cách: 100mm/product

Với throughput 100 pcs/min:
Tốc độ băng tải = 100 × 100mm/min = 10,000 mm/min = 10 m/min
```

---

## 8. Tiêu Chuẩn Nghiệm Thu

### 8.1 Factory Acceptance Test (FAT)

| Test ID | Mô tả | Tiêu chí đạt |
|---------|-------|--------------|
| FAT-01 | Kiểm tra kết nối camera | Ảnh sống hiển thị ổn định |
| FAT-02 | Calibration độ chính xác | Sai số ≤ 0.5% so với mẫu chuẩn |
| FAT-03 | Đo 100 mẫu chuẩn | Repeatability ≤ 0.02mm |
| FAT-04 | Kiểm tra False Rejection | ≤ 0.1% trên 1000 mẫu |
| FAT-05 | Kiểm tra Detection Rate | ≥ 99.9% phát hiện NG |

### 8.2 Site Acceptance Test (SAT)

| Test ID | Mô tả | Tiêu chí đạt |
|---------|-------|--------------|
| SAT-01 | Hoạt động với băng tải thực | Không miss trigger |
| SAT-02 | Tích hợp PLC | Tín hiệu OK/NG chính xác |
| SAT-03 | Chạy liên tục 8 giờ | Không lỗi, không treo |
| SAT-04 | Gauge R&R Study | ≤ 10% |
| SAT-05 | Training nhân viên | Vận hành độc lập |

---

## 9. Rủi Ro và Giải Pháp

| Rủi Ro | Mức độ | Giải pháp |
|--------|--------|-----------|
| Phản xạ bề mặt kim loại | Cao | Sử dụng Backlight + Polarizer |
| Motion blur (với continuous light) | Trung bình | Giảm exposure time ≤50µs, hoặc nâng cấp Strobe |
| Rung động băng tải | Trung bình | Giảm exposure time, cố định camera chắc chắn |
| Bụi bám lens | Trung bình | Vỏ bảo vệ IP65 + Air purge |
| Thay đổi nhiệt độ | Thấp | Re-calibration định kỳ |
| Lỗ không tròn hoàn hảo | Trung bình | Thuật toán Ellipse Fitting bổ sung |
| Nhiều loại sản phẩm | Trung bình | Hệ thống Recipe management |
| LED backlight giảm độ sáng | Thấp | Kiểm tra định kỳ, có LED dự phòng |

---

## 10. Timeline Dự Kiến

| Giai đoạn | Hoạt động |
|-----------|-----------|
| **Phase 1** | Thiết kế chi tiết & Mua sắm thiết bị |
| **Phase 2** | Phát triển phần mềm |
| **Phase 3** | Tích hợp & FAT |
| **Phase 4** | Lắp đặt & SAT |
| **Phase 5** | Training & Bàn giao |

---

## 11. Deliverables

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

## 12. Phụ Lục

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

## 13. Lưu Ý Kỹ Thuật Quan Trọng

### 13.1 Khuyến Nghị Về Cảm Biến Camera

⚠️ **LƯU Ý:** Ống kính HK-YC10-80H được thiết kế tối ưu cho cảm biến 1" (φ16.6mm). Camera Basler acA4600-7gc sử dụng cảm biến 1/2.3" (φ7.7mm) nhỏ hơn nhiều.

**Ưu điểm khi dùng cảm biến nhỏ hơn:**
- Chỉ sử dụng vùng trung tâm của lens (chất lượng quang học tốt nhất)
- Độ méo thấp hơn (vùng trung tâm có distortion thấp nhất)

**Nhược điểm:**
- Không tận dụng hết FOV tối đa của lens (80mm → chỉ dùng 29.7mm)
- Nếu cần FOV lớn hơn, cân nhắc camera với cảm biến 1" (ví dụ: Basler acA4112-30um)

### 13.2 Độ Sâu Trường Ảnh (DoF)

```
DoF của lens: ±14.8mm @F16

Với F/6.5 (mặc định):
- DoF ước tính: ±14.8 × (6.5/16)² ≈ ±2.4mm

➜ Vật thể cần nằm trong khoảng ±2.4mm quanh mặt phẳng tiêu cự
```

### 13.3 Checklist Trước Khi Triển Khai

- [ ] Xác nhận kích thước lỗ thực tế nằm trong FOV (29.7×21.9mm)
- [ ] Kiểm tra độ dày vật thể < DoF (±2.4mm)
- [ ] Đảm bảo vật thể phẳng và vuông góc với trục quang
- [ ] Chuẩn bị mẫu chuẩn cho calibration
- [ ] Kiểm tra điều kiện ánh sáng môi trường

---

**Document Version:** 2.0
**Created Date:** 2025-12-26
**Last Updated:** 2025-12-26
**Author:** Claude AI Assistant
**Status:** Ready for Review

---

**Revision History:**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-26 | Initial draft |
| 1.1 | 2025-12-26 | Updated with confirmed HK-YC10-80H lens specifications from datasheet |
| 1.2 | 2025-12-26 | Changed lighting mode to Continuous (non-strobe), added motion blur calculations |
| 1.3 | 2025-12-26 | Added automatic circle detection algorithm, detailed processing pipeline |
| 2.0 | 2025-12-26 | Added User Stories, Use Cases, Sequence Diagram - PRD Complete |
