"""
Weather service using OpenWeatherMap API.
"""
import requests
from config.settings import OPENWEATHER_API_KEY, WEATHER_CITY, WEATHER_COUNTRY


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str = "") -> str:
        """Get current weather. Returns a spoken-friendly string."""
        if not OPENWEATHER_API_KEY:
            return "Weather not configured. Add OPENWEATHER_API_KEY to .env file."

        target_city = city if city else WEATHER_CITY

        try:
            params = {
                "q": f"{target_city},{WEATHER_COUNTRY}",
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "es",
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            city_name = data["name"]

            return (
                f"In {city_name} it is {temp} degrees, "
                f"feels like {feels_like}. "
                f"{description.capitalize()}. "
                f"Humidity: {humidity}%."
            )

        except requests.RequestException as e:
            return f"Could not get weather: {e}"
        except (KeyError, IndexError):
            return "Error processing weather data."
