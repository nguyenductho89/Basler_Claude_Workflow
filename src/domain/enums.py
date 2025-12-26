"""Enumeration types for the domain layer"""
from enum import Enum, auto


class MeasureStatus(Enum):
    """Status of a measurement result"""
    OK = auto()
    NG = auto()
    PARTIAL = auto()
    SKIPPED = auto()
