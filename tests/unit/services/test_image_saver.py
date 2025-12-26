"""Tests for ImageSaver - Save NG images for quality tracking"""
import pytest
import json
import numpy as np
import cv2
from datetime import datetime, timedelta
from pathlib import Path
from src.services.image_saver import ImageSaver
from src.domain.entities import CircleResult
from src.domain.enums import MeasureStatus


class TestImageSaver:
    """Test ImageSaver for NG image saving functionality"""

    @pytest.fixture
    def image_saver(self, temp_output_dir):
        """Create image saver with temp directory"""
        return ImageSaver(save_dir=str(temp_output_dir))

    @pytest.fixture
    def test_frame(self):
        """Create test frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        return frame

    @pytest.fixture
    def ng_circle(self):
        """Create NG circle result"""
        return CircleResult(
            hole_id=1,
            center_x=320,
            center_y=240,
            radius=50,  # 100px diameter
            diameter_mm=12.0,  # Outside tolerance
            circularity=0.95,
            area_mm2=78.54,
            status=MeasureStatus.NG
        )

    @pytest.fixture
    def ok_circle(self):
        """Create OK circle result"""
        return CircleResult(
            hole_id=2,
            center_x=480,
            center_y=240,
            radius=50,  # 100px diameter
            diameter_mm=10.0,
            circularity=0.95,
            area_mm2=78.54,
            status=MeasureStatus.OK
        )

    # ========== Directory setup ==========
    def test_directories_created(self, image_saver, temp_output_dir):
        """TC-IMG-001: Output directories are created"""
        assert image_saver.ng_image_dir.exists()
        assert image_saver.data_dir.exists()

    def test_ng_image_dir_property(self, image_saver, temp_output_dir):
        """TC-IMG-002: NG image directory property"""
        expected = temp_output_dir / "ng_images"
        assert image_saver.ng_image_dir == expected

    # ========== Save NG images ==========
    def test_save_ng_image(self, image_saver, test_frame, ng_circle):
        """TC-IMG-003: Save NG image successfully"""
        circles = [ng_circle]
        path = image_saver.save_ng_image(test_frame, circles)

        assert path is not None
        assert Path(path).exists()
        assert "NG_" in path

    def test_save_ng_image_with_display_frame(self, image_saver, test_frame, ng_circle):
        """TC-IMG-004: Save NG image with display overlay"""
        display_frame = test_frame.copy()
        cv2.putText(display_frame, "NG", (320, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        circles = [ng_circle]
        path = image_saver.save_ng_image(test_frame, circles, display_frame)

        assert path is not None
        assert Path(path).exists()

    def test_save_ng_creates_date_directory(self, image_saver, test_frame, ng_circle):
        """TC-IMG-005: Save creates date-based directory"""
        circles = [ng_circle]
        path = image_saver.save_ng_image(test_frame, circles)

        today = datetime.now().strftime("%Y%m%d")
        assert today in path

    def test_save_ng_creates_json_data(self, image_saver, test_frame, ng_circle):
        """TC-IMG-006: Save creates JSON measurement data"""
        circles = [ng_circle]
        path = image_saver.save_ng_image(test_frame, circles)

        # Check JSON file exists
        json_path = Path(path).with_suffix(".json")
        assert json_path.exists()

        # Verify JSON content
        with open(json_path) as f:
            data = json.load(f)

        assert "timestamp" in data
        assert data["total_circles"] == 1
        assert data["ng_count"] == 1
        assert len(data["circles"]) == 1
        assert data["circles"][0]["status"] == "NG"

    def test_save_ng_no_ng_circles(self, image_saver, test_frame, ok_circle):
        """TC-IMG-007: Don't save when no NG circles"""
        circles = [ok_circle]
        path = image_saver.save_ng_image(test_frame, circles)

        assert path is None

    def test_save_ng_mixed_circles(self, image_saver, test_frame, ng_circle, ok_circle):
        """TC-IMG-008: Save when at least one NG circle"""
        circles = [ok_circle, ng_circle]
        path = image_saver.save_ng_image(test_frame, circles)

        assert path is not None

        # JSON should include all circles
        json_path = Path(path).with_suffix(".json")
        with open(json_path) as f:
            data = json.load(f)

        assert data["total_circles"] == 2
        assert data["ng_count"] == 1
        assert data["ok_count"] == 1

    def test_save_ng_empty_circles(self, image_saver, test_frame):
        """TC-IMG-009: Don't save when no circles"""
        path = image_saver.save_ng_image(test_frame, [])
        assert path is None

    # ========== Save all images ==========
    def test_save_all_image(self, image_saver, test_frame, ok_circle):
        """TC-IMG-010: Save any image (not just NG)"""
        path = image_saver.save_all_image(test_frame, [ok_circle])

        assert path is not None
        assert Path(path).exists()

    def test_save_all_image_custom_prefix(self, image_saver, test_frame, ok_circle):
        """TC-IMG-011: Save with custom prefix"""
        path = image_saver.save_all_image(test_frame, [ok_circle], prefix="TEST")

        assert path is not None
        assert "TEST_" in path

    # ========== Count functions ==========
    def test_get_ng_image_count(self, image_saver, test_frame, ng_circle):
        """TC-IMG-012: Get NG image count for today"""
        circles = [ng_circle]

        # Save multiple NG images
        image_saver.save_ng_image(test_frame, circles)
        image_saver.save_ng_image(test_frame, circles)
        image_saver.save_ng_image(test_frame, circles)

        count = image_saver.get_ng_image_count()
        assert count == 3

    def test_get_ng_image_count_no_images(self, image_saver):
        """TC-IMG-013: Get count when no NG images"""
        count = image_saver.get_ng_image_count()
        assert count == 0

    def test_get_total_ng_count(self, image_saver, test_frame, ng_circle):
        """TC-IMG-014: Get total NG count across all saves"""
        circles = [ng_circle]

        image_saver.save_ng_image(test_frame, circles)
        image_saver.save_ng_image(test_frame, circles)

        assert image_saver.get_total_ng_count() == 2

    # ========== Cleanup ==========
    def test_cleanup_old_images(self, image_saver, test_frame, ng_circle, temp_output_dir):
        """TC-IMG-015: Cleanup old NG images"""
        # Create an "old" directory (simulate old date)
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
        old_dir = temp_output_dir / "ng_images" / old_date
        old_dir.mkdir(parents=True)

        # Create a file in the old directory
        (old_dir / "NG_test.jpg").touch()

        # Cleanup images older than 30 days
        removed = image_saver.cleanup_old_images(days=30)

        assert removed == 1
        assert not old_dir.exists()

    def test_cleanup_keeps_recent_images(self, image_saver, test_frame, ng_circle):
        """TC-IMG-016: Cleanup keeps recent images"""
        circles = [ng_circle]
        image_saver.save_ng_image(test_frame, circles)

        # Cleanup shouldn't remove today's images
        removed = image_saver.cleanup_old_images(days=30)

        assert removed == 0
        # Today's image should still exist
        assert image_saver.get_ng_image_count() == 1

    # ========== Multiple NG circles ==========
    def test_save_multiple_ng_circles(self, image_saver, test_frame):
        """TC-IMG-017: Save image with multiple NG circles"""
        ng1 = CircleResult(
            hole_id=1, center_x=160, center_y=240,
            radius=40, diameter_mm=8.0,
            circularity=0.9, area_mm2=50.27, status=MeasureStatus.NG
        )
        ng2 = CircleResult(
            hole_id=2, center_x=480, center_y=240,
            radius=60, diameter_mm=12.0,
            circularity=0.92, area_mm2=113.1, status=MeasureStatus.NG
        )

        path = image_saver.save_ng_image(test_frame, [ng1, ng2])
        assert path is not None

        json_path = Path(path).with_suffix(".json")
        with open(json_path) as f:
            data = json.load(f)

        assert data["ng_count"] == 2
        assert len(data["circles"]) == 2

    # ========== Error handling ==========
    def test_save_handles_error_gracefully(self, image_saver, ng_circle):
        """TC-IMG-018: Handle save errors gracefully"""
        # Pass None frame
        path = image_saver.save_ng_image(None, [ng_circle])
        # Should return None without crashing
        assert path is None
