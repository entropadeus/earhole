"""
Hotkey manager using pynput.
Handles global hotkey registration for starting/stopping recording.
"""

from pynput import keyboard
from typing import Callable, Optional, Set
import threading


class HotkeyManager:
    """
    Manages global hotkeys for controlling the STT app.

    Default hotkey: Ctrl+Shift+Space (toggle recording)
    """

    def __init__(self):
        self._listener: Optional[keyboard.Listener] = None
        self._current_keys: Set[keyboard.Key] = set()
        self._callbacks: dict = {}
        self._running = False

        # Define the hotkey combinations
        # Format: frozenset of keys -> callback name
        self._hotkeys = {
            # Ctrl+Shift+Space to toggle recording
            frozenset([
                keyboard.Key.ctrl_l,
                keyboard.Key.shift,
                keyboard.Key.space
            ]): "toggle_recording",
            # Also support right ctrl
            frozenset([
                keyboard.Key.ctrl_r,
                keyboard.Key.shift,
                keyboard.Key.space
            ]): "toggle_recording",
            # Escape to cancel recording
            frozenset([keyboard.Key.esc]): "cancel_recording",
        }

    def register_callback(self, action: str, callback: Callable) -> None:
        """
        Register a callback for an action.

        Args:
            action: Action name ("toggle_recording", "cancel_recording")
            callback: Function to call when the hotkey is pressed
        """
        self._callbacks[action] = callback

    def _on_press(self, key: keyboard.Key) -> None:
        """Handle key press events."""
        # Normalize the key (handle both left and right variants)
        normalized = self._normalize_key(key)
        self._current_keys.add(normalized)

        # Check if current keys match any hotkey
        for hotkey_combo, action in self._hotkeys.items():
            if self._keys_match(hotkey_combo):
                if action in self._callbacks:
                    # Call in a separate thread to avoid blocking
                    threading.Thread(
                        target=self._callbacks[action],
                        daemon=True
                    ).start()
                break

    def _on_release(self, key: keyboard.Key) -> None:
        """Handle key release events."""
        normalized = self._normalize_key(key)
        self._current_keys.discard(normalized)

    def _normalize_key(self, key: keyboard.Key) -> keyboard.Key:
        """Normalize key variants (e.g., left/right ctrl)."""
        # Map right-side keys to left-side equivalents for matching
        key_map = {
            keyboard.Key.ctrl_r: keyboard.Key.ctrl_l,
            keyboard.Key.alt_r: keyboard.Key.alt_l,
            keyboard.Key.shift_r: keyboard.Key.shift,
        }
        return key_map.get(key, key)

    def _keys_match(self, required: frozenset) -> bool:
        """Check if currently pressed keys match the required combination."""
        # For single-key hotkeys (like Escape), just check if that key is pressed
        if len(required) == 1:
            return required <= self._current_keys

        # For multi-key combinations, need exact match (modifiers + trigger)
        # Allow some flexibility - current keys should contain all required
        return required <= self._current_keys

    def start(self) -> None:
        """Start listening for hotkeys."""
        if self._running:
            return

        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()

    def stop(self) -> None:
        """Stop listening for hotkeys."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._current_keys.clear()

    def is_running(self) -> bool:
        """Check if the hotkey listener is running."""
        return self._running


class PushToTalkManager:
    """
    Alternative hotkey manager for push-to-talk mode.
    Records while a key is held down.
    """

    def __init__(self, trigger_key: keyboard.Key = keyboard.Key.f9):
        """
        Args:
            trigger_key: The key to hold for recording.
        """
        self.trigger_key = trigger_key
        self._listener: Optional[keyboard.Listener] = None
        self._on_start: Optional[Callable] = None
        self._on_stop: Optional[Callable] = None
        self._is_pressed = False
        self._running = False

    def set_callbacks(
        self,
        on_start: Callable,
        on_stop: Callable
    ) -> None:
        """Set the callbacks for starting and stopping recording."""
        self._on_start = on_start
        self._on_stop = on_stop

    def _is_trigger_key(self, key) -> bool:
        """Check if the key matches our trigger (handles alt_r/alt_gr variants)."""
        # Direct match
        if key == self.trigger_key:
            return True

        # Handle Right Alt which can appear as alt_r or alt_gr on Windows
        if self.trigger_key == keyboard.Key.alt_r:
            if hasattr(keyboard.Key, 'alt_gr') and key == keyboard.Key.alt_gr:
                return True
            # Sometimes it comes as a KeyCode with vk=165 (VK_RMENU)
            if hasattr(key, 'vk') and key.vk == 165:
                return True

        return False

    def _on_press(self, key) -> None:
        """Handle key press."""
        if self._is_trigger_key(key) and not self._is_pressed:
            self._is_pressed = True
            print(f"Key pressed: {key} - Starting recording")
            if self._on_start:
                threading.Thread(target=self._on_start, daemon=True).start()

    def _on_release(self, key) -> None:
        """Handle key release."""
        if self._is_trigger_key(key) and self._is_pressed:
            self._is_pressed = False
            print(f"Key released: {key} - Stopping recording")
            if self._on_stop:
                threading.Thread(target=self._on_stop, daemon=True).start()

    def start(self) -> None:
        """Start listening."""
        if self._running:
            return

        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.start()
        print("Hotkey listener started - waiting for Right Alt key...")

    def stop(self) -> None:
        """Stop listening."""
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None


if __name__ == "__main__":
    # Quick test
    print("Testing hotkey manager...")
    print("Press Ctrl+Shift+Space to test toggle")
    print("Press Escape to test cancel")
    print("Press Ctrl+C to exit")

    manager = HotkeyManager()

    def on_toggle():
        print(">>> TOGGLE RECORDING <<<")

    def on_cancel():
        print(">>> CANCEL RECORDING <<<")

    manager.register_callback("toggle_recording", on_toggle)
    manager.register_callback("cancel_recording", on_cancel)
    manager.start()

    try:
        import time
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        manager.stop()
