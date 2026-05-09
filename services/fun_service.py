"""
Fun & utility content for Arcanum:
jokes, quotes, fortunes, trivia, riddles, tongue twisters, fun facts,
horoscope, riddles, compliments, stories.
All text-based (no API keys).
"""
import random
import requests
from datetime import datetime


JOKES = [
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
    "Le dicen al perro: '¿qué te pasa?'. Y él: 'guau, qué pregunta'.",
    "¿Cuál es el café más peligroso del mundo? El ex-preso.",
    "—Doctor, me duele aquí. —Pues no se toque ahí.",
    "¿Qué le dijo un techo a otro techo? Techo de menos.",
    "¿Cómo se despiden los químicos? Ácido un placer.",
    "¿Por qué Beethoven se deshizo de su gallina? Porque decía 'bach, bach, bach'.",
    "Tengo un amigo que es daltónico, y lo peor es que no lo sabe… cree que es naranjónico.",
    "—Camarero, hay una mosca en mi sopa. —Tranquilo, ya casi no se mueve.",
    "¿Qué hace un pez? Nada.",
    "Si la vida te da limones, pide tequila y sal.",
    "¿Sabes qué hago cuando estoy triste? Nada. Me quedo triste.",
    "Mi mujer me dijo que dejara de ser tan inmaduro… le contesté '¡no eres mi madre!'.",
    "¿Por qué los esqueletos no pelean? Porque no tienen agallas.",
    "—¿Tienes hora? —Sí. —¿Qué hora es? —Las que tú quieras, soy generoso.",
    "El que ríe último, es porque no entendió el chiste.",
    "¿Cómo se llama el campeón japonés de buceo? Tokofondo. Y el subcampeón: Kasitoko.",
    "¿Qué le dice una iguana a su hermana gemela? 'Somos iguanitas'.",
    "¿Cuál es el último animal que subió al arca de Noé? El del-fin.",
]

FUN_FACTS = [
    "Sabías que… los pulpos tienen tres corazones y sangre azul.",
    "Sabías que… la miel nunca se echa a perder. Se han encontrado tarros de 3000 años aún comestibles.",
    "Sabías que… un grupo de flamencos se llama 'flamboyance'.",
    "Sabías que… los tiburones existen desde antes que los árboles.",
    "Sabías que… Marte tiene una montaña tres veces más alta que el Everest: el Olympus Mons.",
    "Sabías que… los caracoles pueden dormir hasta tres años seguidos.",
    "Sabías que… la Torre Eiffel crece hasta 15 cm en verano por la dilatación del metal.",
    "Sabías que… el corazón de una ballena azul puede pesar lo mismo que un auto.",
    "Sabías que… los humanos compartimos el 60% del ADN con los plátanos.",
    "Sabías que… un día en Venus dura más que un año en Venus.",
    "Sabías que… el ojo del avestruz es más grande que su cerebro.",
    "Sabías que… las nutrias se toman de las patas mientras duermen para no separarse.",
    "Sabías que… la palabra 'jeans' viene de Génova, Italia.",
    "Sabías que… los koalas tienen huellas dactilares casi idénticas a las humanas.",
    "Sabías que… Plutón fue descubierto por un chileno-norteamericano… ¡no, era de EE.UU.! Pero igual es interesante.",
    "Sabías que… los relámpagos son cinco veces más calientes que la superficie del Sol.",
]

QUOTES = [
    "“El éxito es la suma de pequeños esfuerzos repetidos día tras día.” — Robert Collier",
    "“No esperes a que llegue la inspiración: ponte a trabajar y la inspiración te encontrará.” — Pablo Picasso",
    "“La mejor manera de predecir el futuro es crearlo.” — Peter Drucker",
    "“Hazlo con miedo, pero hazlo.” — Anónimo",
    "“No cuentes los días, haz que los días cuenten.” — Muhammad Ali",
    "“Lo que no te mata, te hace más fuerte.” — Friedrich Nietzsche",
    "“La vida es muy peligrosa. No por las personas que hacen el mal, sino por las que se sientan a ver lo que pasa.” — Albert Einstein",
    "“Un viaje de mil kilómetros comienza con un solo paso.” — Lao-Tsé",
    "“Sé tú mismo, los demás puestos están ocupados.” — Oscar Wilde",
    "“Nada es imposible: la palabra misma dice ‘yo soy posible’.” — Audrey Hepburn",
    "“No te rindas; ya casi.” — Tu mejor versión",
    "“La disciplina vence a la motivación.” — Anónimo",
    "“Hoy es un buen día para empezar de nuevo.” — Marco Aurelio",
]

COMPLIMENTS = [
    "Tu energía hoy ilumina todo lo que haces.",
    "Eres más capaz de lo que crees, te lo digo en serio.",
    "Tu sonrisa probablemente le mejoró el día a alguien hoy.",
    "Tienes una mente brillante y un corazón aún mejor.",
    "Tu manera de pensar es única y eso es un superpoder.",
    "Sigues adelante incluso cuando es difícil. Eso es admirable.",
    "Si fueras emoji, serías el de las estrellitas brillantes.",
]

RIDDLES = [
    ("Oro parece, plata no es. ¿Qué es?", "El plátano."),
    ("Tengo agujas y no sé coser, tengo números pero no sé leer. ¿Qué soy?", "Un reloj."),
    ("Blanca por dentro, verde por fuera, si quieres que te lo diga, espera. ¿Qué es?", "La pera."),
    ("Cuanto más le quitas, más grande se hace. ¿Qué es?", "Un agujero."),
    ("Tengo dientes pero no muerdo. ¿Qué soy?", "Un peine."),
    ("Vuela sin alas, silba sin boca, golpea sin manos y nadie lo toca. ¿Qué es?", "El viento."),
    ("Cuanto más se moja, más seca queda. ¿Qué es?", "La toalla."),
    ("Tiene patas pero no camina. ¿Qué es?", "La mesa."),
]

TONGUE_TWISTERS = [
    "Tres tristes tigres tragaban trigo en un trigal.",
    "El cielo está enladrillado, ¿quién lo desenladrillará? El que lo desenladrille buen desenladrillador será.",
    "Pablito clavó un clavito. ¿Qué clavito clavó Pablito?",
    "Erre con erre cigarro, erre con erre barril. Rápido corren los carros del ferrocarril.",
    "Como poco coco como, poco coco compro.",
    "Si tu gusto gustara del gusto que mi gusto gusta, mi gusto también gustaría del gusto que tu gusto gusta.",
]

TRIVIA = [
    ("¿Cuál es el río más largo del mundo?", "El Amazonas."),
    ("¿Cuántos huesos tiene el cuerpo humano adulto?", "206."),
    ("¿Quién pintó la Mona Lisa?", "Leonardo da Vinci."),
    ("¿En qué año llegó el ser humano a la Luna?", "En 1969."),
    ("¿Cuál es el planeta más grande del sistema solar?", "Júpiter."),
    ("¿Cuál es la capital de Australia?", "Canberra."),
    ("¿Cuántos jugadores tiene un equipo de fútbol en la cancha?", "Once."),
    ("¿Qué metal es líquido a temperatura ambiente?", "El mercurio."),
    ("¿Quién escribió Don Quijote de la Mancha?", "Miguel de Cervantes."),
]

STORIES = [
    "Había una vez un programador que decidió descansar. Pero como era programador, lo automatizó. Y vivió feliz para siempre.",
    "Un viajero llegó a un pueblo y preguntó cómo era la gente allí. El sabio le respondió: 'igual a la del lugar de donde vienes'. Lo que llevamos dentro pinta lo que vemos fuera.",
    "Un pequeño bambú tardó 5 años en romper la tierra. Cuando lo hizo, creció 25 metros en 6 semanas. La paciencia construye raíces invisibles.",
]

HOROSCOPES = {
    "aries": "Aries, hoy tu energía está al máximo. Aprovecha para iniciar algo que llevas postergando.",
    "tauro": "Tauro, paciencia: la calma será tu superpoder y traerá buenas decisiones.",
    "géminis": "Géminis, una conversación inesperada te dará claridad. Escucha más de lo que hablas.",
    "geminis": "Géminis, una conversación inesperada te dará claridad. Escucha más de lo que hablas.",
    "cáncer": "Cáncer, dedica unos minutos a tu mundo interior. Tu intuición sabe la respuesta.",
    "cancer": "Cáncer, dedica unos minutos a tu mundo interior. Tu intuición sabe la respuesta.",
    "leo": "Leo, brilla sin pedir permiso. Hoy tu carisma abrirá puertas.",
    "virgo": "Virgo, ordena lo que puedas, suelta lo que no. Tu mente vale más que un detalle perdido.",
    "libra": "Libra, busca el equilibrio, no la perfección. Una pequeña pausa te renueva.",
    "escorpio": "Escorpio, transforma lo que ya no te sirve. Estás en un ciclo poderoso de cambio.",
    "sagitario": "Sagitario, lánzate a una mini-aventura. Lo nuevo te da combustible.",
    "capricornio": "Capricornio, tu disciplina hoy se convertirá en oportunidad. Sigue.",
    "acuario": "Acuario, tus ideas son adelantadas. Compártelas: alguien las necesita.",
    "piscis": "Piscis, tu sensibilidad es brújula. Confía en lo que sientes.",
}


# ============================================================

class FunService:
    def joke(self) -> str:
        # Try internet first (icanhazdadjoke), fallback to local
        try:
            r = requests.get(
                "https://icanhazdadjoke.com/",
                headers={"Accept": "application/json", "User-Agent": "Arcanum"},
                timeout=5,
            )
            joke_en = r.json().get("joke")
            if joke_en:
                # Quick translate to Spanish
                t = requests.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={"client": "gtx", "sl": "en", "tl": "es",
                            "dt": "t", "q": joke_en},
                    timeout=5,
                ).json()
                return "".join(seg[0] for seg in t[0])
        except Exception:
            pass
        return random.choice(JOKES)

    def fun_fact(self) -> str:
        # Try uselessfacts API for fresh content
        try:
            r = requests.get(
                "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en",
                timeout=5,
            )
            fact_en = r.json().get("text")
            if fact_en:
                t = requests.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={"client": "gtx", "sl": "en", "tl": "es",
                            "dt": "t", "q": fact_en},
                    timeout=5,
                ).json()
                return "Sabías que… " + "".join(seg[0] for seg in t[0])
        except Exception:
            pass
        return random.choice(FUN_FACTS)

    def cat_fact(self) -> str:
        try:
            r = requests.get("https://catfact.ninja/fact", timeout=5).json()
            fact_en = r.get("fact", "")
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": fact_en},
                timeout=5,
            ).json()
            return "Dato felino: " + "".join(seg[0] for seg in t[0])
        except Exception:
            return "Dato felino: los gatos pueden hacer más de 100 sonidos diferentes."

    def dog_fact(self) -> str:
        try:
            r = requests.get(
                "https://dogapi.dog/api/v2/facts", timeout=5
            ).json()
            fact_en = r["data"][0]["attributes"]["body"]
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": fact_en},
                timeout=5,
            ).json()
            return "Dato canino: " + "".join(seg[0] for seg in t[0])
        except Exception:
            return "Dato canino: la nariz de cada perro es única, como una huella digital."

    def advice(self) -> str:
        try:
            r = requests.get("https://api.adviceslip.com/advice", timeout=5).json()
            advice_en = r["slip"]["advice"]
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": advice_en},
                timeout=5,
            ).json()
            return "Mi consejo: " + "".join(seg[0] for seg in t[0])
        except Exception:
            return "Mi consejo: respira hondo, todo se resuelve a su tiempo."

    def activity(self) -> str:
        """Suggest something to do (Bored API)."""
        try:
            r = requests.get("https://www.boredapi.com/api/activity",
                             timeout=5).json()
            act = r.get("activity", "")
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": act},
                timeout=5,
            ).json()
            return "¿Qué tal si: " + "".join(seg[0] for seg in t[0]) + "?"
        except Exception:
            return random.choice([
                "¿Qué tal si llamas a un viejo amigo?",
                "¿Qué tal si lees 10 páginas de un libro?",
                "¿Qué tal si das una caminata corta?",
                "¿Qué tal si pruebas una receta nueva?",
            ])

    def number_trivia(self, number: int | None = None) -> str:
        """Numbers API trivia."""
        try:
            target = number if number is not None else "random"
            r = requests.get(
                f"http://numbersapi.com/{target}/trivia?notfound=floor",
                timeout=5,
            )
            text_en = r.text
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": text_en},
                timeout=5,
            ).json()
            return "".join(seg[0] for seg in t[0])
        except Exception:
            return "Un dato curioso de números: el 42 es la respuesta a la vida, el universo y todo lo demás."

    def yes_no(self) -> str:
        """Magic 8-ball-ish using yesno.wtf."""
        try:
            r = requests.get("https://yesno.wtf/api", timeout=5).json()
            answer = r.get("answer", "yes")
            return {"yes": "Sí.", "no": "No.", "maybe": "Tal vez."}.get(answer, "Sí.")
        except Exception:
            return random.choice(["Sí.", "No.", "Tal vez.", "Definitivamente.", "No esta vez."])

    def chuck_norris(self) -> str:
        """Chuck Norris fact translated."""
        try:
            r = requests.get("https://api.chucknorris.io/jokes/random",
                             timeout=5).json()
            text_en = r.get("value", "")
            t = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "es",
                        "dt": "t", "q": text_en},
                timeout=5,
            ).json()
            return "Chuck Norris: " + "".join(seg[0] for seg in t[0])
        except Exception:
            return "Chuck Norris no hace flexiones, empuja la Tierra hacia abajo."

    def dictionary(self, word: str) -> str:
        """Quick definition via dictionaryapi (Spanish via Wiktionary backup)."""
        try:
            r = requests.get(
                f"https://es.wiktionary.org/api/rest_v1/page/definition/{word}",
                timeout=6,
            )
            if r.status_code == 200:
                data = r.json()
                for lang_block in data.get("es", []):
                    defs = lang_block.get("definitions", [])
                    if defs:
                        text = defs[0].get("definition", "")
                        # Strip HTML tags simply
                        import re as _re
                        text = _re.sub(r"<[^>]+>", "", text).strip()
                        if text:
                            return f"{word.capitalize()}: {text}"
        except Exception:
            pass
        return ""

    def quote(self) -> str:
        return random.choice(QUOTES)

    def compliment(self) -> str:
        return random.choice(COMPLIMENTS)

    def story(self) -> str:
        return random.choice(STORIES)

    def trivia(self) -> str:
        q, a = random.choice(TRIVIA)
        return f"{q} … (la respuesta: {a})"

    def riddle(self) -> str:
        q, a = random.choice(RIDDLES)
        return f"{q} … (respuesta: {a})"

    def tongue_twister(self) -> str:
        return random.choice(TONGUE_TWISTERS)

    def horoscope(self, sign: str) -> str:
        sign = sign.lower().strip()
        if sign in HOROSCOPES:
            return HOROSCOPES[sign]
        return "¿Cuál es tu signo? Dime, por ejemplo, 'horóscopo de leo'."

    def flip_coin(self) -> str:
        return f"Salió: {random.choice(['cara', 'sello'])}."

    def roll_dice(self, sides: int = 6, count: int = 1) -> str:
        rolls = [random.randint(1, sides) for _ in range(count)]
        if count == 1:
            return f"Salió un {rolls[0]} (dado de {sides} caras)."
        return f"Resultados: {', '.join(str(r) for r in rolls)}. Total: {sum(rolls)}."

    def random_number(self, lo: int = 1, hi: int = 100) -> str:
        return f"Tu número aleatorio entre {lo} y {hi} es: {random.randint(lo, hi)}."

    def decide(self, options: list[str] | None = None) -> str:
        if options:
            return f"Yo elijo: {random.choice(options)}."
        return random.choice(["Sí, hazlo.", "No, hoy no.", "Espera un poco más.",
                              "Sin duda, adelante.", "Mejor mañana."])

    def rock_paper_scissors(self) -> str:
        choice = random.choice(["piedra", "papel", "tijera"])
        return f"Yo saco: {choice}. ¿Qué sacas tú?"

    def this_day_in_history(self) -> str:
        """Wikipedia 'on this day' (Spanish)."""
        try:
            today = datetime.now()
            url = (
                "https://api.wikimedia.org/feed/v1/wikipedia/es/"
                f"onthisday/events/{today.month:02d}/{today.day:02d}"
            )
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            events = data.get("events") or data.get("selected") or []
            if not events:
                return "No encontré efemérides para hoy."
            ev = random.choice(events[:10])
            text = ev.get("text", "")
            year = ev.get("year", "")
            return f"Un día como hoy de {year}: {text}"
        except Exception:
            return "No pude consultar la efeméride en este momento."
