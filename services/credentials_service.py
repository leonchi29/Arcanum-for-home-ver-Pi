"""
Credentials service for Arcanum.
Stores user credentials per streaming service in a local encrypted-style JSON.
On voice 'login' command, types user/password into the active browser via xdotool.

NOTE: Uses base64 obfuscation only — for true security, use OS keyring.
This stores convenience passwords for a private home device.
"""
import os
import json
import base64
import time


class CredentialsService:
    def __init__(self):
        self._creds_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), ".credentials.json"
        )
        self._creds = self._load()

    def _load(self) -> dict:
        """Load credentials from disk."""
        if not os.path.exists(self._creds_file):
            return {}
        try:
            with open(self._creds_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Decode base64 passwords
            for service, info in data.items():
                if "password" in info and info["password"]:
                    try:
                        info["password"] = base64.b64decode(
                            info["password"].encode()
                        ).decode("utf-8")
                    except Exception:
                        pass
            return data
        except Exception:
            return {}

    def _save(self) -> None:
        """Save credentials to disk (with base64 obfuscation)."""
        try:
            data_to_save = {}
            for service, info in self._creds.items():
                data_to_save[service] = dict(info)
                if "password" in info and info["password"]:
                    data_to_save[service]["password"] = base64.b64encode(
                        info["password"].encode("utf-8")
                    ).decode()
            with open(self._creds_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2)
            os.chmod(self._creds_file, 0o600)
        except Exception as e:
            print(f"[Credentials] Save error: {e}")

    def has_credentials(self, service_key: str) -> bool:
        """Check if credentials exist for a service."""
        return (
            service_key in self._creds
            and self._creds[service_key].get("user")
            and self._creds[service_key].get("password")
        )

    def get_credentials(self, service_key: str) -> dict | None:
        """Get stored credentials for a service."""
        if self.has_credentials(service_key):
            return self._creds[service_key]
        return None

    def save_credentials(self, service_key: str, user: str, password: str) -> None:
        """Save credentials for a service."""
        self._creds[service_key] = {"user": user, "password": password}
        self._save()

    def delete_credentials(self, service_key: str) -> None:
        """Delete credentials for a service."""
        if service_key in self._creds:
            del self._creds[service_key]
            self._save()

    def autofill_login(self, service_key: str, browser_control) -> bool:
        """
        Autofill login form using xdotool.
        Strategy: type user → Tab → type password → Enter.
        """
        creds = self.get_credentials(service_key)
        if not creds:
            return False

        try:
            # Wait briefly for page to load
            time.sleep(2)
            # Click email/user field (usually focused or first Tab)
            browser_control.type_text(creds["user"])
            time.sleep(0.5)
            browser_control.press_tab()
            time.sleep(0.3)
            browser_control.type_text(creds["password"])
            time.sleep(0.3)
            browser_control.click_or_select()
            return True
        except Exception as e:
            print(f"[Credentials] Autofill error: {e}")
            return False
