# Technical Debt Registry

Danh sách các technical debt cần được xử lý trong tương lai.

---

## TD-001: Manual Trigger Button thay thế PLC/IO Trigger

### Mô tả
Thêm nút **Trigger** thủ công trên giao diện Tkinter để kích hoạt camera capture thay vì chờ tín hiệu từ PLC/IO.

### Lý do
- PLC/IO integration chưa sẵn sàng
- Camera đang ở chế độ `software trigger` cần tín hiệu trigger để capture
- Cần solution tạm thời để test và demo hệ thống

### Giải pháp tạm thời
Thêm nút "Trigger" trên UI:
- Vị trí: Control Panel (cạnh nút Start/Stop)
- Chức năng: Gọi `camera.ExecuteSoftwareTrigger.Execute()`
- Có thể giữ nút để trigger liên tục hoặc click từng lần

### Giải pháp đúng (TODO)
- [ ] Tích hợp PLC/IO trigger qua digital input
- [ ] IO Service nhận tín hiệu trigger từ PLC
- [ ] Camera capture được kích hoạt bởi IO trigger
- [ ] Loại bỏ nút trigger thủ công khi IO đã hoạt động

### Files liên quan
- `src/ui/main_window.py` - Thêm nút Trigger
- `src/services/camera_service.py` - Method trigger
- `src/services/io_service.py` - Tích hợp IO trigger (future)

### Priority
Medium

### Estimated Effort
- Tạm thời (nút UI): 1-2 giờ
- Đúng cách (IO integration): 2-3 ngày

### Created
2025-12-27

### Related
- BUG-001: Camera Grab Timeout on Software Trigger Mode

---

## TD-002: [Template cho Tech Debt mới]

### Mô tả
[Mô tả ngắn gọn về tech debt]

### Lý do
[Tại sao cần làm tạm như vậy]

### Giải pháp tạm thời
[Giải pháp đang dùng]

### Giải pháp đúng (TODO)
- [ ] Task 1
- [ ] Task 2

### Files liên quan
- file1.py
- file2.py

### Priority
Low / Medium / High

### Created
YYYY-MM-DD

---

# Summary

| ID | Description | Priority | Status |
|----|-------------|----------|--------|
| TD-001 | Manual Trigger Button thay PLC/IO | Medium | Open |
