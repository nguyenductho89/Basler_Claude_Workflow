"""Results Panel - Display detection results"""
import tkinter as tk
from tkinter import ttk
from typing import List
import logging

from ...domain.entities import CircleResult
from ...domain.enums import MeasureStatus

logger = logging.getLogger(__name__)


class ResultsPanel(ttk.LabelFrame):
    """Panel for displaying detection results"""

    def __init__(self, parent):
        super().__init__(parent, text="Detection Results", padding=10)

        self._circles: List[CircleResult] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Statistics frame
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Detected count
        ttk.Label(stats_frame, text="Detected:").grid(row=0, column=0, sticky=tk.W)
        self.detected_label = ttk.Label(stats_frame, text="0", font=("Arial", 12, "bold"))
        self.detected_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        # OK count
        ttk.Label(stats_frame, text="OK:").grid(row=1, column=0, sticky=tk.W)
        self.ok_label = ttk.Label(stats_frame, text="0", foreground="green", font=("Arial", 12, "bold"))
        self.ok_label.grid(row=1, column=1, sticky=tk.W, padx=5)

        # NG count
        ttk.Label(stats_frame, text="NG:").grid(row=2, column=0, sticky=tk.W)
        self.ng_label = ttk.Label(stats_frame, text="0", foreground="red", font=("Arial", 12, "bold"))
        self.ng_label.grid(row=2, column=1, sticky=tk.W, padx=5)

        # Results treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview with scrollbar
        columns = ("id", "diameter", "circularity", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("diameter", text="Diameter (mm)")
        self.tree.heading("circularity", text="Circularity")
        self.tree.heading("status", text="Status")

        # Define column widths
        self.tree.column("id", width=30, anchor=tk.CENTER)
        self.tree.column("diameter", width=100, anchor=tk.CENTER)
        self.tree.column("circularity", width=80, anchor=tk.CENTER)
        self.tree.column("status", width=50, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure tags for coloring
        self.tree.tag_configure("ok", foreground="green")
        self.tree.tag_configure("ng", foreground="red")
        self.tree.tag_configure("partial", foreground="orange")

        # Clear button
        self.clear_btn = ttk.Button(self, text="Clear Results", command=self.clear)
        self.clear_btn.pack(fill=tk.X, pady=(10, 0))

    def update_results(self, circles: List[CircleResult]) -> None:
        """
        Update the results display

        Args:
            circles: List of detected circles
        """
        self._circles = circles

        # Update statistics
        total = len(circles)
        ok_count = sum(1 for c in circles if c.status == MeasureStatus.OK)
        ng_count = sum(1 for c in circles if c.status == MeasureStatus.NG)

        self.detected_label.config(text=str(total))
        self.ok_label.config(text=str(ok_count))
        self.ng_label.config(text=str(ng_count))

        # Update treeview
        self.tree.delete(*self.tree.get_children())

        for circle in circles:
            status_str = circle.status.name
            tag = status_str.lower()

            self.tree.insert(
                "",
                tk.END,
                values=(
                    circle.hole_id,
                    f"{circle.diameter_mm:.3f}",
                    f"{circle.circularity:.3f}",
                    status_str
                ),
                tags=(tag,)
            )

    def clear(self) -> None:
        """Clear all results"""
        self._circles = []
        self.detected_label.config(text="0")
        self.ok_label.config(text="0")
        self.ng_label.config(text="0")
        self.tree.delete(*self.tree.get_children())

    def get_results(self) -> List[CircleResult]:
        """Get current results"""
        return self._circles

    def get_statistics(self) -> dict:
        """Get current statistics"""
        total = len(self._circles)
        ok_count = sum(1 for c in self._circles if c.status == MeasureStatus.OK)
        ng_count = sum(1 for c in self._circles if c.status == MeasureStatus.NG)

        return {
            "total": total,
            "ok": ok_count,
            "ng": ng_count,
            "ok_rate": ok_count / total if total > 0 else 0.0
        }
