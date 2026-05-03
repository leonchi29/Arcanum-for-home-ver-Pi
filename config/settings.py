"""
Application settings and configuration for Arcanum.
Zero external API keys required — everything works via web.
"""
import os

# Wake word configuration
WAKE_WORD = "arcanum"

# App info
APP_AUTHOR = "Carlos"
APP_NAME = "Arcanum"

# Weather (via wttr.in — no API key needed)
# Use ~location for GPS-like precision, or city name
WEATHER_CITY = "Colina"
WEATHER_COUNTRY = "CL"

# Listen timeout (seconds) — cancels if no speech detected
LISTEN_COMMAND_TIMEOUT = 10

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
        "search_url": "https://open.spotify.com/search/{query}",
        "needs_login": True,
        "type": "audio",
        "categories": {
            "recomendados": "https://open.spotify.com/genre/0JQ5DAqbMKFEC4WFtoNRpw",
            "novedades": "https://open.spotify.com/genre/0JQ5DAqbMKFAXlCG6QvYQ4",
            "top": "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF",
            "podcast": "https://open.spotify.com/genre/podcasts-web",
        },
    },
    "netflix": {
        "name": "Netflix",
        "url": "https://www.netflix.com",
        "search_url": "https://www.netflix.com/search?q={query}",
        "needs_login": True,
        "type": "video",
        "categories": {
            "continuar": "https://www.netflix.com/browse",
            "películas": "https://www.netflix.com/browse/genre/34399",
            "peliculas": "https://www.netflix.com/browse/genre/34399",
            "series": "https://www.netflix.com/browse/genre/83",
            "anime": "https://www.netflix.com/browse/genre/7424",
            "infantil": "https://www.netflix.com/browse/genre/783",
            "familia": "https://www.netflix.com/browse/genre/783",
            "documentales": "https://www.netflix.com/browse/genre/6839",
            "comedia": "https://www.netflix.com/browse/genre/6548",
            "acción": "https://www.netflix.com/browse/genre/801917",
            "accion": "https://www.netflix.com/browse/genre/801917",
            "terror": "https://www.netflix.com/browse/genre/8711",
        },
    },
    "disney": {
        "name": "Disney+",
        "url": "https://www.disneyplus.com",
        "search_url": "https://www.disneyplus.com/search?q={query}",
        "needs_login": True,
        "type": "video",
        "categories": {
            "películas": "https://www.disneyplus.com/movies",
            "peliculas": "https://www.disneyplus.com/movies",
            "series": "https://www.disneyplus.com/series",
            "infantil": "https://www.disneyplus.com/brand/disney",
            "marvel": "https://www.disneyplus.com/brand/marvel",
            "star wars": "https://www.disneyplus.com/brand/star-wars",
        },
    },
    "youtube": {
        "name": "YouTube",
        "url": "https://www.youtube.com",
        "search_url": "https://www.youtube.com/results?search_query={query}",
        "needs_login": False,
        "type": "video",
        "categories": {
            "música": "https://music.youtube.com",
            "musica": "https://music.youtube.com",
            "tendencias": "https://www.youtube.com/feed/trending",
            "suscripciones": "https://www.youtube.com/feed/subscriptions",
            "infantil": "https://www.youtubekids.com",
            "kids": "https://www.youtubekids.com",
        },
    },
    "prime": {
        "name": "Amazon Prime Video",
        "url": "https://www.primevideo.com",
        "search_url": "https://www.primevideo.com/search/?phrase={query}",
        "needs_login": True,
        "type": "video",
        "categories": {},
    },
    "hbo": {
        "name": "Max (HBO)",
        "url": "https://play.max.com",
        "search_url": "https://play.max.com/search?q={query}",
        "needs_login": True,
        "type": "video",
        "categories": {},
    },
    "zapping": {
        "name": "Zapping TV",
        "url": "https://www.zfreetv.com/",
        "search_url": "https://www.zfreetv.com/",
        "needs_login": False,
        "type": "video",
        "categories": {},
    },
    "paramount": {
        "name": "Paramount+",
        "url": "https://www.paramountplus.com",
        "search_url": "https://www.paramountplus.com/search/?q={query}",
        "needs_login": True,
        "type": "video",
        "categories": {},
    },
    "crunchyroll": {
        "name": "Crunchyroll",
        "url": "https://www.crunchyroll.com",
        "search_url": "https://www.crunchyroll.com/search?q={query}",
        "needs_login": True,
        "type": "video",
        "categories": {},
    },
}

# Speech recognition settings
SPEECH_LANGUAGE = "es-CL"
LISTEN_TIMEOUT = 10
PHRASE_TIME_LIMIT = 12

# TTS settings
TTS_LANGUAGE = "es"
TTS_RATE = 160

# Home location
HOME_LOCATION = "Colina, Santiago, Chile"

# User profiles storage
PROFILES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".profiles.json")
MODES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".modes.json")

# Enrollment calibration phrases (7 words/phrases user repeats)
ENROLLMENT_PHRASES = [
    "hola arcanum",
    "reproduce música",
    "qué hora es",
    "sube volumen",
    "abre netflix",
    "para todo",
    "buenas noches",
]

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

# Help / Command catalog (expanded with synonyms and new features)
COMMAND_CATALOG = [
    # --- Música ---
    {
        "command": "reproduce [canción] en [servicio]",
        "description": "Reproduce música en Spotify, YouTube u otro. Si no dices servicio, usa Spotify.",
        "example": "Arcanum, reproduce Bohemian Rhapsody en YouTube",
        "category": "Música",
    },
    {
        "command": "radio [estación]",
        "description": "Sintoniza una radio chilena en segundo plano (Bio Bio, Cooperativa, etc).",
        "example": "Arcanum, ponme radio Bio Bio",
        "category": "Música",
    },
    # --- Streaming ---
    {
        "command": "abre [servicio]",
        "description": "Abre Netflix, Disney+, YouTube, HBO, Prime, Paramount, Crunchyroll, Zapping.",
        "example": "Arcanum, abre Netflix",
        "category": "Streaming",
    },
    {
        "command": "busca [título] en [servicio]",
        "description": "Busca directamente en el servicio de streaming.",
        "example": "Arcanum, busca Los Simpson en Disney",
        "category": "Streaming",
    },
    {
        "command": "recomiéndame [categoría]",
        "description": "Muestra recomendaciones: películas, series, anime, infantil, comedia, terror.",
        "example": "Arcanum, recomiéndame películas de Netflix",
        "category": "Streaming",
    },
    {
        "command": "modo comer / noticias / tele",
        "description": "Abre Zapping TV con noticias en pantalla completa.",
        "example": "Arcanum, modo comer",
        "category": "Streaming",
    },
    {
        "command": "disponible / servicios",
        "description": "Lista todos los servicios y radios disponibles.",
        "example": "Arcanum, qué hay disponible",
        "category": "Streaming",
    },
    # --- Control ---
    {
        "command": "pausa / continua / para todo",
        "description": "Controles de reproducción (pausar, reanudar, parar). Sinónimos: espera, dale, stop.",
        "example": "Arcanum, pausa",
        "category": "Control",
    },
    {
        "command": "siguiente / anterior",
        "description": "Siguiente o anterior canción/video/episodio.",
        "example": "Arcanum, siguiente canción",
        "category": "Control",
    },
    {
        "command": "sube / baja / volumen al [%]",
        "description": "Control de volumen. Sinónimos: más fuerte, más bajo, silencio.",
        "example": "Arcanum, volumen al 60",
        "category": "Control",
    },
    {
        "command": "cierra / salir",
        "description": "Cierra el servicio web o radio actual y vuelve al inicio.",
        "example": "Arcanum, cierra eso",
        "category": "Control",
    },
    # --- Navegación ---
    {
        "command": "baja / sube (scroll)",
        "description": "Desplaza la página arriba o abajo.",
        "example": "Arcanum, baja",
        "category": "Navegación",
    },
    {
        "command": "click / selecciona / enter",
        "description": "Presiona Enter o selecciona el elemento enfocado.",
        "example": "Arcanum, dale click",
        "category": "Navegación",
    },
    {
        "command": "atrás / volver",
        "description": "Retrocede una página en el navegador.",
        "example": "Arcanum, vuelve atrás",
        "category": "Navegación",
    },
    {
        "command": "pantalla completa / fullscreen",
        "description": "Activa o sale de pantalla completa en el navegador.",
        "example": "Arcanum, pantalla completa",
        "category": "Navegación",
    },
    {
        "command": "actualiza / recarga",
        "description": "Recarga la página actual.",
        "example": "Arcanum, actualiza",
        "category": "Navegación",
    },
    {
        "command": "escribe [texto]",
        "description": "Tipea texto en el campo enfocado del navegador.",
        "example": "Arcanum, escribe mi correo",
        "category": "Navegación",
    },
    {
        "command": "teclado",
        "description": "Muestra un teclado en pantalla para ingresar texto manualmente.",
        "example": "Arcanum, teclado",
        "category": "Navegación",
    },
    # --- Info ---
    {
        "command": "qué hora es",
        "description": "Dice la hora actual. Sinónimos: dime la hora, hora actual.",
        "example": "Arcanum, qué hora es",
        "category": "Info",
    },
    {
        "command": "fecha / qué día es",
        "description": "Dice la fecha completa en español.",
        "example": "Arcanum, qué fecha es hoy",
        "category": "Info",
    },
    {
        "command": "clima / temperatura",
        "description": "Reporta el clima actual (sin API, vía web).",
        "example": "Arcanum, cómo está el clima",
        "category": "Info",
    },
    {
        "command": "busca [tema]",
        "description": "Busca información en internet. Sinónimos: qué es, quién es, explica.",
        "example": "Arcanum, quién fue Galileo",
        "category": "Info",
    },
    # --- Utilidades ---
    {
        "command": "alarma [HH:MM]",
        "description": "Configura una alarma. Sinónimos: despiértame, pon alarma.",
        "example": "Arcanum, alarma a las 7:30",
        "category": "Utilidades",
    },
    {
        "command": "temporizador [minutos]",
        "description": "Configura un temporizador. Sinónimos: timer, cuenta regresiva.",
        "example": "Arcanum, temporizador 15",
        "category": "Utilidades",
    },
    {
        "command": "genera QR wifi",
        "description": "Genera un código QR para conectarse al WiFi actual.",
        "example": "Arcanum, genera QR del wifi",
        "category": "Utilidades",
    },
    {
        "command": "inicia sesión",
        "description": "Ingresa credenciales al servicio activo. Guarda usuario y contraseña.",
        "example": "Arcanum, inicia sesión en Netflix",
        "category": "Utilidades",
    },
    # --- Modos (automatización) ---
    {
        "command": "configurar modo",
        "description": "Crea un modo personalizado con secuencia de acciones automáticas.",
        "example": "Arcanum, configurar modo (nombre: Santi, acciones: abre YouTube, busca Super Wings)",
        "category": "Modos",
    },
    {
        "command": "modo [nombre]",
        "description": "Ejecuta un modo guardado con todas sus acciones en secuencia.",
        "example": "Arcanum, modo Santi",
        "category": "Modos",
    },
    {
        "command": "listar modos / borrar modo [nombre]",
        "description": "Lista o elimina los modos guardados.",
        "example": "Arcanum, listar modos",
        "category": "Modos",
    },
    # --- Sistema ---
    {
        "command": "ayuda / comandos",
        "description": "Muestra esta lista de comandos disponibles.",
        "example": "Arcanum, ayuda",
        "category": "Sistema",
    },
    {
        "command": "apaga / reinicia",
        "description": "Apaga o reinicia el sistema (Raspberry Pi).",
        "example": "Arcanum, reinicia",
        "category": "Sistema",
    },
]
