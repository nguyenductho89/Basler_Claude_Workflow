# Operations Guide - Circle Measurement System

## Version: 2.0.0

---

## Table of Contents
1. [Daily Operations](#1-daily-operations)
2. [System Monitoring](#2-system-monitoring)
3. [Backup & Recovery](#3-backup--recovery)
4. [Maintenance](#4-maintenance)
5. [Performance Tuning](#5-performance-tuning)
6. [Incident Response](#6-incident-response)

---

## 1. Daily Operations

### 1.1 System Startup Checklist

```
□ 1. Kiểm tra kết nối camera (cable, power)
□ 2. Kiểm tra ánh sáng (đèn LED, backlight)
□ 3. Khởi động ứng dụng
□ 4. Kết nối camera và kiểm tra live view
□ 5. Load recipe phù hợp với sản phẩm
□ 6. Chạy calibration check (nếu cần)
□ 7. Chạy test với mẫu chuẩn
□ 8. Bắt đầu production
```

### 1.2 System Shutdown Checklist

```
□ 1. Dừng inspection (Stop button)
□ 2. Export statistics nếu cần
□ 3. Disconnect camera
□ 4. Đóng ứng dụng
□ 5. Tắt đèn chiếu sáng
□ 6. Backup dữ liệu (nếu cuối ca/ngày)
```

### 1.3 Shift Handover

| Item | Check |
|------|-------|
| Recipe đang dùng | Ghi lại tên recipe |
| Calibration status | OK / Cần re-calibrate |
| Statistics | Export CSV |
| Issues | Ghi lại vào log book |
| NG Images | Review và clear nếu cần |

---

## 2. System Monitoring

### 2.1 Real-time Monitoring

#### Status Indicators

| Indicator | Green | Yellow | Red |
|-----------|-------|--------|-----|
| Camera | Connected | Connecting | Disconnected |
| Detection | Running | Paused | Error |
| IO/PLC | Ready | Busy | Error |
| Memory | < 70% | 70-85% | > 85% |

#### Key Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Frame Rate | ≥ 10 fps | < 10 fps | < 5 fps |
| Detection Time | < 100ms | > 100ms | > 200ms |
| OK Rate | > 95% | 90-95% | < 90% |
| Uptime | 99% | 95-99% | < 95% |

### 2.2 Log Monitoring

#### Log Files Location

```
logs/
├── circle_measurement_YYYYMMDD_HHMMSS.log  # Main log
├── error_YYYYMMDD.log                       # Error log
└── performance_YYYYMMDD.log                 # Performance log
```

#### Log Levels

| Level | Description | Action |
|-------|-------------|--------|
| DEBUG | Chi tiết debug | Chỉ bật khi troubleshoot |
| INFO | Thông tin hoạt động | Normal |
| WARNING | Cảnh báo | Review định kỳ |
| ERROR | Lỗi | Cần xử lý |
| CRITICAL | Lỗi nghiêm trọng | Xử lý ngay |

#### Common Log Patterns

```bash
# Xem log errors
Select-String -Path "logs/*.log" -Pattern "ERROR|CRITICAL"

# Xem log hôm nay
Get-Content "logs/circle_measurement_$(Get-Date -Format 'yyyyMMdd')*.log" -Tail 100

# Monitor real-time
Get-Content "logs/circle_measurement_*.log" -Wait -Tail 10
```

### 2.3 Performance Monitoring

#### Check Memory Usage

```powershell
# Process memory
Get-Process -Name python | Select-Object Name, WorkingSet64, CPU

# If memory > 500MB, restart recommended
```

#### Check CPU Usage

```powershell
# Average CPU for python process
Get-Counter '\Process(python*)\% Processor Time' -SampleInterval 1 -MaxSamples 5
```

---

## 3. Backup & Recovery

### 3.1 Backup Schedule

| Data Type | Frequency | Retention | Location |
|-----------|-----------|-----------|----------|
| Recipes | Daily | 30 days | `backup/recipes/` |
| Calibration | Daily | 30 days | `backup/calibration/` |
| Statistics CSV | Daily | 90 days | `backup/statistics/` |
| NG Images | Weekly cleanup | 7 days | `output/ng_images/` |
| Logs | Monthly archive | 12 months | `backup/logs/` |

### 3.2 Backup Script

```powershell
# backup.ps1 - Run daily via Task Scheduler

$date = Get-Date -Format "yyyyMMdd"
$backupRoot = "D:\Backup\CircleMeasurement"

# Create backup directories
New-Item -ItemType Directory -Force -Path "$backupRoot\$date\recipes"
New-Item -ItemType Directory -Force -Path "$backupRoot\$date\config"

# Backup recipes
Copy-Item "recipes\*.json" "$backupRoot\$date\recipes\"

# Backup calibration
Copy-Item "config\calibration.json" "$backupRoot\$date\config\"

# Backup statistics
Copy-Item "output\*.csv" "$backupRoot\$date\"

# Cleanup old backups (> 30 days)
Get-ChildItem "$backupRoot" -Directory | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force

Write-Host "Backup completed: $backupRoot\$date"
```

### 3.3 Recovery Procedures

#### Restore Recipe

```powershell
# 1. Stop application
# 2. Copy recipe from backup
Copy-Item "D:\Backup\CircleMeasurement\20241227\recipes\Product_A.json" "recipes\"
# 3. Start application
# 4. Load recipe from menu
```

#### Restore Calibration

```powershell
# 1. Stop application
# 2. Copy calibration from backup
Copy-Item "D:\Backup\CircleMeasurement\20241227\config\calibration.json" "config\"
# 3. Start application
# Calibration will be loaded automatically
```

#### Full System Recovery

```powershell
# 1. Reinstall application (if needed)
# 2. Restore config folder
Copy-Item "D:\Backup\CircleMeasurement\LATEST\config\*" "config\" -Recurse
# 3. Restore recipes
Copy-Item "D:\Backup\CircleMeasurement\LATEST\recipes\*" "recipes\" -Recurse
# 4. Start application and verify
```

---

## 4. Maintenance

### 4.1 Daily Maintenance

| Task | Procedure | Time |
|------|-----------|------|
| Clean camera lens | Dùng khăn microfiber + dung dịch | 2 min |
| Check lighting | Verify đèn sáng đều | 1 min |
| Review NG images | Xem và xóa nếu không cần | 5 min |

### 4.2 Weekly Maintenance

| Task | Procedure | Time |
|------|-----------|------|
| Calibration check | Đo mẫu chuẩn, so sánh | 10 min |
| Log review | Review warnings/errors | 15 min |
| Backup verification | Kiểm tra backup tồn tại | 5 min |
| Disk cleanup | Xóa logs/images cũ | 5 min |

### 4.3 Monthly Maintenance

| Task | Procedure | Time |
|------|-----------|------|
| Full calibration | Re-calibrate với mẫu chuẩn | 15 min |
| Camera alignment | Kiểm tra/điều chỉnh góc camera | 30 min |
| Software update | Check và apply updates | 30 min |
| Performance review | Analyze OK rate trends | 30 min |

### 4.4 Calibration Maintenance

#### When to Re-calibrate

- Sau khi thay đổi camera/lens position
- Sau khi thay đổi working distance
- Khi kết quả đo drift > 0.01mm
- Monthly scheduled maintenance
- Sau khi restart system

#### Calibration Procedure

```
1. Đặt mẫu chuẩn (certified diameter)
2. Đảm bảo ánh sáng ổn định
3. Menu → Settings → Calibration
4. Nhập known diameter (mm)
5. Click "Auto Calibrate"
6. Verify với mẫu thứ 2
7. Save calibration
```

---

## 5. Performance Tuning

### 5.1 Detection Speed Optimization

| Parameter | Default | Optimized | Notes |
|-----------|---------|-----------|-------|
| Blur kernel | 5 | 3 | Giảm nếu ảnh sạch |
| Image resolution | Full | ROI | Crop vùng cần thiết |
| Binary threshold | Auto | Fixed | Set fixed nếu lighting ổn định |

### 5.2 Memory Optimization

```python
# config/app_config.json
{
    "history_max_items": 1000,      # Limit history size
    "frame_buffer_size": 3,         # Limit frame buffer
    "auto_cleanup_interval": 3600   # Cleanup every hour
}
```

### 5.3 Network Optimization (GigE Camera)

```
1. Dedicated NIC for camera
2. Jumbo Frames enabled (9000 bytes)
3. Disable power saving on NIC
4. Static IP (no DHCP)
5. Disable firewall on camera network
```

### 5.4 Threading Configuration

```python
# Optimal thread count
CAMERA_THREAD: 1      # Single camera thread
PROCESS_THREAD: 1     # Single processing thread
IO_THREAD: 1          # Single IO thread
UI_THREAD: 1          # Main thread (Tkinter)
```

---

## 6. Incident Response

### 6.1 Common Issues & Solutions

#### Issue: Camera Not Found

```
Symptoms: No camera in device list
Causes: Cable, IP, driver, firewall

Resolution:
1. Check physical cable connection
2. Run Pylon IP Configurator
3. Verify camera IP in same subnet
4. Disable Windows Firewall temporarily
5. Reinstall Pylon SDK if needed
```

#### Issue: Detection Inaccurate

```
Symptoms: Measured diameter differs from actual
Causes: Calibration drift, lighting change, focus

Resolution:
1. Check calibration date (Menu → Settings → Calibration Info)
2. Run calibration check with known sample
3. Re-calibrate if difference > 0.01mm
4. Check lighting uniformity
5. Check camera focus
```

#### Issue: Application Crash

```
Symptoms: Application closes unexpectedly
Causes: Memory leak, driver issue, exception

Resolution:
1. Check error log: logs/error_YYYYMMDD.log
2. Restart application
3. If recurring:
   - Reduce history_max_items
   - Update pypylon driver
   - Check for memory leak (Task Manager)
```

#### Issue: IO Not Responding

```
Symptoms: PLC signals not working
Causes: Connection, driver, configuration

Resolution:
1. Check IO panel status indicators
2. Verify physical wiring
3. Check device name in config
4. Switch to SIMULATION mode to test software
5. Verify NI-DAQmx/Advantech driver installed
```

### 6.2 Escalation Matrix

| Severity | Examples | Response Time | Escalate To |
|----------|----------|---------------|-------------|
| Critical | System down, production stopped | Immediate | Engineer + Supervisor |
| High | Intermittent failures, accuracy issues | < 1 hour | Engineer |
| Medium | Performance degradation | < 4 hours | Technician |
| Low | UI issues, cosmetic bugs | Next shift | Technician |

### 6.3 Emergency Procedures

#### Production Stop - Camera Failure

```
1. Switch to backup camera (if available)
2. Or switch to manual inspection
3. Log incident in shift report
4. Call engineer for camera replacement
5. Document downtime
```

#### Production Stop - Software Failure

```
1. Restart application
2. If fails: Restart PC
3. If fails: Restore from backup
4. If fails: Reinstall application
5. Call engineer if unresolved
```

### 6.4 Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| Shift Supervisor | [Phone/Radio] | First escalation |
| Maintenance Technician | [Phone] | Hardware issues |
| Vision Engineer | [Phone/Email] | Software issues |
| IT Support | [Phone/Ticket] | Network/PC issues |
| Vendor Support | [Phone/Email] | Camera/Lens issues |

---

## Appendix A: Quick Reference Commands

```powershell
# Start application
cd D:\CircleMeasurement
.\venv\Scripts\activate
python src\main.py

# Check logs
Get-Content logs\*.log -Tail 50

# Backup now
.\scripts\backup.ps1

# Check disk space
Get-PSDrive C | Select-Object Used, Free

# Kill stuck process
Stop-Process -Name python -Force

# Test camera connection
python -c "from pypylon import pylon; print(pylon.TlFactory.GetInstance().EnumerateDevices())"
```

---

*Document Version: 2.0.0*
*Last Updated: December 2024*
