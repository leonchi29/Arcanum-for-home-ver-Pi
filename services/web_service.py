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

    def open_service(self, service_key: str, search_query: str = "",
                     category: str = "") -> dict:
        """
        Open a streaming service in Chromium.
        - search_query: deep-link to search results
        - category: open a specific category URL
        Returns dict with status info.
        """
        if service_key not in STREAMING_SERVICES:
            return {
                "success": False,
                "message": f"Service not found: {service_key}",
            }

        service = STREAMING_SERVICES[service_key]

        # Determine which URL to open
        if category and category in service.get("categories", {}):
            url = service["categories"][category]
        elif search_query and service.get("search_url"):
            url = service["search_url"].format(
                query=search_query.replace(" ", "+")
            )
        else:
            url = service["url"]

        # If same service already open, just navigate (don't restart browser)
        if self.is_active and self.current_service == service_key:
            try:
                # Use xdotool to navigate (Ctrl+L + URL + Enter)
                subprocess.run(
                    ["xdotool", "search", "--name", "Chromium", "windowactivate"],
                    capture_output=True, check=False,
                )
                subprocess.run(["xdotool", "key", "ctrl+l"], capture_output=True, check=False)
                subprocess.run(["xdotool", "type", "--delay", "20", url],
                               capture_output=True, check=False)
                subprocess.run(["xdotool", "key", "Return"], capture_output=True, check=False)
                msg = f"Navigating in {service['name']}"
                if search_query:
                    msg += f": {search_query}"
                return {"success": True, "message": msg, "needs_login": False}
            except Exception:
                pass

        # Close current service if a different one is open
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
                        "--autoplay-policy=no-user-gesture-required",
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

            msg = f"Abriendo {service['name']}"
            if search_query:
                msg += f", buscando: {search_query}"
            elif category:
                msg += f", categoría: {category}"

            return {
                "success": True,
                "message": msg,
                "needs_login": service["needs_login"],
            }

        except FileNotFoundError:
            try:
                import webbrowser
                webbrowser.open(url)
                self.current_service = service_key
                self.is_active = True
                return {
                    "success": True,
                    "message": f"Abriendo {service['name']} en navegador",
                    "needs_login": service["needs_login"],
                }
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
