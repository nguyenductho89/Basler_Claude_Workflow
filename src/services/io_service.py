"""IO Service - PLC/IO communication service"""
import threading
import time
import logging
from typing import Callable, Optional, List
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum

from ..domain.io_config import IOConfig, IOStatus, IOMode

logger = logging.getLogger(__name__)


class IOCommand(Enum):
    """IO command types"""
    SET_OK = "set_ok"
    SET_NG = "set_ng"
    SET_READY = "set_ready"
    SET_ERROR = "set_error"
    SET_BUSY = "set_busy"
    PULSE_OK = "pulse_ok"
    PULSE_NG = "pulse_ng"


@dataclass
class IOCommandMessage:
    """IO command message"""
    command: IOCommand
    value: bool = True


class IOService:
    """
    IO Service for PLC communication

    Supports multiple modes:
    - SIMULATION: No hardware, simulated signals for testing
    - NI_DAQMX: National Instruments DAQmx (future)
    - ADVANTECH: Advantech USB-4750 (future)
    """

    def __init__(self, config: Optional[IOConfig] = None):
        self._config = config or IOConfig()
        self._status = IOStatus()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._command_queue: Queue[IOCommandMessage] = Queue(maxsize=100)

        # Callbacks
        self._trigger_callbacks: List[Callable[[], None]] = []
        self._status_callbacks: List[Callable[[IOStatus], None]] = []

        # Simulation state
        self._sim_inputs = {
            "trigger": False,
            "enable": True,
            "recipe_bit0": False,
            "recipe_bit1": False
        }
        self._sim_outputs = {
            "ok": False,
            "ng": False,
            "ready": False,
            "error": False,
            "busy": False
        }

        # Trigger debounce
        self._last_trigger_time = 0
        self._last_trigger_state = False

        logger.info(f"IOService initialized in {self._config.mode.value} mode")

    @property
    def config(self) -> IOConfig:
        """Get current config"""
        return self._config

    @property
    def status(self) -> IOStatus:
        """Get current IO status"""
        return self._status

    @property
    def is_running(self) -> bool:
        """Check if IO service is running"""
        return self._running

    def initialize(self, config: Optional[IOConfig] = None) -> bool:
        """
        Initialize IO hardware

        Args:
            config: Optional new configuration

        Returns:
            True if successful
        """
        if config:
            self._config = config

        try:
            if self._config.mode == IOMode.SIMULATION:
                self._status.connected = True
                self._status.error_message = ""
                logger.info("IO simulation mode initialized")
                return True

            elif self._config.mode == IOMode.NI_DAQMX:
                # TODO: Initialize NI-DAQmx
                # try:
                #     import nidaqmx
                #     self._task_di = nidaqmx.Task()
                #     self._task_do = nidaqmx.Task()
                #     ...
                # except ImportError:
                #     logger.error("nidaqmx not installed")
                #     return False
                logger.warning("NI-DAQmx mode not yet implemented, using simulation")
                self._config.mode = IOMode.SIMULATION
                self._status.connected = True
                return True

            elif self._config.mode == IOMode.ADVANTECH:
                # TODO: Initialize Advantech
                logger.warning("Advantech mode not yet implemented, using simulation")
                self._config.mode = IOMode.SIMULATION
                self._status.connected = True
                return True

        except Exception as e:
            self._status.connected = False
            self._status.error_message = str(e)
            logger.error(f"Failed to initialize IO: {e}")
            return False

        return False

    def start(self) -> bool:
        """Start IO polling thread"""
        if self._running:
            return True

        if not self._status.connected:
            if not self.initialize():
                return False

        self._running = True
        self._thread = threading.Thread(
            target=self._io_loop,
            name="IOThread",
            daemon=True
        )
        self._thread.start()

        # Set ready signal
        self.set_ready(True)
        logger.info("IO service started")
        return True

    def stop(self) -> None:
        """Stop IO polling thread"""
        self._running = False

        # Clear outputs
        self.set_ready(False)
        self.set_busy(False)
        self.set_error(False)

        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

        logger.info("IO service stopped")

    def cleanup(self) -> None:
        """Release IO resources"""
        self.stop()
        self._status.connected = False
        logger.info("IO service cleaned up")

    def _io_loop(self) -> None:
        """Main IO polling loop"""
        while self._running:
            try:
                # Process commands
                self._process_commands()

                # Read inputs
                self._read_inputs()

                # Update status
                self._update_status()

                # Notify status callbacks
                for callback in self._status_callbacks:
                    try:
                        callback(self._status)
                    except Exception as e:
                        logger.error(f"Status callback error: {e}")

                # Sleep for polling interval
                time.sleep(self._config.polling_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"IO loop error: {e}")
                time.sleep(0.1)

    def _process_commands(self) -> None:
        """Process pending IO commands"""
        while True:
            try:
                msg = self._command_queue.get_nowait()
                self._execute_command(msg)
            except Empty:
                break

    def _execute_command(self, msg: IOCommandMessage) -> None:
        """Execute IO command"""
        if msg.command == IOCommand.SET_OK:
            self._write_output("ok", msg.value)
        elif msg.command == IOCommand.SET_NG:
            self._write_output("ng", msg.value)
        elif msg.command == IOCommand.SET_READY:
            self._write_output("ready", msg.value)
        elif msg.command == IOCommand.SET_ERROR:
            self._write_output("error", msg.value)
        elif msg.command == IOCommand.SET_BUSY:
            self._write_output("busy", msg.value)
        elif msg.command == IOCommand.PULSE_OK:
            self._pulse_output("ok")
        elif msg.command == IOCommand.PULSE_NG:
            self._pulse_output("ng")

    def _read_inputs(self) -> None:
        """Read all digital inputs"""
        if self._config.mode == IOMode.SIMULATION:
            # Use simulated inputs
            trigger = self._sim_inputs["trigger"]
            enable = self._sim_inputs["enable"]
            recipe0 = self._sim_inputs["recipe_bit0"]
            recipe1 = self._sim_inputs["recipe_bit1"]
        else:
            # TODO: Read from hardware
            trigger = False
            enable = True
            recipe0 = False
            recipe1 = False

        # Trigger edge detection with debounce
        current_time = time.time() * 1000
        if trigger and not self._last_trigger_state:
            if current_time - self._last_trigger_time > self._config.trigger_debounce_ms:
                self._last_trigger_time = current_time
                self._on_trigger()

        self._last_trigger_state = trigger

        # Update status
        self._status.trigger = trigger
        self._status.system_enable = enable
        self._status.recipe_bit0 = recipe0
        self._status.recipe_bit1 = recipe1

    def _write_output(self, name: str, value: bool) -> None:
        """Write digital output"""
        if self._config.mode == IOMode.SIMULATION:
            self._sim_outputs[name] = value
        else:
            # TODO: Write to hardware
            pass

        logger.debug(f"IO output {name} = {value}")

    def _pulse_output(self, name: str) -> None:
        """Pulse digital output for configured duration"""
        self._write_output(name, True)
        time.sleep(self._config.result_pulse_ms / 1000.0)
        self._write_output(name, False)

    def _update_status(self) -> None:
        """Update output status from current state"""
        if self._config.mode == IOMode.SIMULATION:
            self._status.result_ok = self._sim_outputs["ok"]
            self._status.result_ng = self._sim_outputs["ng"]
            self._status.system_ready = self._sim_outputs["ready"]
            self._status.system_error = self._sim_outputs["error"]
            self._status.busy = self._sim_outputs["busy"]

    def _on_trigger(self) -> None:
        """Handle trigger signal"""
        logger.info("Trigger received")
        for callback in self._trigger_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Trigger callback error: {e}")

    # Public API

    def register_trigger_callback(self, callback: Callable[[], None]) -> None:
        """Register callback for trigger signal"""
        self._trigger_callbacks.append(callback)

    def register_status_callback(self, callback: Callable[[IOStatus], None]) -> None:
        """Register callback for status updates"""
        self._status_callbacks.append(callback)

    def set_ready(self, ready: bool) -> None:
        """Set system ready signal"""
        self._command_queue.put(IOCommandMessage(IOCommand.SET_READY, ready))

    def set_busy(self, busy: bool) -> None:
        """Set busy signal"""
        self._command_queue.put(IOCommandMessage(IOCommand.SET_BUSY, busy))

    def set_error(self, error: bool) -> None:
        """Set error signal"""
        self._command_queue.put(IOCommandMessage(IOCommand.SET_ERROR, error))

    def set_result(self, ok: bool) -> None:
        """
        Set inspection result with pulse

        Args:
            ok: True for OK result, False for NG result
        """
        if ok:
            self._command_queue.put(IOCommandMessage(IOCommand.PULSE_OK))
        else:
            self._command_queue.put(IOCommandMessage(IOCommand.PULSE_NG))

    # Simulation methods (for testing)

    def sim_set_trigger(self, value: bool) -> None:
        """[Simulation] Set trigger input"""
        if self._config.mode == IOMode.SIMULATION:
            self._sim_inputs["trigger"] = value

    def sim_set_enable(self, value: bool) -> None:
        """[Simulation] Set system enable input"""
        if self._config.mode == IOMode.SIMULATION:
            self._sim_inputs["enable"] = value

    def sim_set_recipe(self, index: int) -> None:
        """[Simulation] Set recipe index (0-3)"""
        if self._config.mode == IOMode.SIMULATION:
            self._sim_inputs["recipe_bit0"] = bool(index & 1)
            self._sim_inputs["recipe_bit1"] = bool(index & 2)

    def sim_pulse_trigger(self) -> None:
        """[Simulation] Generate trigger pulse"""
        if self._config.mode == IOMode.SIMULATION:
            self._sim_inputs["trigger"] = True
            # Trigger will be detected in next polling cycle
            threading.Timer(0.05, lambda: setattr(
                self, '_sim_inputs',
                {**self._sim_inputs, "trigger": False}
            )).start()
