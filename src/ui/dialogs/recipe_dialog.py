"""Recipe Dialog - Save/Load/Manage recipes"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
import logging

from ...services.recipe_service import RecipeService
from ...domain.recipe import Recipe
from ...domain.config import DetectionConfig, ToleranceConfig

logger = logging.getLogger(__name__)


class RecipeDialog(tk.Toplevel):
    """Dialog for managing recipes"""

    def __init__(
        self,
        parent,
        recipe_service: RecipeService,
        get_current_config: Callable[[], tuple],
        on_recipe_load: Optional[Callable[[Recipe], None]] = None,
    ):
        super().__init__(parent)

        self.title("Recipe Manager")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._recipe_service = recipe_service
        self._get_current_config = get_current_config
        self._on_recipe_load = on_recipe_load

        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self) -> None:
        """Setup dialog UI"""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Recipe list
        list_frame = ttk.LabelFrame(main_frame, text="Available Recipes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.recipe_listbox = tk.Listbox(list_container, height=10)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.recipe_listbox.yview)
        self.recipe_listbox.configure(yscrollcommand=scrollbar.set)

        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipe_listbox.bind("<<ListboxSelect>>", self._on_select)
        self.recipe_listbox.bind("<Double-1>", lambda e: self._on_load())

        # Recipe info
        info_frame = ttk.LabelFrame(main_frame, text="Recipe Details", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=5, width=50, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        # Row 1 buttons
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill=tk.X, pady=(0, 5))

        self.load_btn = ttk.Button(row1, text="Load Recipe", command=self._on_load, state=tk.DISABLED)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.save_btn = ttk.Button(row1, text="Save Current as...", command=self._on_save)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.delete_btn = ttk.Button(row1, text="Delete", command=self._on_delete, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT)

        # Row 2 buttons
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill=tk.X, pady=(0, 5))

        self.import_btn = ttk.Button(row2, text="Import...", command=self._on_import)
        self.import_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.export_btn = ttk.Button(row2, text="Export...", command=self._on_export, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.refresh_btn = ttk.Button(row2, text="Refresh", command=self._refresh_list)
        self.refresh_btn.pack(side=tk.LEFT)

        # Close button
        self.close_btn = ttk.Button(btn_frame, text="Close", command=self.destroy)
        self.close_btn.pack(side=tk.RIGHT)

    def _refresh_list(self) -> None:
        """Refresh recipe list"""
        self._recipe_service.refresh()
        self.recipe_listbox.delete(0, tk.END)

        for name in sorted(self._recipe_service.recipe_names):
            self.recipe_listbox.insert(tk.END, name)

        self._update_buttons()
        self._clear_info()

    def _on_select(self, event) -> None:
        """Handle recipe selection"""
        selection = self.recipe_listbox.curselection()
        if selection:
            name = self.recipe_listbox.get(selection[0])
            recipe = self._recipe_service.get_recipe(name)
            if recipe:
                self._show_recipe_info(recipe)

        self._update_buttons()

    def _show_recipe_info(self, recipe: Recipe) -> None:
        """Show recipe details"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = f"Name: {recipe.name}\n"
        info += f"Description: {recipe.description or 'N/A'}\n"
        info += f"Created: {recipe.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        info += f"Tolerance: {recipe.tolerance_config.nominal_mm:.3f} ± {recipe.tolerance_config.tolerance_mm:.3f} mm\n"
        info += f"Diameter Range: {recipe.detection_config.min_diameter_mm:.1f} - {recipe.detection_config.max_diameter_mm:.1f} mm"

        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)

    def _clear_info(self) -> None:
        """Clear info display"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Select a recipe to view details")
        self.info_text.config(state=tk.DISABLED)

    def _update_buttons(self) -> None:
        """Update button states"""
        has_selection = bool(self.recipe_listbox.curselection())
        self.load_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.delete_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

    def _on_load(self) -> None:
        """Load selected recipe"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        name = self.recipe_listbox.get(selection[0])
        recipe = self._recipe_service.get_recipe(name)

        if recipe and self._on_recipe_load:
            self._recipe_service.set_current_recipe(name)
            self._on_recipe_load(recipe)
            messagebox.showinfo("Success", f"Loaded recipe: {name}")
            self.destroy()

    def _on_save(self) -> None:
        """Save current settings as new recipe"""
        # Get current config
        detection_config, tolerance_config, pixel_to_mm = self._get_current_config()

        # Ask for recipe name
        dialog = SaveRecipeDialog(self, self._recipe_service.recipe_names)
        self.wait_window(dialog)

        if dialog.result:
            name, description = dialog.result
            recipe = self._recipe_service.create_recipe(
                name=name,
                description=description,
                detection_config=detection_config,
                tolerance_config=tolerance_config,
                pixel_to_mm=pixel_to_mm,
            )

            if self._recipe_service.save_recipe(recipe):
                messagebox.showinfo("Success", f"Saved recipe: {name}")
                self._refresh_list()
            else:
                messagebox.showerror("Error", "Failed to save recipe")

    def _on_delete(self) -> None:
        """Delete selected recipe"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        name = self.recipe_listbox.get(selection[0])

        if messagebox.askyesno("Confirm", f"Delete recipe '{name}'?"):
            if self._recipe_service.delete_recipe(name):
                self._refresh_list()
            else:
                messagebox.showerror("Error", "Failed to delete recipe")

    def _on_import(self) -> None:
        """Import recipe from file"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])

        if filename:
            recipe = self._recipe_service.import_recipe(filename)
            if recipe:
                messagebox.showinfo("Success", f"Imported recipe: {recipe.name}")
                self._refresh_list()
            else:
                messagebox.showerror("Error", "Failed to import recipe")

    def _on_export(self) -> None:
        """Export selected recipe to file"""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        name = self.recipe_listbox.get(selection[0])

        filename = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")], initialfile=f"{name}.json"
        )

        if filename:
            if self._recipe_service.export_recipe(name, filename):
                messagebox.showinfo("Success", f"Exported recipe to: {filename}")
            else:
                messagebox.showerror("Error", "Failed to export recipe")


class SaveRecipeDialog(tk.Toplevel):
    """Dialog for entering new recipe name"""

    def __init__(self, parent, existing_names: list):
        super().__init__(parent)

        self.title("Save Recipe")
        self.geometry("350x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._existing_names = existing_names
        self.result = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup dialog UI"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Name entry
        ttk.Label(frame, text="Recipe Name:").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(frame, textvariable=self.name_var, width=40)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        # Description entry
        ttk.Label(frame, text="Description (optional):").pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(frame, textvariable=self.desc_var, width=40)
        self.desc_entry.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT)

        self.name_entry.focus_set()
        self.bind("<Return>", lambda e: self._on_save())

    def _on_save(self) -> None:
        """Handle save button"""
        name = self.name_var.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter a recipe name")
            return

        if name in self._existing_names:
            if not messagebox.askyesno("Confirm", f"Recipe '{name}' already exists. Overwrite?"):
                return

        self.result = (name, self.desc_var.get().strip())
        self.destroy()
