"""IO Panel - PLC/IO status display and control"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import logging

from ...domain.io_config import IOConfig, IOStatus, IOMode
from ...services.io_service import IOService

logger = logging.getLogger(__name__)


class IOIndicator(tk.Canvas):
    """LED-style indicator widget"""

    def __init__(self, parent, size: int = 16, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self._size = size
        self._state = False
        self._on_color = "#00ff00"
        self._off_color = "#404040"
        self._draw()

    def _draw(self) -> None:
        """Draw the indicator"""
        self.delete("all")
        color = self._on_color if self._state else self._off_color
        padding = 2
        self.create_oval(
            padding, padding,
            self._size - padding, self._size - padding,
            fill=color, outline="#808080"
        )

    def set_state(self, state: bool) -> None:
        """Set indicator state"""
        if self._state != state:
            self._state = state
            self._draw()

    def set_colors(self, on_color: str, off_color: str = "#404040") -> None:
        """Set indicator colors"""
        self._on_color = on_color
        self._off_color = off_color
        self._draw()


class IOPanel(ttk.LabelFrame):
    """Panel for IO status display and simulation control"""

    def __init__(
        self,
        parent,
        io_service: IOService,
        on_trigger: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent, text="PLC/IO Interface", padding=10)

        self._io_service = io_service
        self._on_trigger = on_trigger
        self._indicators = {}

        self._setup_ui()

        # Register for status updates
        self._io_service.register_status_callback(self._on_status_update)

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Mode display
        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_label = ttk.Label(
            mode_frame,
            text=self._io_service.config.mode.value.upper(),
            font=("Arial", 10, "bold")
        )
        self.mode_label.pack(side=tk.LEFT, padx=5)

        # Connection status
        self.connection_indicator = IOIndicator(mode_frame, highlightthickness=0)
        self.connection_indicator.set_colors("#00ff00", "#ff0000")
        self.connection_indicator.pack(side=tk.RIGHT)

        ttk.Label(mode_frame, text="Connected:").pack(side=tk.RIGHT, padx=(0, 5))

        # Digital Inputs section
        inputs_frame = ttk.LabelFrame(self, text="Digital Inputs (from PLC)", padding=5)
        inputs_frame.pack(fill=tk.X, pady=(0, 10))

        self._create_io_row(inputs_frame, "DI-0", "Trigger", "trigger", is_input=True)
        self._create_io_row(inputs_frame, "DI-1", "System Enable", "enable", is_input=True)
        self._create_io_row(inputs_frame, "DI-2", "Recipe Bit 0", "recipe_bit0", is_input=True)
        self._create_io_row(inputs_frame, "DI-3", "Recipe Bit 1", "recipe_bit1", is_input=True)

        # Digital Outputs section
        outputs_frame = ttk.LabelFrame(self, text="Digital Outputs (to PLC)", padding=5)
        outputs_frame.pack(fill=tk.X, pady=(0, 10))

        self._create_io_row(outputs_frame, "DO-0", "Result OK", "ok", color="#00ff00")
        self._create_io_row(outputs_frame, "DO-1", "Result NG", "ng", color="#ff0000")
        self._create_io_row(outputs_frame, "DO-2", "System Ready", "ready", color="#00ff00")
        self._create_io_row(outputs_frame, "DO-3", "System Error", "error", color="#ff0000")
        self._create_io_row(outputs_frame, "DO-4", "Busy", "busy", color="#ffff00")

        # Simulation controls (only in simulation mode)
        if self._io_service.config.mode == IOMode.SIMULATION:
            sim_frame = ttk.LabelFrame(self, text="Simulation Controls", padding=5)
            sim_frame.pack(fill=tk.X)

            # Trigger button
            self.trigger_btn = ttk.Button(
                sim_frame,
                text="Simulate Trigger",
                command=self._on_sim_trigger
            )
            self.trigger_btn.pack(fill=tk.X, pady=2)

            # Enable toggle
            self.enable_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                sim_frame,
                text="System Enable",
                variable=self.enable_var,
                command=self._on_sim_enable
            ).pack(anchor=tk.W, pady=2)

            # Recipe selector
            recipe_frame = ttk.Frame(sim_frame)
            recipe_frame.pack(fill=tk.X, pady=2)
            ttk.Label(recipe_frame, text="Recipe:").pack(side=tk.LEFT)
            self.recipe_var = tk.IntVar(value=0)
            recipe_spin = ttk.Spinbox(
                recipe_frame,
                from_=0, to=3,
                width=5,
                textvariable=self.recipe_var,
                command=self._on_sim_recipe
            )
            recipe_spin.pack(side=tk.LEFT, padx=5)

        # Start/Stop button
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = ttk.Button(
            control_frame,
            text="Start IO",
            command=self._toggle_io
        )
        self.start_btn.pack(fill=tk.X)

    def _create_io_row(
        self,
        parent,
        channel: str,
        name: str,
        key: str,
        is_input: bool = False,
        color: str = "#00ff00"
    ) -> None:
        """Create an IO status row"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=1)

        # Channel label
        ttk.Label(frame, text=channel, width=6).pack(side=tk.LEFT)

        # Indicator
        indicator = IOIndicator(frame, highlightthickness=0)
        if not is_input:
            indicator.set_colors(color)
        indicator.pack(side=tk.LEFT, padx=5)
        self._indicators[key] = indicator

        # Name label
        ttk.Label(frame, text=name).pack(side=tk.LEFT)

    def _on_status_update(self, status: IOStatus) -> None:
        """Handle IO status update"""
        # Update connection indicator
        self.connection_indicator.set_state(status.connected)

        # Update input indicators
        if "trigger" in self._indicators:
            self._indicators["trigger"].set_state(status.trigger)
        if "enable" in self._indicators:
            self._indicators["enable"].set_state(status.system_enable)
        if "recipe_bit0" in self._indicators:
            self._indicators["recipe_bit0"].set_state(status.recipe_bit0)
        if "recipe_bit1" in self._indicators:
            self._indicators["recipe_bit1"].set_state(status.recipe_bit1)

        # Update output indicators
        if "ok" in self._indicators:
            self._indicators["ok"].set_state(status.result_ok)
        if "ng" in self._indicators:
            self._indicators["ng"].set_state(status.result_ng)
        if "ready" in self._indicators:
            self._indicators["ready"].set_state(status.system_ready)
        if "error" in self._indicators:
            self._indicators["error"].set_state(status.system_error)
        if "busy" in self._indicators:
            self._indicators["busy"].set_state(status.busy)

    def _toggle_io(self) -> None:
        """Toggle IO service"""
        if self._io_service.is_running:
            self._io_service.stop()
            self.start_btn.config(text="Start IO")
        else:
            if self._io_service.start():
                self.start_btn.config(text="Stop IO")

    def _on_sim_trigger(self) -> None:
        """Handle simulate trigger button"""
        self._io_service.sim_pulse_trigger()
        if self._on_trigger:
            self._on_trigger()

    def _on_sim_enable(self) -> None:
        """Handle simulate enable toggle"""
        self._io_service.sim_set_enable(self.enable_var.get())

    def _on_sim_recipe(self) -> None:
        """Handle simulate recipe change"""
        self._io_service.sim_set_recipe(self.recipe_var.get())

    def update_mode(self, mode: IOMode) -> None:
        """Update displayed mode"""
        self.mode_label.config(text=mode.value.upper())
