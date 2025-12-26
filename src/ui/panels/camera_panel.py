"""Camera Panel - Camera connection controls"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class CameraPanel(ttk.LabelFrame):
    """Panel for camera connection controls"""

    def __init__(
        self,
        parent,
        on_connect: Optional[Callable[[int], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None,
        on_refresh: Optional[Callable[[], List[Dict]]] = None
    ):
        super().__init__(parent, text="Camera Connection", padding=10)

        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_refresh = on_refresh
        self._devices: List[Dict] = []
        self._is_connected = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Device selection row
        device_frame = ttk.Frame(self)
        device_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(device_frame, text="Device:").pack(side=tk.LEFT)

        self.device_combo = ttk.Combobox(
            device_frame,
            state="readonly",
            width=35
        )
        self.device_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.refresh_btn = ttk.Button(
            device_frame,
            text="Refresh",
            width=8,
            command=self._on_refresh_click
        )
        self.refresh_btn.pack(side=tk.LEFT)

        # Connection buttons row
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)

        self.connect_btn = ttk.Button(
            btn_frame,
            text="Connect",
            command=self._on_connect_click
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.disconnect_btn = ttk.Button(
            btn_frame,
            text="Disconnect",
            command=self._on_disconnect_click,
            state=tk.DISABLED
        )
        self.disconnect_btn.pack(side=tk.LEFT)

        # Status row
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)

        self.status_label = ttk.Label(
            status_frame,
            text="Disconnected",
            foreground="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

    def _on_refresh_click(self) -> None:
        """Handle refresh button click"""
        if self._on_refresh:
            try:
                self._devices = self._on_refresh()
                self._update_device_list()
            except Exception as e:
                logger.error(f"Error refreshing devices: {e}")
                messagebox.showerror("Error", f"Failed to refresh devices: {e}")

    def _on_connect_click(self) -> None:
        """Handle connect button click"""
        if not self._devices:
            messagebox.showwarning("Warning", "No devices available. Please refresh first.")
            return

        selected_index = self.device_combo.current()
        if selected_index < 0:
            messagebox.showwarning("Warning", "Please select a device.")
            return

        if self._on_connect:
            try:
                self._on_connect(selected_index)
            except Exception as e:
                logger.error(f"Error connecting: {e}")
                messagebox.showerror("Error", f"Failed to connect: {e}")

    def _on_disconnect_click(self) -> None:
        """Handle disconnect button click"""
        if self._on_disconnect:
            try:
                self._on_disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
                messagebox.showerror("Error", f"Failed to disconnect: {e}")

    def _update_device_list(self) -> None:
        """Update the device combobox with found devices"""
        device_names = []
        for dev in self._devices:
            name = f"{dev['model']} ({dev['serial']})"
            if dev.get('ip') and dev['ip'] != 'N/A':
                name += f" - {dev['ip']}"
            device_names.append(name)

        self.device_combo['values'] = device_names

        if device_names:
            self.device_combo.current(0)
            logger.info(f"Found {len(device_names)} device(s)")
        else:
            self.device_combo.set("")
            logger.info("No devices found")

    def set_connected(self, connected: bool, device_info: Optional[Dict] = None) -> None:
        """
        Update UI state based on connection status

        Args:
            connected: Whether camera is connected
            device_info: Optional device information
        """
        self._is_connected = connected

        if connected:
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.device_combo.config(state=tk.DISABLED)
            self.refresh_btn.config(state=tk.DISABLED)

            device_name = device_info.get('name', 'Unknown') if device_info else 'Unknown'
            self.status_label.config(text=f"Connected: {device_name}", foreground="green")
        else:
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
            self.device_combo.config(state="readonly")
            self.refresh_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Disconnected", foreground="red")

    def get_devices(self) -> List[Dict]:
        """Get list of found devices"""
        return self._devices
