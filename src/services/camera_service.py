"""Camera Service - Basler GigE Camera Management"""

import logging
from typing import List, Dict, Any, Optional

import numpy as np

try:
    from pypylon import pylon

    PYLON_AVAILABLE = True
except ImportError:
    PYLON_AVAILABLE = False
    pylon = None

logger = logging.getLogger(__name__)


class TriggerMode:
    """Camera trigger mode constants"""

    SOFTWARE = "software"
    HARDWARE = "hardware"


class BaslerGigECamera:
    """Service for managing Basler GigE camera connection and frame grabbing"""

    def __init__(self):
        self._camera: Optional[Any] = None
        self._converter: Optional[Any] = None
        self._is_connected: bool = False
        self._is_grabbing: bool = False
        self._device_info: Optional[Dict] = None
        self._trigger_mode: str = TriggerMode.SOFTWARE

        if PYLON_AVAILABLE:
            self._converter = pylon.ImageFormatConverter()
            self._converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self._converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    @property
    def is_connected(self) -> bool:
        """Check if camera is connected"""
        return self._is_connected

    @property
    def is_grabbing(self) -> bool:
        """Check if camera is grabbing"""
        return self._is_grabbing

    @property
    def device_info(self) -> Optional[Dict]:
        """Get connected device info"""
        return self._device_info

    @property
    def trigger_mode(self) -> str:
        """Get current trigger mode"""
        return self._trigger_mode

    @staticmethod
    def list_devices() -> List[Dict[str, Any]]:
        """List all available Basler GigE cameras"""
        if not PYLON_AVAILABLE:
            logger.warning("pypylon not available")
            return []

        devices = []
        try:
            tlFactory = pylon.TlFactory.GetInstance()
            device_infos = tlFactory.EnumerateDevices()

            for i, dev_info in enumerate(device_infos):
                devices.append(
                    {
                        "index": i,
                        "model": dev_info.GetModelName(),
                        "serial": dev_info.GetSerialNumber(),
                        "ip": dev_info.GetIpAddress() if hasattr(dev_info, "GetIpAddress") else "N/A",
                        "name": dev_info.GetFriendlyName(),
                        "vendor": dev_info.GetVendorName(),
                    }
                )
                logger.info(f"Found camera: {dev_info.GetFriendlyName()}")

        except Exception as e:
            logger.error(f"Error enumerating devices: {e}")

        return devices

    def connect(self, device_index: int = 0, exposure_us: float = 50.0) -> bool:
        """
        Connect to camera by index

        Args:
            device_index: Index of the camera to connect to
            exposure_us: Initial exposure time in microseconds

        Returns:
            True if connection successful, False otherwise
        """
        if not PYLON_AVAILABLE:
            logger.error("pypylon not available - cannot connect to camera")
            return False

        if self._is_connected:
            logger.warning("Already connected to a camera")
            return True

        try:
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()

            if device_index >= len(devices):
                logger.error(f"Device index {device_index} out of range (found {len(devices)} devices)")
                return False

            self._camera = pylon.InstantCamera(tlFactory.CreateDevice(devices[device_index]))
            self._camera.Open()

            # Store device info
            self._device_info = {
                "model": devices[device_index].GetModelName(),
                "serial": devices[device_index].GetSerialNumber(),
                "name": devices[device_index].GetFriendlyName(),
            }

            # Configure camera
            self._configure_camera(exposure_us)

            self._is_connected = True
            logger.info(f"Connected to camera: {self._device_info['name']}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to camera: {e}")
            self._camera = None
            self._is_connected = False
            return False

    def _configure_camera(self, exposure_us: float) -> None:
        """Configure camera settings"""
        if not self._camera:
            return

        try:
            # Set exposure time
            if hasattr(self._camera, "ExposureTimeAbs"):
                self._camera.ExposureTimeAbs.SetValue(exposure_us)
            elif hasattr(self._camera, "ExposureTime"):
                self._camera.ExposureTime.SetValue(exposure_us)

            # Set software trigger mode by default
            self._camera.TriggerMode.SetValue("Off")
            self._trigger_mode = TriggerMode.SOFTWARE

            logger.info(f"Camera configured: exposure={exposure_us}us, trigger=software")

        except Exception as e:
            logger.warning(f"Error configuring camera: {e}")

    def set_trigger_mode(self, mode: str) -> bool:
        """
        Set camera trigger mode

        Args:
            mode: TriggerMode.SOFTWARE or TriggerMode.HARDWARE

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            logger.warning("Cannot set trigger mode - camera not connected")
            return False

        try:
            if mode == TriggerMode.HARDWARE:
                # Configure for hardware trigger (Line1)
                self._camera.TriggerMode.SetValue("On")
                self._camera.TriggerSource.SetValue("Line1")
                self._camera.TriggerActivation.SetValue("RisingEdge")
                self._trigger_mode = TriggerMode.HARDWARE
                logger.info("Hardware trigger mode enabled (Line1, Rising Edge)")
            else:
                # Configure for continuous/software mode
                self._camera.TriggerMode.SetValue("Off")
                self._trigger_mode = TriggerMode.SOFTWARE
                logger.info("Software trigger mode enabled (continuous)")

            return True

        except Exception as e:
            logger.error(f"Failed to set trigger mode: {e}")
            return False

    def execute_software_trigger(self) -> bool:
        """
        Execute a software trigger (for testing in hardware trigger mode)

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            return False

        try:
            if self._trigger_mode == TriggerMode.HARDWARE:
                # Temporarily switch to software trigger for single shot
                self._camera.TriggerSource.SetValue("Software")
                self._camera.TriggerSoftware.Execute()
                # Switch back to hardware trigger
                self._camera.TriggerSource.SetValue("Line1")
            logger.debug("Software trigger executed")
            return True
        except Exception as e:
            logger.error(f"Failed to execute software trigger: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from camera"""
        if self._camera:
            try:
                if self._is_grabbing:
                    self.stop_grabbing()
                self._camera.Close()
                logger.info("Camera disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting camera: {e}")
            finally:
                self._camera = None
                self._is_connected = False
                self._device_info = None

    def start_grabbing(self) -> None:
        """Start continuous frame grabbing"""
        if not self._is_connected or not self._camera:
            logger.warning("Cannot start grabbing - camera not connected")
            return

        if self._is_grabbing:
            return

        try:
            self._camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self._is_grabbing = True
            logger.info("Started grabbing")
        except Exception as e:
            logger.error(f"Failed to start grabbing: {e}")

    def stop_grabbing(self) -> None:
        """Stop frame grabbing"""
        if self._camera and self._is_grabbing:
            try:
                self._camera.StopGrabbing()
                self._is_grabbing = False
                logger.info("Stopped grabbing")
            except Exception as e:
                logger.error(f"Error stopping grabbing: {e}")

    def grab_frame(self, timeout_ms: int = 1000) -> Optional[np.ndarray]:
        """
        Grab a single frame from the camera

        Args:
            timeout_ms: Timeout in milliseconds

        Returns:
            BGR image as numpy array, or None if grab failed
        """
        if not self._is_connected or not self._camera:
            return None

        if not self._is_grabbing:
            self.start_grabbing()

        try:
            grab_result = self._camera.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                # Convert to BGR format
                image = self._converter.Convert(grab_result)
                frame = image.GetArray().copy()
                grab_result.Release()
                return frame
            else:
                logger.warning(f"Grab failed: {grab_result.ErrorCode} - {grab_result.ErrorDescription}")
                grab_result.Release()
                return None

        except Exception as e:
            logger.error(f"Error grabbing frame: {e}")
            return None

    def set_exposure(self, exposure_us: float) -> None:
        """
        Set exposure time

        Args:
            exposure_us: Exposure time in microseconds
        """
        if not self._camera or not self._is_connected:
            return

        try:
            if hasattr(self._camera, "ExposureTimeAbs"):
                self._camera.ExposureTimeAbs.SetValue(exposure_us)
            elif hasattr(self._camera, "ExposureTime"):
                self._camera.ExposureTime.SetValue(exposure_us)
            logger.info(f"Exposure set to {exposure_us}us")
        except Exception as e:
            logger.error(f"Failed to set exposure: {e}")

    def get_info(self) -> Dict[str, Any]:
        """Get camera information"""
        if not self._is_connected:
            return {"connected": False}

        info = {"connected": True, **self._device_info}

        if self._camera:
            try:
                if hasattr(self._camera, "ExposureTimeAbs"):
                    info["exposure_us"] = self._camera.ExposureTimeAbs.GetValue()
                elif hasattr(self._camera, "ExposureTime"):
                    info["exposure_us"] = self._camera.ExposureTime.GetValue()
            except:
                pass

        return info
