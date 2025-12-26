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

*Document Version: 2.0.0*
*Last Updated: December 2024*
