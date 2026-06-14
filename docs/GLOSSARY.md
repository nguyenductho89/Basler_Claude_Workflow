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

### Boss (Drawn Boss)
Phần kim loại được dập nổi hình tròn (circular drawn boss) trên tấm kim loại phẳng. Trong speed nut / spring nut, boss có đường kính ngoài ~13.2mm và là feature cần đo. Khi chiếu sáng reflected, cạnh ngoài của boss tạo ra vòng sáng trên nền tối.

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

### Distance Histogram Radius
Phương pháp đo bán kính vòng tròn chính xác hơn `minEnclosingCircle` khi contour có nhiễu. Tính khoảng cách từ centroid đến mỗi điểm biên contour, vẽ histogram, lấy bin modal (mode) làm bán kính. Bin modal phản ánh nơi phần lớn điểm biên tập trung — tức là vị trí thực của cạnh boss — không bị ảnh hưởng bởi một vài điểm nhiễu xa nhất.

### Dominant Candidate
Ứng viên chi phối. Trong pipeline phát hiện boss, khi contour lớn nhất trong phạm vi diện tích có diện tích ≥ `dominant_ratio` × diện tích contour lớn thứ hai, nó được chấp nhận ngay lập tức mà không cần kiểm tra circularity hoặc fill_ratio. Điều này giải quyết trường hợp boss có ring fragmentation (circularity rất thấp) nhưng diện tích vẫn lớn hơn nhiễu rất nhiều (ví dụ: 85× lần).

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

### fill_holes
Bước tiền xử lý sau morphological close: flood-fill từ pixel (0,0) — luôn là nền ảnh — để tìm tất cả pixel nền, rồi OR với binary image để lấp đầy các lỗ kín bên trong vùng trắng. Kết quả: vòng khuyên (annulus / ring) biến thành đĩa tròn đặc (solid disk), làm cho circularity và fill_ratio tăng lên gần 1.0. Không có tác dụng nếu ring bị vỡ (nền có thể tiếp cận interior).

### fill_ratio
Tỷ lệ lấp đầy. `fill_ratio = contour_area / (π × enclosing_radius²)`. Đo diện tích contour thực tế so với diện tích vòng tròn bao ngoài (minEnclosingCircle). Khác với `circularity` (dựa trên perimeter), fill_ratio không bị ảnh hưởng bởi biên răng cưa (jagged edges) do blur hoặc nhiễu — một blob tròn mờ vẫn có fill_ratio ≈ 0.85. Giá trị tốt: ≥ 0.65 (mặc định).

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

### Hough Transform / Hough Fallback
Biến đổi Hough (HoughCircles). Thuật toán phát hiện vòng tròn bằng cách tích lũy vote trong không gian tham số (x, y, r). Ưu điểm: hoạt động tốt ngay cả khi chỉ có 30-40% cung tròn hiện diện (ring bị vỡ). Trong hệ thống này, HoughCircles được gọi như "Layer 3 fallback" khi contour detection không tìm được circle nào. Sử dụng `HOUGH_GRADIENT`, `dp=1` (full resolution) để đảm bảo độ chính xác bán kính lớn.

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

### Reflected Light / Coaxial Light
Ánh sáng phản xạ / đồng trục. Phương pháp chiếu sáng từ phía camera xuống vật thể, ánh sáng phản xạ từ bề mặt quay lại camera. Bề mặt phẳng phản xạ mạnh (sáng); bề mặt nghiêng (như thành boss) phản xạ yếu (tối). Phương pháp này phù hợp với speed nut vì boss edge tạo vòng tối rõ nét trên nền phẳng sáng. Đối diện với backlight (ánh sáng xuyên qua lỗ).

### Ring Fragmentation
Sự vỡ vụn của contour vòng. Khi boss edge bị chiếu bằng reflected ring light trên bề mặt mạ kẽm (zinc-plated), phản xạ đặc biệt (specular reflection) tạo ra điểm sáng không đồng đều — một số phần của vòng quá sáng, một số quá tối — khiến binary threshold cắt vòng thành nhiều cung ngắn. Mỗi cung là một contour riêng biệt với circularity rất thấp (~0.07). Ba lớp phát hiện boss được thiết kế để xử lý trường hợp này.

### Rolling Shutter
Màn trập cuộn. Loại sensor đọc từng dòng tuần tự (có thể gây biến dạng với vật di chuyển nhanh).

### Rolling Shutter
Màn trập cuộn. Loại sensor đọc từng dòng tuần tự (có thể gây biến dạng với vật di chuyển nhanh).

### ROI (Region of Interest)
Vùng quan tâm. Xem AOI.

---

## S

### Sensor
Cảm biến ảnh. Chip chuyển đổi ánh sáng thành tín hiệu điện (CCD hoặc CMOS).

### Speed Nut / Spring Nut / Spring Clip Nut
U-shaped Carbon Steel Spring Clip Nut. Đai ốc lò xo dập từ thép carbon, mạ kẽm (zinc-plated). Kích thước tổng ~22×16mm. Cấu tạo: tấm kim loại phẳng + boss tròn dập vào (~Ø13.2mm) + lỗ spring butterfly bên trong boss (hình bất quy tắc). Boss outer diameter là feature cần đo bằng hệ thống vision này. Không dùng backlight (butterfly không tròn), phải dùng reflected light.

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

## Formulas (continued)

### Distance Histogram Radius
```
dists = norm(boundary_points - centroid)
hist, edges = histogram(dists, bins=max(50, (max-min)/5))
radius = (edges[argmax(hist)] + edges[argmax(hist)+1]) / 2
```

### fill_ratio
```
fill_ratio = contour_area / (π × enclosing_radius²)
```

### Dominant candidate condition
```
IF top_contour_area / second_contour_area ≥ dominant_ratio THEN
    accept without shape checks
ELSE
    apply circularity + fill_ratio filters
```

---

*Document Version: 1.1*
*Last Updated: 2026-06-14*
