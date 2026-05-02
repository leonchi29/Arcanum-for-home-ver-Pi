"""
News mode service - Opens Zapping TV for live Chilean news.
'Modo comer' activates this to watch news while eating.
"""
import subprocess
import platform
from config.settings import ZAPPING_URL


class NewsService:
    def __init__(self):
        self.process = None
        self.is_active = False

    def start_news(self) -> bool:
        """Open Zapping TV news in the default browser (fullscreen on Pi)."""
        try:
            system = platform.system()

            if system == "Linux":
                # On Raspberry Pi, open Chromium in kiosk mode
                self.process = subprocess.Popen(
                    [
                        "chromium-browser",
                        "--kiosk",
                        "--noerrdialogs",
                        "--disable-infobars",
                        "--no-first-run",
                        ZAPPING_URL,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Fallback for other systems
                import webbrowser
                webbrowser.open(ZAPPING_URL)

            self.is_active = True
            print(f"[News] Modo comer activated - Zapping TV: {ZAPPING_URL}")
            return True

        except FileNotFoundError:
            # Try alternative browser
            try:
                import webbrowser
                webbrowser.open(ZAPPING_URL)
                self.is_active = True
                print(f"[News] Modo comer activated (browser): {ZAPPING_URL}")
                return True
            except Exception as e:
                print(f"[News] Error opening news: {e}")
                return False
        except Exception as e:
            print(f"[News] Error: {e}")
            return False

    def stop_news(self) -> bool:
        """Close the news browser."""
        try:
            if self.process:
                self.process.terminate()
                self.process = None

            self.is_active = False
            print("[News] Modo comer deactivated.")
            return True
        except Exception as e:
            print(f"[News] Error stopping: {e}")
            return False
