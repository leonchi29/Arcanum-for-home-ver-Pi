"""
Intent recognition module for Arcanum.
Maps user voice phrases (with synonyms) to specific intents.
Supports wide Spanish/Chilean colloquial variations.
"""
import re
import unicodedata


# ============================================================
# INTENT DEFINITIONS
# Each intent has many synonyms to make the assistant universal.
# Order matters: more specific intents go first.
# ============================================================

INTENTS = {
    # ----------- HELP & SYSTEM -----------
    "help": {
        "phrases": [
            "ayuda", "ayudame", "ayúdame", "auxilio", "help",
            "comandos", "lista de comandos", "qué comandos", "que comandos",
            "qué puedes hacer", "que puedes hacer", "qué sabes hacer",
            "que sabes hacer", "muéstrame los comandos", "muestrame los comandos",
            "mostrar comandos", "ver comandos", "opciones", "qué opciones",
            "que opciones", "qué se puede", "que se puede", "manual",
            "instrucciones", "menú", "menu", "qué haces",
        ],
    },
    "hide_help": {
        "phrases": [
            "cierra ayuda", "cerrar ayuda", "ocultar ayuda", "quita ayuda",
            "salir de ayuda", "salir ayuda", "cierra menú", "cierra menu",
            "cerrar menú", "cerrar menu", "vuelve atrás", "vuelve atras",
            "atrás", "atras",
        ],
    },

    # ----------- SHUTDOWN / RESTART -----------
    "shutdown": {
        "phrases": [
            "apaga el sistema", "apaga la raspberry", "apaga el pi",
            "apaga arcanum", "apágate", "apagate", "shutdown",
            "duerme la pi", "duérmete", "duermete",
        ],
    },
    "restart": {
        "phrases": [
            "reinicia", "reiniciar", "reinicia el sistema", "reboot",
            "reinicia la pi", "reinicia la raspberry",
        ],
    },

    # ----------- TIME & DATE -----------
    "time": {
        "phrases": [
            "qué hora es", "que hora es", "dime la hora", "la hora",
            "hora actual", "qué horas son", "que horas son", "dame la hora",
            "qué hora tienes", "que hora tienes", "tell me the time",
        ],
    },
    "date": {
        "phrases": [
            "qué día es", "que dia es", "qué fecha es", "que fecha es",
            "dime la fecha", "la fecha", "fecha actual", "qué día es hoy",
            "que dia es hoy", "qué fecha", "que fecha", "qué día estamos",
            "que dia estamos", "en qué fecha", "en que fecha",
        ],
    },

    # ----------- WEATHER -----------
    "weather": {
        "phrases": [
            "clima", "el clima", "qué clima", "que clima", "cómo está el clima",
            "como esta el clima", "tiempo", "qué tiempo", "que tiempo",
            "temperatura", "qué temperatura", "que temperatura", "calor",
            "frío", "frio", "llueve", "está lloviendo", "esta lloviendo",
            "lluvia", "va a llover", "pronóstico", "pronostico",
            "cómo está el tiempo", "como esta el tiempo", "weather",
        ],
    },

    # ----------- ALARM & TIMER -----------
    "alarm": {
        "phrases": [
            "alarma", "pon alarma", "pone alarma", "configura alarma",
            "despiértame", "despiertame", "ponme alarma", "ponme una alarma",
            "agenda alarma", "alarm", "wake me up",
        ],
    },
    "timer": {
        "phrases": [
            "temporizador", "timer", "cronómetro", "cronometro",
            "cuenta regresiva", "ponme temporizador", "pone temporizador",
            "minutos", "marca", "configura temporizador",
        ],
    },
    "cancel_alarm": {
        "phrases": [
            "cancela alarma", "cancelar alarma", "quita alarma", "quitar alarma",
            "elimina alarma", "borra alarma", "sin alarma", "no alarma",
            "cancela el temporizador", "quita temporizador", "para alarma",
            "detén alarma", "deten alarma",
        ],
    },

    # ----------- WIFI QR -----------
    "wifi_qr": {
        "phrases": [
            "qr wifi", "qr del wifi", "código qr wifi", "codigo qr wifi",
            "genera qr", "generar qr", "muestra qr", "mostrar qr",
            "compartir wifi", "comparte wifi", "código del wifi",
            "codigo del wifi", "qr para wifi", "código para wifi",
            "código para conectarse", "como me conecto al wifi",
            "cómo me conecto al wifi", "wifi qr",
        ],
    },
    "hide_qr": {
        "phrases": [
            "oculta qr", "ocultar qr", "quita qr", "cierra qr", "borra qr",
        ],
    },

    # ----------- RADIO -----------
    "radio": {
        "phrases": [
            "radio", "pon radio", "ponme radio", "pone radio",
            "reproduce radio", "escuchar radio", "estación", "estacion",
            "emisora", "fm", "sintonizar", "sintoniza",
        ],
    },

    # ----------- SPECIFIC SERVICE OPENING -----------
    # These match when user explicitly mentions service name
    "open_spotify": {
        "phrases": [
            "abre spotify", "abrir spotify", "spotify", "ve a spotify",
            "lanza spotify", "iniciar spotify",
        ],
    },
    "open_netflix": {
        "phrases": [
            "abre netflix", "abrir netflix", "netflix", "ve a netflix",
            "ver netflix", "lanza netflix", "iniciar netflix",
        ],
    },
    "open_youtube": {
        "phrases": [
            "abre youtube", "abrir youtube", "youtube", "ve a youtube",
            "ver youtube", "yutu", "yutub",
        ],
    },
    "open_disney": {
        "phrases": [
            "abre disney", "abrir disney", "disney", "ve a disney",
            "disney plus", "disney+", "ver disney",
        ],
    },
    "open_hbo": {
        "phrases": [
            "abre hbo", "abrir hbo", "hbo", "max", "hbo max",
            "abre max", "abrir max", "ver max", "ver hbo",
        ],
    },
    "open_prime": {
        "phrases": [
            "prime video", "amazon prime", "abre prime", "abrir prime",
            "ver prime", "ver amazon", "prime",
        ],
    },
    "open_paramount": {
        "phrases": [
            "paramount", "paramount plus", "paramount+", "abre paramount",
            "ver paramount",
        ],
    },
    "open_crunchyroll": {
        "phrases": [
            "crunchyroll", "abre crunchyroll", "ver crunchyroll", "anime",
            "ver anime",
        ],
    },
    "open_zapping": {
        "phrases": [
            "zapping", "modo comer", "noticias", "noticiero", "televisión",
            "television", "tele", "ver tele", "ver televisión",
            "ver television", "abre la tele", "abre tele",
        ],
    },

    # ----------- GENERIC PLAY (multi-target) -----------
    # "Reproduce X" → routes to Spotify by default, unless service mentioned
    "play_media": {
        "phrases": [
            "reproduce", "reproducir", "pon", "ponme", "pone", "quiero escuchar",
            "escuchar", "escucha", "play", "pon música", "pon musica",
            "música", "musica", "canción", "cancion", "tema", "playlist",
            "lista de reproducción", "mix", "álbum", "album",
            "quiero oír", "quiero oir", "ponle", "dame música", "dame musica",
        ],
    },

    # ----------- VIDEO CONTENT -----------
    "play_video": {
        "phrases": [
            "ver película", "ver pelicula", "ver una película",
            "ver una pelicula", "pon película", "pon pelicula",
            "ver serie", "ver una serie", "pon serie", "ver capítulo",
            "ver capitulo", "ver episodio", "siguiente episodio",
            "siguiente capítulo", "siguiente capitulo", "ver documental",
            "ver anime", "ver dibujos", "ver caricaturas",
        ],
    },

    # ----------- RECOMMENDATIONS -----------
    "recommend": {
        "phrases": [
            "recomienda", "recomiéndame", "recomiendame", "qué recomiendas",
            "que recomiendas", "qué me recomiendas", "que me recomiendas",
            "sugerencia", "sugerencias", "sugiéreme", "sugiereme",
            "qué puedo ver", "que puedo ver", "qué hay para ver",
            "que hay para ver", "qué ver", "que ver",
        ],
    },
    "continue_watching": {
        "phrases": [
            "continuar viendo", "seguir viendo", "continuá viendo",
            "lo que estaba viendo", "donde lo dejé", "donde lo deje",
            "retomar", "continúa", "continuar", "sigue donde estaba",
            "seguir donde estaba",
        ],
    },

    # ----------- LIST / DISCOVERY -----------
    "list_services": {
        "phrases": [
            "qué hay disponible", "que hay disponible", "qué disponible",
            "que disponible", "servicios", "qué servicios", "que servicios",
            "qué servicios hay", "que servicios hay", "plataformas",
            "qué plataformas", "que plataformas", "qué tienes",
            "que tienes", "qué puedo ver", "que puedo ver",
            "qué puedo escuchar", "que puedo escuchar", "lista servicios",
            "lista de servicios", "muéstrame servicios", "muestrame servicios",
        ],
    },
    "list_radios": {
        "phrases": [
            "qué radios hay", "que radios hay", "lista radios", "lista de radios",
            "radios disponibles", "qué emisoras", "que emisoras",
            "muéstrame radios", "muestrame radios",
        ],
    },

    # ----------- CLOSE / STOP -----------
    "close_service": {
        "phrases": [
            "cierra", "cerrar", "cierra eso", "cierra la web", "cierra la página",
            "cierra la pagina", "cierra el video", "cierra el navegador",
            "salir", "sal de aquí", "sal de aqui", "vuelve a la pantalla",
            "vuelve al inicio", "ir al inicio", "regresar", "vuelve",
            "ciérralo", "cierralo", "close",
        ],
    },
    "stop_all": {
        "phrases": [
            "para todo", "detener todo", "detén todo", "deten todo",
            "stop todo", "apaga todo", "para", "detener", "detén", "deten",
            "detente", "alto", "stop", "ya", "basta", "suficiente", "silencio",
            "termina", "finalizar", "cállate", "callate",
        ],
    },

    # ----------- PLAYBACK CONTROL -----------
    "pause": {
        "phrases": [
            "pausa", "pausar", "pause", "espera", "esperar", "pause eso",
            "ponlo en pausa", "pon pausa", "haz pausa",
        ],
    },
    "resume": {
        "phrases": [
            "continua", "continúa", "continuar", "sigue", "seguir",
            "resume", "reanuda", "reanudar", "play", "reproducir de nuevo",
            "vuelve a reproducir", "quita pausa", "saca pausa",
            "saca de pausa", "dale", "dale play",
        ],
    },
    "next_track": {
        "phrases": [
            "siguiente", "next", "salta", "saltar", "skip", "otra",
            "otra canción", "otra cancion", "siguiente canción",
            "siguiente cancion", "próxima", "proxima", "próxima canción",
            "proxima cancion", "cambia", "cambiar canción", "cambiar cancion",
            "siguiente pista", "salta pista",
        ],
    },
    "previous_track": {
        "phrases": [
            "anterior", "previa", "previous", "atrás canción",
            "atras cancion", "vuelve atrás", "vuelve atras",
            "canción anterior", "cancion anterior", "vuelve a la anterior",
            "regresa canción", "regresa cancion",
        ],
    },

    # ----------- VOLUME -----------
    "volume_up": {
        "phrases": [
            "sube volumen", "sube el volumen", "más volumen", "mas volumen",
            "más fuerte", "mas fuerte", "más alto", "mas alto", "más sonido",
            "mas sonido", "subir volumen", "aumenta volumen", "aumentar volumen",
            "no escucho", "no se escucha", "más bocina", "mas bocina",
        ],
    },
    "volume_down": {
        "phrases": [
            "baja volumen", "baja el volumen", "menos volumen", "más bajo",
            "mas bajo", "más bajito", "mas bajito", "menos fuerte",
            "bajar volumen", "disminuye volumen", "disminuir volumen",
            "muy fuerte", "está muy fuerte", "esta muy fuerte", "más suave",
            "mas suave",
        ],
    },
    "volume_set": {
        "phrases": [
            "volumen al", "volumen en", "pon volumen", "ponme volumen",
            "establece volumen", "configura volumen", "volumen a",
        ],
    },
    "mute": {
        "phrases": [
            "silencio", "silencia", "silenciar", "mute", "mutea", "muteala",
            "quita el sonido", "quita sonido", "sin sonido", "sin audio",
            "apaga sonido",
        ],
    },
    "unmute": {
        "phrases": [
            "quita silencio", "saca silencio", "unmute", "vuelve sonido",
            "regresa sonido", "pon sonido", "activa sonido",
        ],
    },

    # ----------- BROWSER NAVIGATION -----------
    "scroll_down": {
        "phrases": [
            "scroll abajo", "baja", "scrollea abajo", "desplaza abajo",
            "muévete abajo", "muevete abajo", "más abajo", "mas abajo",
            "ve abajo", "página abajo", "pagina abajo",
        ],
    },
    "scroll_up": {
        "phrases": [
            "scroll arriba", "sube", "scrollea arriba", "desplaza arriba",
            "muévete arriba", "muevete arriba", "más arriba", "mas arriba",
            "ve arriba", "página arriba", "pagina arriba",
        ],
    },
    "click": {
        "phrases": [
            "click", "haz click", "selecciona", "seleccionar", "elige",
            "elegir", "presiona", "pulsa", "dale click", "tap", "enter",
            "acepta", "aceptar", "ok", "dale enter",
        ],
    },
    "back": {
        "phrases": [
            "volver atrás", "volver atras", "regresa", "back", "página anterior",
            "pagina anterior", "atrás página", "atras pagina", "vuelve",
        ],
    },
    "fullscreen": {
        "phrases": [
            "pantalla completa", "fullscreen", "pantalla grande", "agranda",
            "agrandar", "maximizar", "maximiza", "pon pantalla completa",
        ],
    },
    "exit_fullscreen": {
        "phrases": [
            "salir pantalla completa", "minimiza", "minimizar", "achica",
            "achicar", "quita pantalla completa",
        ],
    },
    "refresh": {
        "phrases": [
            "actualiza", "actualizar", "refresca", "refrescar", "recarga",
            "recargar", "f5", "refresh",
        ],
    },
    "search_in_page": {
        "phrases": [
            "buscar en página", "buscar en pagina", "busca aquí", "busca aqui",
            "ctrl f",
        ],
    },

    # ----------- KEYBOARD ACTIONS -----------
    "press_enter": {
        "phrases": [
            "enter", "entrar", "presiona enter", "dale enter", "intro",
            "presiona intro", "confirmar", "confirma",
        ],
    },
    "type_text": {
        "phrases": [
            "escribe", "escribir", "tipea", "tipear", "ingresa", "ingresar",
            "pon el texto", "type",
        ],
    },

    # ----------- LOGIN -----------
    "login": {
        "phrases": [
            "inicia sesión", "iniciar sesión", "iniciar sesion", "inicia sesion",
            "login", "loguéate", "logueate", "ingresa con mi cuenta",
            "entrar con mi cuenta", "loggearse", "loggear", "loggea",
        ],
    },

    # ----------- SEARCH (INTERNET) -----------
    "search_web": {
        "phrases": [
            "busca", "búsqueda", "busqueda", "investiga", "buscar",
            "qué es", "que es", "quién es", "quien es", "quién fue",
            "quien fue", "dime sobre", "dime quién", "dime quien",
            "dime qué", "dime que", "información", "informacion",
            "cuéntame", "cuentame", "explica", "explícame", "explicame",
            "definición", "definicion", "qué significa", "que significa",
            "cómo se", "como se", "dónde está", "donde esta",
            "dónde queda", "donde queda", "cuál es", "cual es",
            "cuándo", "cuando", "por qué", "por que", "porque",
        ],
    },

    # ----------- GREETINGS -----------
    "greeting": {
        "phrases": [
            "hola", "hola arcanum", "hey", "qué tal", "que tal",
            "buenos días", "buenos dias", "buenas tardes", "buenas noches",
            "saludos",
        ],
    },
    "thanks": {
        "phrases": [
            "gracias", "muchas gracias", "te lo agradezco", "thanks",
            "thank you",
        ],
    },

    # ----------- AUTOMATION MODES -----------
    "configure_mode": {
        "phrases": [
            "configurar modo", "configurar un modo", "crear modo",
            "nuevo modo", "crea modo", "crea un modo", "guardar modo",
            "agregar modo",
        ],
    },
    "execute_mode": {
        "phrases": [
            "modo", "ejecutar modo", "activar modo", "pon modo",
            "lanzar modo",
        ],
    },
    "list_modes": {
        "phrases": [
            "listar modos", "lista modos", "qué modos hay", "que modos hay",
            "modos disponibles", "mis modos", "ver modos",
        ],
    },
    "delete_mode": {
        "phrases": [
            "borrar modo", "eliminar modo", "quitar modo", "borra modo",
            "elimina modo",
        ],
    },

    # ----------- ON-SCREEN KEYBOARD -----------
    "show_keyboard": {
        "phrases": [
            "teclado", "muestra teclado", "teclado en pantalla",
            "abrir teclado", "abre teclado", "mostrar teclado",
            "keyboard",
        ],
    },
    "hide_keyboard": {
        "phrases": [
            "cierra teclado", "cerrar teclado", "oculta teclado",
            "esconde teclado", "quita teclado",
        ],
    },
}


# ============================================================
# MATCHING ENGINE
# ============================================================

def normalize(text: str) -> str:
    """Lowercase + strip accents for fuzzy matching."""
    text = text.lower().strip()
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def detect_intent(command: str) -> tuple[str, str] | tuple[None, str]:
    """
    Detect the intent from a command.
    Returns (intent_name, original_command) or (None, command).
    Order of INTENTS dict matters — first match wins.
    """
    if not command:
        return None, command

    cmd_norm = normalize(command)

    # Score each intent by best phrase match length
    best_intent = None
    best_score = 0

    for intent_name, data in INTENTS.items():
        for phrase in data["phrases"]:
            phrase_norm = normalize(phrase)
            # Match as whole word or substring
            if phrase_norm in cmd_norm:
                score = len(phrase_norm)
                if score > best_score:
                    best_score = score
                    best_intent = intent_name

    return best_intent, command


def extract_after(command: str, trigger_phrases: list[str]) -> str:
    """
    Extract text that comes after a trigger phrase.
    Useful for: "reproduce X" → "X", "alarma a las 7:30" → "7:30"
    """
    cmd_norm = normalize(command)
    for phrase in trigger_phrases:
        phrase_norm = normalize(phrase)
        idx = cmd_norm.find(phrase_norm)
        if idx >= 0:
            # Find the original-case position
            after = command[idx + len(phrase_norm):].strip()
            if after:
                return after
    return ""


# ============================================================
# QUERY EXTRACTION HELPERS
# ============================================================

# Common stop words to remove when extracting search queries
STOP_WORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "en", "y", "o", "a", "al", "por", "para",
    "con", "sin", "que", "como", "mi", "tu", "su",
    # Service connectors
    "spotify", "youtube", "netflix", "disney", "hbo", "prime",
    "paramount", "crunchyroll", "max",
    # Action words
    "reproduce", "reproducir", "pon", "ponme", "pone", "ponle",
    "escucha", "escuchar", "play", "ver", "abre", "abrir",
    "busca", "buscar", "música", "musica", "canción", "cancion",
    "video", "película", "pelicula", "serie", "capítulo", "capitulo",
}


def extract_search_query(command: str, intent: str = "") -> str:
    """Extract the actual search subject from a command."""
    words = command.lower().split()
    filtered = [w for w in words if normalize(w) not in STOP_WORDS]
    return " ".join(filtered).strip()


def detect_target_service(command: str) -> str | None:
    """
    Detect if a command mentions a specific streaming service.
    Returns the service key (e.g. 'youtube') or None.
    """
    cmd_norm = normalize(command)
    service_map = {
        "youtube": ["youtube", "yutu", "yutub"],
        "spotify": ["spotify"],
        "netflix": ["netflix"],
        "disney": ["disney"],
        "hbo": ["hbo", "max"],
        "prime": ["prime", "amazon"],
        "paramount": ["paramount"],
        "crunchyroll": ["crunchyroll", "anime"],
        "zapping": ["zapping"],
    }
    for service, keywords in service_map.items():
        for kw in keywords:
            if kw in cmd_norm:
                return service
    return None
