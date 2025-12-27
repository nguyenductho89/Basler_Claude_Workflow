"""FastAPI dependency injection.

This module provides dependencies for accessing AppCore
and its services in route handlers.
"""

from typing import Optional

from src.core import AppCore


def get_app_core() -> AppCore:
    """Get the AppCore singleton instance.

    Returns:
        AppCore singleton instance
    """
    return AppCore()


def get_recipe_service():
    """Get the recipe service from AppCore.

    Returns:
        RecipeService instance or None
    """
    return get_app_core().recipe_service


def get_calibration_service():
    """Get the calibration service from AppCore.

    Returns:
        CalibrationService instance or None
    """
    return get_app_core().calibration_service


def get_statistics():
    """Get the statistics from AppCore.

    Returns:
        Statistics instance or None
    """
    return get_app_core().statistics


def get_io_status():
    """Get the IO status from AppCore.

    Returns:
        IOStatus instance or None
    """
    return get_app_core().io_status
