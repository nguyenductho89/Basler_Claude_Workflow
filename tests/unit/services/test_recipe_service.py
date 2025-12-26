"""Tests for RecipeService"""

import pytest
from src.services.recipe_service import RecipeService
from src.domain.recipe import Recipe
from src.domain.config import DetectionConfig, ToleranceConfig


class TestRecipeService:
    """Test RecipeService"""

    @pytest.fixture
    def recipe_service(self, temp_recipe_dir):
        """Create recipe service with temp directory"""
        return RecipeService(recipe_dir=str(temp_recipe_dir))

    @pytest.fixture
    def default_detection_config(self):
        return DetectionConfig()

    @pytest.fixture
    def default_tolerance_config(self):
        return ToleranceConfig()

    def test_create_recipe(self, recipe_service, default_detection_config, default_tolerance_config):
        """TC-RCP-001: Create new recipe"""
        recipe = recipe_service.create_recipe(
            name="Test Recipe",
            description="Test description",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        assert recipe.name == "Test Recipe"
        assert recipe.description == "Test description"
        assert recipe.detection_config is not None
        assert recipe.tolerance_config is not None

    def test_create_recipe_with_custom_config(self, recipe_service):
        """TC-RCP-002: Create recipe with custom config"""
        detection = DetectionConfig(min_diameter_mm=5.0)
        tolerance = ToleranceConfig(enabled=True, nominal_mm=10.0)

        recipe = recipe_service.create_recipe(
            name="CustomConfig", detection_config=detection, tolerance_config=tolerance, pixel_to_mm=0.01
        )

        assert recipe.detection_config.min_diameter_mm == 5.0
        assert recipe.tolerance_config.enabled == True
        assert recipe.tolerance_config.nominal_mm == 10.0

    def test_save_and_get_recipe(self, recipe_service, default_detection_config, default_tolerance_config):
        """TC-RCP-003: Save and retrieve recipe"""
        recipe = recipe_service.create_recipe(
            name="SaveTest",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        assert recipe_service.save_recipe(recipe)

        loaded = recipe_service.get_recipe("SaveTest")
        assert loaded is not None
        assert loaded.name == "SaveTest"

    def test_get_nonexistent_recipe(self, recipe_service):
        """TC-RCP-004: Get non-existent recipe returns None"""
        loaded = recipe_service.get_recipe("NonExistent")
        assert loaded is None

    def test_list_recipes(self, recipe_service, default_detection_config, default_tolerance_config):
        """TC-RCP-005: List all recipes"""
        for name in ["Recipe1", "Recipe2", "Recipe3"]:
            recipe = recipe_service.create_recipe(
                name=name,
                detection_config=default_detection_config,
                tolerance_config=default_tolerance_config,
                pixel_to_mm=0.00644,
            )
            recipe_service.save_recipe(recipe)

        recipes = recipe_service.recipe_names
        assert len(recipes) == 3
        assert "Recipe1" in recipes
        assert "Recipe2" in recipes
        assert "Recipe3" in recipes

    def test_delete_recipe(self, recipe_service, default_detection_config, default_tolerance_config):
        """TC-RCP-006: Delete recipe"""
        recipe = recipe_service.create_recipe(
            name="ToDelete",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        recipe_service.save_recipe(recipe)
        assert "ToDelete" in recipe_service.recipe_names

        assert recipe_service.delete_recipe("ToDelete")
        assert "ToDelete" not in recipe_service.recipe_names

    def test_delete_nonexistent_recipe(self, recipe_service):
        """TC-RCP-007: Delete non-existent recipe returns False"""
        assert recipe_service.delete_recipe("NonExistent") == False

    def test_export_recipe(self, recipe_service, tmp_path, default_detection_config, default_tolerance_config):
        """TC-RCP-008: Export recipe to file"""
        recipe = recipe_service.create_recipe(
            name="ExportTest",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        recipe_service.save_recipe(recipe)

        export_path = tmp_path / "exported.json"
        assert recipe_service.export_recipe("ExportTest", str(export_path))
        assert export_path.exists()

    def test_import_recipe(self, recipe_service, tmp_path, default_detection_config, default_tolerance_config):
        """TC-RCP-009: Import recipe from file"""
        # Create and export a recipe
        recipe = recipe_service.create_recipe(
            name="ImportTest",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        recipe_service.save_recipe(recipe)
        export_path = tmp_path / "to_import.json"
        recipe_service.export_recipe("ImportTest", str(export_path))

        # Delete original and import
        recipe_service.delete_recipe("ImportTest")
        assert recipe_service.import_recipe(str(export_path))
        assert "ImportTest" in recipe_service.recipe_names

    def test_overwrite_existing_recipe(self, recipe_service, default_detection_config, default_tolerance_config):
        """TC-RCP-010: Overwrite existing recipe"""
        recipe1 = recipe_service.create_recipe(
            name="Overwrite",
            description="Original",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        recipe_service.save_recipe(recipe1)

        recipe2 = recipe_service.create_recipe(
            name="Overwrite",
            description="Updated",
            detection_config=default_detection_config,
            tolerance_config=default_tolerance_config,
            pixel_to_mm=0.00644,
        )
        recipe_service.save_recipe(recipe2)

        loaded = recipe_service.get_recipe("Overwrite")
        assert loaded.description == "Updated"

    def test_create_default_recipe(self, recipe_service):
        """TC-RCP-011: Create default recipe"""
        recipe = recipe_service.create_default_recipe()
        assert recipe.name == "Default"
        assert recipe.description is not None
