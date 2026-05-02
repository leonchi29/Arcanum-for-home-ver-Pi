"""
Audio manager - Controls system volume mute/unmute.
Used when switching between services and Arcanum main screen.
"""
import subprocess
import platform


class AudioManager:
    def __init__(self):
        self._muted = False
        self._system = platform.system()

    def mute(self) -> None:
        """Mute system audio."""
        if self._muted:
            return
        try:
            if self._system == "Linux":
                subprocess.run(["amixer", "set", "Master", "mute"],
                               capture_output=True, check=False)
            self._muted = True
            print("[Audio] Muted.")
        except Exception as e:
            print(f"[Audio] Mute error: {e}")

    def unmute(self) -> None:
        """Unmute system audio."""
        if not self._muted:
            return
        try:
            if self._system == "Linux":
                subprocess.run(["amixer", "set", "Master", "unmute"],
                               capture_output=True, check=False)
            self._muted = False
            print("[Audio] Unmuted.")
        except Exception as e:
            print(f"[Audio] Unmute error: {e}")

    def set_volume(self, percent: int) -> None:
        """Set system volume (0-100)."""
        percent = max(0, min(100, percent))
        try:
            if self._system == "Linux":
                subprocess.run(["amixer", "set", "Master", f"{percent}%"],
                               capture_output=True, check=False)
            print(f"[Audio] Volume: {percent}%")
        except Exception as e:
            print(f"[Audio] Volume error: {e}")

    @property
    def is_muted(self) -> bool:
        return self._muted
