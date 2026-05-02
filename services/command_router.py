"""
Command router - Interprets voice commands and dispatches to services.
Handles: music, radio, streaming, weather, time, alarm, search, and more.
"""
import re
from datetime import datetime
from services.radio_service import RadioService
from services.web_service import WebService
from services.weather_service import WeatherService
from services.alarm_service import AlarmService
from services.search_service import SearchService
from services.audio_manager import AudioManager
from services.wifi_qr_service import WifiQRService
from config.settings import STREAMING_SERVICES


class CommandRouter:
    def __init__(self, on_alarm_callback=None):
        self.radio = RadioService()
        self.web = WebService()
        self.weather = WeatherService()
        self.alarm = AlarmService(on_alarm_callback=on_alarm_callback)
        self.search = SearchService()
        self.audio = AudioManager()
        self.wifi_qr = WifiQRService()

    def process_command(self, command: str) -> str:
        """
        Parse and route a voice command to the appropriate service.
        Returns the response text to display and speak.
        """
        if not command:
            return "No command received."

        # Music / Spotify (web)
        if self._matches(command, ["reproduce", "pon música", "pon musica", "escuchar",
                                     "canción", "cancion", "playlist", "play", "música",
                                     "musica", "ponme", "spotify"]):
            return self._handle_spotify(command)

        # Radio
        if self._matches(command, ["radio", "emisora", "estación", "estacion", "fm"]):
            return self._handle_radio(command)

        # Streaming services (Netflix, Disney, etc.)
        if self._matches(command, ["netflix", "disney", "youtube", "prime", "hbo",
                                     "paramount", "crunchyroll", "ver serie",
                                     "ver película", "ver pelicula"]):
            return self._handle_streaming(command)

        # Zapping / modo comer / noticias
        if self._matches(command, ["modo comer", "noticias", "zapping", "televisión",
                                     "television", "tele", "noticiero"]):
            return self._handle_zapping(command)

        # Close current web service
        if self._matches(command, ["cierra", "cerrar", "close"]):
            return self._handle_close()

        # Available services
        if self._matches(command, ["disponible", "qué hay", "que hay", "servicios",
                                     "plataformas", "qué puedo ver", "que puedo ver"]):
            return self._handle_list_services()

        # Time
        if self._matches(command, ["hora", "qué hora", "que hora", "time"]):
            return self._handle_time()

        # Date
        if self._matches(command, ["fecha", "día", "dia", "qué día", "que dia"]):
            return self._handle_date()

        # Weather
        if self._matches(command, ["clima", "tiempo", "temperatura", "weather",
                                     "llueve", "lluvia"]):
            return self._handle_weather(command)

        # Alarm
        if self._matches(command, ["alarma", "despiértame", "despiertame", "alarm"]):
            return self._handle_alarm(command)

        # Timer
        if self._matches(command, ["temporizador", "timer", "cronómetro", "cronometro",
                                     "cuenta regresiva"]):
            return self._handle_timer(command)

        # Cancel alarms
        if self._matches(command, ["cancela alarma", "quita alarma", "sin alarma"]):
            return self.alarm.cancel_alarms()

        # Stop / Pause everything
        if self._matches(command, ["para todo", "stop", "detener", "detente",
                                     "apaga todo"]):
            return self._handle_stop_all()

        # Pause
        if self._matches(command, ["pausa", "pausar", "pause"]):
            return self._handle_pause()

        # Resume
        if self._matches(command, ["continua", "continúa", "sigue", "resume",
                                     "reanuda"]):
            return self._handle_resume()

        # Volume
        if self._matches(command, ["volumen", "volume", "sube", "baja"]):
            return self._handle_volume(command)

        # WiFi QR
        if self._matches(command, ["qr", "wifi", "código qr", "codigo qr",
                                     "conectar wifi"]):
            return self._handle_wifi_qr()

        # Internet search / questions
        if self._matches(command, ["busca", "búsqueda", "busqueda", "qué es",
                                     "que es", "quién es", "quien es", "dime sobre",
                                     "información", "informacion", "investiga",
                                     "cuéntame", "cuentame", "explica"]):
            return self._handle_search(command)

        # Help
        if self._matches(command, ["ayuda", "help", "comandos", "qué puedes hacer",
                                     "que puedes hacer"]):
            return self._handle_help()

        # Close help
        if self._matches(command, ["cierra ayuda", "cerrar ayuda"]):
            return "__HIDE_HELP__"

        # Default: try internet search
        return self._handle_search(command)

    # --- Matchers ---

    def _matches(self, cmd: str, keywords: list[str]) -> bool:
        return any(kw in cmd for kw in keywords)

    # --- Handlers ---

    def _handle_spotify(self, command: str) -> str:
        query = self._extract_query(command, [
            "reproduce", "pon", "ponme", "música", "musica", "canción", "cancion",
            "escuchar", "play", "playlist", "en", "spotify", "de", "la", "el",
        ])

        result = self.web.open_service("spotify", search_query=query)
        if result["success"]:
            return f"Opening Spotify. Searching: {query}" if query else "Opening Spotify."
        return result["message"]

    def _handle_radio(self, command: str) -> str:
        if self.radio.is_playing:
            self.radio.stop()

        station_name = self._extract_query(command, [
            "pon", "ponme", "la", "el", "radio", "emisora", "estación",
            "estacion", "fm", "reproduce",
        ])

        if station_name:
            if self.radio.play_station(station_name):
                station = self.radio.find_station(station_name)
                return f"Playing Radio {station.title() if station else station_name}."
            else:
                stations = ", ".join(self.radio.get_available_stations())
                return f"Station not found. Available: {stations}"
        else:
            stations = ", ".join(self.radio.get_available_stations())
            return f"Which station? Available: {stations}"

    def _handle_streaming(self, command: str) -> str:
        # Detect which service
        for key in STREAMING_SERVICES:
            if key in command:
                result = self.web.open_service(key)
                return result["message"]

        # Generic: try to find service from command
        service = self.web.find_service(command)
        if service:
            result = self.web.open_service(service)
            return result["message"]

        return self._handle_list_services()

    def _handle_zapping(self, command: str) -> str:
        result = self.web.open_service("zapping")
        return "Modo comer activated. Enjoy the news!" if result["success"] else result["message"]

    def _handle_close(self) -> str:
        if self.web.is_active:
            msg = self.web.close_service()
            return msg
        if self.radio.is_playing:
            self.radio.stop()
            return "Radio stopped."
        return "Nothing to close."

    def _handle_list_services(self) -> str:
        services = self.web.get_available_services()
        radios = self.radio.get_available_stations()
        return (
            f"Streaming available: {', '.join(services)}. "
            f"Radios: {', '.join(r.title() for r in radios)}."
        )

    def _handle_time(self) -> str:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        return f"It's {hour}:{minute:02d}."

    def _handle_date(self) -> str:
        now = datetime.now()
        return now.strftime("Today is %A %d of %B, %Y.")

    def _handle_weather(self, command: str) -> str:
        # Check if a specific city is mentioned
        city = self._extract_query(command, [
            "clima", "tiempo", "temperatura", "weather", "en", "de",
            "el", "la", "llueve", "lluvia", "cómo", "como", "está", "esta",
        ])
        return self.weather.get_weather(city)

    def _handle_alarm(self, command: str) -> str:
        # Extract time from command like "alarma a las 7" or "alarma 7:30"
        time_match = re.search(r"(\d{1,2})[:\s]?(\d{2})?", command)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return self.alarm.set_alarm(hour, minute)
        return "Tell me the time. Example: 'alarm at 7:30'."

    def _handle_timer(self, command: str) -> str:
        # Extract minutes from command
        num_match = re.search(r"(\d+)", command)
        if num_match:
            minutes = int(num_match.group(1))
            if 1 <= minutes <= 1440:
                return self.alarm.set_timer(minutes)
        return "How many minutes? Example: 'timer 10 minutes'."

    def _handle_stop_all(self) -> str:
        msgs = []
        if self.radio.is_playing:
            self.radio.stop()
            msgs.append("Radio stopped")
        if self.web.is_active:
            self.web.close_service()
            msgs.append("Service closed")
        if not msgs:
            return "Nothing active to stop."
        return ". ".join(msgs) + "."

    def _handle_pause(self) -> str:
        self.audio.mute()
        return "Paused."

    def _handle_resume(self) -> str:
        self.audio.unmute()
        return "Resumed."

    def _handle_volume(self, command: str) -> str:
        if "sube" in command or "más" in command or "mas" in command:
            self.audio.set_volume(90)
            self.radio.set_volume(90)
            return "Volume up."
        elif "baja" in command or "menos" in command:
            self.audio.set_volume(40)
            self.radio.set_volume(40)
            return "Volume down."
        else:
            numbers = [int(s) for s in command.split() if s.isdigit()]
            if numbers:
                vol = max(0, min(100, numbers[0]))
                self.audio.set_volume(vol)
                self.radio.set_volume(vol)
                return f"Volume at {vol}%."
        return "Volume: say 'volume up', 'volume down' or a number."

    def _handle_search(self, command: str) -> str:
        query = self._extract_query(command, [
            "busca", "búsqueda", "busqueda", "qué", "que", "quién", "quien",
            "es", "dime", "sobre", "información", "informacion", "investiga",
            "cuéntame", "cuentame", "explica", "arcanum",
        ])
        if not query:
            query = command
        return self.search.search(query)

    def _handle_wifi_qr(self) -> str:
        qr_path = self.wifi_qr.generate_qr()
        if qr_path:
            wifi_text = self.wifi_qr.get_wifi_text()
            return f"__SHOW_QR__{qr_path}__|__{wifi_text}"
        return "No pude leer la información del WiFi."

    def _handle_help(self) -> str:
        return "__SHOW_HELP__"

    # --- Helpers ---

    def _extract_query(self, command: str, remove_words: list[str]) -> str:
        words = command.split()
        filtered = [w for w in words if w not in remove_words]
        return " ".join(filtered).strip()

    def cleanup(self):
        """Release all resources."""
        self.alarm.stop()
        if self.radio.is_playing:
            self.radio.stop()
        if self.web.is_active:
            self.web.close_service()
