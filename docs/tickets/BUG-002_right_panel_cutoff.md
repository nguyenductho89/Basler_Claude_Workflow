# BUG-002: Right Panel Controls Bị Cắt Do Không Responsive

## Summary
Right panel chứa các buttons, sliders và controls bị cắt mất phần bên phải do UI không responsive khi resize window hoặc trên màn hình có resolution khác nhau.

## Priority
**Medium** - Ảnh hưởng UX nhưng không block chức năng chính

## Status
**Resolved** - Fixed in commit `3609c25`

## Environment
- Framework: Tkinter
- File: `src/ui/main_window.py`
- Panel: Right control panel (scrollable)

## Steps to Reproduce
1. Mở application
2. Quan sát right panel với các controls
3. Controls bị cắt mất phần bên phải

## Expected Behavior
- Right panel hiển thị đầy đủ tất cả controls
- Khi resize window, panel tự động adjust
- Scrollbar hoạt động đúng khi content overflow

## Actual Behavior
- Buttons, sliders bị cắt mất phần bên phải
- Không thể thấy/click được phần bị cắt
- Panel không responsive theo window size

## Root Cause Analysis
Có thể do:
1. Fixed width của `right_outer` frame (320px) quá nhỏ
2. Canvas width cố định (300px) không match với content
3. `pack_propagate(False)` ngăn auto-resize
4. Thiếu proper padding/margin cho scrollable content

## Proposed Fix

### Option A: Tăng Width và Fix Padding
```python
# Tăng width cho right panel
right_outer = ttk.Frame(main_frame, width=350)  # Tăng từ 320

# Tăng canvas width
canvas = tk.Canvas(right_outer, width=330, highlightthickness=0)  # Tăng từ 300

# Thêm padding cho scrollable frame content
scrollable_frame = ttk.Frame(canvas, padding=(0, 0, 10, 0))  # Right padding
```

### Option B: Responsive Layout
```python
# Bỏ fixed width, dùng minsize thay vì width cố định
right_outer = ttk.Frame(main_frame)
right_outer.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

# Configure minimum size
self._root.update_idletasks()
right_outer.configure(width=350)
```

### Option C: Grid Layout thay vì Pack
Chuyển từ pack layout sang grid layout cho better control.

## Files to Modify
- `src/ui/main_window.py` - `_setup_ui()` method, lines ~141-159

## Code Location
```python
# Current code (main_window.py:141-159)
right_outer = ttk.Frame(main_frame, width=320)
right_outer.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
right_outer.pack_propagate(False)

canvas = tk.Canvas(right_outer, width=300, highlightthickness=0)
```

## Acceptance Criteria
- [ ] Tất cả controls trong right panel hiển thị đầy đủ
- [ ] Buttons và sliders không bị cắt
- [ ] Scrollbar hoạt động bình thường
- [ ] UI vẫn đẹp trên các resolution khác nhau
- [ ] Không ảnh hưởng đến video panel bên trái

## Screenshots
(Cần thêm screenshot để minh họa vấn đề)

## Related
- `src/ui/main_window.py:_setup_ui()`
- `src/ui/panels/*.py` - Các panel con

## Created
2025-12-27

## Labels
`bug`, `ui`, `tkinter`, `medium-priority`

## Resolution
Fixed với responsive layout approach:
- Bỏ fixed width constraints
- Canvas tự động adjust width theo content
- Thêm padding (5, 0, 15, 0) cho scrollable frame
- Thêm mouse wheel scrolling
- Set minimum width 340px

**Commit:** `3609c25`
**Date:** 2025-12-27
