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

# Radio stations (streaming URLs) — Chile + internacionales + temáticas
RADIO_STATIONS = {
    # ============== CHILE ==============
    # Noticias / hablada
    "bio bio": "https://playerservices.streamtheworld.com/api/livestream-redirect/BBCL_SC",
    "cooperativa": "https://playerservices.streamtheworld.com/api/livestream-redirect/COOPERATIVA_SC",
    "adn": "https://playerservices.streamtheworld.com/api/livestream-redirect/ADN_SC",
    "agricultura": "https://server4.servers15.com:7022/stream",
    "duna": "https://playerservices.streamtheworld.com/api/livestream-redirect/DUNA_SC",
    "la clave": "https://playerservices.streamtheworld.com/api/livestream-redirect/LACLAVE_SC",
    "infinita": "https://playerservices.streamtheworld.com/api/livestream-redirect/INFINITA_SC",
    "uchile": "https://radio.uchile.cl:8443/stream",
    # Música chilena / popular
    "rock and pop": "https://playerservices.streamtheworld.com/api/livestream-redirect/ROCKANDPOP_SC",
    "futuro": "https://playerservices.streamtheworld.com/api/livestream-redirect/FUTURO_SC",
    "concierto": "https://playerservices.streamtheworld.com/api/livestream-redirect/CONCIERTO_SC",
    "pudahuel": "https://playerservices.streamtheworld.com/api/livestream-redirect/PUDAHUEL_SC",
    "corazon": "https://playerservices.streamtheworld.com/api/livestream-redirect/CORAZON_SC",
    "universo": "https://playerservices.streamtheworld.com/api/livestream-redirect/UNIVERSO_SC",
    "activa": "https://playerservices.streamtheworld.com/api/livestream-redirect/ACTIVA_SC",
    "tiempo": "https://playerservices.streamtheworld.com/api/livestream-redirect/TIEMPO_SC",
    "imagina": "https://playerservices.streamtheworld.com/api/livestream-redirect/IMAGINA_SC",
    "romantica": "https://playerservices.streamtheworld.com/api/livestream-redirect/ROMANTICA_SC",
    "carolina": "https://playerservices.streamtheworld.com/api/livestream-redirect/CAROLINA_SC",
    "fmdos": "https://playerservices.streamtheworld.com/api/livestream-redirect/FMDOS_SC",
    "oasis": "https://playerservices.streamtheworld.com/api/livestream-redirect/OASIS_SC",
    "uno": "https://playerservices.streamtheworld.com/api/livestream-redirect/UNO_SC",
    # Cristiana
    "armonia": "https://radioarmonia.cl/stream",
    "shalom": "https://server.radioshalom.cl/stream",
    # ============== INTERNACIONALES ==============
    "bbc": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
    "bbc news": "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
    "cnn": "https://tunein.streamguys1.com/cnni",
    "npr": "https://npr-ice.streamguys1.com/live.mp3",
    "rfi": "http://live02.rfi.fr/rfimonde-64.mp3",
    "deutsche welle": "https://dwstream02-lh.akamaihd.net/i/dwstream2_live@131329/master.m3u8",
    "radio france": "http://direct.franceinter.fr/live/franceinter-midfi.mp3",
    # ============== TEMÁTICAS / GLOBALES ==============
    "lofi": "https://streams.ilovemusic.de/iloveradio17.mp3",
    "lo-fi": "https://streams.ilovemusic.de/iloveradio17.mp3",
    "chill": "https://streams.ilovemusic.de/iloveradio17.mp3",
    "jazz": "https://wwfm.streamguys1.com/wwfm-mp3",
    "jazz radio": "https://jazz-wr04.ice.infomaniak.ch/jazz-wr04-128.mp3",
    "clasica": "https://streams.classicalking.org/king",
    "clásica": "https://streams.classicalking.org/king",
    "clasical": "https://streams.classicalking.org/king",
    "salsa": "https://stream.zeno.fm/0r0xa792kwzuv",
    "reggaeton": "https://stream.zeno.fm/yn65fsaurfhvv",
    "trap": "https://stream.zeno.fm/3a2ffhz5ad0uv",
    "rock": "https://radio.streemlion.com:2199/tunein/classicrock.pls",
    "rock clasico": "https://radio.streemlion.com:2199/tunein/classicrock.pls",
    "rock clásico": "https://radio.streemlion.com:2199/tunein/classicrock.pls",
    "metal": "https://0n-metal.radionetz.de/0n-metal.mp3",
    "electronica": "https://streams.ilovemusic.de/iloveradio2.mp3",
    "electrónica": "https://streams.ilovemusic.de/iloveradio2.mp3",
    "house": "https://streams.ilovemusic.de/iloveradio4.mp3",
    "techno": "https://streams.ilovemusic.de/iloveradio16.mp3",
    "edm": "https://streams.ilovemusic.de/iloveradio2.mp3",
    "pop": "https://streams.ilovemusic.de/iloveradio.mp3",
    "ochenta": "https://streams.ilovemusic.de/iloveradio6.mp3",
    "ochentas": "https://streams.ilovemusic.de/iloveradio6.mp3",
    "noventa": "https://streams.ilovemusic.de/iloveradio7.mp3",
    "noventas": "https://streams.ilovemusic.de/iloveradio7.mp3",
    "country": "https://18723.live.streamtheworld.com/977_COUNTRY.mp3",
    "indie": "https://24493.live.streamtheworld.com/SAM01AAC158_SC",
    "blues": "https://stream.zeno.fm/4w8ftd49a1zuv",
    "soul": "https://stream.zeno.fm/k1f4z8c1f98uv",
    "kpop": "https://streams.ilovemusic.de/iloveradio14.mp3",
    "k-pop": "https://streams.ilovemusic.de/iloveradio14.mp3",
    "anime": "https://kathy.torontocast.com:3060/;",
    "ambient": "https://streams.ilovemusic.de/iloveradio17.mp3",
    "meditacion": "https://streams.ilovemusic.de/iloveradio17.mp3",
    "meditación": "https://streams.ilovemusic.de/iloveradio17.mp3",
}

# Sonidos ambientales (loops curados en YouTube)
AMBIENT_SOUNDS = {
    "lluvia": "https://www.youtube.com/watch?v=mPZkdNFkNps",
    "tormenta": "https://www.youtube.com/watch?v=nDq6TstdEi8",
    "bosque": "https://www.youtube.com/watch?v=xNN7iTA57jM",
    "mar": "https://www.youtube.com/watch?v=bn9F19Hi1Lk",
    "olas": "https://www.youtube.com/watch?v=bn9F19Hi1Lk",
    "rio": "https://www.youtube.com/watch?v=GgynWKWxpIg",
    "río": "https://www.youtube.com/watch?v=GgynWKWxpIg",
    "fogata": "https://www.youtube.com/watch?v=L_LUpnjgPso",
    "fuego": "https://www.youtube.com/watch?v=L_LUpnjgPso",
    "ruido blanco": "https://www.youtube.com/watch?v=nMfPqeZjc2c",
    "ruido rosa": "https://www.youtube.com/watch?v=ZXtimhT-ff4",
    "ruido marron": "https://www.youtube.com/watch?v=RqzGzwTY-6w",
    "ruido marrón": "https://www.youtube.com/watch?v=RqzGzwTY-6w",
    "viento": "https://www.youtube.com/watch?v=eA3ZS1qg9q4",
    "cafeteria": "https://www.youtube.com/watch?v=BOdLmxy06H0",
    "cafetería": "https://www.youtube.com/watch?v=BOdLmxy06H0",
    "tren": "https://www.youtube.com/watch?v=ohj0a4QObTw",
    "ventilador": "https://www.youtube.com/watch?v=BL8KroGnK6Q",
    "ballenas": "https://www.youtube.com/watch?v=ev7ZsoSAOso",
    "binaural": "https://www.youtube.com/watch?v=K-S2VXlW9aM",
    "frecuencia 432": "https://www.youtube.com/watch?v=M7lc1UVf-VE",
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
        "url": "https://app.zapping.com/",
        "search_url": "https://app.zapping.com/search?q={query}",
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
SCREENSAVER_TIMEOUT = 180  # Seconds of inactivity before screensaver

# ============================================================
# GUI THEME — Modern dark with purple/cyan accents
# ============================================================
# Primary backgrounds (deep, premium feel)
COLOR_BG = "#0a0e1a"           # Main background - deep midnight
COLOR_BG_CARD = "#141a2e"      # Card surface - slightly elevated
COLOR_BG_HEADER = "#070a14"    # Top/bottom bars - darkest
COLOR_BG_ELEVATED = "#1c2340"  # Hover/active state
COLOR_BORDER = "#252d4a"       # Subtle borders

# Text
COLOR_TEXT = "#f0f4ff"         # Primary text - warm white
COLOR_TEXT_SOFT = "#c4cce0"    # Secondary text
COLOR_DIM = "#6b7896"          # Muted/disabled

# Accents (vibrant)
COLOR_ACCENT = "#7c3aed"       # Primary accent - vibrant purple
COLOR_ACCENT_2 = "#06d6a0"     # Secondary accent - mint green
COLOR_ACCENT_3 = "#22d3ee"     # Tertiary - cyan

# Conversation
COLOR_USER = "#60a5fa"         # User messages - sky blue
COLOR_BOT = "#a78bfa"          # Arcanum messages - lavender
COLOR_SYSTEM = "#94a3b8"       # System messages - slate

# States
COLOR_LISTENING = "#fb7185"    # Listening - coral
COLOR_LISTENING_BG = "#1a1129" # Listening background - deep purple-black
COLOR_PROCESSING = "#fbbf24"   # Processing - amber
COLOR_SUCCESS = "#10b981"      # Success - emerald
COLOR_ERROR = "#ef4444"        # Error - red

# Overlays
COLOR_HELP_BG = "#0d1124"
COLOR_OVERLAY = "#000000"

# Typography
FONT_FAMILY = "Inter"          # Falls back to system if not installed
FONT_FAMILY_MONO = "JetBrains Mono"

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
    {
        "command": "captura de pantalla",
        "description": "Toma un screenshot y lo guarda en tu carpeta personal.",
        "example": "Arcanum, toma una captura",
        "category": "Sistema",
    },
    {
        "command": "batería / nivel de batería",
        "description": "Reporta el estado de la batería (si aplica).",
        "example": "Arcanum, cuánta batería queda",
        "category": "Sistema",
    },
    {
        "command": "estado del sistema / cpu / memoria",
        "description": "Muestra uso de CPU, RAM y temperatura del Pi.",
        "example": "Arcanum, cómo está el sistema",
        "category": "Sistema",
    },
    {
        "command": "mi ip",
        "description": "Dice la IP local y pública del dispositivo.",
        "example": "Arcanum, cuál es mi IP",
        "category": "Sistema",
    },
    {
        "command": "estado del wifi / señal",
        "description": "Muestra calidad de la señal Wi-Fi.",
        "example": "Arcanum, cómo está el wifi",
        "category": "Sistema",
    },
    {
        "command": "test de velocidad",
        "description": "Mide la latencia de tu conexión a internet.",
        "example": "Arcanum, velocidad de internet",
        "category": "Sistema",
    },

    # --- Diversión ---
    {
        "command": "cuéntame un chiste",
        "description": "Cuenta un chiste aleatorio.",
        "example": "Arcanum, dime un chiste",
        "category": "Diversión",
    },
    {
        "command": "dato curioso / sabías que",
        "description": "Comparte un dato curioso al azar.",
        "example": "Arcanum, dime un dato curioso",
        "category": "Diversión",
    },
    {
        "command": "frase del día / motívame",
        "description": "Lee una frase motivacional o inspiradora.",
        "example": "Arcanum, dame una frase motivacional",
        "category": "Diversión",
    },
    {
        "command": "halágame / dime algo bonito",
        "description": "Te dice algo positivo para alegrar tu día.",
        "example": "Arcanum, hálagame",
        "category": "Diversión",
    },
    {
        "command": "cuéntame un cuento",
        "description": "Narra un mini-cuento o historia.",
        "example": "Arcanum, cuéntame una historia",
        "category": "Diversión",
    },
    {
        "command": "trivia / hazme una pregunta",
        "description": "Lanza una pregunta de cultura general.",
        "example": "Arcanum, juguemos trivia",
        "category": "Diversión",
    },
    {
        "command": "trabalenguas",
        "description": "Recita un trabalenguas clásico.",
        "example": "Arcanum, dime un trabalenguas",
        "category": "Diversión",
    },
    {
        "command": "adivinanza / acertijo",
        "description": "Lanza un acertijo (con respuesta).",
        "example": "Arcanum, dime una adivinanza",
        "category": "Diversión",
    },
    {
        "command": "horóscopo de [signo]",
        "description": "Lee el horóscopo del día para tu signo.",
        "example": "Arcanum, horóscopo de leo",
        "category": "Diversión",
    },
    {
        "command": "qué pasó un día como hoy",
        "description": "Cuenta una efeméride de la historia para la fecha actual.",
        "example": "Arcanum, efemérides",
        "category": "Diversión",
    },

    # --- Juegos / Azar ---
    {
        "command": "lanza moneda / cara o sello",
        "description": "Tira una moneda virtual.",
        "example": "Arcanum, cara o sello",
        "category": "Juegos",
    },
    {
        "command": "tira dados [N caras] [cantidad]",
        "description": "Tira uno o más dados de N caras.",
        "example": "Arcanum, tira dos dados de 20 caras",
        "category": "Juegos",
    },
    {
        "command": "número aleatorio entre [a] y [b]",
        "description": "Da un número aleatorio en el rango pedido.",
        "example": "Arcanum, número aleatorio entre 1 y 50",
        "category": "Juegos",
    },
    {
        "command": "decide por mí",
        "description": "Te ayuda a decidir cuando no puedes.",
        "example": "Arcanum, ayúdame a decidir",
        "category": "Juegos",
    },
    {
        "command": "piedra papel tijera / cachipún",
        "description": "Juega cachipún contigo.",
        "example": "Arcanum, juguemos cachipún",
        "category": "Juegos",
    },

    # --- Conocimiento ---
    {
        "command": "cuánto es [operación]",
        "description": "Calculadora de voz: suma, resta, multiplica, divide, raíz, factorial, %.",
        "example": "Arcanum, cuánto es 12 por 7 más 4",
        "category": "Conocimiento",
    },
    {
        "command": "qué significa [palabra]",
        "description": "Da la definición de una palabra.",
        "example": "Arcanum, qué significa idiosincrasia",
        "category": "Conocimiento",
    },
    {
        "command": "traduce [frase] al [idioma]",
        "description": "Traduce a inglés, francés, alemán, italiano, japonés, etc.",
        "example": "Arcanum, traduce 'buenos días' al japonés",
        "category": "Conocimiento",
    },
    {
        "command": "deletrea [palabra]",
        "description": "Deletrea una palabra letra por letra.",
        "example": "Arcanum, deletrea Mississippi",
        "category": "Conocimiento",
    },
    {
        "command": "valor del dólar / euro / UF / UTM",
        "description": "Consulta tipos de cambio actualizados (mindicador.cl).",
        "example": "Arcanum, cuánto vale la UF",
        "category": "Conocimiento",
    },
    {
        "command": "cuánto es X dólares en pesos",
        "description": "Conversor de moneda en tiempo real.",
        "example": "Arcanum, cuánto es 50 euros en pesos",
        "category": "Conocimiento",
    },
    {
        "command": "cuántos km son X millas (y otros)",
        "description": "Convierte km/millas, °C/°F, kg/libras, m/pies, pulgadas/cm.",
        "example": "Arcanum, cuántos kilómetros son 10 millas",
        "category": "Conocimiento",
    },

    # --- Noticias / actualidad ---
    {
        "command": "noticias / titulares",
        "description": "Abre las últimas noticias en pantalla.",
        "example": "Arcanum, dame las noticias",
        "category": "Info",
    },
    {
        "command": "noticias de deportes / fútbol",
        "description": "Abre noticias deportivas.",
        "example": "Arcanum, qué pasó en el fútbol",
        "category": "Info",
    },

    # --- Sonidos ambientales ---
    {
        "command": "sonido de [lluvia/olas/bosque/...]",
        "description": "Reproduce sonidos ambientales: lluvia, tormenta, bosque, mar, río, fogata, ruido blanco/rosa/marrón, viento, café, tren, ventilador, ballenas, binaurales, 432Hz.",
        "example": "Arcanum, ponme sonido de lluvia",
        "category": "Ambiente",
    },

    # --- Bienestar ---
    {
        "command": "ejercicio de respiración",
        "description": "Te guía con la técnica 4-7-8 para calmar la ansiedad.",
        "example": "Arcanum, ayúdame a relajarme",
        "category": "Bienestar",
    },
    {
        "command": "meditación",
        "description": "Pone una pista para meditar.",
        "example": "Arcanum, quiero meditar",
        "category": "Bienestar",
    },
    {
        "command": "estiramientos",
        "description": "Te recita una rutina de estiramiento básica.",
        "example": "Arcanum, dame una rutina de estiramiento",
        "category": "Bienestar",
    },

    # --- Cocina ---
    {
        "command": "receta de [plato]",
        "description": "Busca recetas en internet.",
        "example": "Arcanum, receta de pan amasado",
        "category": "Cocina",
    },
    {
        "command": "agrega [item] a la lista",
        "description": "Agrega ítems a tu lista de compras.",
        "example": "Arcanum, agrega tomates a la lista",
        "category": "Cocina",
    },
    {
        "command": "ver mi lista / borrar lista",
        "description": "Lee o limpia la lista de compras.",
        "example": "Arcanum, qué hay en mi lista",
        "category": "Cocina",
    },

    # --- Notas / recordatorios ---
    {
        "command": "anota [texto]",
        "description": "Guarda una nota rápida.",
        "example": "Arcanum, anota: comprar pasaporte mañana",
        "category": "Notas",
    },
    {
        "command": "ver mis notas",
        "description": "Lee todas las notas guardadas.",
        "example": "Arcanum, leer mis notas",
        "category": "Notas",
    },
    {
        "command": "borrar notas",
        "description": "Elimina todas las notas.",
        "example": "Arcanum, limpia notas",
        "category": "Notas",
    },
    {
        "command": "recuérdame [a las HH:MM o en N minutos]",
        "description": "Crea un recordatorio (alarma o temporizador).",
        "example": "Arcanum, recuérdame en 15 minutos",
        "category": "Notas",
    },

    # --- Comunicación ---
    {
        "command": "abre correo",
        "description": "Abre Gmail en el navegador.",
        "example": "Arcanum, abre mi correo",
        "category": "Comunicación",
    },
    {
        "command": "abre calendario",
        "description": "Abre Google Calendar.",
        "example": "Arcanum, qué tengo hoy en mi agenda",
        "category": "Comunicación",
    },
    {
        "command": "abre maps / cómo llego a [lugar]",
        "description": "Abre Google Maps con o sin destino.",
        "example": "Arcanum, cómo llego a Plaza de Armas",
        "category": "Comunicación",
    },
    {
        "command": "envía mensaje / WhatsApp",
        "description": "Abre WhatsApp Web.",
        "example": "Arcanum, abre WhatsApp",
        "category": "Comunicación",
    },

    # --- Identidad ---
    {
        "command": "quién eres",
        "description": "Te cuenta qué es Arcanum.",
        "example": "Arcanum, preséntate",
        "category": "Identidad",
    },
    {
        "command": "quién soy",
        "description": "Reconocimiento de usuario.",
        "example": "Arcanum, sabes quién soy",
        "category": "Identidad",
    },
    {
        "command": "habla más rápido / más lento",
        "description": "Ajusta la velocidad de la voz.",
        "example": "Arcanum, habla más rápido",
        "category": "Identidad",
    },
    {
        "command": "adiós / chao",
        "description": "Despedida.",
        "example": "Arcanum, hasta luego",
        "category": "Identidad",
    },

    # --- Contenido de internet (APIs gratis) ---
    {
        "command": "dato de gatos",
        "description": "Curiosidad sobre gatos (cat-fact API + traducción).",
        "example": "Arcanum, dato felino",
        "category": "Diversión",
    },
    {
        "command": "dato de perros",
        "description": "Curiosidad sobre perros (Dog API).",
        "example": "Arcanum, cuéntame algo de perros",
        "category": "Diversión",
    },
    {
        "command": "consejo / aconséjame",
        "description": "Da un consejo sabio del día (Advice Slip).",
        "example": "Arcanum, dame un consejo",
        "category": "Diversión",
    },
    {
        "command": "estoy aburrido / qué hago",
        "description": "Sugiere una actividad random (Bored API).",
        "example": "Arcanum, dame una idea",
        "category": "Diversión",
    },
    {
        "command": "trivia del número [N]",
        "description": "Trivia matemática/histórica de un número (Numbers API).",
        "example": "Arcanum, dame trivia del número 42",
        "category": "Diversión",
    },
    {
        "command": "bola mágica / sí o no",
        "description": "Oráculo binario que responde sí/no/tal vez.",
        "example": "Arcanum, ¿llueve mañana? Bola mágica",
        "category": "Juegos",
    },
    {
        "command": "chuck norris",
        "description": "Una verdad universal sobre Chuck Norris.",
        "example": "Arcanum, dato de Chuck Norris",
        "category": "Diversión",
    },
    {
        "command": "sorpréndeme",
        "description": "Devuelve algo aleatorio de Wikipedia.",
        "example": "Arcanum, sorpréndeme",
        "category": "Diversión",
    },
]
