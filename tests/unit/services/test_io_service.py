"""Tests for IOService"""

import pytest
import time
from src.services.io_service import IOService
from src.domain.io_config import IOConfig, IOMode, IOStatus


class TestIOService:
    """Test IOService"""

    @pytest.fixture
    def io_service(self):
        """Create IO service in simulation mode"""
        service = IOService(IOConfig(mode=IOMode.SIMULATION))
        yield service
        if service.is_running:
            service.stop()
        service.cleanup()

    def test_default_config(self, io_service):
        """TC-IO-001: Default configuration"""
        assert io_service.config.mode == IOMode.SIMULATION
        assert io_service.config.trigger_channel == 0
        assert io_service.config.ok_channel == 0
        assert io_service.config.ng_channel == 1

    def test_initialize_simulation(self, io_service):
        """TC-IO-002: Initialize in simulation mode"""
        assert io_service.initialize()
        assert io_service.status.connected

    def test_start_stop(self, io_service):
        """TC-IO-003: Start and stop IO service"""
        io_service.initialize()

        assert io_service.start()
        assert io_service.is_running

        io_service.stop()
        assert not io_service.is_running

    def test_status_initial(self, io_service):
        """TC-IO-004: Initial status values"""
        status = io_service.status
        assert status.trigger == False
        assert status.system_enable == False
        assert status.connected == False

    def test_set_ready_signal(self, io_service):
        """TC-IO-005: Set ready signal"""
        io_service.initialize()
        io_service.start()

        io_service.set_ready(True)
        time.sleep(0.1)  # Wait for command to process

        assert io_service.status.system_ready == True

    def test_set_busy_signal(self, io_service):
        """TC-IO-006: Set busy signal"""
        io_service.initialize()
        io_service.start()

        io_service.set_busy(True)
        time.sleep(0.1)

        assert io_service.status.busy == True

    def test_set_error_signal(self, io_service):
        """TC-IO-007: Set error signal"""
        io_service.initialize()
        io_service.start()

        io_service.set_error(True)
        time.sleep(0.1)

        assert io_service.status.system_error == True

    def test_set_result_ok(self, io_service):
        """TC-IO-008: Set OK result (pulse)"""
        io_service.initialize()
        io_service.start()

        io_service.set_result(ok=True)
        # Result is a pulse, so we just verify no exception

    def test_set_result_ng(self, io_service):
        """TC-IO-009: Set NG result (pulse)"""
        io_service.initialize()
        io_service.start()

        io_service.set_result(ok=False)
        # Result is a pulse, so we just verify no exception

    def test_trigger_callback(self, io_service):
        """TC-IO-010: Trigger callback invocation"""
        triggered = []

        def on_trigger():
            triggered.append(True)

        io_service.register_trigger_callback(on_trigger)
        io_service.initialize()
        io_service.start()

        io_service.sim_pulse_trigger()
        time.sleep(0.2)  # Wait for trigger detection

        assert len(triggered) > 0

    def test_status_callback(self, io_service):
        """TC-IO-011: Status callback invocation"""
        statuses = []

        def on_status(status: IOStatus):
            statuses.append(status)

        io_service.register_status_callback(on_status)
        io_service.initialize()
        io_service.start()

        time.sleep(0.1)  # Wait for a few polling cycles

        assert len(statuses) > 0

    def test_sim_set_enable(self, io_service):
        """TC-IO-012: Simulation set enable"""
        io_service.initialize()
        io_service.start()

        io_service.sim_set_enable(True)
        time.sleep(0.1)

        assert io_service.status.system_enable == True

        io_service.sim_set_enable(False)
        time.sleep(0.1)

        assert io_service.status.system_enable == False

    def test_sim_set_recipe(self, io_service):
        """TC-IO-013: Simulation set recipe index"""
        io_service.initialize()
        io_service.start()

        # Test recipe index 0
        io_service.sim_set_recipe(0)
        time.sleep(0.1)
        assert io_service.status.recipe_index == 0

        # Test recipe index 2 (binary: 10)
        io_service.sim_set_recipe(2)
        time.sleep(0.1)
        assert io_service.status.recipe_index == 2

        # Test recipe index 3 (binary: 11)
        io_service.sim_set_recipe(3)
        time.sleep(0.1)
        assert io_service.status.recipe_index == 3

    def test_cleanup(self, io_service):
        """TC-IO-014: Cleanup releases resources"""
        io_service.initialize()
        io_service.start()
        io_service.cleanup()

        assert not io_service.is_running
        assert not io_service.status.connected

    def test_multiple_start_stop(self, io_service):
        """TC-IO-015: Multiple start/stop cycles"""
        io_service.initialize()

        for _ in range(3):
            io_service.start()
            assert io_service.is_running
            io_service.stop()
            assert not io_service.is_running
