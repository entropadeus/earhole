"""
Earworm - GUI window for STT status display.
Shows recording status and provides visual feedback with animations.
"""

import tkinter as tk
from tkinter import ttk
import threading
import math
from typing import Callable, Optional, List
from PIL import Image, ImageDraw, ImageTk


def create_ear_icon(size: int = 32, color: str = "#4CAF50") -> Image.Image:
    """Create an ear-shaped icon programmatically."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size / 64

    margin = int(2 * s)
    draw.ellipse([margin, margin, size - margin, size - margin],
                 fill="#1e1e1e", outline=color, width=max(1, int(2 * s)))

    ear_points = [
        (40 * s, 12 * s), (50 * s, 20 * s), (52 * s, 32 * s),
        (48 * s, 44 * s), (40 * s, 50 * s), (32 * s, 50 * s),
        (28 * s, 46 * s), (30 * s, 40 * s), (34 * s, 44 * s),
        (40 * s, 40 * s), (44 * s, 32 * s), (42 * s, 22 * s),
        (34 * s, 16 * s), (26 * s, 20 * s), (22 * s, 30 * s),
        (24 * s, 42 * s),
    ]

    for i in range(len(ear_points) - 1):
        draw.line([ear_points[i], ear_points[i + 1]], fill=color, width=max(2, int(3 * s)))

    wave_color = color
    draw.arc([int(8 * s), int(24 * s), int(18 * s), int(40 * s)],
             start=60, end=300, fill=wave_color, width=max(1, int(2 * s)))
    draw.arc([int(2 * s), int(20 * s), int(14 * s), int(44 * s)],
             start=60, end=300, fill=wave_color, width=max(1, int(2 * s)))

    return img


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def lerp_color(color1: str, color2: str, t: float) -> str:
    """Linearly interpolate between two hex colors."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = r1 + (r2 - r1) * t
    g = g1 + (g2 - g1) * t
    b = b1 + (b2 - b1) * t
    return rgb_to_hex((r, g, b))


class StatusWindow:
    """A small always-on-top window showing Earworm status with animations."""

    STATE_IDLE = "idle"
    STATE_RECORDING = "recording"
    STATE_PROCESSING = "processing"

    # Color scheme
    COLORS = {
        "bg": "#0d0d0d",
        "bg_secondary": "#1a1a1a",
        "idle": "#00d26a",
        "idle_glow": "#00ff80",
        "recording": "#ff4757",
        "recording_glow": "#ff6b7a",
        "processing": "#ffa502",
        "processing_glow": "#ffbe33",
        "text": "#ffffff",
        "text_dim": "#888888",
    }

    def __init__(self):
        self._root: Optional[tk.Tk] = None
        self._canvas: Optional[tk.Canvas] = None
        self._state = self.STATE_IDLE
        self._callbacks = {}
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()
        self._icon_photo = None
        self._animation_id = None
        self._animation_frame = 0
        self._soundwave_bars: List[int] = []
        self._loader_arc = None
        self._glow_circle = None
        self._text_id = None
        self._subtext_id = None
        self._pulse_phase = 0
        self._drag_x = 0
        self._drag_y = 0

    def _create_window(self) -> None:
        """Create the tkinter window with canvas-based UI."""
        self._root = tk.Tk()
        self._root.title("Earworm")
        self._root.attributes('-topmost', True)
        self._root.resizable(False, False)
        self._root.overrideredirect(True)  # Borderless window

        # Set window icon
        try:
            icon = create_ear_icon(32, self.COLORS["idle"])
            self._icon_photo = ImageTk.PhotoImage(icon)
            self._root.iconphoto(True, self._icon_photo)
        except (tk.TclError, OSError):
            pass

        # Window dimensions
        width, height = 200, 80
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()

        # Position bottom-right with padding
        x = screen_w - width - 20
        y = screen_h - height - 60
        self._root.geometry(f"{width}x{height}+{x}+{y}")

        # Main canvas
        self._canvas = tk.Canvas(
            self._root,
            width=width,
            height=height,
            bg=self.COLORS["bg"],
            highlightthickness=0
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # Draw rounded rectangle background
        self._draw_rounded_rect(2, 2, width - 2, height - 2, 16, self.COLORS["bg_secondary"])

        # Initial state setup
        self._setup_idle_state()

        # Handle window close via right-click
        self._canvas.bind("<Button-3>", lambda e: self._on_close())

        # Allow dragging
        self._canvas.bind("<Button-1>", self._start_drag)
        self._canvas.bind("<B1-Motion>", self._drag)

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._ready.set()

        # Start animation loop
        self._animate()

    def _draw_rounded_rect(self, x1: int, y1: int, x2: int, y2: int, radius: int, color: str, tag: str = None) -> int:
        """Draw a rounded rectangle on the canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1,
        ]
        return self._canvas.create_polygon(points, fill=color, smooth=True, tags=tag)

    def _start_drag(self, event):
        """Start window drag."""
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag(self, event):
        """Drag window."""
        x = self._root.winfo_x() + (event.x - self._drag_x)
        y = self._root.winfo_y() + (event.y - self._drag_y)
        self._root.geometry(f"+{x}+{y}")

    def _clear_animations(self) -> None:
        """Clear all animated elements."""
        self._canvas.delete("animated")
        self._soundwave_bars = []
        self._loader_arc = None
        self._glow_circle = None

    def _setup_idle_state(self) -> None:
        """Setup the idle/ready state visuals."""
        self._clear_animations()

        # Glow circle (will pulse)
        cx, cy = 36, 40
        self._glow_circle = self._canvas.create_oval(
            cx - 12, cy - 12, cx + 12, cy + 12,
            fill=self.COLORS["idle"],
            outline="",
            tags="animated"
        )

        # Status text
        self._text_id = self._canvas.create_text(
            115, 32,
            text="Ready",
            font=("Segoe UI", 14, "bold"),
            fill=self.COLORS["idle"],
            tags="animated"
        )

        self._subtext_id = self._canvas.create_text(
            115, 52,
            text="Hold F9 to speak",
            font=("Segoe UI", 9),
            fill=self.COLORS["text_dim"],
            tags="animated"
        )

    def _setup_recording_state(self) -> None:
        """Setup the recording state with soundwave animation."""
        self._clear_animations()

        # Create soundwave bars
        bar_count = 5
        bar_width = 4
        bar_spacing = 7
        start_x = 20
        center_y = 40

        for i in range(bar_count):
            x = start_x + i * bar_spacing
            bar = self._canvas.create_rectangle(
                x, center_y - 8,
                x + bar_width, center_y + 8,
                fill=self.COLORS["recording"],
                outline="",
                tags="animated"
            )
            self._soundwave_bars.append(bar)

        # Status text
        self._text_id = self._canvas.create_text(
            125, 32,
            text="Listening",
            font=("Segoe UI", 14, "bold"),
            fill=self.COLORS["recording"],
            tags="animated"
        )

        self._subtext_id = self._canvas.create_text(
            125, 52,
            text="Release to finish",
            font=("Segoe UI", 9),
            fill=self.COLORS["text_dim"],
            tags="animated"
        )

    def _setup_processing_state(self) -> None:
        """Setup the processing/transcribing state with spinner."""
        self._clear_animations()

        cx, cy = 36, 40
        radius = 14

        # Background circle
        self._canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline=self.COLORS["bg"],
            width=3,
            tags="animated"
        )

        # Spinning arc (loader)
        self._loader_arc = self._canvas.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=0,
            extent=90,
            style=tk.ARC,
            outline=self.COLORS["processing"],
            width=3,
            tags="animated"
        )

        # Status text
        self._text_id = self._canvas.create_text(
            125, 32,
            text="Transcribing",
            font=("Segoe UI", 14, "bold"),
            fill=self.COLORS["processing"],
            tags="animated"
        )

        self._subtext_id = self._canvas.create_text(
            125, 52,
            text="Please wait...",
            font=("Segoe UI", 9),
            fill=self.COLORS["text_dim"],
            tags="animated"
        )

    def _animate(self) -> None:
        """Main animation loop."""
        if self._canvas is None or self._root is None:
            return

        self._animation_frame += 1

        if self._state == self.STATE_IDLE:
            self._animate_idle()
        elif self._state == self.STATE_RECORDING:
            self._animate_recording()
        elif self._state == self.STATE_PROCESSING:
            self._animate_processing()

        self._animation_id = self._root.after(33, self._animate)  # ~30 FPS

    def _animate_idle(self) -> None:
        """Animate the idle state - gentle pulse."""
        if self._glow_circle is None:
            return

        self._pulse_phase += 0.08
        pulse = (math.sin(self._pulse_phase) + 1) / 2  # 0 to 1

        cx, cy = 36, 40
        base_radius = 10
        pulse_amount = 4
        radius = base_radius + pulse * pulse_amount

        self._canvas.coords(
            self._glow_circle,
            cx - radius, cy - radius,
            cx + radius, cy + radius
        )

        # Subtle color pulse
        color = lerp_color(self.COLORS["idle"], self.COLORS["idle_glow"], pulse * 0.5)
        self._canvas.itemconfig(self._glow_circle, fill=color)

    def _animate_recording(self) -> None:
        """Animate the recording state - soundwave bars."""
        if not self._soundwave_bars:
            return

        center_y = 40

        for i, bar in enumerate(self._soundwave_bars):
            # Each bar has a different phase for wave effect
            phase = self._animation_frame * 0.15 + i * 0.8
            height = 6 + abs(math.sin(phase)) * 16

            coords = self._canvas.coords(bar)
            x1 = coords[0]
            x2 = coords[2]

            self._canvas.coords(
                bar,
                x1, center_y - height,
                x2, center_y + height
            )

            # Color pulse
            intensity = abs(math.sin(phase))
            color = lerp_color(self.COLORS["recording"], self.COLORS["recording_glow"], intensity)
            self._canvas.itemconfig(bar, fill=color)

    def _animate_processing(self) -> None:
        """Animate the processing state - spinning loader."""
        if self._loader_arc is None:
            return

        # Rotate the arc
        angle = (self._animation_frame * 8) % 360
        self._canvas.itemconfig(self._loader_arc, start=angle)

        # Pulse the extent for a more dynamic feel
        extent_pulse = 70 + math.sin(self._animation_frame * 0.1) * 30
        self._canvas.itemconfig(self._loader_arc, extent=extent_pulse)

        # Color shimmer
        shimmer = (math.sin(self._animation_frame * 0.15) + 1) / 2
        color = lerp_color(self.COLORS["processing"], self.COLORS["processing_glow"], shimmer)
        self._canvas.itemconfig(self._loader_arc, outline=color)

    def _on_close(self) -> None:
        """Handle window close."""
        if "exit" in self._callbacks:
            self._callbacks["exit"]()

    def _run_loop(self) -> None:
        """Run the tkinter main loop."""
        self._create_window()
        self._root.mainloop()

    def set_callback(self, action: str, callback: Callable) -> None:
        """Register a callback."""
        self._callbacks[action] = callback

    def set_state(self, state: str) -> None:
        """Update the display state."""
        self._state = state

        if self._root is None:
            return

        def update():
            if self._canvas is None:
                return

            if state == self.STATE_IDLE:
                self._setup_idle_state()
            elif state == self.STATE_RECORDING:
                self._setup_recording_state()
            elif state == self.STATE_PROCESSING:
                self._setup_processing_state()

        self._root.after(0, update)

    def update_title(self, title: str) -> None:
        """Update window title (no-op for borderless window)."""
        pass

    def notify(self, title: str, message: str) -> None:
        """Show a brief notification."""
        if self._root is None or self._canvas is None:
            return

        def show():
            self._clear_animations()

            # Success checkmark animation
            cx, cy = 36, 40

            # Draw checkmark
            self._canvas.create_line(
                cx - 8, cy,
                cx - 2, cy + 6,
                cx + 10, cy - 8,
                fill="#00d26a",
                width=3,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
                tags="animated"
            )

            self._text_id = self._canvas.create_text(
                125, 32,
                text=title,
                font=("Segoe UI", 14, "bold"),
                fill="#2196F3",
                tags="animated"
            )

            self._subtext_id = self._canvas.create_text(
                125, 52,
                text=message,
                font=("Segoe UI", 9),
                fill=self.COLORS["text_dim"],
                tags="animated"
            )

            def restore():
                self.set_state(self._state)

            self._root.after(2000, restore)

        self._root.after(0, show)

    def start(self) -> None:
        """Start the GUI in a background thread."""
        if self._thread is not None:
            return

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)

    def stop(self) -> None:
        """Stop the GUI."""
        if self._animation_id and self._root:
            self._root.after_cancel(self._animation_id)
        if self._root:
            self._root.after(0, self._root.destroy)


if __name__ == "__main__":
    import time

    print("Testing Earworm window...")

    window = StatusWindow()
    window.start()

    time.sleep(2)
    window.set_state(StatusWindow.STATE_RECORDING)

    time.sleep(2)
    window.set_state(StatusWindow.STATE_PROCESSING)

    time.sleep(2)
    window.notify("Done", "Test complete!")

    time.sleep(3)
    window.stop()
