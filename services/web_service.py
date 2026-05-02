"""
Web service manager - Manages Chromium browser for streaming services.
Handles Spotify (web), Netflix, Zapping, Disney+, etc.
"""
import subprocess
import platform
from config.settings import STREAMING_SERVICES


class WebService:
    def __init__(self):
        self.process = None
        self.current_service = None
        self.is_active = False
        self._system = platform.system()

    def get_available_services(self) -> list[str]:
        """Return list of available streaming service names."""
        return [info["name"] for info in STREAMING_SERVICES.values()]

    def find_service(self, query: str) -> str | None:
        """Find a service matching the query."""
        query_lower = query.lower().strip()
        for key, info in STREAMING_SERVICES.items():
            if query_lower in key or key in query_lower:
                return key
            if query_lower in info["name"].lower():
                return key
        return None

    def open_service(self, service_key: str, search_query: str = "") -> dict:
        """
        Open a streaming service in Chromium.
        Returns dict with status info.
        """
        if service_key not in STREAMING_SERVICES:
            return {
                "success": False,
                "message": f"Service not found: {service_key}",
            }

        service = STREAMING_SERVICES[service_key]
        url = service["url"]

        # If there's a search query for Spotify web
        if search_query and service_key == "spotify":
            url = f"{url}/search/{search_query}"
        elif search_query and service_key == "youtube":
            url = f"{url}/results?search_query={search_query}"

        # Close current service if any
        if self.is_active:
            self.close_service()

        try:
            if self._system == "Linux":
                self.process = subprocess.Popen(
                    [
                        "chromium-browser",
                        "--kiosk",
                        "--noerrdialogs",
                        "--disable-infobars",
                        "--no-first-run",
                        "--disable-session-crashed-bubble",
                        "--disable-restore-session-state",
                        url,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                import webbrowser
                webbrowser.open(url)

            self.current_service = service_key
            self.is_active = True

            msg = f"Opening {service['name']}"
            if service["needs_login"]:
                msg += ". This service may require login."

            return {"success": True, "message": msg}

        except FileNotFoundError:
            try:
                import webbrowser
                webbrowser.open(url)
                self.current_service = service_key
                self.is_active = True
                return {"success": True, "message": f"Opening {service['name']} in browser"}
            except Exception as e:
                return {"success": False, "message": f"Error: {e}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def close_service(self) -> str:
        """Close the current web service."""
        service_name = "service"
        if self.current_service and self.current_service in STREAMING_SERVICES:
            service_name = STREAMING_SERVICES[self.current_service]["name"]

        try:
            if self.process:
                self.process.terminate()
                self.process = None
            elif self._system == "Linux":
                # Kill any Chromium kiosk instance
                subprocess.run(["pkill", "-f", "chromium-browser.*kiosk"],
                               capture_output=True, check=False)
        except Exception:
            pass

        self.current_service = None
        self.is_active = False
        return f"{service_name} closed."

    def minimize_service(self) -> None:
        """Minimize/hide the browser to show Arcanum UI."""
        if self._system == "Linux":
            try:
                subprocess.run(["xdotool", "key", "super+d"],
                               capture_output=True, check=False)
            except Exception:
                pass

    def restore_service(self) -> None:
        """Restore/show the browser window."""
        if self._system == "Linux":
            try:
                subprocess.run(
                    ["xdotool", "search", "--name", "Chromium", "windowactivate"],
                    capture_output=True, check=False,
                )
            except Exception:
                pass
