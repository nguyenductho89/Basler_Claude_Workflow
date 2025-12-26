# Glossary - Circle Measurement System

Bảng thuật ngữ chuyên ngành sử dụng trong hệ thống.

---

## A

### AOI (Area of Interest)
Vùng quan tâm trên ảnh. Camera có thể chỉ capture phần AOI để tăng tốc độ frame rate.

### Accuracy
Độ chính xác. Mức độ gần của giá trị đo được so với giá trị thực.

---

## B

### Binary Image
Ảnh nhị phân. Ảnh chỉ có 2 mức: đen (0) và trắng (255). Dùng để tách đối tượng khỏi nền.

### Blur (Gaussian Blur)
Làm mờ Gaussian. Kỹ thuật làm mịn ảnh để giảm nhiễu trước khi xử lý.

---

## C

### Calibration
Hiệu chuẩn. Quá trình xác định tỷ lệ pixel-to-mm bằng mẫu chuẩn có kích thước đã biết.

### Circularity
Độ tròn. Thông số đánh giá hình dạng có tròn hay không.
- Formula: `4 × π × Area / Perimeter²`
- Range: 0.0 (không tròn) → 1.0 (tròn hoàn hảo)

### Contour
Đường viền. Đường cong nối các điểm liên tục có cùng màu hoặc cường độ.

### C-Mount
Chuẩn gắn kết lens với camera. Thread: 1" diameter, 32 TPI, flange distance: 17.526mm.

---

## D

### Debounce
Chống rung. Kỹ thuật lọc tín hiệu để tránh trigger nhiều lần từ một sự kiện.

### DOF (Depth of Field)
Độ sâu trường ảnh. Khoảng cách trên trục Z mà vật thể vẫn còn trong focus.

### DI (Digital Input)
Ngõ vào số. Tín hiệu điện tử nhận từ PLC (ON/OFF, 24V/0V).

### DO (Digital Output)
Ngõ ra số. Tín hiệu điện tử gửi đến PLC (ON/OFF, 24V/0V).

---

## E

### Exposure Time
Thời gian phơi sáng. Thời gian sensor thu nhận ánh sáng (đơn vị: µs hoặc ms).

### Edge Detection
Phát hiện biên. Kỹ thuật tìm ranh giới giữa các vùng khác biệt trong ảnh.

---

## F

### FOV (Field of View)
Trường nhìn. Kích thước vùng mà camera có thể quan sát được (mm × mm).

### FPS (Frames Per Second)
Số khung hình/giây. Tốc độ capture của camera.

---

## G

### GigE Vision
Chuẩn giao tiếp camera công nghiệp qua Ethernet (Gigabit). Cho phép cable dài đến 100m.

### GenICam
Generic Interface for Cameras. Chuẩn API thống nhất để điều khiển camera công nghiệp.

### Grayscale
Ảnh xám. Ảnh chỉ có các mức xám từ 0 (đen) đến 255 (trắng).

---

## H

### Hardware Trigger
Trigger phần cứng. Tín hiệu điện tử từ PLC/sensor để yêu cầu camera chụp ảnh.

---

## I

### IO (Input/Output)
Vào/Ra. Giao tiếp tín hiệu số giữa máy tính và PLC/thiết bị ngoại vi.

---

## L

### Live View
Xem trực tiếp. Hiển thị hình ảnh liên tục từ camera theo thời gian thực.

---

## M

### Magnification
Độ phóng đại. Tỷ lệ giữa kích thước ảnh trên sensor và kích thước vật thực.
- β = image size / object size

### Machine Vision
Thị giác máy. Công nghệ sử dụng camera và xử lý ảnh để kiểm tra/đo lường tự động.

### MTF (Modulation Transfer Function)
Hàm truyền điều biến. Thông số đánh giá độ phân giải và độ sắc nét của lens.

---

## N

### NG (No Good)
Không đạt. Sản phẩm có kích thước nằm ngoài dung sai cho phép.

### NI-DAQmx
Driver của National Instruments cho các thiết bị thu thập dữ liệu (DAQ).

### Nominal Value
Giá trị danh định. Kích thước mục tiêu/thiết kế của sản phẩm.

---

## O

### OK
Đạt. Sản phẩm có kích thước nằm trong dung sai cho phép.

### Otsu's Method
Phương pháp Otsu. Thuật toán tự động tìm ngưỡng tối ưu để chuyển ảnh sang binary.

### Overlay
Lớp phủ. Thông tin vẽ thêm lên ảnh (contour, label, measurement line).

---

## P

### Pixel
Điểm ảnh. Đơn vị nhỏ nhất của ảnh số.

### Pixel-to-mm Ratio
Tỷ lệ pixel/mm. Hệ số chuyển đổi từ đơn vị pixel sang mm, xác định qua calibration.

### PLC (Programmable Logic Controller)
Bộ điều khiển logic khả trình. Thiết bị điều khiển tự động trong nhà máy.

### PoE (Power over Ethernet)
Công nghệ cấp nguồn qua cáp mạng Ethernet.

### Pylon SDK
Bộ phát triển phần mềm của Basler để điều khiển camera.

### pypylon
Python wrapper cho Pylon SDK.

---

## R

### Recipe
Công thức. Tập hợp các thông số cấu hình cho một loại sản phẩm cụ thể.

### Rolling Shutter
Màn trập cuộn. Loại sensor đọc từng dòng tuần tự (có thể gây biến dạng với vật di chuyển nhanh).

### ROI (Region of Interest)
Vùng quan tâm. Xem AOI.

---

## S

### Sensor
Cảm biến ảnh. Chip chuyển đổi ánh sáng thành tín hiệu điện (CCD hoặc CMOS).

### Software Trigger
Trigger phần mềm. Lệnh từ phần mềm yêu cầu camera chụp ảnh.

---

## T

### Telecentric Lens
Ống kính viễn tâm. Loại lens có góc nhìn song song, không bị méo phối cảnh.

### Threshold
Ngưỡng. Giá trị phân biệt để chuyển ảnh sang binary.

### Tolerance
Dung sai. Sai lệch cho phép so với giá trị danh định (±mm).

### Trigger
Kích hoạt. Tín hiệu yêu cầu camera chụp ảnh hoặc hệ thống thực hiện đo.

---

## U

### USB3 Vision
Chuẩn giao tiếp camera công nghiệp qua USB 3.0.

---

## W

### Working Distance (WD)
Khoảng cách làm việc. Khoảng cách từ mặt trước lens đến bề mặt vật thể.

---

## Symbols

### β (Beta)
Ký hiệu độ phóng đại (Magnification).

### px
Viết tắt của pixel.

### mm
Millimet (1/1000 mét).

### µs
Micro giây (1/1,000,000 giây).

### ms
Mili giây (1/1000 giây).

---

## Formulas

### Pixel to mm Conversion
```
size_mm = size_px × pixel_to_mm
```

### Circularity
```
circularity = 4 × π × area / perimeter²
```

### FOV Calculation
```
FOV = sensor_size / magnification
```

### OK/NG Check
```
IF |measured - nominal| ≤ tolerance THEN OK
ELSE NG
```

---

*Document Version: 1.0*
*Last Updated: December 2024*
