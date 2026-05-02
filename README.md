# Arcanum - Voice Assistant for Raspberry Pi 5

Voice-controlled home assistant by **Carlos**. Responds to the wake word **"Arcanum"** with a fullscreen GUI, text-to-speech, and USB microphone support.

## Features

### Voice Commands

| Command | Action |
|---------|--------|
| "Arcanum, reproduce [song]" | Open Spotify Web and search |
| "Arcanum, radio [station]" | Play Chilean FM radio |
| "Arcanum, modo comer" | Open Zapping TV news |
| "Arcanum, netflix / disney / youtube" | Open streaming service |
| "Arcanum, qué hora es" | Tell current time |
| "Arcanum, fecha" | Tell current date |
| "Arcanum, clima" | Weather report |
| "Arcanum, alarma 7:30" | Set alarm |
| "Arcanum, temporizador 10" | Set 10-minute timer |
| "Arcanum, busca [topic]" | Search internet (shown in app) |
| "Arcanum, disponible" | List all available services |
| "Arcanum, cierra" | Close current web service |
| "Arcanum, pausa" | Mute/pause current audio |
| "Arcanum, continua" | Resume audio |
| "Arcanum, sube/baja volumen" | Volume control |
| "Arcanum, para todo" | Stop everything |
| "Arcanum, ayuda" | List all commands |

### Streaming Services
Spotify, Netflix, Disney+, YouTube, Amazon Prime Video, Max (HBO), Paramount+, Crunchyroll, Zapping TV

### Radio Stations (Chile)
Bio Bio, Cooperativa, Rock and Pop, Futuro, Concierto, Pudahuel, Corazón, ADN, La Clave, Infinita, Duna, Universo

### GUI Features
- Fullscreen display showing conversation (what you say + Arcanum's response)
- Animated screensaver: "ARCANUM by Carlos" with floating clock
- Listening indicator (red pulsing)
- Active service status bar
- Auto-screensaver after inactivity

### Smart Behavior
- **Wake word interrupt**: Say "Arcanum" while using Spotify/Netflix/Radio — it mutes current audio, brings Arcanum to front, takes your command, then restores the service
- **Service login**: Services that need login (Netflix, Spotify, etc.) will prompt you
- **USB mic auto-detect**: Automatically finds USB microphone on Raspberry Pi
- **Internet search**: Results shown in the app (not in a browser)
- **Text-to-speech**: Arcanum speaks all responses

## Setup on Raspberry Pi 5

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-tk \
    portaudio19-dev vlc chromium-browser espeak xdotool
```

### 2. Create virtual environment

```bash
cd Arcanum-for-home-ver-Pi
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python packages

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

```bash
cp .env.example .env
nano .env
```

Fill in:
- **PICOVOICE_ACCESS_KEY**: Free at https://console.picovoice.ai/
- **OPENWEATHER_API_KEY**: Free at https://openweathermap.org/api

### 5. Connect USB microphone

Plug in your USB mic. Arcanum auto-detects it on startup.

### 6. Run

```bash
python main.py
```

## Auto-start on Boot (systemd)

```bash
sudo nano /etc/systemd/system/arcanum.service
```

```ini
[Unit]
Description=Arcanum Voice Assistant
After=network.target sound.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Arcanum-for-home-ver-Pi
ExecStart=/home/pi/Arcanum-for-home-ver-Pi/venv/bin/python main.py
Restart=always
RestartSec=5
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority

[Install]
WantedBy=graphical.target
```

```bash
sudo systemctl enable arcanum
sudo systemctl start arcanum
```

## Project Structure

```
Arcanum-for-home-ver-Pi/
├── main.py                        # Entry point (GUI + voice loop)
├── requirements.txt               # Python dependencies
├── .env.example                   # Template for credentials
├── config/
│   └── settings.py                # All configuration
├── services/
│   ├── speech_service.py          # USB mic + voice recognition
│   ├── tts_service.py             # Text-to-speech (speaks responses)
│   ├── wake_word_service.py       # "Arcanum" detection (Porcupine)
│   ├── command_router.py          # Command interpretation & routing
│   ├── audio_manager.py           # System mute/unmute/volume
│   ├── web_service.py             # Chromium manager (streaming)
│   ├── radio_service.py           # Chilean radio streaming (VLC)
│   ├── weather_service.py         # Weather info (OpenWeatherMap)
│   ├── alarm_service.py           # Alarms & timers
│   └── search_service.py          # Internet search (DuckDuckGo/Wikipedia)
└── ui/
    ├── app_window.py              # Fullscreen Tkinter GUI
    └── screensaver.py             # Animated screensaver
```
