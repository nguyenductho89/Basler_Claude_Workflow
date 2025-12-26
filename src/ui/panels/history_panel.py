"""History Panel - Measurement history display"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
from datetime import datetime
from dataclasses import dataclass
import csv
import logging

from ...domain.entities import CircleResult
from ...domain.enums import MeasureStatus

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """Single history entry"""
    timestamp: datetime
    circles: List[CircleResult]
    total_count: int
    ok_count: int
    ng_count: int


class HistoryPanel(ttk.LabelFrame):
    """Panel for displaying measurement history"""

    MAX_HISTORY_SIZE = 100

    def __init__(self, parent):
        super().__init__(parent, text="Measurement History", padding=10)

        self._history: List[HistoryEntry] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Statistics summary
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(stats_frame, text="Total Measurements:").grid(row=0, column=0, sticky=tk.W)
        self.total_label = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        self.total_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(stats_frame, text="OK Rate:").grid(row=1, column=0, sticky=tk.W)
        self.rate_label = ttk.Label(stats_frame, text="0%", foreground="green", font=("Arial", 10, "bold"))
        self.rate_label.grid(row=1, column=1, sticky=tk.W, padx=5)

        # History treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("time", "count", "ok", "ng")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)

        self.tree.heading("time", text="Time")
        self.tree.heading("count", text="Total")
        self.tree.heading("ok", text="OK")
        self.tree.heading("ng", text="NG")

        self.tree.column("time", width=80, anchor=tk.CENTER)
        self.tree.column("count", width=50, anchor=tk.CENTER)
        self.tree.column("ok", width=50, anchor=tk.CENTER)
        self.tree.column("ng", width=50, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure tags
        self.tree.tag_configure("ok", foreground="green")
        self.tree.tag_configure("ng", foreground="red")
        self.tree.tag_configure("mixed", foreground="orange")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.export_btn = ttk.Button(
            btn_frame,
            text="Export CSV",
            command=self._export_csv
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_btn = ttk.Button(
            btn_frame,
            text="Clear",
            command=self.clear
        )
        self.clear_btn.pack(side=tk.LEFT)

    def add_measurement(self, circles: List[CircleResult]) -> None:
        """
        Add a measurement to history

        Args:
            circles: List of detected circles
        """
        if not circles:
            return

        # Create history entry
        ok_count = sum(1 for c in circles if c.status == MeasureStatus.OK)
        ng_count = sum(1 for c in circles if c.status == MeasureStatus.NG)

        entry = HistoryEntry(
            timestamp=datetime.now(),
            circles=circles.copy(),
            total_count=len(circles),
            ok_count=ok_count,
            ng_count=ng_count
        )

        # Add to history (limit size)
        self._history.append(entry)
        if len(self._history) > self.MAX_HISTORY_SIZE:
            self._history.pop(0)

        # Update display
        self._update_display()

    def _update_display(self) -> None:
        """Update the UI display"""
        # Update statistics
        total_measurements = len(self._history)
        total_ok = sum(e.ok_count for e in self._history)
        total_all = sum(e.total_count for e in self._history)

        self.total_label.config(text=str(total_measurements))

        if total_all > 0:
            ok_rate = (total_ok / total_all) * 100
            self.rate_label.config(text=f"{ok_rate:.1f}%")

            if ok_rate >= 95:
                self.rate_label.config(foreground="green")
            elif ok_rate >= 80:
                self.rate_label.config(foreground="orange")
            else:
                self.rate_label.config(foreground="red")
        else:
            self.rate_label.config(text="0%", foreground="gray")

        # Update treeview (show latest 50)
        self.tree.delete(*self.tree.get_children())

        for entry in reversed(self._history[-50:]):
            time_str = entry.timestamp.strftime("%H:%M:%S")

            # Determine tag based on results
            if entry.ng_count == 0:
                tag = "ok"
            elif entry.ok_count == 0:
                tag = "ng"
            else:
                tag = "mixed"

            self.tree.insert(
                "",
                tk.END,
                values=(time_str, entry.total_count, entry.ok_count, entry.ng_count),
                tags=(tag,)
            )

    def _export_csv(self) -> None:
        """Export history to CSV file"""
        if not self._history:
            messagebox.showwarning("Warning", "No history to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"measurements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    "Timestamp", "Hole_ID", "Diameter_mm", "Circularity",
                    "Center_X", "Center_Y", "Status"
                ])

                # Write data
                for entry in self._history:
                    for circle in entry.circles:
                        writer.writerow([
                            entry.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                            circle.hole_id,
                            f"{circle.diameter_mm:.4f}",
                            f"{circle.circularity:.4f}",
                            f"{circle.center_x:.2f}",
                            f"{circle.center_y:.2f}",
                            circle.status.name
                        ])

            messagebox.showinfo("Success", f"History exported to:\n{filename}")
            logger.info(f"History exported to {filename}")

        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            messagebox.showerror("Error", f"Failed to export: {e}")

    def clear(self) -> None:
        """Clear all history"""
        self._history = []
        self.tree.delete(*self.tree.get_children())
        self.total_label.config(text="0")
        self.rate_label.config(text="0%", foreground="gray")

    def get_history(self) -> List[HistoryEntry]:
        """Get full history"""
        return self._history.copy()

    def get_statistics(self) -> dict:
        """Get overall statistics"""
        total_measurements = len(self._history)
        total_ok = sum(e.ok_count for e in self._history)
        total_ng = sum(e.ng_count for e in self._history)
        total_all = sum(e.total_count for e in self._history)

        return {
            "measurements": total_measurements,
            "total_circles": total_all,
            "ok_count": total_ok,
            "ng_count": total_ng,
            "ok_rate": (total_ok / total_all * 100) if total_all > 0 else 0.0
        }
