"""Pytest configuration and fixtures"""

import sys
import os
import pytest
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_image_single_circle():
    """Create test image with single circle"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)
    return img


@pytest.fixture
def test_image_multiple_circles():
    """Create test image with multiple circles"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(img, (160, 240), 40, (255, 255, 255), -1)
    cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)
    cv2.circle(img, (480, 240), 30, (255, 255, 255), -1)
    return img


@pytest.fixture
def test_image_no_circles():
    """Create blank test image"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def test_image_ellipse():
    """Create test image with ellipse (non-circular)"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.ellipse(img, (320, 240), (80, 40), 0, 0, 360, (255, 255, 255), -1)
    return img


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def temp_recipe_dir(tmp_path):
    """Create temporary recipe directory"""
    recipe_dir = tmp_path / "recipes"
    recipe_dir.mkdir()
    return recipe_dir


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
