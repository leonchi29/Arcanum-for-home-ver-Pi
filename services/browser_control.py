"""
Browser control service for Arcanum.
Sends keystrokes to Chromium via xdotool for voice-controlled navigation.
Works with Netflix, YouTube, Spotify Web, Disney+, etc.
"""
import subprocess
import platform
import time


class BrowserControl:
    """Voice-driven browser control via xdotool keystrokes."""

    def __init__(self):
        self._system = platform.system()
        self._available = self._check_xdotool()

    def _check_xdotool(self) -> bool:
        """Check if xdotool is installed (Linux only)."""
        if self._system != "Linux":
            return False
        try:
            subprocess.run(
                ["xdotool", "--version"],
                capture_output=True, check=True,
            )
            return True
        except Exception:
            print("[BrowserControl] xdotool not available.")
            return False

    def _focus_chromium(self) -> bool:
        """Focus the Chromium window before sending keys."""
        if not self._available:
            return False
        try:
            subprocess.run(
                ["xdotool", "search", "--name", "Chromium", "windowactivate"],
                capture_output=True, check=False,
            )
            time.sleep(0.2)
            return True
        except Exception:
            return False

    def _send_key(self, key: str) -> bool:
        """Send a key press to the focused window."""
        if not self._available:
            return False
        try:
            self._focus_chromium()
            subprocess.run(
                ["xdotool", "key", key],
                capture_output=True, check=False,
            )
            return True
        except Exception:
            return False

    def _send_keys_repeated(self, key: str, times: int) -> bool:
        """Send a key multiple times."""
        for _ in range(times):
            if not self._send_key(key):
                return False
            time.sleep(0.05)
        return True

    # ===== NAVIGATION =====

    def scroll_down(self, amount: int = 5) -> bool:
        """Scroll down by sending Page Down."""
        return self._send_keys_repeated("Page_Down", amount)

    def scroll_up(self, amount: int = 5) -> bool:
        """Scroll up by sending Page Up."""
        return self._send_keys_repeated("Page_Up", amount)

    def scroll_to_top(self) -> bool:
        """Scroll to top with Home key."""
        return self._send_key("Home")

    def scroll_to_bottom(self) -> bool:
        """Scroll to bottom with End key."""
        return self._send_key("End")

    def click_or_select(self) -> bool:
        """Press Enter to activate focused element."""
        return self._send_key("Return")

    def press_tab(self) -> bool:
        """Move focus to next element."""
        return self._send_key("Tab")

    def press_back(self) -> bool:
        """Browser back (Alt+Left)."""
        return self._send_key("alt+Left")

    def press_forward(self) -> bool:
        """Browser forward (Alt+Right)."""
        return self._send_key("alt+Right")

    def refresh_page(self) -> bool:
        """Reload current page (F5)."""
        return self._send_key("F5")

    def fullscreen(self) -> bool:
        """Toggle fullscreen (F11)."""
        return self._send_key("F11")

    def play_pause(self) -> bool:
        """Toggle play/pause for HTML5 video (Spacebar / K)."""
        # Try K (YouTube) first, fallback to Space
        return self._send_key("k") or self._send_key("space")

    def video_seek_forward(self) -> bool:
        """Seek forward 5s in HTML5 video (Right arrow)."""
        return self._send_key("Right")

    def video_seek_back(self) -> bool:
        """Seek backward 5s (Left arrow)."""
        return self._send_key("Left")

    def video_next_episode(self) -> bool:
        """Next episode (Shift+N for Netflix)."""
        return self._send_key("shift+n")

    def video_skip_intro(self) -> bool:
        """Skip intro (S key on Netflix)."""
        return self._send_key("s")

    def open_search(self) -> bool:
        """Open in-page search (Ctrl+F)."""
        return self._send_key("ctrl+f")

    def close_tab(self) -> bool:
        """Close current tab (Ctrl+W)."""
        return self._send_key("ctrl+w")

    # ===== TEXT INPUT =====

    def type_text(self, text: str) -> bool:
        """Type text into the focused element."""
        if not self._available:
            return False
        try:
            self._focus_chromium()
            subprocess.run(
                ["xdotool", "type", "--delay", "30", text],
                capture_output=True, check=False,
            )
            return True
        except Exception:
            return False

    def navigate_to(self, url: str) -> bool:
        """Navigate to a URL by typing in address bar."""
        if not self._available:
            return False
        self._focus_chromium()
        # Ctrl+L focuses the address bar
        self._send_key("ctrl+l")
        time.sleep(0.3)
        self.type_text(url)
        time.sleep(0.2)
        return self._send_key("Return")

    # ===== MOUSE CONTROL =====

    def mouse_move_relative(self, dx: int, dy: int) -> bool:
        """Move mouse relative."""
        if not self._available:
            return False
        try:
            subprocess.run(
                ["xdotool", "mousemove_relative", "--", str(dx), str(dy)],
                capture_output=True, check=False,
            )
            return True
        except Exception:
            return False

    def mouse_click(self, button: int = 1) -> bool:
        """Click mouse button (1=left, 2=middle, 3=right)."""
        if not self._available:
            return False
        try:
            subprocess.run(
                ["xdotool", "click", str(button)],
                capture_output=True, check=False,
            )
            return True
        except Exception:
            return False
