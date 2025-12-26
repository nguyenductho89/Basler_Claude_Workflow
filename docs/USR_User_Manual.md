# User Manual - Circle Measurement System v2.0.0

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Main Interface](#main-interface)
4. [Camera Operations](#camera-operations)
5. [Detection & Measurement](#detection--measurement)
6. [Calibration](#calibration)
7. [Recipe Management](#recipe-management)
8. [Production Statistics](#production-statistics)
9. [IO/PLC Integration](#ioplc-integration)
10. [Keyboard Shortcuts](#keyboard-shortcuts)
11. [FAQ (Frequently Asked Questions)](#faq)
12. [Troubleshooting Guide](#troubleshooting-guide)

---

## 1. Overview

The Circle Measurement System is an automated vision inspection application designed to measure circular holes on metal parts. It uses a Basler industrial camera to capture images and OpenCV for circle detection and measurement.

### Key Features
- Real-time circle detection and measurement
- Automatic OK/NG classification based on tolerance
- Recipe management for multiple products
- Production statistics tracking
- PLC/IO integration for automation
- Hardware trigger support

---

## 2. Getting Started

### 2.1 Starting the Application

1. Open Command Prompt or PowerShell
2. Navigate to application directory:
   ```cmd
   cd C:\CircleMeasurement
   ```
3. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
4. Start application:
   ```cmd
   python main.py
   ```

### 2.2 First-Time Setup

1. **Connect Camera**: `Camera > Connect`
2. **Calibrate**: `Settings > Calibration`
3. **Create Recipe**: `Recipe > New Recipe`
4. **Start Inspection**: Click "Start" or press `F5`

---

## 3. Main Interface

```
+------------------------------------------------------------------+
|  File  Camera  Recipe  Settings  View  Help                      |
+------------------------------------------------------------------+
|                                                                  |
|  +------------------------+  +--------------------------------+  |
|  |                        |  |  Detection Parameters          |  |
|  |                        |  |  - Min Diameter: [____] mm     |  |
|  |    Camera View         |  |  - Max Diameter: [____] mm     |  |
|  |    (Live/Result)       |  |  - Circularity:  [____]        |  |
|  |                        |  |  - Threshold:    [____]        |  |
|  |                        |  +--------------------------------+  |
|  |                        |  |  Tolerance Settings            |  |
|  |                        |  |  - Nominal:   [____] mm        |  |
|  +------------------------+  |  - Tolerance: [____] mm        |  |
|  +------------------------+  +--------------------------------+  |
|  |   Binary View          |  |  Results                       |  |
|  |   (Threshold Result)   |  |  Diameter: 10.05 mm    [OK]    |  |
|  +------------------------+  |  Circularity: 0.95             |  |
|                              +--------------------------------+  |
|  [Start] [Stop] [Single] [Clear]          Status: Connected     |
+------------------------------------------------------------------+
```

### 3.1 Display Areas

| Area | Description |
|------|-------------|
| Camera View | Live camera feed or detection result |
| Binary View | Thresholded image showing detected contours |
| Parameters Panel | Detection and tolerance settings |
| Results Panel | Measurement results and OK/NG status |
| Control Buttons | Start/Stop inspection, Single shot |
| Status Bar | Connection status, frame rate, statistics |

---

## 4. Camera Operations

### 4.1 Connecting Camera

1. Go to `Camera > Connect`
2. Select camera from dropdown list
3. Click `Connect`
4. Status bar shows "Connected"

### 4.2 Camera Settings

Access via `Camera > Settings`:

| Setting | Description | Typical Value |
|---------|-------------|---------------|
| Exposure | Exposure time (us) | 10000-50000 |
| Gain | Analog gain (dB) | 0-12 |
| Frame Rate | Frames per second | 10-30 |

### 4.3 Trigger Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Software | Continuous capture | Testing, setup |
| Hardware | External trigger | Production |

Set via `Camera > Trigger Mode`

### 4.4 Disconnecting

- `Camera > Disconnect`
- Or close application (auto-disconnect)

---

## 5. Detection & Measurement

### 5.1 Single Shot Measurement

1. Place part under camera
2. Click `Single Shot` or press `F6`
3. View results in Results Panel

### 5.2 Continuous Measurement

1. Click `Start` or press `F5`
2. Parts are measured automatically
3. Click `Stop` or press `F5` to stop

### 5.3 Detection Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| Min Diameter | Minimum circle size to detect | 1-100 mm |
| Max Diameter | Maximum circle size to detect | 1-100 mm |
| Min Circularity | Shape filter (1.0 = perfect circle) | 0.7-1.0 |
| Binary Threshold | Image threshold for edge detection | 0-255 |
| Blur Size | Gaussian blur kernel size | 3-15 |

### 5.4 Tolerance Settings

| Parameter | Description |
|-----------|-------------|
| Enabled | Enable/disable tolerance checking |
| Nominal | Target diameter in mm |
| Tolerance | Acceptable deviation (+/-) in mm |

**Example**: Nominal = 10.0 mm, Tolerance = 0.5 mm
- OK Range: 9.5 mm to 10.5 mm
- NG: < 9.5 mm or > 10.5 mm

### 5.5 Understanding Results

| Status | Color | Meaning |
|--------|-------|---------|
| OK | Green | Within tolerance |
| NG | Red | Out of tolerance |
| NONE | Gray | Tolerance disabled |

---

## 6. Calibration

### 6.1 Why Calibrate?

Calibration converts pixel measurements to real-world units (mm). Without calibration, measurements are meaningless.

### 6.2 Calibration Procedure

1. Place calibration target (circle with known diameter)
2. Go to `Settings > Calibration`
3. Capture image of calibration target
4. Enter known diameter in mm
5. System calculates pixel-to-mm ratio
6. Click `Save Calibration`

### 6.3 Calibration Tips

- Use precision machined calibration target
- Ensure target is at same distance as parts
- Re-calibrate if camera position changes
- Re-calibrate periodically for accuracy

### 6.4 Viewing Calibration

Current calibration shown in Settings:
- **Pixel to mm**: Conversion factor (e.g., 0.00644)
- **Reference size**: Calibration target size

---

## 7. Recipe Management

### 7.1 What is a Recipe?

A recipe stores all settings for a specific product:
- Detection parameters
- Tolerance settings
- Calibration data

### 7.2 Creating a Recipe

1. Go to `Recipe > New Recipe`
2. Enter recipe name
3. Configure detection parameters
4. Set tolerance values
5. Click `Save`

### 7.3 Loading a Recipe

1. Go to `Recipe > Load Recipe`
2. Select recipe from list
3. Settings are applied automatically

### 7.4 Managing Recipes

| Action | Menu Path |
|--------|-----------|
| Create | Recipe > New Recipe |
| Load | Recipe > Load Recipe > [name] |
| Edit | Recipe > Edit Recipe |
| Delete | Recipe > Delete Recipe |
| Export | Recipe > Export Recipe |
| Import | Recipe > Import Recipe |

### 7.5 Recipe Files

Recipes are stored as JSON files in `recipes/` directory:
```json
{
  "name": "Product_A",
  "detection_config": {
    "min_diameter_mm": 8.0,
    "max_diameter_mm": 12.0,
    "min_circularity": 0.85
  },
  "tolerance_config": {
    "enabled": true,
    "nominal_mm": 10.0,
    "tolerance_mm": 0.5
  },
  "pixel_to_mm": 0.00644
}
```

---

## 8. Production Statistics

### 8.1 Statistics Panel

Enable via `View > Statistics Panel`

| Metric | Description |
|--------|-------------|
| Total | Total parts inspected |
| OK Count | Parts within tolerance |
| NG Count | Parts out of tolerance |
| OK Rate | Percentage of OK parts |
| Throughput | Parts per minute |

### 8.2 Exporting Statistics

1. Go to `File > Export Statistics`
2. Select save location
3. Choose format (CSV)
4. Click `Save`

Exported CSV contains:
- Timestamp
- Diameter measurement
- OK/NG status
- Recipe name

### 8.3 Resetting Statistics

- `File > Reset Statistics`
- Confirms before clearing

### 8.4 Auto-Save NG Images

Enable via `Settings > Auto-save NG Images`

NG images are saved to `logs/ng_images/` with timestamp.

---

## 9. IO/PLC Integration

### 9.1 IO Panel

Enable via `View > IO Panel`

### 9.2 Input Signals

| Signal | Function |
|--------|----------|
| Trigger (DI0) | Start measurement cycle |

### 9.3 Output Signals

| Signal | Function |
|--------|----------|
| OK (DO0) | Part is within tolerance |
| NG (DO1) | Part is out of tolerance |
| Ready (DO2) | System ready for trigger |
| Error (DO3) | System error occurred |

### 9.4 Simulation Mode

For testing without hardware:
1. Enable `Simulation Mode` in IO Panel
2. Click `Trigger` button to simulate input
3. Observe output indicators

### 9.5 Hardware Modes

| Mode | Hardware | Configuration |
|------|----------|---------------|
| NI_DAQMX | National Instruments DAQ | Via NI MAX |
| ADVANTECH | Advantech ADAM series | Via Navigator |

---

## 10. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Start/Stop continuous mode |
| `F6` | Single shot capture |
| `F7` | Connect camera |
| `F8` | Disconnect camera |
| `Ctrl+S` | Save current settings |
| `Ctrl+O` | Open/Load recipe |
| `Ctrl+N` | New recipe |
| `Ctrl+E` | Export statistics |
| `Ctrl+Q` | Quit application |
| `Space` | Trigger (in simulation mode) |

---

## Appendix A: Best Practices

### Lighting
- Consistent lighting is critical
- Avoid shadows and reflections
- Use diffuse lighting when possible

### Part Positioning
- Consistent part placement improves accuracy
- Use fixtures for repeatability
- Ensure part is in focus

### Maintenance
- Clean camera lens regularly
- Re-calibrate after camera adjustment
- Backup recipes regularly

### Troubleshooting
- Check `logs/` for error details
- Verify camera connection
- Ensure proper lighting
- Re-calibrate if measurements drift

---

## Appendix B: Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "No camera found" | Camera not connected | Check connection, install driver |
| "Detection failed" | No circles found | Adjust parameters, check lighting |
| "Calibration invalid" | Bad calibration data | Re-calibrate |
| "IO Error" | Hardware communication failed | Check connections, restart |

---

## 11. FAQ (Frequently Asked Questions)

### General Questions

**Q: What camera models are supported?**
A: The system supports all Basler cameras with GigE Vision or USB3 Vision interfaces, including ace, ace 2, and dart series. Minimum resolution requirement is 1280x960 pixels.

**Q: Can I use cameras from other manufacturers?**
A: Currently, only Basler cameras are supported due to the pypylon SDK dependency. Support for GenICam-compatible cameras from other manufacturers may be added in future versions.

**Q: What is the minimum circle size that can be detected?**
A: The minimum detectable circle depends on camera resolution and optical setup. Generally, circles should be at least 20 pixels in diameter for reliable detection. Use appropriate magnification for small features.

**Q: How many circles can be detected in one image?**
A: The system can detect multiple circles simultaneously. The practical limit depends on image resolution and processing power. Typically, 10-20 circles can be detected without performance issues.

### Calibration Questions

**Q: How often should I recalibrate?**
A: Recalibrate in these situations:
- After any camera or lens adjustment
- When ambient temperature changes significantly (>5°C)
- Weekly during normal operation
- After any system restart (if high accuracy is critical)

**Q: What size calibration target should I use?**
A: Use a calibration target similar in size to your actual parts. The target should:
- Be precision-machined (tolerance < 0.01mm)
- Have a matte finish to avoid reflections
- Be placed at the same working distance as parts

**Q: Why do my measurements drift over time?**
A: Common causes include:
- Temperature changes affecting camera/lens
- Mechanical vibration loosening camera mount
- Lighting intensity changes
- Lens focus drift

**Q: Can I use auto-calibration in production?**
A: Auto-calibration is useful for initial setup. For production, manual calibration with a certified reference standard is recommended for traceable measurements.

### Detection Questions

**Q: Why are some circles not being detected?**
A: Check these factors:
1. Threshold setting: Adjust binary threshold for better contrast
2. Size filters: Ensure min/max diameter includes your circles
3. Circularity: Lower threshold if parts have slight imperfections
4. Lighting: Ensure consistent, shadow-free illumination
5. Edge quality: Circles touching image edges are filtered out

**Q: How can I improve detection accuracy?**
A: Best practices:
- Use telecentric lens for parallel projection
- Use backlight for silhouette imaging (best edge contrast)
- Increase camera resolution if possible
- Apply appropriate blur to reduce noise
- Ensure consistent part positioning

**Q: Why do I get different measurements on the same part?**
A: Measurement variation causes:
- Part positioning variation (use fixtures)
- Lighting fluctuation (use stable LED lighting)
- Camera noise (increase exposure, reduce gain)
- Focus variation (use telecentric lens or DOF)

**Q: What is circularity and what value should I use?**
A: Circularity measures how close a shape is to a perfect circle (1.0 = perfect). Recommended values:
- Precision machined holes: 0.90-0.95
- Stamped/punched holes: 0.80-0.90
- Cast/molded features: 0.70-0.85

### Recipe Questions

**Q: How do I transfer recipes to another machine?**
A: Two methods:
1. **Export/Import**: Use `Recipe > Export Recipe` and `Recipe > Import Recipe`
2. **File copy**: Copy JSON files from `recipes/` folder

Note: Calibration may need adjustment on different machines due to optical differences.

**Q: Can I edit recipe files manually?**
A: Yes, recipes are stored as JSON files in `recipes/` folder. Edit with any text editor, but ensure valid JSON format. Restart application to load changes.

**Q: What happens if I delete a recipe that's currently loaded?**
A: The current settings remain active in memory. The recipe will be unavailable after restart. Always save changes to a new recipe before deleting.

### IO/PLC Integration Questions

**Q: What PLC protocols are supported?**
A: Currently supported:
- Digital IO via NI-DAQmx devices
- Digital IO via Advantech ADAM modules
- Simulation mode for testing

Modbus TCP and EtherNet/IP support planned for future versions.

**Q: What is the response time for trigger-to-output?**
A: Typical response times:
- Camera trigger to image capture: < 1ms (hardware trigger)
- Image capture to detection complete: 20-50ms (depends on resolution)
- Detection complete to IO output: < 5ms
- Total trigger-to-output: 25-60ms typical

**Q: Can I use multiple trigger inputs?**
A: Currently, single trigger input is supported. Use PLC logic to combine multiple trigger sources before the camera trigger input.

**Q: How do I test IO without PLC connected?**
A: Use Simulation mode:
1. Enable `View > IO Panel`
2. Check `Simulation Mode`
3. Use GUI buttons to simulate inputs
4. Monitor output indicators

### Performance Questions

**Q: Why is the frame rate low?**
A: Common causes:
- High image resolution (reduce or use ROI)
- CPU overload (close other applications)
- Network issues (GigE cameras need dedicated NIC)
- Processing time (simplify detection parameters)

**Q: How can I improve throughput?**
A: Optimization tips:
- Use hardware trigger instead of continuous mode
- Reduce image resolution or use ROI
- Optimize detection parameters (fewer blur iterations)
- Use SSD for NG image storage
- Disable unnecessary overlays

**Q: What is the maximum part rate?**
A: Theoretical maximum depends on:
- Camera frame rate (30-60 fps typical)
- Processing time (20-50ms per frame)
- Practical limit: 15-30 parts/second

### Data & Statistics Questions

**Q: Where is measurement data stored?**
A: Data locations:
- Statistics: `logs/statistics/` (CSV files)
- NG images: `logs/ng_images/` (JPEG files)
- Logs: `logs/` (log files)

**Q: How long is data retained?**
A: Default retention:
- Statistics: Indefinite (manual cleanup)
- NG images: Indefinite (configure auto-cleanup)
- Logs: 30 days (auto-rotated)

**Q: Can I export data to a database?**
A: Currently, data exports to CSV files. Database integration (SQLite/PostgreSQL) is planned for future versions.

---

## 12. Troubleshooting Guide

### 12.1 Camera Problems

#### Camera Not Found
| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| No cameras in list | Pylon not installed | Install Basler Pylon SDK |
| No cameras in list | Network/USB issue | Check cables, try different port |
| Camera found but can't connect | IP conflict | Use Pylon IP Configurator |
| Camera found but can't connect | Another app using camera | Close Pylon Viewer, other apps |
| Intermittent connection | Bad cable | Replace Ethernet/USB cable |
| Intermittent connection | Power issue (USB) | Use powered USB hub |

**Resolution Steps:**
1. Open Pylon Viewer - can it see the camera?
2. Check Device Manager for unknown devices
3. Ping camera IP (GigE): `ping 192.168.1.10`
4. Try different USB port (USB3 cameras)
5. Reinstall Pylon SDK drivers

#### Image Quality Problems
| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| Dark image | Low exposure | Increase exposure time |
| Bright/washed out | High exposure | Decrease exposure, check lighting |
| Noisy image | High gain | Lower gain, increase lighting |
| Blurry image | Focus issue | Adjust lens focus |
| Blurry image | Motion blur | Decrease exposure, add strobe |
| Bands/stripes | Lighting frequency | Use DC lighting, adjust exposure |

### 12.2 Detection Problems

#### No Circles Detected
**Diagnostic Checklist:**
1. [ ] Check Binary View - is the circle visible?
2. [ ] Is threshold appropriate? (adjust until circle is clear)
3. [ ] Are min/max diameter settings correct?
4. [ ] Is the circle complete (not cut off at edges)?
5. [ ] Is circularity threshold too high?

**Common Fixes:**
```
Problem: Circle visible in camera but not in Binary View
→ Adjust threshold (lower for dark circles, higher for bright)

Problem: Circle visible in Binary View but not detected
→ Check diameter filters match actual circle size
→ Lower circularity threshold (try 0.7)

Problem: Wrong circles being detected
→ Narrow diameter range
→ Increase circularity threshold
```

#### Incorrect Measurements
| Issue | Cause | Fix |
|-------|-------|-----|
| All measurements too large | Bad calibration | Re-calibrate |
| All measurements too small | Bad calibration | Re-calibrate |
| Random variation | Poor edge detection | Improve lighting, adjust blur |
| Consistent offset | Lens distortion | Use telecentric lens |
| Measurements drift | Temperature change | Re-calibrate, stabilize environment |

### 12.3 Calibration Problems

#### Calibration Fails
**Symptoms and Solutions:**
```
Error: "No circle detected for calibration"
→ Ensure calibration target is visible and in focus
→ Adjust threshold until target appears in Binary View
→ Check diameter filters include calibration target size

Error: "Multiple circles detected"
→ Use single-circle calibration target
→ Mask or remove other circular features from view

Error: "Calibration value out of range"
→ Check reference size is entered in mm
→ Verify reference size matches actual target
```

#### Poor Calibration Accuracy
| Problem | Cause | Solution |
|---------|-------|----------|
| >1% error | Wrong reference size | Measure target with caliper |
| >1% error | Target at wrong distance | Position at same WD as parts |
| Variable error | Lens distortion | Use center of field, telecentric lens |
| Drift after calibration | Temperature change | Allow system to warm up first |

### 12.4 IO/PLC Problems

#### No Trigger Response
**Diagnostic Steps:**
1. Check IO Panel shows "Ready" status
2. Verify trigger signal in simulation mode works
3. Check wiring: trigger should be 24V pulse to DI0
4. Verify NI MAX or Advantech Navigator sees the device
5. Check `io_config.json` for correct channel assignments

#### Output Not Activating
**Check These:**
- Is PLC reading correct channel? (DO0=OK, DO1=NG)
- Is pulse duration long enough? (default 100ms)
- Is output voltage correct? (open collector or relay)
- In simulation mode, do output indicators light up?

### 12.5 Performance Problems

#### Application Freezes
**Immediate Actions:**
1. Wait 30 seconds - processing may be intensive
2. Check CPU usage in Task Manager
3. If frozen > 1 minute, close and restart application

**Prevention:**
- Don't change parameters during detection
- Allow detection to complete before stopping
- Clear history periodically (large history uses memory)

#### Memory Usage Growing
**Symptoms:** Application uses more memory over time (>1GB)

**Solutions:**
1. Clear measurement history: `File > Clear History`
2. Disable image history if not needed
3. Limit NG image retention
4. Restart application periodically (daily)

#### Slow Frame Rate
| Expected | Actual | Cause | Fix |
|----------|--------|-------|-----|
| 30 fps | <10 fps | Large image | Use ROI or lower resolution |
| 30 fps | <10 fps | CPU maxed | Close other applications |
| 30 fps | <10 fps | Network (GigE) | Check Jumbo Frames, use dedicated NIC |
| 30 fps | Variable | Lighting auto-adjust | Use fixed exposure |

### 12.6 Recipe Problems

#### Recipe Won't Load
**Error Messages:**
```
"Recipe file not found"
→ Recipe may have been deleted
→ Check recipes/ folder for file

"Invalid recipe format"
→ Recipe JSON is corrupted
→ Restore from backup or recreate

"Incompatible recipe version"
→ Recipe from older version
→ Create new recipe with current settings
```

#### Recipe Settings Not Applied
**Verify These:**
1. Check status bar shows loaded recipe name
2. Parameters panel should update after load
3. If settings unchanged, restart application
4. Check for error messages in log files

### 12.7 Error Codes Quick Reference

| Code | Message | Meaning | Action |
|------|---------|---------|--------|
| E101 | Camera not found | No camera detected | Check connection, drivers |
| E102 | Camera connection failed | Can't open camera | Close other apps, restart |
| E103 | Grab timeout | No image received | Check trigger mode |
| E201 | Detection failed | No circles found | Adjust parameters |
| E202 | Multiple circles | More than expected | Narrow diameter range |
| E301 | Calibration invalid | Bad calibration | Re-calibrate |
| E401 | IO init failed | Can't connect to IO | Check hardware, config |
| E402 | Trigger error | Trigger malfunction | Check wiring, debounce |
| E501 | Recipe load failed | Can't read recipe | Check file exists |

### 12.8 Getting Help

**Before Contacting Support:**
1. Note the exact error message
2. Export log files: `logs/app_*.log`
3. Document steps to reproduce problem
4. Capture screenshots if visual issue
5. Note software and firmware versions

**Log File Locations:**
```
logs/
├── app_YYYYMMDD.log      # Application log
├── error_YYYYMMDD.log    # Errors only
└── debug_YYYYMMDD.log    # Detailed debug (if enabled)
```

**Enable Debug Logging:**
Edit `config/app_config.json`:
```json
{
  "logging": {
    "level": "DEBUG",
    "file_enabled": true
  }
}
```

---

*Document Version: 2.0.0*
*Last Updated: December 2024*
