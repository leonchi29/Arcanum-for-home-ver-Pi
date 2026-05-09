"""
Command router — Intent-based voice command dispatcher.
Uses services/intents.py for synonym matching.
Supports: music, video, radio, navigation, controls, alarms, search,
           login, automation modes, on-screen keyboard.
Zero external API keys required.
"""
import re
import time
import threading
from datetime import datetime

from services.radio_service import RadioService
from services.web_service import WebService
from services.weather_service import WeatherService
from services.alarm_service import AlarmService
from services.search_service import SearchService
from services.audio_manager import AudioManager
from services.wifi_qr_service import WifiQRService
from services.browser_control import BrowserControl
from services.credentials_service import CredentialsService
from services.automation_modes import AutomationModes
from services.fun_service import FunService
from services.utility_services import (
    Calculator, Translator, CurrencyConverter, UnitConverter,
    NotesService, SystemInfo,
)
from services.intents import (
    detect_intent, extract_search_query, detect_target_service,
)
from config.settings import STREAMING_SERVICES, AMBIENT_SOUNDS


# Special response sentinels for the GUI/main to intercept
SENTINEL_SHOW_HELP = "__SHOW_HELP__"
SENTINEL_HIDE_HELP = "__HIDE_HELP__"
SENTINEL_SHOW_QR = "__SHOW_QR__"
SENTINEL_HIDE_QR = "__HIDE_QR__"
SENTINEL_SHUTDOWN = "__SHUTDOWN__"
SENTINEL_RESTART = "__RESTART__"
SENTINEL_SHOW_KEYBOARD = "__SHOW_KEYBOARD__"
SENTINEL_HIDE_KEYBOARD = "__HIDE_KEYBOARD__"
SENTINEL_CONFIGURE_MODE = "__CONFIGURE_MODE__"
SENTINEL_LOGIN_PROMPT = "__LOGIN_PROMPT__"


class CommandRouter:
    def __init__(self, on_alarm_callback=None, prompt_callback=None):
        """
        prompt_callback(question: str) -> str | None
            Called when Arcanum needs to ask a follow-up via voice.
        """
        self.radio = RadioService()
        self.web = WebService()
        self.weather = WeatherService()
        self.alarm = AlarmService(on_alarm_callback=on_alarm_callback)
        self.search = SearchService()
        self.audio = AudioManager()
        self.wifi_qr = WifiQRService()
        self.browser = BrowserControl()
        self.credentials = CredentialsService()
        self.modes = AutomationModes()
        self.fun = FunService()
        self.calc = Calculator()
        self.translator = Translator()
        self.currency = CurrencyConverter()
        self.units = UnitConverter()
        self.notes = NotesService()
        self.sysinfo = SystemInfo()

        self._prompt = prompt_callback

    # ============================================================
    # MAIN ROUTER
    # ============================================================

    def process_command(self, command: str) -> str:
        """Detect intent and dispatch to the proper handler."""
        if not command:
            return "No te entendí, intenta de nuevo."

        # Check if command matches an automation mode first
        mode = self.modes.find_mode(command)
        if mode:
            return self._execute_mode(mode)

        intent, _ = detect_intent(command)

        handlers = {
            # Help / system
            "help": self._handle_help,
            "hide_help": lambda c: SENTINEL_HIDE_HELP,
            "shutdown": lambda c: SENTINEL_SHUTDOWN,
            "restart": lambda c: SENTINEL_RESTART,
            # Time / date / weather
            "time": self._handle_time,
            "date": self._handle_date,
            "weather": self._handle_weather,
            # Alarms
            "alarm": self._handle_alarm,
            "timer": self._handle_timer,
            "cancel_alarm": lambda c: self.alarm.cancel_alarms(),
            # WiFi
            "wifi_qr": self._handle_wifi_qr,
            "hide_qr": lambda c: SENTINEL_HIDE_QR,
            # Radio
            "radio": self._handle_radio,
            "list_radios": self._handle_list_radios,
            # Streaming services (specific)
            "open_spotify": lambda c: self._open_streaming("spotify", c),
            "open_netflix": lambda c: self._open_streaming("netflix", c),
            "open_youtube": lambda c: self._open_streaming("youtube", c),
            "open_disney": lambda c: self._open_streaming("disney", c),
            "open_hbo": lambda c: self._open_streaming("hbo", c),
            "open_prime": lambda c: self._open_streaming("prime", c),
            "open_paramount": lambda c: self._open_streaming("paramount", c),
            "open_crunchyroll": lambda c: self._open_streaming("crunchyroll", c),
            "open_zapping": self._handle_zapping,
            # Generic media
            "play_media": self._handle_play_media,
            "play_video": self._handle_play_video,
            # Recommendations
            "recommend": self._handle_recommend,
            "continue_watching": self._handle_continue_watching,
            # Lists
            "list_services": self._handle_list_services,
            # Close / stop
            "close_service": self._handle_close,
            "stop_all": self._handle_stop_all,
            # Playback
            "pause": self._handle_pause,
            "resume": self._handle_resume,
            "next_track": self._handle_next,
            "previous_track": self._handle_previous,
            # Volume
            "volume_up": lambda c: self._set_volume(90),
            "volume_down": lambda c: self._set_volume(40),
            "volume_set": self._handle_volume_set,
            "mute": lambda c: (self.audio.mute(), "Silenciado.")[-1],
            "unmute": lambda c: (self.audio.unmute(), "Sonido restaurado.")[-1],
            # Browser navigation
            "scroll_down": lambda c: (self.browser.scroll_down(), "Bajando.")[-1],
            "scroll_up": lambda c: (self.browser.scroll_up(), "Subiendo.")[-1],
            "click": lambda c: (self.browser.click_or_select(), "Listo.")[-1],
            "back": lambda c: (self.browser.press_back(), "Atrás.")[-1],
            "fullscreen": lambda c: (self.browser.fullscreen(), "Pantalla completa.")[-1],
            "exit_fullscreen": lambda c: (self.browser.fullscreen(), "Listo.")[-1],
            "refresh": lambda c: (self.browser.refresh_page(), "Recargando.")[-1],
            "search_in_page": lambda c: (self.browser.open_search(), "Busca en la página.")[-1],
            "press_enter": lambda c: (self.browser.click_or_select(), "Enter.")[-1],
            "type_text": self._handle_type_text,
            # Login
            "login": self._handle_login,
            # Search
            "search_web": self._handle_search,
            # Greetings
            "greeting": lambda c: "Hola! ¿Cómo te puedo ayudar?",
            "thanks": lambda c: "De nada! Estoy para servirte.",
            # Modes
            "configure_mode": lambda c: SENTINEL_CONFIGURE_MODE,
            "execute_mode": self._handle_execute_mode,
            "list_modes": lambda c: self.modes.list_modes(),
            "delete_mode": self._handle_delete_mode,
            # Keyboard
            "show_keyboard": lambda c: SENTINEL_SHOW_KEYBOARD,
            "hide_keyboard": lambda c: SENTINEL_HIDE_KEYBOARD,
            # ===== Diversión =====
            "joke": lambda c: self.fun.joke(),
            "fun_fact": lambda c: self.fun.fun_fact(),
            "quote": lambda c: self.fun.quote(),
            "compliment": lambda c: self.fun.compliment(),
            "tell_story": lambda c: self.fun.story(),
            "sing": lambda c: "La la la… la, la la… mejor pongo música. Di 'reproduce algo'.",
            "beatbox": lambda c: "Boots and cats and boots and cats… 🎤",
            # ===== Juegos / azar =====
            "flip_coin": lambda c: self.fun.flip_coin(),
            "roll_dice": self._handle_dice,
            "random_number": self._handle_random_number,
            "decide": lambda c: self.fun.decide(),
            "rock_paper_scissors": lambda c: self.fun.rock_paper_scissors(),
            # ===== Calculadora / matemáticas =====
            "calculate": lambda c: self.calc.calculate(c),
            # ===== Definición / traducción =====
            "definition": self._handle_definition,
            "translate": lambda c: self.translator.translate(c),
            "spell": lambda c: self.translator.spell(c),
            # ===== Conversiones =====
            "convert_currency": lambda c: self.currency.convert(c),
            "convert_unit": lambda c: self.units.convert(c),
            # ===== Trivia / cultura =====
            "trivia": lambda c: self.fun.trivia(),
            "tongue_twister": lambda c: self.fun.tongue_twister(),
            "riddle": lambda c: self.fun.riddle(),
            # ===== Noticias =====
            "news": self._handle_news,
            "sports_news": self._handle_sports_news,
            # ===== Sonidos ambientales =====
            "ambient_sound": self._handle_ambient,
            # ===== Salud / bienestar =====
            "breathing": self._handle_breathing,
            "meditation": self._handle_meditation,
            "stretch": self._handle_stretch,
            # ===== Cocina =====
            "recipe": self._handle_recipe,
            "shopping_list": self._handle_shopping,
            # ===== Notas / recordatorios =====
            "add_note": lambda c: self.notes.add_note(c),
            "list_notes": lambda c: self.notes.list_notes(),
            "clear_notes": lambda c: self.notes.clear_notes(),
            "reminder": self._handle_reminder,
            # ===== Comunicación =====
            "call_person": self._handle_call,
            "send_message": self._handle_message,
            "open_email": lambda c: self._open_url("https://mail.google.com", "correo"),
            "open_calendar": lambda c: self._open_url("https://calendar.google.com", "calendario"),
            "open_maps": self._handle_maps,
            # ===== Sistema avanzado =====
            "screenshot": lambda c: self.sysinfo.screenshot(),
            "battery": lambda c: self.sysinfo.battery(),
            "system_info": lambda c: self.sysinfo.cpu_ram() + " " + self.sysinfo.temperature(),
            "ip_info": lambda c: self.sysinfo.ip_address(),
            "wifi_status": lambda c: self.sysinfo.wifi_status(),
            "speedtest": lambda c: self.sysinfo.speedtest(),
            # ===== Horóscopo / efemérides =====
            "horoscope": self._handle_horoscope,
            "this_day": lambda c: self.fun.this_day_in_history(),
            # ===== Usuario / voz =====
            "who_am_i": lambda c: "Eres mi usuario favorito. Si quieres registrarte, ejecuta el enrolamiento de voz.",
            "who_are_you": lambda c: "Soy Arcanum, tu asistente de voz para el hogar. Puedo poner música, controlar streaming, contarte chistes, gestionar tus notas y mucho más. Di 'ayuda' para verlo todo.",
            "tts_speed_up": lambda c: "Ok, hablaré más rápido en la próxima sesión.",
            "tts_speed_down": lambda c: "Ok, hablaré más pausado en la próxima sesión.",
            # ===== Despedida =====
            "goodbye": lambda c: "¡Hasta luego! Aquí estaré cuando me necesites.",
            # ===== Contenido de internet (APIs gratis) =====
            "cat_fact": lambda c: self.fun.cat_fact(),
            "dog_fact": lambda c: self.fun.dog_fact(),
            "advice": lambda c: self.fun.advice(),
            "activity": lambda c: self.fun.activity(),
            "number_trivia": self._handle_number_trivia,
            "yes_no_oracle": lambda c: self.fun.yes_no(),
            "chuck_norris": lambda c: self.fun.chuck_norris(),
            "wiki_random": lambda c: self.search.search("wikipedia random"),
        }

        if intent in handlers:
            return handlers[intent](command)

        # No intent matched → ask user instead of silently web-searching
        cmd_clean = command.strip()
        if len(cmd_clean.split()) <= 2:
            return "No te he entendido. ¿Puedes repetir o decir 'ayuda'?"
        # For longer phrases assume it's a real question → search the web
        return self._handle_search(command)

    # ============================================================
    # MEDIA HANDLERS
    # ============================================================

    def _handle_play_media(self, command: str) -> str:
        """Play music. Detects target service or defaults to Spotify."""
        target = detect_target_service(command) or "spotify"
        query = extract_search_query(command)

        if "radio" in command.lower() or self.radio.find_station(query):
            return self._handle_radio(command)

        if not query:
            return f"¿Qué quieres reproducir en {STREAMING_SERVICES[target]['name']}?"

        return self._open_streaming(target, command, search_query=query)

    def _handle_play_video(self, command: str) -> str:
        """Play video content — route to appropriate service."""
        target = detect_target_service(command)
        query = extract_search_query(command)

        if not target:
            # Default to YouTube for video content
            target = "youtube"

        if not query:
            return self._open_streaming(target, command)

        return self._open_streaming(target, command, search_query=query)

    def _open_streaming(self, service_key: str, command: str,
                        search_query: str = "") -> str:
        """Open a specific streaming service with optional search."""
        if not search_query:
            search_query = extract_search_query(command)
            for word in [service_key, "spotify", "netflix", "youtube", "disney",
                         "hbo", "max", "prime", "paramount", "crunchyroll"]:
                search_query = search_query.replace(word, "").strip()

        # Detect category
        service = STREAMING_SERVICES.get(service_key, {})
        category = ""
        for cat_name in service.get("categories", {}):
            if cat_name in command.lower():
                category = cat_name
                break

        result = self.web.open_service(
            service_key,
            search_query=search_query if not category else "",
            category=category,
        )

        if not result["success"]:
            return result["message"]

        msg = result["message"]

        # Auto-login if we have credentials
        if result.get("needs_login") and self.credentials.has_credentials(service_key):
            threading.Thread(
                target=self._auto_login_after_delay,
                args=(service_key,),
                daemon=True,
            ).start()
            msg += ". Iniciando sesión automáticamente."
        elif result.get("needs_login") and not self.credentials.has_credentials(service_key):
            msg += ". Si necesitas iniciar sesión, di 'inicia sesión'."

        return msg

    def _auto_login_after_delay(self, service_key: str):
        """Wait for page to load then autofill credentials."""
        time.sleep(4)
        self.credentials.autofill_login(service_key, self.browser)

    # ============================================================
    # LOGIN
    # ============================================================

    def _handle_login(self, command: str) -> str:
        """Handle login — prompts for credentials via voice."""
        service_key = self.web.current_service
        if not service_key:
            return "No hay servicio activo. Abre un servicio primero."

        service_name = STREAMING_SERVICES[service_key]["name"]

        if self.credentials.has_credentials(service_key):
            self.credentials.autofill_login(service_key, self.browser)
            return f"Iniciando sesión en {service_name}."

        # Return sentinel so main.py handles the voice prompt flow
        return f"{SENTINEL_LOGIN_PROMPT}{service_key}"

    # ============================================================
    # RADIO
    # ============================================================

    def _handle_radio(self, command: str) -> str:
        if self.radio.is_playing:
            self.radio.stop()

        station_query = extract_search_query(command)
        for w in ["radio", "emisora", "estación", "estacion", "fm", "sintoniza",
                   "sintonizar", "ponme", "pon", "pone", "escuchar"]:
            station_query = station_query.replace(w, "").strip()

        if not station_query:
            return self._handle_list_radios(command)

        if self.radio.play_station(station_query):
            station = self.radio.find_station(station_query)
            return f"Reproduciendo Radio {station.title() if station else station_query} en segundo plano."

        stations = ", ".join(self.radio.get_available_stations())
        return f"Estación no encontrada. Disponibles: {stations}"

    def _handle_list_radios(self, command: str) -> str:
        stations = ", ".join(r.title() for r in self.radio.get_available_stations())
        return f"Radios disponibles: {stations}"

    # ============================================================
    # ZAPPING
    # ============================================================

    def _handle_zapping(self, command: str) -> str:
        result = self.web.open_service("zapping")
        return "Modo comer activado. ¡A disfrutar las noticias!" if result["success"] else result["message"]

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================

    def _handle_recommend(self, command: str) -> str:
        cmd_lower = command.lower()
        target = detect_target_service(command)

        category_keywords = {
            "infantil": ["infantil", "niños", "ninos", "kids", "familia", "familiar"],
            "películas": ["película", "pelicula", "películas", "peliculas"],
            "series": ["serie", "series"],
            "anime": ["anime", "animé"],
            "documentales": ["documental", "documentales"],
            "comedia": ["comedia", "cómico", "comico"],
            "acción": ["acción", "accion"],
            "terror": ["terror", "horror", "miedo"],
            "música": ["música", "musica"],
            "tendencias": ["tendencias", "trending"],
        }

        detected_cat = None
        for cat, keywords in category_keywords.items():
            if any(kw in cmd_lower for kw in keywords):
                detected_cat = cat
                break

        if not target:
            target = "netflix"

        service = STREAMING_SERVICES.get(target, {})
        if detected_cat and detected_cat in service.get("categories", {}):
            result = self.web.open_service(target, category=detected_cat)
            return result["message"]

        result = self.web.open_service(target)
        if not detected_cat:
            return f"Abriendo {service.get('name', target)}. Dime qué categoría quieres ver."
        return result["message"]

    def _handle_continue_watching(self, command: str) -> str:
        target = detect_target_service(command) or "netflix"
        return self._open_streaming(target, command)

    # ============================================================
    # LIST / DISCOVERY
    # ============================================================

    def _handle_list_services(self, command: str) -> str:
        services = ", ".join(info["name"] for info in STREAMING_SERVICES.values())
        radios = ", ".join(r.title() for r in self.radio.get_available_stations())
        return f"Streaming: {services}. Radios: {radios}."

    # ============================================================
    # CLOSE / STOP
    # ============================================================

    def _handle_close(self, command: str) -> str:
        if self.web.is_active:
            return self.web.close_service()
        if self.radio.is_playing:
            self.radio.stop()
            return "Radio detenida."
        return "Nada que cerrar."

    def _handle_stop_all(self, command: str) -> str:
        msgs = []
        if self.radio.is_playing:
            self.radio.stop()
            msgs.append("Radio detenida")
        if self.web.is_active:
            self.web.close_service()
            msgs.append("Servicio cerrado")
        if not msgs:
            return "Nada activo para detener."
        return ". ".join(msgs) + "."

    # ============================================================
    # PLAYBACK
    # ============================================================

    def _handle_pause(self, command: str) -> str:
        if self.web.is_active:
            self.browser.play_pause()
            return "Pausado."
        if self.radio.is_playing:
            self.audio.mute()
            return "Radio pausada."
        return "Nada para pausar."

    def _handle_resume(self, command: str) -> str:
        if self.web.is_active:
            self.browser.play_pause()
            return "Continuando."
        if self.radio.is_playing:
            self.audio.unmute()
            return "Radio reanudada."
        return "Nada para reanudar."

    def _handle_next(self, command: str) -> str:
        if self.web.is_active:
            self.browser.video_next_episode()
            return "Siguiente."
        return "Sin siguiente disponible."

    def _handle_previous(self, command: str) -> str:
        if self.web.is_active:
            self.browser.video_seek_back()
            return "Atrás."
        return "Sin anterior disponible."

    # ============================================================
    # VOLUME
    # ============================================================

    def _set_volume(self, level: int) -> str:
        self.audio.set_volume(level)
        self.radio.set_volume(level)
        return f"Volumen al {level}%."

    def _handle_volume_set(self, command: str) -> str:
        numbers = [int(s) for s in re.findall(r"\d+", command)]
        if numbers:
            vol = max(0, min(100, numbers[0]))
            return self._set_volume(vol)
        return "Dime el porcentaje. Ejemplo: volumen al 60."

    # ============================================================
    # TIME / DATE / WEATHER
    # ============================================================

    def _handle_time(self, command: str) -> str:
        now = datetime.now()
        return f"Son las {now.hour}:{now.minute:02d}."

    def _handle_date(self, command: str) -> str:
        now = datetime.now()
        days_es = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        months_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"Hoy es {days_es[now.weekday()]} {now.day} de {months_es[now.month - 1]} de {now.year}."

    def _handle_weather(self, command: str) -> str:
        city_query = extract_search_query(command)
        for w in ["clima", "tiempo", "temperatura", "llueve", "lluvia",
                   "como", "cómo", "esta", "está", "pronostico", "pronóstico"]:
            city_query = city_query.replace(w, "").strip()
        return self.weather.get_weather(city_query)

    # ============================================================
    # ALARM / TIMER
    # ============================================================

    def _handle_alarm(self, command: str) -> str:
        time_match = re.search(r"(\d{1,2})[:\s]?(\d{2})?", command)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.alarm.set_alarm(hour, minute)
                return f"Alarma configurada para las {hour}:{minute:02d}."
        return "Dime la hora. Ejemplo: alarma a las 7:30."

    def _handle_timer(self, command: str) -> str:
        num_match = re.search(r"(\d+)", command)
        if num_match:
            minutes = int(num_match.group(1))
            if 1 <= minutes <= 1440:
                self.alarm.set_timer(minutes)
                return f"Temporizador de {minutes} minutos iniciado."
        return "¿Cuántos minutos? Ejemplo: temporizador 10 minutos."

    # ============================================================
    # WIFI QR
    # ============================================================

    def _handle_wifi_qr(self, command: str) -> str:
        qr_path = self.wifi_qr.generate_qr()
        if qr_path:
            wifi_text = self.wifi_qr.get_wifi_text()
            return f"{SENTINEL_SHOW_QR}{qr_path}__|__{wifi_text}"
        return "No pude leer la información del WiFi."

    # ============================================================
    # SEARCH
    # ============================================================

    def _handle_search(self, command: str) -> str:
        query = extract_search_query(command)
        if not query:
            query = command
        return self.search.search(query)

    # ============================================================
    # HELP
    # ============================================================

    def _handle_help(self, command: str) -> str:
        return SENTINEL_SHOW_HELP

    # ============================================================
    # TYPE TEXT
    # ============================================================

    def _handle_type_text(self, command: str) -> str:
        text = extract_search_query(command)
        for w in ["escribe", "escribir", "tipea", "tipear", "ingresa",
                   "ingresar", "type", "pon", "texto"]:
            text = text.replace(w, "").strip()
        if text:
            self.browser.type_text(text)
            return f"Escribiendo: {text}"
        return "¿Qué quieres escribir?"

    # ============================================================
    # AUTOMATION MODES
    # ============================================================

    def _handle_execute_mode(self, command: str) -> str:
        """Execute a named mode."""
        mode = self.modes.find_mode(command)
        if mode:
            return self._execute_mode(mode)
        # Extract mode name
        name = command.lower().replace("modo", "").replace("ejecutar", "").replace(
            "activar", "").replace("pon", "").replace("lanzar", "").strip()
        return f"No encontré el modo '{name}'. Di 'listar modos' para ver los disponibles."

    def _execute_mode(self, mode: dict) -> str:
        """Execute all actions in a mode sequentially."""
        name = mode["name"]
        actions = mode["actions"]
        results = []

        for action in actions:
            result = self.process_command(action)
            # Skip sentinels in mode execution (don't trigger UI actions)
            if not result.startswith("__"):
                results.append(result)
            time.sleep(1)  # Brief pause between actions

        summary = f"Modo {name} ejecutado: {len(actions)} acciones."
        return summary

    def _handle_delete_mode(self, command: str) -> str:
        """Delete a named mode."""
        name = command.lower()
        for prefix in ["borrar modo ", "eliminar modo ", "quitar modo ",
                        "borra modo ", "elimina modo "]:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
                break
        return self.modes.delete_mode(name)

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self):
        """Release all resources."""
        self.alarm.stop()
        if self.radio.is_playing:
            self.radio.stop()
        if self.web.is_active:
            self.web.close_service()

    # ============================================================
    # NEW HANDLERS — DIVERSIÓN, JUEGOS, INFO, MODOS DE AMBIENTE
    # ============================================================

    def _handle_dice(self, command: str) -> str:
        nums = re.findall(r"\d+", command)
        sides = int(nums[0]) if nums else 6
        count = int(nums[1]) if len(nums) > 1 else 1
        sides = max(2, min(100, sides))
        count = max(1, min(10, count))
        return self.fun.roll_dice(sides, count)

    def _handle_random_number(self, command: str) -> str:
        nums = [int(n) for n in re.findall(r"\d+", command)]
        if len(nums) >= 2:
            return self.fun.random_number(min(nums[0], nums[1]), max(nums[0], nums[1]))
        if len(nums) == 1:
            return self.fun.random_number(1, nums[0])
        return self.fun.random_number()

    def _handle_number_trivia(self, command: str) -> str:
        nums = [int(n) for n in re.findall(r"\d+", command)]
        return self.fun.number_trivia(nums[0] if nums else None)

    def _handle_definition(self, command: str) -> str:
        text = command.lower()
        for trig in ["qué significa", "que significa", "significado de",
                     "definición de", "definicion de", "define",
                     "qué quiere decir", "que quiere decir"]:
            text = text.replace(trig, "")
        text = text.strip(" :,.")
        if not text:
            return "¿Qué palabra quieres definir?"
        return self.search.search(f"definición {text}")

    def _handle_news(self, command: str) -> str:
        return self._open_url(
            "https://www.biobiochile.cl/", "noticias del día"
        )

    def _handle_sports_news(self, command: str) -> str:
        return self._open_url(
            "https://www.adnradio.cl/deportes/", "noticias deportivas"
        )

    def _handle_ambient(self, command: str) -> str:
        cmd = command.lower()
        match = None
        for sound_name in AMBIENT_SOUNDS:
            if sound_name in cmd:
                match = sound_name
                break
        if not match:
            options = ", ".join(list(AMBIENT_SOUNDS.keys())[:10])
            return f"¿Qué sonido? Disponibles: {options}…"
        url = AMBIENT_SOUNDS[match]
        result = self.web._open_url(url) if hasattr(self.web, "_open_url") else None
        # Use generic open
        try:
            self.web.close_service()
        except Exception:
            pass
        import webbrowser
        webbrowser.open(url)
        return f"Reproduciendo sonido de {match}."

    def _handle_breathing(self, command: str) -> str:
        return ("Vamos a respirar juntos. Inhala 4 segundos… "
                "retén 7 segundos… exhala 8 segundos. "
                "Repite tres veces. Ya estás más calmado.")

    def _handle_meditation(self, command: str) -> str:
        return self._handle_ambient("ponme meditación")

    def _handle_stretch(self, command: str) -> str:
        return ("Rutina de estiramiento: 1) Cuello en círculos. "
                "2) Hombros arriba y abajo. 3) Toca tus pies. "
                "4) Estira los brazos al cielo. Cada uno 30 segundos.")

    def _handle_recipe(self, command: str) -> str:
        text = command.lower()
        for trig in ["receta de", "receta", "cómo hago", "como hago",
                     "cómo se prepara", "como se prepara", "ingredientes para"]:
            text = text.replace(trig, "")
        text = text.strip(" :,.")
        if not text:
            return "¿Receta de qué?"
        return self._open_url(
            f"https://www.google.com/search?q=receta+{text.replace(' ', '+')}",
            f"recetas de {text}"
        )

    def _handle_shopping(self, command: str) -> str:
        cmd = command.lower()
        if any(t in cmd for t in ["ver lista", "qué hay", "que hay", "mi lista"]):
            return self.notes.show_list()
        if any(t in cmd for t in ["borrar lista", "limpia la lista", "limpiar lista", "vacía", "vacia"]):
            return self.notes.clear_list()
        return self.notes.add_to_list(command)

    def _handle_reminder(self, command: str) -> str:
        # Try to extract HH:MM
        time_match = re.search(r"(\d{1,2})[:\s](\d{2})", command)
        if time_match:
            h, m = int(time_match.group(1)), int(time_match.group(2))
            self.alarm.set_alarm(h, m)
            return f"Recordatorio puesto para las {h}:{m:02d}."
        # In N minutes
        min_match = re.search(r"en\s+(\d+)\s*minutos?", command.lower())
        if min_match:
            mins = int(min_match.group(1))
            self.alarm.set_timer(mins)
            return f"Te recordaré en {mins} minutos."
        return "Dime cuándo. Ejemplo: recuérdame en 10 minutos, o a las 18:30."

    # ----------- COMUNICACIÓN -----------

    def _handle_call(self, command: str) -> str:
        text = command.lower()
        for t in ["llama a", "llamar a", "marca a", "telefonéame", "telefoneame a"]:
            text = text.replace(t, "")
        name = text.strip(" :,.")
        return f"No tengo telefonía conectada todavía. Pero apunté: 'llamar a {name}'."

    def _handle_message(self, command: str) -> str:
        return self._open_url("https://web.whatsapp.com", "WhatsApp Web")

    def _handle_maps(self, command: str) -> str:
        text = command.lower()
        for t in ["abre maps", "abre mapas", "abre google maps", "muéstrame el mapa",
                  "muestrame el mapa", "cómo llego a", "como llego a", "ruta a",
                  "rutas a", "dirección a", "direccion a"]:
            text = text.replace(t, "")
        dest = text.strip(" :,.")
        if dest:
            url = f"https://www.google.com/maps/dir/?api=1&destination={dest.replace(' ', '+')}"
            return self._open_url(url, f"ruta a {dest}")
        return self._open_url("https://maps.google.com", "Google Maps")

    def _handle_horoscope(self, command: str) -> str:
        text = command.lower().replace("horóscopo de", "").replace("horoscopo de", "")
        text = text.replace("horóscopo", "").replace("horoscopo", "")
        text = text.replace("mi signo es", "").replace("signo", "").strip()
        if not text:
            return "¿Cuál es tu signo? Por ejemplo: 'horóscopo de leo'."
        return self.fun.horoscope(text.split()[0])

    # ----------- HELPER: open arbitrary URL -----------

    def _open_url(self, url: str, label: str = "") -> str:
        try:
            import webbrowser
            webbrowser.open(url)
            return f"Abriendo {label or 'la página'}."
        except Exception:
            return "No pude abrir esa página."
