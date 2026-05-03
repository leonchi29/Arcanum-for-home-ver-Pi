# Arcanum — Voice Assistant for Raspberry Pi 5

Asistente de voz inteligente por **Carlos**. Pantalla completa, control por voz en español, sin API keys.

## Características

### Zero API Keys
Todo funciona sin configurar ninguna clave. El clima viene de la web, la voz usa Google Speech Recognition gratuito, y los servicios se abren directamente en Chromium.

### Enrollment de Voz
La primera vez que ejecutas Arcanum, te pide repetir 7 frases para calibrar el micrófono y luego pregunta tu nombre. Después te saluda personalmente: *"Claro Carlos, aquí tienes."*

### Modos de Automatización
Crea secuencias de acciones con voz:
- Di: *"Arcanum, configurar modo"*
- Nombre: *"modo Santi"*
- Acciones: *"abre YouTube"*, *"busca Super Wings"*, *"listo"*
- Después solo di: *"Arcanum, modo Santi"* y ejecuta todo automáticamente.

### Comandos de Voz (con sinónimos)

| Comando | Ejemplos / Sinónimos |
|---------|---------------------|
| **Reproducir música** | reproduce, pon, ponme, escucha, play, dame música |
| **Radio** | radio, pon radio, sintoniza, emisora, fm |
| **Abrir servicio** | abre Netflix, ve a YouTube, lanza Spotify |
| **Buscar en servicio** | busca Los Simpson en Disney |
| **Recomendaciones** | recomiéndame, qué puedo ver, sugerencias |
| **Hora / Fecha** | qué hora es, dime la hora, qué día es |
| **Clima** | clima, temperatura, llueve, pronóstico |
| **Alarma / Timer** | alarma 7:30, temporizador 10, despiértame |
| **WiFi QR** | genera QR, comparte wifi |
| **Pausa / Continua** | pausa, espera, dale play, continua, reanuda |
| **Siguiente / Anterior** | siguiente, salta, skip, anterior, otra canción |
| **Volumen** | sube volumen, más fuerte, baja, volumen al 60 |
| **Silencio** | silencio, mute, quita sonido |
| **Scroll** | baja, sube, desplaza abajo/arriba |
| **Click / Enter** | click, selecciona, dale enter, acepta |
| **Atrás** | volver atrás, regresa, back |
| **Pantalla completa** | pantalla completa, fullscreen |
| **Actualizar** | actualiza, recarga, refresh |
| **Escribir texto** | escribe mi correo, tipea |
| **Teclado** | teclado (muestra teclado en pantalla) |
| **Login** | inicia sesión, login |
| **Modos** | modo Santi, configurar modo, listar modos |
| **Buscar** | busca, qué es, quién es, explica |
| **Cerrar** | cierra, salir, cierra eso |
| **Parar todo** | para todo, stop, basta, callate |
| **Apagar / Reiniciar** | apaga, reinicia, shutdown, reboot |
| **Ayuda** | ayuda, comandos, qué puedes hacer |

### Servicios de Streaming
Spotify, Netflix, Disney+, YouTube, Amazon Prime Video, Max (HBO), Paramount+, Crunchyroll, Zapping TV

### Radios Chilenas
Bio Bio, Cooperativa, Rock and Pop, Futuro, Concierto, Pudahuel, Corazón, ADN, La Clave, Infinita, Duna, Universo

### GUI
- Dashboard fullscreen estilo Alexa con tema azul oscuro
- Reloj, fecha, clima, ubicación
- Indicador de escucha animado (punto rojo pulsante)
- Chat de conversación (lo que dices + respuesta)
- Salvapantalla flotante con "ARCANUM by Carlos"
- Overlay de ayuda con todos los comandos agrupados
- Teclado en pantalla para credenciales y captchas

## Instalación en Raspberry Pi 5

### 1. Instalar dependencias del sistema
```bash
sudo apt update
sudo apt install -y git python3-dev python3-venv python3-tk python3-pil python3-pil.imagetk \
  portaudio19-dev vlc chromium espeak espeak-data espeak-ng espeak-ng-data \
  xdotool wireless-tools alsa-utils pulseaudio libatlas3-base flac \
  libjpeg-dev libpng-dev libtiff-dev libfreetype6-dev \
  liblcms2-dev libwebp-dev zlib1g-dev libffi-dev libopenjp2-7-dev libharfbuzz-dev
```

### 2. Clonar el repositorio
```bash
git clone https://github.com/leonchi29/Arcanum-for-home-ver-Pi.git
cd Arcanum-for-home-ver-Pi
```

### 3. Crear entorno virtual con paquetes del sistema
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

### 4. Instalar paquetes Python
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Ejecutar
```bash
source venv/bin/activate
python main.py
```

### Auto-inicio (opcional)
Ejecuta el instalador para configurar el servicio systemd que arranca Arcanum al encender:
```bash
chmod +x install.sh
./install.sh
sudo reboot
```

### Si Pillow da error al instalar
```bash
rm -rf venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Primera Ejecución
1. Conecta tu micrófono USB
2. Arcanum te pide repetir 7 frases para calibrar
3. Te pregunta tu nombre
4. ¡Listo! Di **"Arcanum"** o toca el botón 🎤 para activar

### Cómo cerrar Arcanum
- **Ctrl+Q** — cierra la app inmediatamente
- **ESC** — sale de pantalla completa (puedes cerrar la ventana con X)
- **Desde otra terminal**: `sudo systemctl stop arcanum`
- **Di "Arcanum, apaga el sistema"** — apaga la Pi

---

## Pruebas de Micrófono USB

Si Arcanum no te escucha, sigue estos pasos para diagnosticar:

### 1. Verificar que la Pi detecta el mic
```bash
arecord -l
```
Debe mostrar algo como `card 2: USB Audio`. Anota el número de card.

### 2. Ver dispositivos USB conectados
```bash
lsusb
```

### 3. Subir volumen de captura al máximo
```bash
# Reemplaza 2 por tu número de card
amixer -c 2 set Capture 100% unmute
amixer -c 2 sset Mic 100% unmute
```

### 4. Ver controles del mic
```bash
amixer -c 2 contents
```

### 5. Grabar audio de prueba (habla fuerte y cerca, 5 segundos)
```bash
# Reemplaza 2 por tu número de card
arecord -D plughw:2,0 -d 5 -f S16_LE -r 16000 test.wav
```
Detener grabación: **Ctrl+C**

### 6. Reproducir grabación
```bash
aplay test.wav
```

### 7. Probar con Python (requiere venv activado)
```bash
source venv/bin/activate
python3 -c "
import speech_recognition as sr
r = sr.Recognizer()
r.energy_threshold = 200
m = sr.Microphone(device_index=2)
print('Habla ahora...')
with m as s:
    audio = r.listen(s, timeout=5)
print('Reconociendo...')
print(r.recognize_google(audio, language='es-CL'))
"
```
Si imprime lo que dijiste, el mic funciona con Arcanum.

### 8. Si nada funciona
- Prueba **otro puerto USB** de la Pi
- Prueba el mic en otra PC para verificar que no está dañado
- Compra un **adaptador USB de audio genérico** (~$2 USD) — funcionan siempre en Linux
- Verifica internet: `ping -c 3 google.com` (Google Speech necesita conexión)

### 9. Configurar audio HDMI (salida por TV)
```bash
# Ver salidas disponibles
pactl list sinks short

# Poner HDMI como salida (reemplaza con el nombre que salga con "hdmi")
pactl set-default-sink NOMBRE_DEL_SINK_HDMI

# Subir volumen
pactl set-sink-volume @DEFAULT_SINK@ 100%
pactl set-sink-mute @DEFAULT_SINK@ 0

# Probar audio
speaker-test -c 2 -t wav
```

### 10. Configurar mic como entrada por defecto
```bash
# Ver fuentes de entrada
pactl list sources short

# Poner mic USB como fuente por defecto (reemplaza con nombre que tenga "usb")
pactl set-default-source NOMBRE_DEL_SOURCE_USB

# Subir volumen de entrada
pactl set-source-volume @DEFAULT_SOURCE@ 100%
pactl set-source-mute @DEFAULT_SOURCE@ 0
```

---

## Estructura del Proyecto

```
Arcanum-for-home-ver-Pi/
├── main.py                          # Punto de entrada (GUI + voz + enrollment)
├── requirements.txt                 # Dependencias Python (sin API keys)
├── install.sh                       # Instalador profesional para Pi
├── config/
│   └── settings.py                  # Configuración (colores, radios, servicios)
├── services/
│   ├── intents.py                   # 50+ intents con sinónimos en español
│   ├── command_router.py            # Router de comandos basado en intents
│   ├── speech_service.py            # Reconocimiento de voz (USB mic, 10s timeout)
│   ├── tts_service.py               # Text-to-speech offline (pyttsx3)
│   ├── wake_word_service.py         # Detección "Arcanum" (sin Porcupine)
│   ├── voice_enrollment.py          # Calibración de voz + perfiles de usuario
│   ├── automation_modes.py          # Modos de automatización (macros por voz)
│   ├── browser_control.py           # Control de Chromium por voz (xdotool)
│   ├── credentials_service.py       # Almacenamiento de credenciales
│   ├── web_service.py               # Gestor de Chromium (streaming)
│   ├── radio_service.py             # Radio chilena (VLC)
│   ├── weather_service.py           # Clima sin API (wttr.in)
│   ├── alarm_service.py             # Alarmas y temporizadores
│   ├── search_service.py            # Búsqueda internet (DuckDuckGo/Wikipedia)
│   ├── audio_manager.py             # Control volumen sistema (amixer)
│   └── wifi_qr_service.py           # Generador QR WiFi
└── ui/
    ├── app_window.py                # Dashboard fullscreen + teclado en pantalla
    ├── help_overlay.py              # Overlay de ayuda con todos los comandos
    └── screensaver.py               # Salvapantalla animado
```
