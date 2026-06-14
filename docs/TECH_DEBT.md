# Technical Debt Registry

Danh sách các technical debt cần được xử lý trong tương lai.

---

## TD-001: Manual Trigger Button thay thế PLC/IO Trigger

### Mô tả
Thêm nút **Trigger** thủ công trên giao diện Tkinter để kích hoạt camera capture thay vì chờ tín hiệu từ PLC/IO.

### Status
**✅ Resolved** — Cả hai giải pháp đều đã implemented:
- **Temp fix**: Nút Trigger trên UI → gọi `camera_service.execute_software_trigger()`
- **Proper fix**: IO service (`io_service.py`) nhận tín hiệu digital input từ PLC, debounce, gọi trigger callback

### Files đã modify
- `src/ui/main_window.py` — Trigger button
- `src/services/camera_service.py` — `execute_software_trigger()`, `TriggerMode` enum
- `src/services/io_service.py` — `_on_trigger()`, `register_trigger_callback()`

### Resolved
2026-06-14

---

# Summary

| ID | Description | Priority | Status |
|----|-------------|----------|--------|
| TD-001 | Manual Trigger Button thay PLC/IO | Medium | ✅ Resolved |
