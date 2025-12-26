# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-camera support
- Database integration for statistics
- Web-based monitoring dashboard
- Auto-learning detection parameters

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
| 2.0.0 | 2024-12-27 | IO/PLC, Statistics, CI/CD |
| 1.5.0 | 2024-12-26 | Recipe management |
| 1.4.0 | 2024-12-26 | Calibration system |
| 1.3.0 | 2024-12-26 | Tolerance checking |
| 1.2.0 | 2024-12-26 | Visualization overlay |
| 1.1.0 | 2024-12-26 | Multi-circle detection |
| 1.0.0 | 2024-12-25 | Initial release |

---

## Upgrade Notes

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

[Unreleased]: https://github.com/nguyenductho89/Basler_Claude_Workflow/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/nguyenductho89/Basler_Claude_Workflow/releases/tag/v2.0.0
