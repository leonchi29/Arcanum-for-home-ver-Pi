"""
Weather service using wttr.in — no API key needed.
Scrapes weather data from the web, returns spoken-friendly Spanish text.
"""
import requests
from config.settings import WEATHER_CITY


class WeatherService:
    """Weather via wttr.in (free, no API key)."""

    WTTR_URL = "https://wttr.in"

    def get_weather(self, city: str = "") -> str:
        """Get current weather. Returns a spoken-friendly Spanish string."""
        target_city = city.strip() if city else WEATHER_CITY

        # Try wttr.in JSON format
        result = self._wttr_json(target_city)
        if result:
            return result

        # Fallback: wttr.in one-line format
        result = self._wttr_oneline(target_city)
        if result:
            return result

        return "No pude obtener el clima. Verifica tu conexión a internet."

    def _wttr_json(self, city: str) -> str | None:
        """Get weather from wttr.in JSON endpoint."""
        try:
            url = f"{self.WTTR_URL}/{city}?format=j1&lang=es"
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Arcanum/1.0",
                "Accept-Language": "es",
            })
            response.raise_for_status()
            data = response.json()

            current = data["current_condition"][0]
            temp = current["temp_C"]
            feels = current["FeelsLikeC"]
            humidity = current["humidity"]
            # Spanish description
            desc = current.get("lang_es", [{}])
            if isinstance(desc, list) and desc:
                desc_text = desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", ""))
            else:
                desc_text = current.get("weatherDesc", [{}])[0].get("value", "")

            wind = current.get("windspeedKmph", "")

            # Get city name from area
            area = data.get("nearest_area", [{}])
            if area:
                city_name = area[0].get("areaName", [{}])[0].get("value", city)
                country = area[0].get("country", [{}])[0].get("value", "")
            else:
                city_name = city
                country = ""

            result = (
                f"En {city_name} hay {temp} grados, "
                f"sensación térmica de {feels}. "
                f"{desc_text.capitalize()}. "
                f"Humedad: {humidity}%."
            )
            if wind:
                result += f" Viento: {wind} km/h."

            return result

        except Exception:
            return None

    def _wttr_oneline(self, city: str) -> str | None:
        """Fallback: get weather as one-line text."""
        try:
            # Format: City: ☁️ +15°C
            url = f"{self.WTTR_URL}/{city}?format=%l:+%C+%t+sensación+%f+humedad+%h&lang=es"
            response = requests.get(url, timeout=10, headers={
                "User-Agent": "Arcanum/1.0",
            })
            response.raise_for_status()
            text = response.text.strip()
            if text and "Unknown" not in text:
                return text
            return None
        except Exception:
            return None
