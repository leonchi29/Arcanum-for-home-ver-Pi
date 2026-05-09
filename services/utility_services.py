"""
Utility services for Arcanum:
- Calculator (safe math eval)
- Translator (Google free unofficial endpoint)
- Definitions (Spanish DRAE via DLE / Wikcionario fallback)
- Currency converter (CLP / USD / EUR via free APIs)
- Unit converter (km/mi, kg/lb, C/F, etc.)
- Notes & shopping list (json file)
- System info (CPU, RAM, battery, IP)
- Speedtest (basic latency)
"""
import os
import re
import json
import math
import socket
import shutil
import subprocess
import requests

NOTES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".notes.json",
)


# ============================================================
# CALCULATOR
# ============================================================

class Calculator:
    SPANISH_OPS = {
        "más": "+", "mas": "+", "y": "+",
        "menos": "-",
        "por": "*", "multiplicado por": "*", "veces": "*",
        "entre": "/", "dividido por": "/", "dividido entre": "/",
        "elevado a": "**", "al cuadrado": "**2", "al cubo": "**3",
        "raíz cuadrada de": "sqrt", "raiz cuadrada de": "sqrt",
        "factorial de": "fact",
        "porciento de": "*0.01*", "por ciento de": "*0.01*",
        "porcentaje de": "*0.01*",
    }

    SAFE_NAMES = {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log10, "ln": math.log, "pi": math.pi, "e": math.e,
        "fact": math.factorial,
    }

    def calculate(self, expr: str) -> str:
        text = expr.lower().strip()
        # Remove triggers
        for w in ["cuánto es", "cuanto es", "calcula", "calcular",
                  "resuelve", "resultado de", "matemática", "matematica"]:
            text = text.replace(w, "")
        text = text.strip()

        # Translate Spanish operators
        for spa, op in self.SPANISH_OPS.items():
            text = text.replace(spa, f" {op} ")

        # Strip non-math chars but keep operators, digits, parens, dots
        text = re.sub(r"[^\d\.\+\-\*\/\(\)\^\s\w]", "", text)
        text = text.replace("^", "**")

        if not text.strip():
            return "Dime una operación, por ejemplo: cuánto es 12 más 7."

        try:
            result = eval(text, {"__builtins__": {}}, self.SAFE_NAMES)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"El resultado es {result}."
        except Exception:
            return "No pude resolver esa operación."


# ============================================================
# TRANSLATOR
# ============================================================

class Translator:
    URL = "https://translate.googleapis.com/translate_a/single"

    LANG_MAP = {
        "inglés": "en", "ingles": "en", "english": "en",
        "francés": "fr", "frances": "fr", "french": "fr",
        "alemán": "de", "aleman": "de", "german": "de",
        "italiano": "it", "italian": "it",
        "portugués": "pt", "portugues": "pt", "portuguese": "pt",
        "japonés": "ja", "japones": "ja", "japanese": "ja",
        "chino": "zh-CN", "chinese": "zh-CN",
        "coreano": "ko", "korean": "ko",
        "ruso": "ru", "russian": "ru",
        "árabe": "ar", "arabe": "ar",
        "español": "es", "espanol": "es", "spanish": "es",
    }

    def translate(self, command: str) -> str:
        cmd = command.lower()
        # Detect target language
        target = "en"
        for lang, code in self.LANG_MAP.items():
            if lang in cmd:
                target = code
                break

        # Extract phrase
        text = cmd
        for trig in ["traduce a", "traduce al", "traducir a", "traducir al",
                     "cómo se dice", "como se dice",
                     "traduce", "traducir", "translate"]:
            text = text.replace(trig, "")
        for lang in self.LANG_MAP:
            text = text.replace(lang, "")
        text = text.replace("en", "").strip(" :,.")

        if not text:
            return "¿Qué quieres traducir?"

        try:
            params = {
                "client": "gtx", "sl": "auto", "tl": target,
                "dt": "t", "q": text,
            }
            r = requests.get(self.URL, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            translation = "".join(seg[0] for seg in data[0])
            return f'En {target}: "{translation}"'
        except Exception:
            return "No pude traducir en este momento."

    def spell(self, command: str) -> str:
        text = command.lower()
        for trig in ["deletrea", "cómo se deletrea", "como se deletrea", "spell"]:
            text = text.replace(trig, "")
        text = text.strip(" :,.")
        if not text:
            return "¿Qué palabra deletreo?"
        return " - ".join(text.upper())


# ============================================================
# CURRENCY
# ============================================================

class CurrencyConverter:
    """Uses mindicador.cl (CLP rates, free, no key) + open.er-api fallback."""
    MINDICADOR = "https://mindicador.cl/api/{indicator}"
    OPEN_ER = "https://open.er-api.com/v6/latest/USD"

    INDICATOR_MAP = {
        "uf": "uf", "utm": "utm",
        "dolar": "dolar", "dólar": "dolar", "usd": "dolar",
        "euro": "euro", "eur": "euro",
    }

    def convert(self, command: str) -> str:
        cmd = command.lower()

        # Special CL indicators
        for kw in ["uf", "utm"]:
            if f" {kw} " in f" {cmd} " or cmd.endswith(kw):
                return self._mindicador(kw)

        # "valor del dólar" / "tipo de cambio"
        if any(t in cmd for t in ["valor del dolar", "valor del dólar", "valor del euro",
                                   "tipo de cambio"]):
            ind = "euro" if "euro" in cmd else "dolar"
            return self._mindicador(ind)

        # "cuánto es 100 dólares en pesos"
        nums = re.findall(r"\d+(?:\.\d+)?", cmd)
        if not nums:
            return "Dime un monto, por ejemplo: cuánto es 100 dólares en pesos."
        amount = float(nums[0])

        # Detect from/to
        if "dólar" in cmd or "dolar" in cmd or "usd" in cmd:
            from_cur = "USD"
        elif "euro" in cmd:
            from_cur = "EUR"
        else:
            from_cur = "CLP"

        if "peso" in cmd or "clp" in cmd:
            to_cur = "CLP"
        elif "euro" in cmd and from_cur != "EUR":
            to_cur = "EUR"
        elif ("dólar" in cmd or "dolar" in cmd) and from_cur != "USD":
            to_cur = "USD"
        else:
            to_cur = "USD" if from_cur != "USD" else "CLP"

        try:
            r = requests.get(self.OPEN_ER, timeout=10).json()
            rates = r["rates"]
            # Convert via USD pivot
            usd_amount = amount / rates.get(from_cur, 1)
            converted = usd_amount * rates.get(to_cur, 1)
            return f"{amount:g} {from_cur} = {converted:,.2f} {to_cur}."
        except Exception:
            return "No pude consultar el tipo de cambio."

    def _mindicador(self, indicator: str) -> str:
        try:
            r = requests.get(self.MINDICADOR.format(indicator=indicator), timeout=10).json()
            value = r["serie"][0]["valor"]
            unit = r.get("unidad_medida", "CLP")
            name = r.get("nombre", indicator.upper())
            return f"{name}: {value:,.2f} {unit}."
        except Exception:
            return f"No pude obtener el valor de {indicator.upper()}."


# ============================================================
# UNIT CONVERTER
# ============================================================

class UnitConverter:
    def convert(self, command: str) -> str:
        cmd = command.lower()
        nums = re.findall(r"\d+(?:\.\d+)?", cmd)
        if not nums:
            return "Dime un valor numérico para convertir."
        v = float(nums[0])

        if "kilómetros" in cmd or "kilometros" in cmd or "km" in cmd:
            if "millas" in cmd or "mile" in cmd:
                return f"{v:g} km = {v * 0.621371:.2f} millas."
        if "millas" in cmd or "miles" in cmd:
            if "kilómetros" in cmd or "kilometros" in cmd or "km" in cmd:
                return f"{v:g} millas = {v * 1.60934:.2f} km."
        if "celsius" in cmd or "°c" in cmd:
            return f"{v:g}°C = {v * 9/5 + 32:.1f}°F."
        if "fahrenheit" in cmd or "°f" in cmd:
            return f"{v:g}°F = {(v - 32) * 5/9:.1f}°C."
        if "kilo" in cmd and ("libra" in cmd or "lb" in cmd):
            return f"{v:g} kg = {v * 2.20462:.2f} lb."
        if "libra" in cmd and ("kilo" in cmd or "kg" in cmd):
            return f"{v:g} lb = {v * 0.453592:.2f} kg."
        if "metro" in cmd and ("pie" in cmd or "feet" in cmd):
            return f"{v:g} m = {v * 3.28084:.2f} pies."
        if "pulgada" in cmd and ("centi" in cmd or "cm" in cmd):
            return f"{v:g} pulgadas = {v * 2.54:.2f} cm."

        return "No reconozco esa conversión. Prueba con km, millas, °C, °F, kg o libras."


# ============================================================
# NOTES & SHOPPING LIST
# ============================================================

class NotesService:
    def __init__(self):
        if not os.path.exists(NOTES_FILE):
            self._save({"notes": [], "shopping": []})

    def _load(self) -> dict:
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"notes": [], "shopping": []}

    def _save(self, data: dict) -> None:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _strip(self, command: str, triggers: list[str]) -> str:
        text = command.lower()
        for t in triggers:
            text = text.replace(t, "")
        return text.strip(" :,.")

    def add_note(self, command: str) -> str:
        text = self._strip(command, [
            "agrega nota", "añade nota", "guarda nota", "anota esto",
            "toma nota", "anótalo", "anotalo", "recuerda esto",
        ])
        if not text:
            return "¿Qué quieres anotar?"
        data = self._load()
        data["notes"].append(text)
        self._save(data)
        return f"Anotado: {text}"

    def list_notes(self) -> str:
        data = self._load()
        if not data["notes"]:
            return "No tienes notas guardadas."
        return "Tus notas: " + " | ".join(
            f"{i+1}. {n}" for i, n in enumerate(data["notes"])
        )

    def clear_notes(self) -> str:
        data = self._load()
        data["notes"] = []
        self._save(data)
        return "Notas borradas."

    def add_to_list(self, command: str) -> str:
        text = self._strip(command, [
            "agrega a la lista", "añade a la lista", "lista de compras",
            "anota", "agrega", "añade",
        ])
        if not text:
            return "¿Qué agrego a tu lista?"
        data = self._load()
        data["shopping"].append(text)
        self._save(data)
        return f"Agregado a tu lista: {text}"

    def show_list(self) -> str:
        data = self._load()
        if not data["shopping"]:
            return "Tu lista de compras está vacía."
        return "En tu lista: " + ", ".join(data["shopping"]) + "."

    def clear_list(self) -> str:
        data = self._load()
        data["shopping"] = []
        self._save(data)
        return "Lista de compras vaciada."


# ============================================================
# SYSTEM INFO
# ============================================================

class SystemInfo:
    def battery(self) -> str:
        try:
            import psutil
            b = psutil.sensors_battery()
            if not b:
                return "Este dispositivo no tiene batería detectable (probablemente conectado a corriente)."
            charging = "cargando" if b.power_plugged else "descargando"
            return f"Batería al {b.percent:.0f}%, {charging}."
        except Exception:
            return "No pude leer la batería."

    def cpu_ram(self) -> str:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            return f"CPU al {cpu:.0f}%, memoria RAM al {ram:.0f}%."
        except Exception:
            return "No pude leer el estado del sistema."

    def temperature(self) -> str:
        # Raspberry Pi temp
        try:
            out = subprocess.check_output(
                ["vcgencmd", "measure_temp"], text=True, timeout=3
            )
            return f"Temperatura del sistema: {out.strip().replace('temp=', '')}."
        except Exception:
            pass
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                t = int(f.read().strip()) / 1000
            return f"Temperatura del sistema: {t:.1f}°C."
        except Exception:
            return "No pude leer la temperatura."

    def ip_address(self) -> str:
        try:
            local = socket.gethostbyname(socket.gethostname())
        except Exception:
            local = "desconocida"
        public = "desconocida"
        try:
            public = requests.get("https://api.ipify.org", timeout=5).text.strip()
        except Exception:
            pass
        return f"IP local: {local}. IP pública: {public}."

    def wifi_status(self) -> str:
        try:
            out = subprocess.check_output(
                ["iwconfig"], text=True, stderr=subprocess.DEVNULL, timeout=3
            )
            for line in out.splitlines():
                if "Signal level" in line or "Link Quality" in line:
                    return f"Wi-Fi: {line.strip()}"
            return "Wi-Fi conectado."
        except Exception:
            return "No pude leer el estado del Wi-Fi."

    def speedtest(self) -> str:
        """Basic ping-based latency test."""
        try:
            import time
            start = time.time()
            requests.get("https://www.google.com", timeout=5)
            latency = (time.time() - start) * 1000
            quality = "excelente" if latency < 200 else "buena" if latency < 500 else "lenta"
            return f"Latencia: {latency:.0f} ms. Conexión {quality}."
        except Exception:
            return "No pude medir la velocidad."

    def screenshot(self) -> str:
        try:
            from datetime import datetime
            path = os.path.expanduser(
                f"~/arcanum_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            for cmd in [
                ["scrot", path],
                ["gnome-screenshot", "-f", path],
                ["import", "-window", "root", path],
            ]:
                if shutil.which(cmd[0]):
                    subprocess.run(cmd, check=False, timeout=5)
                    if os.path.exists(path):
                        return f"Captura guardada en {path}"
            return "No encontré una herramienta para captura. Instala 'scrot' o 'gnome-screenshot'."
        except Exception:
            return "No pude tomar la captura."
