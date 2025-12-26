"""Logging configuration"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List


def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> None:
    """
    Setup logging configuration

    Args:
        log_dir: Directory to store log files
        level: Logging level
    """
    # Create logs directory if not exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"circle_measurement_{timestamp}.log"

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Setup handlers
    handlers: List[logging.Handler] = [logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()]

    # Configure root logger
    logging.basicConfig(level=level, format=log_format, datefmt=date_format, handlers=handlers)

    # Set third-party loggers to WARNING
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
