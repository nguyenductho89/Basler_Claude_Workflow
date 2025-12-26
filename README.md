# Circle Measurement System

![Build Status](https://github.com/nguyenductho89/Basler_Claude_Workflow/actions/workflows/test.yml/badge.svg)

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
