"""
Circle Measurement System - Main Entry Point

Automated Quality Inspection System using Machine Vision
for measuring circular hole dimensions on metal parts.

Release 2.0 - Full Production Ready
Features:
- Basler GigE camera integration
- Real-time circle detection with tolerance checking
- Calibration system (pixel to mm)
- Recipe management
- Production statistics
- PLC/IO integration
- NG image saving
"""
import sys
import os
import logging
import traceback
from tkinter import messagebox

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.logger import setup_logging
from src.ui.main_window import MainWindow
from src.utils.constants import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)


def show_error_dialog(title: str, message: str) -> None:
    """Show error dialog to user"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except:
        print(f"ERROR: {title}\n{message}")


def check_dependencies() -> bool:
    """Check if required dependencies are available"""
    missing = []

    # Check OpenCV
    try:
        import cv2
        logger.info(f"OpenCV version: {cv2.__version__}")
    except ImportError:
        missing.append("opencv-python")

    # Check numpy
    try:
        import numpy as np
        logger.info(f"NumPy version: {np.__version__}")
    except ImportError:
        missing.append("numpy")

    # Check Pillow
    try:
        from PIL import Image
        import PIL
        logger.info(f"Pillow version: {PIL.__version__}")
    except ImportError:
        missing.append("Pillow")

    # Check pypylon (optional - camera won't work without it)
    try:
        from pypylon import pylon
        logger.info("pypylon available - camera support enabled")
    except ImportError:
        logger.warning("pypylon not available - camera simulation mode only")

    if missing:
        error_msg = f"Missing required packages: {', '.join(missing)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing)}"
        show_error_dialog("Missing Dependencies", error_msg)
        return False

    return True


def main() -> int:
    """
    Main entry point

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Setup logging first
    setup_logging()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

    # Check dependencies
    if not check_dependencies():
        return 1

    try:
        # Create and run main window
        app = MainWindow()
        logger.info("Application initialized successfully")
        app.run()
        logger.info("Application closed normally")
        return 0

    except Exception as e:
        error_msg = f"An unexpected error occurred:\n\n{str(e)}\n\n"
        error_msg += "See log file for details."
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        show_error_dialog("Fatal Error", error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())
