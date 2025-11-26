"""
System tray icon and menu using pystray.
Provides visual feedback and quick access to controls.
"""

import pystray
from PIL import Image, ImageDraw
from typing import Callable, Optional
import threading


class TrayIcon:
    """System tray icon with status indication and menu."""

    # Icon states
    STATE_IDLE = "idle"
    STATE_RECORDING = "recording"
    STATE_PROCESSING = "processing"

    def __init__(self):
        self._icon: Optional[pystray.Icon] = None
        self._state = self.STATE_IDLE
        self._callbacks = {}
        self._thread: Optional[threading.Thread] = None

        # Create icons for different states
        self._icons = {
            self.STATE_IDLE: self._create_icon("#4CAF50"),      # Green
            self.STATE_RECORDING: self._create_icon("#F44336"),  # Red
            self.STATE_PROCESSING: self._create_icon("#FFC107"), # Yellow/Orange
        }

    def _create_icon(self, color: str, size: int = 64) -> Image.Image:
        """Create a simple circular icon with the given color."""
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw filled circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
            outline="#FFFFFF",
            width=2
        )

        # Add microphone symbol (simplified)
        mic_color = "#FFFFFF"
        center_x = size // 2
        center_y = size // 2

        # Microphone body (rectangle with rounded top)
        mic_width = size // 5
        mic_height = size // 3
        mic_left = center_x - mic_width // 2
        mic_top = center_y - mic_height // 2 - 4

        draw.rounded_rectangle(
            [mic_left, mic_top, mic_left + mic_width, mic_top + mic_height],
            radius=mic_width // 2,
            fill=mic_color
        )

        # Microphone stand (arc + line)
        stand_top = mic_top + mic_height - 4
        arc_width = mic_width + 8
        arc_left = center_x - arc_width // 2
        draw.arc(
            [arc_left, stand_top - 8, arc_left + arc_width, stand_top + 12],
            start=0, end=180,
            fill=mic_color,
            width=2
        )

        # Stand line
        draw.line(
            [center_x, stand_top + 10, center_x, stand_top + 18],
            fill=mic_color,
            width=2
        )

        return image

    def set_callback(self, action: str, callback: Callable) -> None:
        """Register a callback for a menu action."""
        self._callbacks[action] = callback

    def _create_menu(self) -> pystray.Menu:
        """Create the context menu."""
        return pystray.Menu(
            pystray.MenuItem(
                "Hold Right Alt to Record",
                self._on_toggle,
                default=True  # Double-click action
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Status: " + self._get_status_text(),
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings...", self._on_settings),
            pystray.MenuItem("Exit", self._on_exit),
        )

    def _get_status_text(self) -> str:
        """Get human-readable status text."""
        status_map = {
            self.STATE_IDLE: "Ready",
            self.STATE_RECORDING: "Recording...",
            self.STATE_PROCESSING: "Processing...",
        }
        return status_map.get(self._state, "Unknown")

    def _on_toggle(self, icon, item) -> None:
        """Handle toggle recording menu click."""
        if "toggle_recording" in self._callbacks:
            threading.Thread(
                target=self._callbacks["toggle_recording"],
                daemon=True
            ).start()

    def _on_settings(self, icon, item) -> None:
        """Handle settings menu click."""
        if "settings" in self._callbacks:
            self._callbacks["settings"]()

    def _on_exit(self, icon, item) -> None:
        """Handle exit menu click."""
        if "exit" in self._callbacks:
            self._callbacks["exit"]()
        self.stop()

    def set_state(self, state: str) -> None:
        """Update the tray icon state."""
        if state not in self._icons:
            return

        self._state = state
        if self._icon:
            self._icon.icon = self._icons[state]
            self._icon.menu = self._create_menu()  # Update status text

    def start(self) -> None:
        """Start the tray icon in a background thread."""
        if self._icon is not None:
            return

        self._icon = pystray.Icon(
            name="LocalSTT",
            icon=self._icons[self.STATE_IDLE],
            title="Local STT - Ready",
            menu=self._create_menu()
        )

        # Run in background thread
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon:
            self._icon.stop()
            self._icon = None

    def update_title(self, title: str) -> None:
        """Update the tray icon tooltip."""
        if self._icon:
            self._icon.title = title

    def notify(self, title: str, message: str) -> None:
        """Show a notification balloon."""
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                # Notifications might not be supported on all systems
                pass


if __name__ == "__main__":
    # Quick test
    import time

    print("Testing tray icon...")
    print("Look for the icon in your system tray")

    tray = TrayIcon()

    def on_toggle():
        print("Toggle clicked!")
        # Cycle through states for demo
        states = [TrayIcon.STATE_RECORDING, TrayIcon.STATE_PROCESSING, TrayIcon.STATE_IDLE]
        current = states.index(tray._state) if tray._state in states else -1
        next_state = states[(current + 1) % len(states)]
        tray.set_state(next_state)
        print(f"State: {next_state}")

    def on_exit():
        print("Exit clicked!")

    tray.set_callback("toggle_recording", on_toggle)
    tray.set_callback("exit", on_exit)
    tray.start()

    print("Tray icon started. Right-click to see menu.")
    print("Press Ctrl+C to exit")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        tray.stop()
