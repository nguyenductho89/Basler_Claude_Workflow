# Circle Measurement System

[![Release](https://img.shields.io/github/v/release/nguyenductho89/Basler_Claude_Workflow?include_prereleases&style=flat-square)](https://github.com/nguyenductho89/Basler_Claude_Workflow/releases/latest)
[![Build Status](https://github.com/nguyenductho89/Basler_Claude_Workflow/actions/workflows/test.yml/badge.svg)](https://github.com/nguyenductho89/Basler_Claude_Workflow/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/nguyenductho89/Basler_Claude_Workflow/graph/badge.svg)](https://codecov.io/gh/nguyenductho89/Basler_Claude_Workflow)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red?style=flat-square)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-available-brightgreen?style=flat-square)](docs/)

Industrial circle measurement system using Basler cameras with real-time detection and PLC integration.

## Features

- Real-time circle detection using OpenCV
- Basler camera integration (pypylon)
- PLC/IO support via NI-DAQmx
- Recipe management for different product configurations
- Calibration tools for accurate measurements

## Requirements

- Python 3.11+
- OpenCV 4.5+
- NumPy 1.21+

### Optional
- pypylon (Basler camera support)
- nidaqmx (PLC/IO support)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
├── src/
│   ├── domain/         # Domain entities and configurations
│   └── services/       # Business logic services
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
└── recipes/            # Product recipe files
```

## Documentation

- [Installation Guide](docs/INS_Installation_Guide.md)
- [User Manual](docs/USR_User_Manual.md)
- [Architecture Design](docs/ARD_Architecture_Design.md)
- [CI/CD Guide](docs/DEV_CICD_Guide.md)
- [Test Plan](docs/TST_Test_Plan.md)

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## License

Proprietary - All rights reserved.
