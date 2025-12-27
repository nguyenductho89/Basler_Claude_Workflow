"""REST API endpoints for Web Dashboard.

This module provides all REST API endpoints for the Web Dashboard.
"""

import csv
import io
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.core import AppCore
from src.web.dependencies import get_app_core
from src.web.schemas import (
    SystemStatusSchema,
    StatisticsSchema,
    RecipeListSchema,
    RecipeDetailSchema,
    DetectionConfigSchema,
    ToleranceConfigSchema,
    IOStatusSchema,
    CalibrationSchema,
    HistoryResponseSchema,
    HistoryItemSchema,
    CircleResultSchema,
    MeasureStatusEnum,
)

router = APIRouter(prefix="/api", tags=["api"])


def _get_status_string(status: Any) -> str:
    """Convert status to string for MeasureStatusEnum.

    Args:
        status: Status value (enum, string, or None)

    Returns:
        Uppercase status string
    """
    if status is None:
        return "NONE"
    if hasattr(status, "value"):
        return str(status.value).upper()
    return str(status).upper()


@router.get("/status", response_model=SystemStatusSchema)
async def get_status(app_core: AppCore = Depends(get_app_core)):
    """Get current system status."""
    status = app_core.get_status()
    return SystemStatusSchema(
        camera_connected=status["camera_connected"],
        is_running=status["is_running"],
        current_recipe=status["current_recipe"],
        fps=status["fps"],
        web_clients=status["web_clients"],
        timestamp=datetime.fromisoformat(status["timestamp"]),
    )


@router.get("/statistics", response_model=StatisticsSchema)
async def get_statistics(app_core: AppCore = Depends(get_app_core)):
    """Get production statistics."""
    stats = app_core.statistics

    if stats is None:
        return StatisticsSchema(
            total_inspections=0,
            ok_count=0,
            ng_count=0,
            ok_rate=0.0,
            throughput_per_minute=0.0,
            runtime_seconds=0,
            last_result=None,
            session_start=None,
        )

    # Get statistics data
    try:
        total = stats.total_count
        ok = stats.ok_count
        ng = stats.ng_count
        ok_rate = stats.ok_rate
        throughput = getattr(stats, "throughput_per_minute", 0.0)
        runtime = getattr(stats, "runtime_seconds", 0)
        session_start = getattr(stats, "session_start", None)
        last = getattr(stats, "last_result", None)
    except AttributeError:
        total = 0
        ok = 0
        ng = 0
        ok_rate = 0.0
        throughput = 0.0
        runtime = 0
        session_start = None
        last = None

    return StatisticsSchema(
        total_inspections=total,
        ok_count=ok,
        ng_count=ng,
        ok_rate=ok_rate,
        throughput_per_minute=throughput,
        runtime_seconds=runtime,
        last_result=MeasureStatusEnum(last.value.upper()) if last else None,
        session_start=session_start,
    )


@router.get("/statistics/export")
async def export_statistics(app_core: AppCore = Depends(get_app_core)):
    """Export statistics as CSV file."""
    stats = app_core.statistics

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["timestamp", "total", "ok", "ng", "ok_rate"])

    # Data
    if stats is not None:
        try:
            writer.writerow(
                [
                    datetime.now().isoformat(),
                    stats.total_count,
                    stats.ok_count,
                    stats.ng_count,
                    stats.ok_rate,
                ]
            )
        except AttributeError:
            writer.writerow([datetime.now().isoformat(), 0, 0, 0, 0.0])

    output.seek(0)

    # Generate filename
    filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/recipes", response_model=RecipeListSchema)
async def get_recipes(app_core: AppCore = Depends(get_app_core)):
    """Get list of available recipes."""
    recipe_service = app_core.recipe_service

    if recipe_service is None:
        return RecipeListSchema(recipes=[], current=None, count=0)

    try:
        recipes = recipe_service.recipe_names
        current = app_core.current_recipe
    except AttributeError:
        recipes = []
        current = None

    return RecipeListSchema(recipes=recipes, current=current, count=len(recipes))


@router.get("/recipes/{name}", response_model=RecipeDetailSchema)
async def get_recipe(name: str, app_core: AppCore = Depends(get_app_core)):
    """Get recipe details by name."""
    recipe_service = app_core.recipe_service

    if recipe_service is None:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {name}")

    try:
        recipe = recipe_service.get_recipe(name)
    except Exception:
        recipe = None

    if recipe is None:
        raise HTTPException(status_code=404, detail=f"Recipe not found: {name}")

    # Build response
    detection_config = DetectionConfigSchema(
        pixel_to_mm=recipe.detection_config.pixel_to_mm,
        min_diameter_mm=recipe.detection_config.min_diameter_mm,
        max_diameter_mm=recipe.detection_config.max_diameter_mm,
        min_circularity=recipe.detection_config.min_circularity,
        blur_kernel=recipe.detection_config.blur_kernel,
        binary_threshold=recipe.detection_config.binary_threshold,
    )

    tolerance_config = ToleranceConfigSchema(
        enabled=recipe.tolerance_config.enabled,
        nominal_mm=recipe.tolerance_config.nominal_mm,
        tolerance_mm=recipe.tolerance_config.tolerance_mm,
    )

    return RecipeDetailSchema(
        name=recipe.name,
        description=recipe.description or "",
        detection_config=detection_config,
        tolerance_config=tolerance_config,
        created_at=getattr(recipe, "created_at", None),
        updated_at=getattr(recipe, "updated_at", None),
    )


@router.get("/io/status", response_model=IOStatusSchema)
async def get_io_status(app_core: AppCore = Depends(get_app_core)):
    """Get IO/PLC status."""
    io_status = app_core.io_status

    if io_status is None:
        return IOStatusSchema(
            connected=False,
            mode="simulation",
            trigger_state=False,
            system_enable=False,
            system_ready=False,
            result_ok=False,
            result_ng=False,
            busy=False,
            error=False,
            recipe_index=0,
        )

    try:
        recipe_bit0 = getattr(io_status, "recipe_bit0", False)
        recipe_bit1 = getattr(io_status, "recipe_bit1", False)
        recipe_index = (1 if recipe_bit1 else 0) * 2 + (1 if recipe_bit0 else 0)
    except AttributeError:
        recipe_index = 0

    return IOStatusSchema(
        connected=getattr(io_status, "connected", False),
        mode=getattr(io_status, "mode", "simulation"),
        trigger_state=getattr(io_status, "trigger", False),
        system_enable=getattr(io_status, "system_enable", False),
        system_ready=getattr(io_status, "system_ready", False),
        result_ok=getattr(io_status, "result_ok", False),
        result_ng=getattr(io_status, "result_ng", False),
        busy=getattr(io_status, "busy", False),
        error=getattr(io_status, "system_error", False),
        recipe_index=recipe_index,
    )


@router.get("/calibration", response_model=CalibrationSchema)
async def get_calibration(app_core: AppCore = Depends(get_app_core)):
    """Get calibration information."""
    calib_service = app_core.calibration_service

    if calib_service is None:
        return CalibrationSchema(
            is_calibrated=False,
            pixel_to_mm=0.00644,
            reference_size_mm=None,
            reference_size_px=None,
            calibrated_at=None,
        )

    try:
        is_calibrated = calib_service.is_calibrated
        pixel_to_mm = calib_service.pixel_to_mm
        calib_data = getattr(calib_service, "calibration_data", None)

        if calib_data:
            reference_size_mm = calib_data.reference_size_mm
            reference_size_px = calib_data.reference_size_px
            calibrated_at = calib_data.calibrated_at
        else:
            reference_size_mm = None
            reference_size_px = None
            calibrated_at = None
    except AttributeError:
        is_calibrated = False
        pixel_to_mm = 0.00644
        reference_size_mm = None
        reference_size_px = None
        calibrated_at = None

    return CalibrationSchema(
        is_calibrated=is_calibrated,
        pixel_to_mm=pixel_to_mm,
        reference_size_mm=reference_size_mm,
        reference_size_px=reference_size_px,
        calibrated_at=calibrated_at,
    )


@router.get("/history", response_model=HistoryResponseSchema)
async def get_history(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    app_core: AppCore = Depends(get_app_core),
):
    """Get measurement history."""
    history = app_core.get_history(limit=limit, offset=offset)
    total = app_core.get_history_count()

    items = []
    for item in history:
        try:
            result = item.get("result", [])
            circles = []

            if isinstance(result, list):
                for circle in result:
                    try:
                        circles.append(
                            CircleResultSchema(
                                center_x=getattr(circle, "center_x", 0),
                                center_y=getattr(circle, "center_y", 0),
                                diameter_mm=getattr(circle, "diameter_mm", 0),
                                diameter_px=getattr(circle, "diameter_px", 0),
                                circularity=getattr(circle, "circularity", 0),
                                status=MeasureStatusEnum(_get_status_string(getattr(circle, "status", None))),
                            )
                        )
                    except Exception:
                        pass

            # Determine overall status
            if circles:
                if any(c.status == MeasureStatusEnum.NG for c in circles):
                    overall = MeasureStatusEnum.NG
                elif all(c.status == MeasureStatusEnum.OK for c in circles):
                    overall = MeasureStatusEnum.OK
                else:
                    overall = MeasureStatusEnum.NONE
            else:
                overall = MeasureStatusEnum.NONE

            items.append(
                HistoryItemSchema(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    circles=circles,
                    overall_status=overall,
                )
            )
        except Exception:
            pass

    return HistoryResponseSchema(items=items, total=total, limit=limit, offset=offset)
