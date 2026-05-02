"""
WiFi QR code generator service.
Reads the current WiFi connection and generates a QR code
so other devices can scan and connect.
"""
import subprocess
import platform
import os
import qrcode
from io import BytesIO


class WifiQRService:
    def __init__(self):
        self._qr_image_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "wifi_qr.png"
        )

    def get_wifi_info(self) -> dict | None:
        """Get current WiFi SSID and password from the system."""
        system = platform.system()

        if system == "Linux":
            return self._get_wifi_linux()
        elif system == "Windows":
            return self._get_wifi_windows()
        return None

    def _get_wifi_linux(self) -> dict | None:
        """Read WiFi credentials on Linux/Raspberry Pi."""
        try:
            # Get current SSID
            result = subprocess.run(
                ["iwgetid", "-r"],
                capture_output=True, text=True, check=False,
            )
            ssid = result.stdout.strip()

            if not ssid:
                return None

            # Try to read password from NetworkManager
            password = ""
            try:
                result = subprocess.run(
                    ["sudo", "cat", f"/etc/NetworkManager/system-connections/{ssid}.nmconnection"],
                    capture_output=True, text=True, check=False,
                )
                for line in result.stdout.splitlines():
                    if line.strip().startswith("psk="):
                        password = line.strip().split("=", 1)[1]
                        break
            except Exception:
                pass

            # Fallback: try wpa_supplicant
            if not password:
                try:
                    result = subprocess.run(
                        ["sudo", "cat", "/etc/wpa_supplicant/wpa_supplicant.conf"],
                        capture_output=True, text=True, check=False,
                    )
                    in_network = False
                    for line in result.stdout.splitlines():
                        line = line.strip()
                        if line.startswith("network="):
                            in_network = False
                        if f'ssid="{ssid}"' in line:
                            in_network = True
                        if in_network and line.startswith("psk="):
                            password = line.split("=", 1)[1].strip('"')
                            break
                except Exception:
                    pass

            return {"ssid": ssid, "password": password, "security": "WPA"}

        except Exception:
            return None

    def _get_wifi_windows(self) -> dict | None:
        """Read WiFi credentials on Windows."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True, check=False,
            )
            ssid = ""
            for line in result.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":", 1)[1].strip()
                    break

            if not ssid:
                return None

            result = subprocess.run(
                ["netsh", "wlan", "show", "profile", ssid, "key=clear"],
                capture_output=True, text=True, check=False,
            )
            password = ""
            for line in result.stdout.splitlines():
                if "Key Content" in line or "Contenido de la clave" in line:
                    password = line.split(":", 1)[1].strip()
                    break

            return {"ssid": ssid, "password": password, "security": "WPA"}

        except Exception:
            return None

    def generate_qr(self) -> str | None:
        """
        Generate a WiFi QR code image.
        Returns the path to the saved PNG, or None on failure.
        """
        info = self.get_wifi_info()
        if not info or not info["ssid"]:
            return None

        # WiFi QR standard format
        wifi_string = f"WIFI:T:{info['security']};S:{info['ssid']};P:{info['password']};;"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(wifi_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#00b4d8", back_color="#0b1929")
        img.save(self._qr_image_path)

        return self._qr_image_path

    def get_wifi_text(self) -> str:
        """Get a text description of the WiFi connection."""
        info = self.get_wifi_info()
        if not info:
            return "Could not read WiFi information."
        return f"WiFi: {info['ssid']} | Password: {info['password'] or '(hidden)'}"
