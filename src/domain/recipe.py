"""Recipe model for saving/loading configurations"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import json

from .config import DetectionConfig, ToleranceConfig


@dataclass
class Recipe:
    """Recipe containing all configuration for a product type"""
    name: str
    description: str = ""
    detection_config: DetectionConfig = field(default_factory=DetectionConfig)
    tolerance_config: ToleranceConfig = field(default_factory=ToleranceConfig)
    pixel_to_mm: float = 0.00644
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "detection": {
                "pixel_to_mm": self.pixel_to_mm,
                "min_diameter_mm": self.detection_config.min_diameter_mm,
                "max_diameter_mm": self.detection_config.max_diameter_mm,
                "min_circularity": self.detection_config.min_circularity,
                "blur_kernel": self.detection_config.blur_kernel,
                "edge_margin": self.detection_config.edge_margin,
                "show_contours": self.detection_config.show_contours,
                "show_diameter_line": self.detection_config.show_diameter_line,
                "show_label": self.detection_config.show_label
            },
            "tolerance": {
                "enabled": self.tolerance_config.enabled,
                "nominal_mm": self.tolerance_config.nominal_mm,
                "tolerance_mm": self.tolerance_config.tolerance_mm
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create recipe from dictionary"""
        detection_data = data.get("detection", {})
        tolerance_data = data.get("tolerance", {})

        detection_config = DetectionConfig(
            pixel_to_mm=detection_data.get("pixel_to_mm", 0.00644),
            min_diameter_mm=detection_data.get("min_diameter_mm", 1.0),
            max_diameter_mm=detection_data.get("max_diameter_mm", 20.0),
            min_circularity=detection_data.get("min_circularity", 0.85),
            blur_kernel=detection_data.get("blur_kernel", 5),
            edge_margin=detection_data.get("edge_margin", 10),
            show_contours=detection_data.get("show_contours", True),
            show_diameter_line=detection_data.get("show_diameter_line", True),
            show_label=detection_data.get("show_label", True)
        )

        tolerance_config = ToleranceConfig(
            enabled=tolerance_data.get("enabled", False),
            nominal_mm=tolerance_data.get("nominal_mm", 10.0),
            tolerance_mm=tolerance_data.get("tolerance_mm", 0.05)
        )

        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))

        return cls(
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            created_at=created_at,
            updated_at=updated_at,
            detection_config=detection_config,
            tolerance_config=tolerance_config,
            pixel_to_mm=detection_data.get("pixel_to_mm", 0.00644)
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Recipe':
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))
