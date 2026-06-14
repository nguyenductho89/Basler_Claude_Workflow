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

    FREERUN = "freerun"  # Continuous acquisition, no trigger needed
    SOFTWARE = "software"  # Software trigger, need to call execute_software_trigger()
    HARDWARE = "hardware"  # Hardware trigger from external signal (Line1)


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
    def list_devices(gige_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all available Basler cameras

        Args:
            gige_only: If True, only return GigE cameras (default: True)
        """
        if not PYLON_AVAILABLE:
            logger.warning("pypylon not available")
            return []

        devices = []
        try:
            tlFactory = pylon.TlFactory.GetInstance()

            if gige_only:
                # Create filter for GigE devices only
                device_filter = [pylon.DeviceInfo()]
                device_filter[0].SetDeviceClass("BaslerGigE")
                logger.info("Scanning for GigE cameras...")
                device_infos = tlFactory.EnumerateDevices(device_filter)
            else:
                logger.info("Scanning for all cameras...")
                device_infos = tlFactory.EnumerateDevices()

            logger.info(f"EnumerateDevices returned {len(device_infos)} device(s)")

            for i, dev_info in enumerate(device_infos):
                device_class = dev_info.GetDeviceClass()
                ip_address = "N/A"

                # Get IP address for GigE devices
                if device_class == "BaslerGigE":
                    try:
                        ip_address = dev_info.GetIpAddress()
                    except Exception:
                        ip_address = "N/A"

                devices.append(
                    {
                        "index": i,
                        "model": dev_info.GetModelName(),
                        "serial": dev_info.GetSerialNumber(),
                        "ip": ip_address,
                        "name": dev_info.GetFriendlyName(),
                        "vendor": dev_info.GetVendorName(),
                        "device_class": device_class,
                    }
                )
                logger.info(f"Found camera: {dev_info.GetFriendlyName()} ({device_class}) IP: {ip_address}")

        except Exception as e:
            logger.error(f"Error enumerating devices: {e}", exc_info=True)

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

            # Use GigE filter to match list_devices behavior
            device_filter = [pylon.DeviceInfo()]
            device_filter[0].SetDeviceClass("BaslerGigE")
            devices = tlFactory.EnumerateDevices(device_filter)

            if device_index >= len(devices):
                logger.error(f"Device index {device_index} out of range (found {len(devices)} GigE devices)")
                return False

            logger.info(f"Connecting to device {device_index}: {devices[device_index].GetFriendlyName()}")
            self._camera = pylon.InstantCamera(tlFactory.CreateDevice(devices[device_index]))
            self._camera.Open()

            # Store device info
            ip_address = "N/A"
            try:
                ip_address = devices[device_index].GetIpAddress()
            except Exception:
                pass

            self._device_info = {
                "model": devices[device_index].GetModelName(),
                "serial": devices[device_index].GetSerialNumber(),
                "name": devices[device_index].GetFriendlyName(),
                "ip": ip_address,
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

            # Set free-run mode by default (continuous acquisition)
            self._camera.TriggerMode.SetValue("Off")
            self._trigger_mode = TriggerMode.FREERUN

            logger.info(f"Camera configured: exposure={exposure_us}us, trigger=freerun")

        except Exception as e:
            logger.warning(f"Error configuring camera: {e}")

    def set_trigger_mode(self, mode: str) -> bool:
        """
        Set camera trigger mode

        Args:
            mode: TriggerMode.FREERUN, TriggerMode.SOFTWARE, or TriggerMode.HARDWARE

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
            elif mode == TriggerMode.SOFTWARE:
                # Configure for software trigger
                self._camera.TriggerMode.SetValue("On")
                self._camera.TriggerSource.SetValue("Software")
                self._trigger_mode = TriggerMode.SOFTWARE
                logger.info("Software trigger mode enabled")
            else:
                # Configure for free-run mode (continuous)
                self._camera.TriggerMode.SetValue("Off")
                self._trigger_mode = TriggerMode.FREERUN
                logger.info("Free-run mode enabled (continuous)")

            return True

        except Exception as e:
            logger.error(f"Failed to set trigger mode: {e}")
            return False

    def execute_software_trigger(self) -> bool:
        """
        Execute a software trigger to capture one frame

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            return False

        try:
            if self._trigger_mode == TriggerMode.SOFTWARE:
                # Execute software trigger in software trigger mode
                self._camera.TriggerSoftware.Execute()
                logger.debug("Software trigger executed")
            elif self._trigger_mode == TriggerMode.HARDWARE:
                # Temporarily switch to software trigger for single shot
                self._camera.TriggerSource.SetValue("Software")
                self._camera.TriggerSoftware.Execute()
                # Switch back to hardware trigger
                self._camera.TriggerSource.SetValue("Line1")
                logger.debug("Software trigger executed (override hardware)")
            else:
                # Free-run mode - no trigger needed
                logger.debug("Camera in free-run mode, trigger ignored")
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

    def get_exposure_range(self) -> tuple:
        """Get exposure range (min, max) in microseconds from camera hardware"""
        if not self._camera or not self._is_connected:
            return (35.0, 1_000_000.0)
        try:
            if hasattr(self._camera, "ExposureTimeAbs"):
                return (self._camera.ExposureTimeAbs.GetMin(), self._camera.ExposureTimeAbs.GetMax())
            elif hasattr(self._camera, "ExposureTime"):
                return (self._camera.ExposureTime.GetMin(), self._camera.ExposureTime.GetMax())
        except Exception as e:
            logger.warning(f"Failed to get exposure range: {e}")
        return (35.0, 1_000_000.0)

    def set_exposure(self, exposure_us: float) -> None:
        """
        Set exposure time

        Args:
            exposure_us: Exposure time in microseconds (clamped to camera hardware limits)
        """
        if not self._camera or not self._is_connected:
            return

        try:
            if hasattr(self._camera, "ExposureTimeAbs"):
                min_exp = self._camera.ExposureTimeAbs.GetMin()
                max_exp = self._camera.ExposureTimeAbs.GetMax()
                clamped = max(min_exp, min(max_exp, exposure_us))
                if clamped != exposure_us:
                    logger.warning(
                        f"Exposure {exposure_us}us out of range [{min_exp}, {max_exp}], clamped to {clamped}us"
                    )
                self._camera.ExposureTimeAbs.SetValue(clamped)
            elif hasattr(self._camera, "ExposureTime"):
                min_exp = self._camera.ExposureTime.GetMin()
                max_exp = self._camera.ExposureTime.GetMax()
                clamped = max(min_exp, min(max_exp, exposure_us))
                if clamped != exposure_us:
                    logger.warning(
                        f"Exposure {exposure_us}us out of range [{min_exp}, {max_exp}], clamped to {clamped}us"
                    )
                self._camera.ExposureTime.SetValue(clamped)
            logger.info(f"Exposure set to {clamped}us")
        except Exception as e:
            logger.error(f"Failed to set exposure: {e}")

    def set_gain(self, gain_db: float) -> bool:
        """
        Set camera gain

        Args:
            gain_db: Gain value in dB (typically 0-24 dB for Basler cameras)

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            return False

        try:
            # Disable auto gain first
            if hasattr(self._camera, "GainAuto"):
                self._camera.GainAuto.SetValue("Off")

            # Set gain value (GainRaw for older cameras, Gain for newer)
            if hasattr(self._camera, "GainRaw"):
                # Convert dB to raw value (approximate)
                self._camera.GainRaw.SetValue(int(gain_db * 10))
            elif hasattr(self._camera, "Gain"):
                self._camera.Gain.SetValue(gain_db)

            logger.info(f"Gain set to {gain_db} dB")
            return True
        except Exception as e:
            logger.error(f"Failed to set gain: {e}")
            return False

    def get_gain(self) -> float:
        """Get current gain value in dB"""
        if not self._camera or not self._is_connected:
            return 0.0

        try:
            if hasattr(self._camera, "Gain"):
                return self._camera.Gain.GetValue()
            elif hasattr(self._camera, "GainRaw"):
                return self._camera.GainRaw.GetValue() / 10.0
        except Exception as e:
            logger.warning(f"Failed to get gain: {e}")
        return 0.0

    def get_gain_range(self) -> tuple:
        """Get gain range (min, max) in dB"""
        if not self._camera or not self._is_connected:
            return (0.0, 24.0)

        try:
            if hasattr(self._camera, "Gain"):
                return (self._camera.Gain.GetMin(), self._camera.Gain.GetMax())
            elif hasattr(self._camera, "GainRaw"):
                return (self._camera.GainRaw.GetMin() / 10.0, self._camera.GainRaw.GetMax() / 10.0)
        except Exception as e:
            logger.warning(f"Failed to get gain range: {e}")
        return (0.0, 24.0)

    def set_gamma(self, gamma: float) -> bool:
        """
        Set camera gamma correction

        Args:
            gamma: Gamma value (typically 0.25-2.0, 1.0 = no correction)

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            return False

        try:
            # Enable gamma correction
            if hasattr(self._camera, "GammaEnable"):
                self._camera.GammaEnable.SetValue(True)

            # Set gamma value
            if hasattr(self._camera, "Gamma"):
                self._camera.Gamma.SetValue(gamma)
                logger.info(f"Gamma set to {gamma}")
                return True
            else:
                logger.warning("Camera does not support Gamma adjustment")
                return False
        except Exception as e:
            logger.error(f"Failed to set gamma: {e}")
            return False

    def get_gamma(self) -> float:
        """Get current gamma value"""
        if not self._camera or not self._is_connected:
            return 1.0

        try:
            if hasattr(self._camera, "Gamma"):
                return self._camera.Gamma.GetValue()
        except Exception as e:
            logger.warning(f"Failed to get gamma: {e}")
        return 1.0

    def get_gamma_range(self) -> tuple:
        """Get gamma range (min, max)"""
        if not self._camera or not self._is_connected:
            return (0.25, 2.0)

        try:
            if hasattr(self._camera, "Gamma"):
                return (self._camera.Gamma.GetMin(), self._camera.Gamma.GetMax())
        except Exception as e:
            logger.warning(f"Failed to get gamma range: {e}")
        return (0.25, 2.0)

    def set_sharpness(self, sharpness: float) -> bool:
        """
        Set camera sharpness enhancement

        Args:
            sharpness: Sharpness value (typically 0-1.0 or 0-4.0 depending on camera)

        Returns:
            True if successful
        """
        if not self._camera or not self._is_connected:
            return False

        try:
            # Try different sharpness parameter names used by Basler cameras
            if hasattr(self._camera, "SharpnessEnhancement"):
                self._camera.SharpnessEnhancement.SetValue(sharpness)
                logger.info(f"SharpnessEnhancement set to {sharpness}")
                return True
            elif hasattr(self._camera, "DemosaicingMode"):
                # Some cameras use DemosaicingMode for sharpness
                # BaslerPGI mode enables sharpening
                if sharpness > 0:
                    self._camera.DemosaicingMode.SetValue("BaslerPGI")
                    if hasattr(self._camera, "NoiseReduction"):
                        self._camera.NoiseReduction.SetValue(max(0, 1.0 - sharpness))
                    if hasattr(self._camera, "SharpnessEnhancement"):
                        self._camera.SharpnessEnhancement.SetValue(sharpness)
                else:
                    self._camera.DemosaicingMode.SetValue("Simple")
                logger.info(f"Sharpness mode set (BaslerPGI: {sharpness > 0})")
                return True
            else:
                logger.warning("Camera does not support Sharpness adjustment")
                return False
        except Exception as e:
            logger.error(f"Failed to set sharpness: {e}")
            return False

    def get_sharpness(self) -> float:
        """Get current sharpness value"""
        if not self._camera or not self._is_connected:
            return 0.0

        try:
            if hasattr(self._camera, "SharpnessEnhancement"):
                return self._camera.SharpnessEnhancement.GetValue()
        except Exception as e:
            logger.warning(f"Failed to get sharpness: {e}")
        return 0.0

    def get_sharpness_range(self) -> tuple:
        """Get sharpness range (min, max)"""
        if not self._camera or not self._is_connected:
            return (0.0, 4.0)

        try:
            if hasattr(self._camera, "SharpnessEnhancement"):
                return (
                    self._camera.SharpnessEnhancement.GetMin(),
                    self._camera.SharpnessEnhancement.GetMax(),
                )
        except Exception as e:
            logger.warning(f"Failed to get sharpness range: {e}")
        return (0.0, 4.0)

    def has_sharpness_support(self) -> bool:
        """Check if camera supports sharpness enhancement"""
        if not self._camera or not self._is_connected:
            return False

        try:
            return hasattr(self._camera, "SharpnessEnhancement") or hasattr(self._camera, "DemosaicingMode")
        except:
            return False

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

                # Add gain, gamma, sharpness info
                info["gain_db"] = self.get_gain()
                info["gamma"] = self.get_gamma()
                info["sharpness"] = self.get_sharpness()
                info["has_sharpness"] = self.has_sharpness_support()
            except:
                pass

        return info
