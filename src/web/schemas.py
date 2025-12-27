"""Pydantic schemas for Web API responses.

This module defines all request/response models for the REST API
and WebSocket events.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MeasureStatusEnum(str, Enum):
    """Measurement status enumeration."""

    OK = "OK"
    NG = "NG"
    NONE = "NONE"
    PARTIAL = "PARTIAL"


class CircleResultSchema(BaseModel):
    """Schema for a single circle detection result."""

    center_x: float
    center_y: float
    diameter_mm: float
    diameter_px: float
    circularity: float
    status: MeasureStatusEnum

    class Config:
        from_attributes = True


class DetectionResultSchema(BaseModel):
    """Schema for detection result."""

    timestamp: datetime
    circles: List[CircleResultSchema]
    overall_status: MeasureStatusEnum
    detection_time_ms: float


class SystemStatusSchema(BaseModel):
    """Schema for system status."""

    camera_connected: bool
    is_running: bool
    current_recipe: Optional[str] = None
    fps: float
    web_clients: int
    timestamp: datetime


class StatisticsSchema(BaseModel):
    """Schema for production statistics."""

    total_inspections: int
    ok_count: int
    ng_count: int
    ok_rate: float
    throughput_per_minute: float
    runtime_seconds: int
    last_result: Optional[MeasureStatusEnum] = None
    session_start: Optional[datetime] = None


class IOStatusSchema(BaseModel):
    """Schema for IO status."""

    connected: bool
    mode: str
    trigger_state: bool
    system_enable: bool
    system_ready: bool
    result_ok: bool
    result_ng: bool
    busy: bool
    error: bool
    recipe_index: int


class CalibrationSchema(BaseModel):
    """Schema for calibration info."""

    is_calibrated: bool
    pixel_to_mm: float
    reference_size_mm: Optional[float] = None
    reference_size_px: Optional[float] = None
    calibrated_at: Optional[datetime] = None


class RecipeListSchema(BaseModel):
    """Schema for recipe list."""

    recipes: List[str]
    current: Optional[str] = None
    count: int


class DetectionConfigSchema(BaseModel):
    """Schema for detection configuration."""

    pixel_to_mm: float
    min_diameter_mm: float
    max_diameter_mm: float
    min_circularity: float
    blur_kernel: int
    binary_threshold: int


class ToleranceConfigSchema(BaseModel):
    """Schema for tolerance configuration."""

    enabled: bool
    nominal_mm: float
    tolerance_mm: float


class RecipeDetailSchema(BaseModel):
    """Schema for recipe details."""

    name: str
    description: str
    detection_config: DetectionConfigSchema
    tolerance_config: ToleranceConfigSchema
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HistoryItemSchema(BaseModel):
    """Schema for a history item."""

    timestamp: datetime
    circles: List[CircleResultSchema]
    overall_status: MeasureStatusEnum


class HistoryResponseSchema(BaseModel):
    """Schema for history response."""

    items: List[HistoryItemSchema]
    total: int
    limit: int
    offset: int


class WebSocketEventSchema(BaseModel):
    """Schema for WebSocket events."""

    event: str
    data: dict


class ErrorResponseSchema(BaseModel):
    """Schema for error responses."""

    detail: str
    error_code: Optional[str] = None
