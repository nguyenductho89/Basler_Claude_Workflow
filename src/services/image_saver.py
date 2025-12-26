"""Image Saver Service - Save NG images and measurements"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import json

import cv2
import numpy as np

from ..domain.entities import CircleResult
from ..domain.enums import MeasureStatus

logger = logging.getLogger(__name__)


class ImageSaver:
    """Service for saving NG images and measurement data"""

    DEFAULT_SAVE_DIR = "output"

    def __init__(self, save_dir: Optional[str] = None):
        self._save_dir = Path(save_dir or self.DEFAULT_SAVE_DIR)
        self._ng_dir = self._save_dir / "ng_images"
        self._data_dir = self._save_dir / "data"

        # Create directories
        self._ng_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._save_count = 0

    @property
    def ng_image_dir(self) -> Path:
        """Get NG image directory"""
        return self._ng_dir

    @property
    def data_dir(self) -> Path:
        """Get data directory"""
        return self._data_dir

    def save_ng_image(
        self, frame: np.ndarray, circles: List[CircleResult], display_frame: Optional[np.ndarray] = None
    ) -> Optional[str]:
        """
        Save NG image with measurement data

        Args:
            frame: Original frame
            circles: List of detected circles
            display_frame: Optional frame with overlay

        Returns:
            Path to saved image, or None if no NG circles
        """
        # Check if any circles are NG
        ng_circles = [c for c in circles if c.status == MeasureStatus.NG]
        if not ng_circles:
            return None

        try:
            timestamp = datetime.now()
            date_dir = self._ng_dir / timestamp.strftime("%Y%m%d")
            date_dir.mkdir(exist_ok=True)

            # Generate filename
            filename = timestamp.strftime("%H%M%S_%f")[:-3]
            self._save_count += 1

            # Save display frame (with overlay)
            if display_frame is not None:
                img_path = date_dir / f"NG_{filename}.jpg"
                cv2.imwrite(str(img_path), display_frame)
            else:
                img_path = date_dir / f"NG_{filename}.jpg"
                cv2.imwrite(str(img_path), frame)

            # Save measurement data
            data_path = date_dir / f"NG_{filename}.json"
            self._save_measurement_data(data_path, timestamp, circles)

            logger.info(f"Saved NG image: {img_path}")
            return str(img_path)

        except Exception as e:
            logger.error(f"Failed to save NG image: {e}")
            return None

    def _save_measurement_data(self, file_path: Path, timestamp: datetime, circles: List[CircleResult]) -> None:
        """Save measurement data to JSON file"""
        data = {
            "timestamp": timestamp.isoformat(),
            "total_circles": len(circles),
            "ng_count": sum(1 for c in circles if c.status == MeasureStatus.NG),
            "ok_count": sum(1 for c in circles if c.status == MeasureStatus.OK),
            "circles": [
                {
                    "hole_id": c.hole_id,
                    "center_x": c.center_x,
                    "center_y": c.center_y,
                    "diameter_mm": c.diameter_mm,
                    "circularity": c.circularity,
                    "area_mm2": c.area_mm2,
                    "status": c.status.name,
                }
                for c in circles
            ],
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_all_image(self, frame: np.ndarray, circles: List[CircleResult], prefix: str = "IMG") -> Optional[str]:
        """Save any image (not just NG)"""
        try:
            timestamp = datetime.now()
            date_dir = self._data_dir / timestamp.strftime("%Y%m%d")
            date_dir.mkdir(exist_ok=True)

            filename = timestamp.strftime("%H%M%S_%f")[:-3]
            img_path = date_dir / f"{prefix}_{filename}.jpg"

            cv2.imwrite(str(img_path), frame)
            logger.debug(f"Saved image: {img_path}")
            return str(img_path)

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None

    def get_ng_image_count(self, date: Optional[datetime] = None) -> int:
        """Get count of NG images for a specific date"""
        if date is None:
            date = datetime.now()

        date_dir = self._ng_dir / date.strftime("%Y%m%d")
        if not date_dir.exists():
            return 0

        return len(list(date_dir.glob("NG_*.jpg")))

    def get_total_ng_count(self) -> int:
        """Get total NG image count"""
        return self._save_count

    def cleanup_old_images(self, days: int = 30) -> int:
        """Remove images older than specified days"""
        import shutil
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for date_dir in self._ng_dir.iterdir():
            if not date_dir.is_dir():
                continue

            try:
                dir_date = datetime.strptime(date_dir.name, "%Y%m%d")
                if dir_date < cutoff:
                    shutil.rmtree(date_dir)
                    removed += 1
                    logger.info(f"Removed old directory: {date_dir}")
            except ValueError:
                continue

        return removed
