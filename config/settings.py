"""
Application settings and configuration for Arcanum.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Picovoice wake word detection
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")

# Wake word configuration
WAKE_WORD = "arcanum"

# App info
APP_AUTHOR = "Carlos"
APP_NAME = "Arcanum"

# Weather API (OpenWeatherMap free tier)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "Santiago")
WEATHER_COUNTRY = os.getenv("WEATHER_COUNTRY", "CL")

# Chilean radio stations (streaming URLs)
RADIO_STATIONS = {
    "bio bio": "https://playerservices.streamtheworld.com/api/livestream-redirect/BBCL_SC",
    "cooperativa": "https://playerservices.streamtheworld.com/api/livestream-redirect/COOPERATIVA_SC",
    "rock and pop": "https://playerservices.streamtheworld.com/api/livestream-redirect/ROCKANDPOP_SC",
    "futuro": "https://playerservices.streamtheworld.com/api/livestream-redirect/FUTURO_SC",
    "concierto": "https://playerservices.streamtheworld.com/api/livestream-redirect/CONCIERTO_SC",
    "pudahuel": "https://playerservices.streamtheworld.com/api/livestream-redirect/PUDAHUEL_SC",
    "corazon": "https://playerservices.streamtheworld.com/api/livestream-redirect/CORAZON_SC",
    "adn": "https://playerservices.streamtheworld.com/api/livestream-redirect/ADN_SC",
    "la clave": "https://playerservices.streamtheworld.com/api/livestream-redirect/LACLAVE_SC",
    "infinita": "https://playerservices.streamtheworld.com/api/livestream-redirect/INFINITA_SC",
    "duna": "https://playerservices.streamtheworld.com/api/livestream-redirect/DUNA_SC",
    "universo": "https://playerservices.streamtheworld.com/api/livestream-redirect/UNIVERSO_SC",
}

# Streaming services (web-based via Chromium)
STREAMING_SERVICES = {
    "spotify": {
        "name": "Spotify",
        "url": "https://open.spotify.com",
        "needs_login": True,
    },
    "netflix": {
        "name": "Netflix",
        "url": "https://www.netflix.com",
        "needs_login": True,
    },
    "disney": {
        "name": "Disney+",
        "url": "https://www.disneyplus.com",
        "needs_login": True,
    },
    "youtube": {
        "name": "YouTube",
        "url": "https://www.youtube.com",
        "needs_login": False,
    },
    "prime": {
        "name": "Amazon Prime Video",
        "url": "https://www.primevideo.com",
        "needs_login": True,
    },
    "hbo": {
        "name": "Max (HBO)",
        "url": "https://play.max.com",
        "needs_login": True,
    },
    "zapping": {
        "name": "Zapping TV",
        "url": "https://www.zfreetv.com/",
        "needs_login": False,
    },
    "paramount": {
        "name": "Paramount+",
        "url": "https://www.paramountplus.com",
        "needs_login": True,
    },
    "crunchyroll": {
        "name": "Crunchyroll",
        "url": "https://www.crunchyroll.com",
        "needs_login": True,
    },
}

# Speech recognition settings
SPEECH_LANGUAGE = "es-CL"
LISTEN_TIMEOUT = 7
PHRASE_TIME_LIMIT = 12

# TTS settings
TTS_LANGUAGE = "es"
TTS_RATE = 160

# Home location
HOME_LOCATION = os.getenv("HOME_LOCATION", "Santiago, Chile")

# Screensaver settings
SCREENSAVER_TIMEOUT = 120  # Seconds of inactivity before screensaver

# GUI colors (dark blue theme)
COLOR_BG = "#0b1929"
COLOR_BG_CARD = "#0f2744"
COLOR_BG_HEADER = "#081a2e"
COLOR_TEXT = "#e0e8f0"
COLOR_ACCENT = "#00b4d8"
COLOR_USER = "#4fc3f7"
COLOR_BOT = "#00e676"
COLOR_DIM = "#4a6a8a"
COLOR_LISTENING = "#ff5722"
COLOR_LISTENING_BG = "#1a1a2e"
COLOR_HELP_BG = "#0d2137"

# Help / Command catalog
COMMAND_CATALOG = [
    {
        "command": "reproduce [canción]",
        "description": "Abre Spotify Web y busca la canción o artista.",
        "example": "Arcanum, reproduce Bohemian Rhapsody",
        "category": "Música",
    },
    {
        "command": "radio [estación]",
        "description": "Reproduce una radio chilena en streaming por VLC.",
        "example": "Arcanum, radio Bio Bio",
        "category": "Música",
    },
    {
        "command": "modo comer",
        "description": "Abre Zapping TV con noticias en pantalla completa.",
        "example": "Arcanum, modo comer",
        "category": "Streaming",
    },
    {
        "command": "netflix / disney / youtube / hbo / prime",
        "description": "Abre el servicio de streaming en Chromium.",
        "example": "Arcanum, abre Netflix",
        "category": "Streaming",
    },
    {
        "command": "disponible",
        "description": "Lista todos los servicios y radios disponibles.",
        "example": "Arcanum, qué hay disponible",
        "category": "Streaming",
    },
    {
        "command": "cierra",
        "description": "Cierra el servicio web o radio actual.",
        "example": "Arcanum, cierra",
        "category": "Control",
    },
    {
        "command": "pausa / continua / para todo",
        "description": "Controles de reproducción (pausar, reanudar, parar).",
        "example": "Arcanum, pausa",
        "category": "Control",
    },
    {
        "command": "sube / baja volumen",
        "description": "Sube o baja el volumen del sistema.",
        "example": "Arcanum, sube volumen",
        "category": "Control",
    },
    {
        "command": "qué hora es",
        "description": "Dice la hora actual.",
        "example": "Arcanum, qué hora es",
        "category": "Info",
    },
    {
        "command": "fecha",
        "description": "Dice la fecha actual completa.",
        "example": "Arcanum, qué fecha es",
        "category": "Info",
    },
    {
        "command": "clima",
        "description": "Reporta el clima actual de tu ciudad.",
        "example": "Arcanum, cómo está el clima",
        "category": "Info",
    },
    {
        "command": "alarma [HH:MM]",
        "description": "Configura una alarma para una hora específica.",
        "example": "Arcanum, alarma a las 7:30",
        "category": "Utilidades",
    },
    {
        "command": "temporizador [minutos]",
        "description": "Configura un temporizador en minutos.",
        "example": "Arcanum, temporizador 15",
        "category": "Utilidades",
    },
    {
        "command": "genera QR wifi",
        "description": "Genera un código QR para conectarse al WiFi.",
        "example": "Arcanum, genera QR del wifi",
        "category": "Utilidades",
    },
    {
        "command": "busca [tema]",
        "description": "Busca información en internet y la muestra en pantalla.",
        "example": "Arcanum, busca quién fue Galileo",
        "category": "Info",
    },
    {
        "command": "ayuda",
        "description": "Muestra esta lista de comandos disponibles.",
        "example": "Arcanum, ayuda",
        "category": "Sistema",
    },
]
