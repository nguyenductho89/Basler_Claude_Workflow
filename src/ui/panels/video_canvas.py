"""Video Canvas - Display live camera feed"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import logging

import numpy as np
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class VideoCanvas(ttk.Frame):
    """Canvas for displaying live video from camera"""

    def __init__(self, parent, width: int = 800, height: int = 600):
        super().__init__(parent)

        self._display_width = width
        self._display_height = height
        self._photo_image: Optional[ImageTk.PhotoImage] = None
        self._current_frame: Optional[np.ndarray] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components"""
        # Main canvas
        self.canvas = tk.Canvas(self, width=self._display_width, height=self._display_height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Display placeholder text
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Show placeholder when no camera is connected"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self._display_width // 2,
            self._display_height // 2,
            text="No Camera Connected",
            fill="gray",
            font=("Arial", 16),
        )

    def update_frame(self, frame: np.ndarray) -> None:
        """
        Update the canvas with a new frame

        Args:
            frame: BGR image as numpy array
        """
        if frame is None:
            return

        try:
            self._current_frame = frame.copy()

            # Convert BGR to RGB
            rgb_frame = frame[:, :, ::-1]

            # Resize to fit display
            h, w = rgb_frame.shape[:2]
            scale = min(self._display_width / w, self._display_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)

            # Convert to PIL Image and resize
            pil_image = Image.fromarray(rgb_frame)
            pil_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            self._photo_image = ImageTk.PhotoImage(pil_image)

            # Calculate center position
            x = (self._display_width - new_w) // 2
            y = (self._display_height - new_h) // 2

            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(x, y, anchor=tk.NW, image=self._photo_image)

        except Exception as e:
            logger.error(f"Error updating frame: {e}")

    def clear(self) -> None:
        """Clear the canvas and show placeholder"""
        self._current_frame = None
        self._photo_image = None
        self._show_placeholder()

    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current displayed frame"""
        return self._current_frame

    def resize(self, width: int, height: int) -> None:
        """Resize the display area"""
        self._display_width = width
        self._display_height = height
        self.canvas.config(width=width, height=height)
