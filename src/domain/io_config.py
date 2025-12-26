"""IO Configuration - PLC/IO interface settings"""

from dataclasses import dataclass, field
from typing import Dict
from enum import Enum


class IOMode(Enum):
    """IO operation mode"""

    SIMULATION = "simulation"  # No hardware, simulated signals
    NI_DAQMX = "ni_daqmx"  # National Instruments DAQmx
    ADVANTECH = "advantech"  # Advantech USB-4750


@dataclass
class IOConfig:
    """I/O card configuration"""

    # Device settings
    mode: IOMode = IOMode.SIMULATION
    device_name: str = "Dev1"  # NI-DAQmx device name

    # Digital Input channels (from PLC)
    trigger_channel: int = 0  # DI-0: Trigger signal
    enable_channel: int = 1  # DI-1: System enable
    recipe_bit0_channel: int = 2  # DI-2: Recipe select bit 0
    recipe_bit1_channel: int = 3  # DI-3: Recipe select bit 1

    # Digital Output channels (to PLC)
    ok_channel: int = 0  # DO-0: Result OK
    ng_channel: int = 1  # DO-1: Result NG
    ready_channel: int = 2  # DO-2: System ready
    error_channel: int = 3  # DO-3: System error
    busy_channel: int = 4  # DO-4: Busy processing

    # Timing settings
    trigger_debounce_ms: int = 10  # Trigger debounce time
    result_pulse_ms: int = 100  # OK/NG pulse duration
    polling_interval_ms: int = 5  # Input polling interval

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "mode": self.mode.value,
            "device_name": self.device_name,
            "trigger_channel": self.trigger_channel,
            "enable_channel": self.enable_channel,
            "recipe_bit0_channel": self.recipe_bit0_channel,
            "recipe_bit1_channel": self.recipe_bit1_channel,
            "ok_channel": self.ok_channel,
            "ng_channel": self.ng_channel,
            "ready_channel": self.ready_channel,
            "error_channel": self.error_channel,
            "busy_channel": self.busy_channel,
            "trigger_debounce_ms": self.trigger_debounce_ms,
            "result_pulse_ms": self.result_pulse_ms,
            "polling_interval_ms": self.polling_interval_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "IOConfig":
        """Create from dictionary"""
        mode_str = data.get("mode", "simulation")
        try:
            mode = IOMode(mode_str)
        except ValueError:
            mode = IOMode.SIMULATION

        return cls(
            mode=mode,
            device_name=data.get("device_name", "Dev1"),
            trigger_channel=data.get("trigger_channel", 0),
            enable_channel=data.get("enable_channel", 1),
            recipe_bit0_channel=data.get("recipe_bit0_channel", 2),
            recipe_bit1_channel=data.get("recipe_bit1_channel", 3),
            ok_channel=data.get("ok_channel", 0),
            ng_channel=data.get("ng_channel", 1),
            ready_channel=data.get("ready_channel", 2),
            error_channel=data.get("error_channel", 3),
            busy_channel=data.get("busy_channel", 4),
            trigger_debounce_ms=data.get("trigger_debounce_ms", 10),
            result_pulse_ms=data.get("result_pulse_ms", 100),
            polling_interval_ms=data.get("polling_interval_ms", 5),
        )


@dataclass
class IOStatus:
    """Current IO status"""

    # Digital inputs
    trigger: bool = False
    system_enable: bool = False
    recipe_bit0: bool = False
    recipe_bit1: bool = False

    # Digital outputs
    result_ok: bool = False
    result_ng: bool = False
    system_ready: bool = False
    system_error: bool = False
    busy: bool = False

    # Connection status
    connected: bool = False
    error_message: str = ""

    @property
    def recipe_index(self) -> int:
        """Get recipe index from recipe bits"""
        return (int(self.recipe_bit1) << 1) | int(self.recipe_bit0)
