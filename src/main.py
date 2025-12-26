"""
Circle Measurement System - Main Entry Point

Automated Quality Inspection System using Machine Vision
for measuring circular hole dimensions on metal parts.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.logger import setup_logging
from src.ui.main_window import MainWindow


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Create and run main window
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
