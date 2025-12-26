# Installation Guide - Circle Measurement System v2.0.0

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Software Installation](#software-installation)
3. [Hardware Setup](#hardware-setup)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## 1. System Requirements

### 1.1 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Intel Core i5 (4 cores) | Intel Core i7 (8 cores) |
| RAM | 8 GB | 16 GB |
| Storage | 50 GB SSD | 256 GB NVMe SSD |
| Display | 1920x1080 | 2560x1440 |
| Network | Gigabit Ethernet | Dual Gigabit Ethernet |

### 1.2 Camera Requirements

- **Supported Models**: Basler ace, Basler ace 2, Basler dart
- **Interface**: GigE Vision (recommended) or USB3 Vision
- **Resolution**: Minimum 1280x960 pixels
- **Frame Rate**: Minimum 30 fps

### 1.3 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Windows | 10/11 (64-bit) | Operating System |
| Python | 3.10 or higher | Runtime |
| Pylon SDK | 7.x | Camera driver |

### 1.4 Optional Hardware

- **PLC/IO Module**: NI DAQmx or Advantech ADAM series
- **Lighting**: LED ring light or backlight
- **Fixture**: Custom mounting for parts

---

## 2. Software Installation

### 2.1 Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run installer with options:
   - [x] Add Python to PATH
   - [x] Install pip
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### 2.2 Install Basler Pylon SDK

1. Download Pylon SDK from [Basler website](https://www.baslerweb.com/en/downloads/software-downloads/)
2. Run `Basler_pylon_x.x.x.exe`
3. Select components:
   - [x] pylon Viewer
   - [x] pylon SDK
   - [x] GigE Vision drivers (if using GigE camera)
   - [x] USB3 Vision drivers (if using USB camera)
4. Complete installation and restart if prompted

### 2.3 Install Application

1. Extract the application package:
   ```cmd
   unzip CircleMeasurementSystem-2.0.0.zip -d C:\CircleMeasurement
   ```

2. Navigate to application directory:
   ```cmd
   cd C:\CircleMeasurement
   ```

3. Create virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

### 2.4 Verify Installation

```cmd
python -c "import cv2; import numpy; import pypylon; print('All dependencies OK')"
```

---

## 3. Hardware Setup

### 3.1 Camera Connection (GigE)

1. **Network Configuration**:
   - Use dedicated NIC for camera (not shared with LAN)
   - Set static IP on NIC: `192.168.1.1`, Subnet: `255.255.255.0`
   - Configure camera IP: `192.168.1.10` (via Pylon IP Configurator)

2. **Jumbo Frames** (Recommended):
   - Open Network Adapter settings
   - Enable Jumbo Frames (9000 bytes)
   - Match setting on camera

3. **Firewall**:
   - Allow Pylon and Python through Windows Firewall
   - Or disable firewall on camera NIC

### 3.2 Camera Connection (USB3)

1. Connect camera to USB 3.0 port (blue connector)
2. Avoid USB hubs - connect directly to motherboard
3. Install USB3 Vision driver if prompted

### 3.3 Lighting Setup

1. **Ring Light** (Front lighting):
   - Mount concentrically with camera lens
   - Adjust intensity to avoid reflections
   - Suitable for: matte surfaces

2. **Backlight** (Silhouette):
   - Place behind transparent/thin parts
   - Provides high contrast edges
   - Suitable for: precise edge detection

### 3.4 PLC/IO Connection (Optional)

#### NI DAQmx:
1. Install NI-DAQmx driver from [ni.com](https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html)
2. Connect USB or PCIe DAQ device
3. Configure channels in NI MAX

#### Advantech ADAM:
1. Install Advantech driver
2. Connect via USB or Ethernet
3. Configure in Advantech Navigator

---

## 4. Configuration

### 4.1 Application Configuration

Configuration files are stored in `config/` directory:

```
config/
├── app_config.json      # Application settings
├── camera_config.json   # Camera parameters
└── calib.json           # Calibration data
```

### 4.2 Initial Setup

1. **Start Application**:
   ```cmd
   python main.py
   ```

2. **Connect Camera**:
   - Go to `Camera > Connect`
   - Select camera from list
   - Click Connect

3. **Calibration**:
   - Place calibration target (known size circle)
   - Go to `Settings > Calibration`
   - Enter reference size in mm
   - Click Calibrate

4. **Create Recipe**:
   - Go to `Recipe > New Recipe`
   - Set detection parameters
   - Set tolerance values
   - Save recipe

### 4.3 IO Configuration

Edit `config/io_config.json`:

```json
{
  "mode": "SIMULATION",
  "trigger_channel": "DI0",
  "ok_channel": "DO0",
  "ng_channel": "DO1",
  "ready_channel": "DO2",
  "pulse_duration_ms": 100
}
```

Modes: `SIMULATION`, `NI_DAQMX`, `ADVANTECH`

---

## 5. Verification

### 5.1 Camera Test

1. Open Pylon Viewer
2. Select camera and click "Continuous Shot"
3. Verify image is displayed correctly
4. Check frame rate and exposure

### 5.2 Detection Test

1. Start application
2. Connect camera
3. Place test part with known circle
4. Click "Single Shot"
5. Verify circle is detected
6. Check diameter measurement

### 5.3 IO Test (Simulation Mode)

1. Enable IO Panel (`View > IO Panel`)
2. Enable Simulation mode
3. Click "Trigger" button
4. Verify detection runs
5. Check OK/NG outputs respond

### 5.4 Run Test Suite

```cmd
pytest tests/ -v
```

Expected: All tests pass (50+ tests)

---

## 6. Troubleshooting

### 6.1 Camera Not Found

| Symptom | Cause | Solution |
|---------|-------|----------|
| No cameras listed | Driver not installed | Install Pylon SDK |
| Camera shown but can't connect | IP conflict | Use IP Configurator |
| Intermittent disconnection | Network issue | Check cable, use dedicated NIC |
| USB camera not recognized | Wrong port | Use USB 3.0 port |

### 6.2 Detection Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| No circles detected | Threshold too high | Lower binary threshold |
| Wrong circles detected | Size filter wrong | Adjust min/max diameter |
| Partial circles | Poor lighting | Improve illumination |
| Noisy detection | Image quality | Add blur, adjust exposure |

### 6.3 Calibration Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Inaccurate measurements | Bad calibration | Re-calibrate with precision target |
| Measurement drift | Temperature change | Re-calibrate periodically |
| Large error | Wrong reference size | Verify calibration target |

### 6.4 Performance Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Low frame rate | CPU overload | Reduce image resolution |
| GUI freezing | Threading issue | Check worker thread status |
| Memory growth | Image accumulation | Clear history periodically |

### 6.5 Log Files

Application logs are stored in `logs/` directory:
```
logs/
├── app_YYYYMMDD.log      # Application log
└── error_YYYYMMDD.log    # Error log
```

Review logs for detailed error information.

---

## Support

For technical support:
- Review documentation in `docs/` folder
- Check GitHub issues
- Contact system administrator

---

*Document Version: 2.0.0*
*Last Updated: December 2024*
