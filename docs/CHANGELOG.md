# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-camera support
- Database integration for statistics
- Auto-learning detection parameters
- Web Dashboard authentication/login
- WebSocket control commands

---

## [2.2.0] - 2026-06-14

### Added
- **Three-Layer Boss Detection Pipeline** for U-shaped Carbon Steel Spring Clip Nuts (speed nuts)
  - **Layer 1 – Dominant Candidate**: When the largest in-range contour is ≥ `dominant_ratio` (default 5.0×) the second-largest, it is accepted as the boss without circularity or fill_ratio checks. Radius is measured via a **distance histogram** on boundary points (modal distance from centroid) — immune to noise protrusions that inflate `minEnclosingCircle`.
  - **Layer 2 – fill_holes + normal path**: Flood-fill from the image border to find background pixels, then OR to convert closed annular rings into solid disks; standard circularity + fill_ratio checks then succeed.
  - **Layer 3 – Hough fallback**: When contour detection finds 0 circles, `detect_with_hough()` is called with `HOUGH_GRADIENT`, `dp=1`, param sets `[(100,50),(80,40),(60,30),(40,20)]`. Selects the largest valid circle (boss) and stops.

- **New `DetectionConfig` fields**:
  - `fill_holes: bool = True` — flood-fill preprocessing to convert ring→disk
  - `dominant_ratio: float = 5.0` — area ratio threshold for dominant candidate path
  - `min_fill_ratio: float = 0.65` — `contour_area / (π × enclosing_radius²)`; blur-resistant complement to perimeter circularity

- **Camera exposure clamping** in `CameraService.set_exposure()`: clamps to hardware min (35µs on acA4600-7gc) to prevent `OutOfRangeException`. Added `get_exposure_range()` method.

- **Visualizer label scaling** for 14MP→800×600 display (scale ≈ 0.17×):
  - Circle edge thickness: 2→8px; diameter line thickness: 1→5px; center dot radius: 3→15px
  - Label `font_scale`: 0.5→4.0 (~80px source → ~14px on canvas); thickness: 1→5
  - Statistics `font_scale`: 0.6→2.5; `line_height`: 25→80px

- **Recipe serialization** of new `DetectionConfig` fields (`fill_holes`, `min_fill_ratio`) with backward-compatible `from_dict()` using `DetectionConfig()` defaults.

- **Calibration updated**: `pixel_to_mm = 0.0064516129032258064` (1550px = 10mm reference; acA4600-7gc + HK-YC10-80H @ WD=228mm).

### Changed
- `DetectionConfig` defaults updated for 14MP speed nut detection:
  - `min_diameter_mm`: 5.0 → 3.0mm
  - `max_diameter_mm`: 25.0 → 20.0mm
  - `min_circularity`: 0.85 → 0.75
  - `blur_kernel`: 5 → 31
  - `morph_close_kernel`: 5 → 15

### Fixed
- Boss outer diameter (~13.2mm) rejected by area filter when `max_diameter_mm` default was too small — fixed by updating default to 20.0mm
- Boss with fragmented ring contour (circularity ≈ 0.07, fill_ratio ≈ 0.47 from zinc specular reflections) now detected via dominant candidate path
- `minEnclosingCircle` overestimating boss radius by ~4mm due to noise protrusions — fixed by distance histogram radius measurement

---

## [2.1.0] - 2024-12-27

### Added
- **Web Dashboard for Remote Monitoring**
  - Real-time video streaming via MJPEG (10 FPS)
  - Live detection results via WebSocket
  - Production statistics display
  - IO status monitoring
  - Measurement history table
  - CSV export from browser
  - Support for 5+ concurrent viewers
  - Responsive design for mobile devices

- **AppCore Shared State Container**
  - Singleton pattern for shared services
  - Event bus for decoupled communication
  - Thread-safe frame buffer access
  - Centralized state management

- **REST API Endpoints**
  - `GET /api/status` - System status
  - `GET /api/statistics` - Production stats
  - `GET /api/statistics/export` - CSV export
  - `GET /api/recipes` - Recipe list
  - `GET /api/recipes/{name}` - Recipe details
  - `GET /api/io/status` - IO status
  - `GET /api/calibration` - Calibration info
  - `GET /api/history` - Measurement history
  - `GET /stream/video` - MJPEG stream

- **WebSocket Real-time Events**
  - `detection_result` - Circle detection results
  - `statistics_update` - Statistics updates (5s)
  - `io_status` - IO status changes (500ms)
  - `system_status` - System status (10s)
  - `recipe_changed` - Recipe change notifications

- **Web Frontend Dashboard**
  - Pure HTML/JavaScript (no build required)
  - CSS Grid responsive layout
  - Auto-reconnecting WebSocket client
  - Real-time status indicators

- **New Dependencies**
  - FastAPI for REST API
  - Uvicorn ASGI server
  - WebSockets library
  - Python-multipart

### Changed
- Main application now creates AppCore on startup
- MainWindow accepts AppCore parameter
- Web server runs in background thread (port 8080)
- Detection results published to event bus

### Technical
- Hybrid architecture: Desktop (Tkinter) + Web (FastAPI)
- Detection FPS unaffected by web clients
- Web stream independent at 10 FPS
- Thread-safe design for concurrent access

### Documentation
- Updated PRD with Web Dashboard requirements (US-12)
- Updated ARD with Web Layer architecture (Section 16)
- Updated TST with Web API test cases (Section 11)
- Updated API Reference with Web endpoints (Section 5)
- Updated User Manual with Web Dashboard guide (Section 13)

---

## [2.0.0] - 2024-12-27

### Added
- **IO/PLC Integration**
  - IOService for PLC communication
  - Support for NI-DAQmx and Advantech hardware
  - Simulation mode for testing without hardware
  - Trigger signal input with debounce
  - OK/NG/Ready/Error output signals
  - Recipe selection via IO bits

- **Production Statistics**
  - Real-time OK/NG counting
  - OK rate percentage display
  - Throughput calculation (pcs/min)
  - Runtime tracking
  - Statistics export to CSV

- **NG Image Saving**
  - Auto-save NG images with timestamp
  - Configurable save directory
  - Both original and processed images saved

- **Recipe Management Enhancements**
  - Export/Import recipes to/from files
  - Recipe description field
  - Created/Updated timestamps

- **CI/CD Pipeline**
  - GitHub Actions workflow with self-hosted runner
  - Automated testing with pytest
  - Code coverage with Codecov
  - Ruff linting
  - Mypy type checking
  - Pre-commit hooks

- **Documentation**
  - API Reference documentation
  - Operations Guide
  - Requirements Traceability Matrix
  - CI/CD Guide
  - Updated Installation and User Guides

### Changed
- Improved circle detection algorithm stability
- Enhanced tolerance checking with MeasureStatus enum
- Better error handling throughout services
- Optimized threading model for IO operations

### Fixed
- Memory leak in long-running detection loop
- Camera reconnection handling
- Recipe loading with missing optional fields
- Calibration persistence across restarts

---

## [1.5.0] - 2024-12-26

### Added
- Recipe management system
  - Save/Load/Delete recipes
  - Recipe includes detection config, tolerance, calibration
- History tracking with measurement records
- Export history to CSV

### Changed
- Refactored configuration into separate config classes
- Improved UI layout for recipe panel

---

## [1.4.0] - 2024-12-26

### Added
- Calibration system
  - Manual calibration with known reference
  - Auto-calibration from detected circle
  - Calibration persistence in JSON
- Calibration dialog in UI

### Changed
- All measurements now use calibrated pixel-to-mm ratio
- Detection config includes calibration reference

---

## [1.3.0] - 2024-12-26

### Added
- Tolerance checking (OK/NG classification)
  - Configurable nominal diameter
  - Configurable tolerance (+/- mm)
  - Color-coded results (Green=OK, Red=NG)
- Tolerance panel in UI

### Changed
- CircleResult now includes MeasureStatus
- Visualizer draws different colors based on status

---

## [1.2.0] - 2024-12-26

### Added
- Circle visualization overlay
  - Edge highlighting
  - Diameter line drawing
  - Measurement labels
- Display options (show/hide each overlay type)
- Binary image preview panel

### Changed
- Improved detection accuracy with configurable blur kernel
- Edge margin filtering to ignore partial circles

---

## [1.1.0] - 2024-12-26

### Added
- Multi-circle detection in single frame
- Diameter and area calculation
- Circularity filtering
- Configurable min/max diameter limits

### Changed
- Refactored detector to use contour analysis
- Improved performance with NumPy optimizations

---

## [1.0.0] - 2024-12-25

### Added
- Initial release
- Basler GigE camera integration via pypylon
- Basic circle detection using OpenCV
- Live camera view with Tkinter UI
- Camera connection/disconnection
- Exposure control
- Frame rate display

### Technical
- Python 3.11 support
- Clean architecture with layers (Domain, Services, UI, Infrastructure)
- Logging infrastructure

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 2.1.0 | 2024-12-27 | Web Dashboard, REST API, WebSocket |
| 2.0.0 | 2024-12-27 | IO/PLC, Statistics, CI/CD |
| 1.5.0 | 2024-12-26 | Recipe management |
| 1.4.0 | 2024-12-26 | Calibration system |
| 1.3.0 | 2024-12-26 | Tolerance checking |
| 1.2.0 | 2024-12-26 | Visualization overlay |
| 1.1.0 | 2024-12-26 | Multi-circle detection |
| 1.0.0 | 2024-12-25 | Initial release |

---

## Upgrade Notes

### Upgrading to 2.1.0

1. **New Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   New packages: fastapi, uvicorn, websockets, python-multipart

2. **Configuration Changes**
   - No configuration changes required
   - Web server auto-starts on port 8080

3. **Firewall**
   - Allow TCP port 8080 for remote access
   - See User Manual Section 13.3.3

4. **Breaking Changes**
   - None (backward compatible)

### Upgrading to 2.0.0

1. **New Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration Changes**
   - New `config/io_config.json` file required
   - Recipe format updated (backward compatible)

3. **Database Migration**
   - No database changes (file-based storage)

4. **Breaking Changes**
   - None

---

## Contributors

- Development Team
- Claude AI Assistant

---

[Unreleased]: https://github.com/nguyenductho89/Basler_Claude_Workflow/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/nguyenductho89/Basler_Claude_Workflow/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/nguyenductho89/Basler_Claude_Workflow/releases/tag/v2.0.0
