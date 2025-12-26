"""Statistics Panel - Production statistics display"""

import tkinter as tk
from tkinter import ttk
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StatisticsPanel(ttk.LabelFrame):
    """Panel for displaying production statistics"""

    def __init__(self, parent):
        super().__init__(parent, text="Production Statistics", padding=10)

        self._stats = {
            "total_inspections": 0,
            "total_circles": 0,
            "ok_count": 0,
            "ng_count": 0,
            "start_time": datetime.now(),
        }

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Main stats grid
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X)

        # Row 0: Total inspections
        ttk.Label(stats_frame, text="Inspections:").grid(row=0, column=0, sticky=tk.W)
        self.inspections_label = ttk.Label(stats_frame, text="0", font=("Arial", 11, "bold"))
        self.inspections_label.grid(row=0, column=1, sticky=tk.W, padx=10)

        # Row 1: Total circles
        ttk.Label(stats_frame, text="Circles Measured:").grid(row=1, column=0, sticky=tk.W)
        self.circles_label = ttk.Label(stats_frame, text="0", font=("Arial", 11, "bold"))
        self.circles_label.grid(row=1, column=1, sticky=tk.W, padx=10)

        # Row 2: OK count
        ttk.Label(stats_frame, text="OK:").grid(row=2, column=0, sticky=tk.W)
        self.ok_label = ttk.Label(stats_frame, text="0", foreground="green", font=("Arial", 11, "bold"))
        self.ok_label.grid(row=2, column=1, sticky=tk.W, padx=10)

        # Row 3: NG count
        ttk.Label(stats_frame, text="NG:").grid(row=3, column=0, sticky=tk.W)
        self.ng_label = ttk.Label(stats_frame, text="0", foreground="red", font=("Arial", 11, "bold"))
        self.ng_label.grid(row=3, column=1, sticky=tk.W, padx=10)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Rate display
        rate_frame = ttk.Frame(self)
        rate_frame.pack(fill=tk.X)

        ttk.Label(rate_frame, text="OK Rate:").pack(side=tk.LEFT)
        self.rate_label = ttk.Label(rate_frame, text="---%", font=("Arial", 14, "bold"), foreground="gray")
        self.rate_label.pack(side=tk.LEFT, padx=10)

        # Progress bar
        self.rate_bar = ttk.Progressbar(self, length=200, mode="determinate")
        self.rate_bar.pack(fill=tk.X, pady=5)

        # Runtime display
        runtime_frame = ttk.Frame(self)
        runtime_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(runtime_frame, text="Runtime:").pack(side=tk.LEFT)
        self.runtime_label = ttk.Label(runtime_frame, text="00:00:00")
        self.runtime_label.pack(side=tk.LEFT, padx=10)

        # Throughput
        ttk.Label(runtime_frame, text="Rate:").pack(side=tk.LEFT)
        self.throughput_label = ttk.Label(runtime_frame, text="-- pcs/min")
        self.throughput_label.pack(side=tk.LEFT, padx=10)

        # Reset button
        self.reset_btn = ttk.Button(self, text="Reset Statistics", command=self.reset)
        self.reset_btn.pack(anchor=tk.W, pady=(10, 0))

        # Start runtime update
        self._update_runtime()

    def add_inspection(self, ok_count: int, ng_count: int) -> None:
        """
        Add inspection result to statistics

        Args:
            ok_count: Number of OK circles
            ng_count: Number of NG circles
        """
        self._stats["total_inspections"] += 1
        self._stats["total_circles"] += ok_count + ng_count
        self._stats["ok_count"] += ok_count
        self._stats["ng_count"] += ng_count

        self._update_display()

    def _update_display(self) -> None:
        """Update the display"""
        # Update counts
        self.inspections_label.config(text=str(self._stats["total_inspections"]))
        self.circles_label.config(text=str(self._stats["total_circles"]))
        self.ok_label.config(text=str(self._stats["ok_count"]))
        self.ng_label.config(text=str(self._stats["ng_count"]))

        # Calculate and update rate
        total = self._stats["ok_count"] + self._stats["ng_count"]
        if total > 0:
            rate = (self._stats["ok_count"] / total) * 100
            self.rate_label.config(text=f"{rate:.1f}%")
            self.rate_bar["value"] = rate

            # Color based on rate
            if rate >= 95:
                self.rate_label.config(foreground="green")
            elif rate >= 80:
                self.rate_label.config(foreground="orange")
            else:
                self.rate_label.config(foreground="red")
        else:
            self.rate_label.config(text="---%", foreground="gray")
            self.rate_bar["value"] = 0

        # Update throughput
        runtime = datetime.now() - self._stats["start_time"]
        minutes = runtime.total_seconds() / 60
        if minutes > 0:
            throughput = self._stats["total_inspections"] / minutes
            self.throughput_label.config(text=f"{throughput:.1f} pcs/min")
        else:
            self.throughput_label.config(text="-- pcs/min")

    def _update_runtime(self) -> None:
        """Update runtime display"""
        runtime = datetime.now() - self._stats["start_time"]
        hours, remainder = divmod(int(runtime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.runtime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        # Schedule next update
        self.after(1000, self._update_runtime)

    def reset(self) -> None:
        """Reset all statistics"""
        self._stats = {
            "total_inspections": 0,
            "total_circles": 0,
            "ok_count": 0,
            "ng_count": 0,
            "start_time": datetime.now(),
        }
        self._update_display()
        logger.info("Statistics reset")

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        runtime = datetime.now() - self._stats["start_time"]
        total = self._stats["ok_count"] + self._stats["ng_count"]

        return {
            **self._stats,
            "runtime_seconds": runtime.total_seconds(),
            "ok_rate": (self._stats["ok_count"] / total * 100) if total > 0 else 0.0,
        }
