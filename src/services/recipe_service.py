"""Recipe Service - Save/Load recipe configurations"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from ..domain.recipe import Recipe
from ..domain.config import DetectionConfig, ToleranceConfig

logger = logging.getLogger(__name__)


class RecipeService:
    """Service for managing recipes"""

    DEFAULT_RECIPE_DIR = "config/recipes"

    def __init__(self, recipe_dir: Optional[str] = None):
        self._recipe_dir = Path(recipe_dir or self.DEFAULT_RECIPE_DIR)
        self._recipe_dir.mkdir(parents=True, exist_ok=True)
        self._current_recipe: Optional[Recipe] = None
        self._recipes: Dict[str, Recipe] = {}
        self._load_all_recipes()

    @property
    def current_recipe(self) -> Optional[Recipe]:
        """Get current active recipe"""
        return self._current_recipe

    @property
    def recipe_names(self) -> List[str]:
        """Get list of available recipe names"""
        return list(self._recipes.keys())

    def _load_all_recipes(self) -> None:
        """Load all recipes from directory"""
        self._recipes = {}

        for recipe_file in self._recipe_dir.glob("*.json"):
            try:
                recipe = self._load_recipe_file(recipe_file)
                if recipe:
                    self._recipes[recipe.name] = recipe
                    logger.info(f"Loaded recipe: {recipe.name}")
            except Exception as e:
                logger.error(f"Failed to load recipe {recipe_file}: {e}")

        logger.info(f"Loaded {len(self._recipes)} recipes")

    def _load_recipe_file(self, file_path: Path) -> Optional[Recipe]:
        """Load a single recipe file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Recipe.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading recipe file {file_path}: {e}")
            return None

    def get_recipe(self, name: str) -> Optional[Recipe]:
        """Get recipe by name"""
        return self._recipes.get(name)

    def save_recipe(self, recipe: Recipe) -> bool:
        """Save recipe to file"""
        try:
            recipe.updated_at = datetime.now()
            file_path = self._recipe_dir / f"{self._sanitize_filename(recipe.name)}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recipe.to_dict(), f, indent=2)

            self._recipes[recipe.name] = recipe
            logger.info(f"Saved recipe: {recipe.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save recipe: {e}")
            return False

    def delete_recipe(self, name: str) -> bool:
        """Delete a recipe"""
        if name not in self._recipes:
            return False

        try:
            file_path = self._recipe_dir / f"{self._sanitize_filename(name)}.json"
            if file_path.exists():
                file_path.unlink()

            del self._recipes[name]

            if self._current_recipe and self._current_recipe.name == name:
                self._current_recipe = None

            logger.info(f"Deleted recipe: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete recipe: {e}")
            return False

    def set_current_recipe(self, name: str) -> bool:
        """Set current active recipe"""
        recipe = self._recipes.get(name)
        if recipe:
            self._current_recipe = recipe
            logger.info(f"Set current recipe: {name}")
            return True
        return False

    def create_recipe(
        self,
        name: str,
        detection_config: DetectionConfig,
        tolerance_config: ToleranceConfig,
        pixel_to_mm: float,
        description: str = ""
    ) -> Recipe:
        """Create a new recipe from current settings"""
        recipe = Recipe(
            name=name,
            description=description,
            detection_config=detection_config,
            tolerance_config=tolerance_config,
            pixel_to_mm=pixel_to_mm
        )
        return recipe

    def create_default_recipe(self) -> Recipe:
        """Create a default recipe"""
        return Recipe(
            name="Default",
            description="Default recipe with standard settings"
        )

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize recipe name for use as filename"""
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        result = name
        for char in invalid_chars:
            result = result.replace(char, '_')
        return result

    def refresh(self) -> None:
        """Refresh recipe list from disk"""
        self._load_all_recipes()

    def export_recipe(self, name: str, file_path: str) -> bool:
        """Export recipe to external file"""
        recipe = self._recipes.get(name)
        if not recipe:
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recipe.to_dict(), f, indent=2)
            logger.info(f"Exported recipe to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export recipe: {e}")
            return False

    def import_recipe(self, file_path: str) -> Optional[Recipe]:
        """Import recipe from external file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            recipe = Recipe.from_dict(data)
            self._recipes[recipe.name] = recipe
            self.save_recipe(recipe)
            logger.info(f"Imported recipe: {recipe.name}")
            return recipe

        except Exception as e:
            logger.error(f"Failed to import recipe: {e}")
            return None
