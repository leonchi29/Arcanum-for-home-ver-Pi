#!/bin/bash
# ============================================================
#  ARCANUM — Professional Installer for Raspberry Pi 5
#  Zero API keys required. Full voice assistant.
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No color

# Progress counter
STEP=0
TOTAL_STEPS=7

step() {
    STEP=$((STEP + 1))
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  [${STEP}/${TOTAL_STEPS}] $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

ok() {
    echo -e "  ${GREEN}✓${NC} $1"
}

warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    exit 1
}

# ============================================================
# HEADER
# ============================================================
clear
echo -e "${BLUE}"
echo "    ╔═══════════════════════════════════════════╗"
echo "    ║                                           ║"
echo "    ║     █████╗ ██████╗  ██████╗ █████╗        ║"
echo "    ║    ██╔══██╗██╔══██╗██╔════╝██╔══██╗       ║"
echo "    ║    ███████║██████╔╝██║     ███████║       ║"
echo "    ║    ██╔══██║██╔══██╗██║     ██╔══██║       ║"
echo "    ║    ██║  ██║██║  ██║╚██████╗██║  ██║       ║"
echo "    ║    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ║"
echo "    ║                                           ║"
echo "    ║         ARCANUM Voice Assistant            ║"
echo "    ║           Installer v2.0                   ║"
echo "    ║                                           ║"
echo "    ╚═══════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "  ${BOLD}Zero API keys required.${NC} Everything works via web."
echo -e "  Voice enrollment · Automation modes · Streaming"
echo ""

# ============================================================
# CHECK PREREQUISITES
# ============================================================
step "Checking system..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    warn "Running as root. Recommended to run as normal user with sudo access."
fi

# Detect Raspberry Pi model
if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(cat /proc/device-tree/model)
    ok "Detected: ${PI_MODEL}"
else
    warn "Not running on Raspberry Pi (or model not detected)."
    PI_MODEL="Unknown"
fi

# Check architecture
ARCH=$(uname -m)
ok "Architecture: ${ARCH}"

# Check internet
if ping -c 1 google.com &>/dev/null; then
    ok "Internet connection: OK"
else
    fail "No internet connection. Please connect and try again."
fi

# Check available disk space (need at least 500MB)
AVAIL=$(df -m . | tail -1 | awk '{print $4}')
if [ "$AVAIL" -lt 500 ]; then
    fail "Not enough disk space (${AVAIL}MB free, need 500MB+)."
fi
ok "Disk space: ${AVAIL}MB available"

# ============================================================
# UPDATE SYSTEM
# ============================================================
step "Updating system packages..."

sudo apt update -qq
sudo apt upgrade -y -qq
ok "System updated"

# ============================================================
# INSTALL SYSTEM DEPENDENCIES
# ============================================================
step "Installing system dependencies..."

PACKAGES=(
    python3-pip
    python3-venv
    python3-dev
    python3-tk
    python3-pil
    python3-pil.imagetk
    portaudio19-dev
    vlc
    chromium-browser
    firefox
    espeak
    espeak-data
    espeak-ng
    espeak-ng-data
    xdotool
    git
    wireless-tools
    network-manager
    alsa-utils
    pulseaudio
    pulseaudio-utils
    pipewire
    pipewire-pulse
    wireplumber
    libopenblas-dev
    flac
    libjpeg-dev
    libpng-dev
    libtiff-dev
    libfreetype6-dev
    liblcms2-dev
    libwebp-dev
    zlib1g-dev
    libffi-dev
    libopenjp2-7-dev
    libharfbuzz-dev
    fonts-inter
    fonts-noto-color-emoji
)

for pkg in "${PACKAGES[@]}"; do
    if dpkg -s "$pkg" &>/dev/null; then
        ok "${pkg} (already installed)"
    else
        sudo apt install -y -qq "$pkg" && ok "${pkg}" || warn "Failed: ${pkg}"
    fi
done

# ============================================================
# CREATE VIRTUAL ENVIRONMENT
# ============================================================
step "Setting up Python environment..."

if [ -d "venv" ]; then
    ok "Virtual environment exists"
else
    python3 -m venv --system-site-packages venv
    ok "Virtual environment created"
fi

source venv/bin/activate
ok "Activated: $(python3 --version)"

# ============================================================
# INSTALL PYTHON PACKAGES
# ============================================================
step "Installing Python packages..."

pip install --upgrade pip setuptools wheel -q
ok "pip upgraded"

pip install -r requirements.txt -q || {
    warn "Some packages failed, trying one by one..."
    while IFS= read -r pkg || [[ -n "$pkg" ]]; do
        [[ -z "$pkg" || "$pkg" =~ ^# ]] && continue
        pip install "$pkg" -q 2>/dev/null && ok "$pkg" || warn "Failed: $pkg"
    done < requirements.txt
}
ok "Python packages installed"

# Verify critical imports
python3 -c "import speech_recognition" 2>/dev/null && ok "SpeechRecognition OK" || warn "SpeechRecognition failed"
python3 -c "import pyttsx3" 2>/dev/null && ok "pyttsx3 OK" || warn "pyttsx3 failed"
python3 -c "import vlc" 2>/dev/null && ok "python-vlc OK" || warn "python-vlc failed"
python3 -c "import qrcode" 2>/dev/null && ok "qrcode OK" || warn "qrcode failed"
python3 -c "import PIL" 2>/dev/null && ok "Pillow OK" || warn "Pillow failed"

# ============================================================
# AUDIO CONFIGURATION
# ============================================================
step "Configuring audio..."

# Ensure user is in audio group
if groups | grep -q audio; then
    ok "User in audio group"
else
    sudo usermod -aG audio "$(whoami)"
    ok "Added to audio group (reboot may be needed)"
fi

# Set default volume
amixer set Master 70% unmute 2>/dev/null && ok "Volume set to 70%" || warn "Could not set volume"

# ============================================================
# SYSTEMD SERVICE
# ============================================================
step "Setting up auto-start service..."

CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)
SERVICE_FILE="/etc/systemd/system/arcanum.service"

if [ -f "$SERVICE_FILE" ]; then
    ok "Service already exists"
    echo -e "  ${YELLOW}To update:${NC} sudo systemctl daemon-reload && sudo systemctl restart arcanum"
else
    sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Arcanum Voice Assistant
After=network.target sound.target graphical.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=5
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$CURRENT_USER/.Xauthority
Environment=PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native

[Install]
WantedBy=graphical.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable arcanum
    ok "Service installed and enabled"
fi

# ============================================================
# DONE
# ============================================================
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  ✓ INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}No API keys needed.${NC} Everything is ready."
echo ""
echo -e "  ${CYAN}To run now:${NC}"
echo -e "    source venv/bin/activate"
echo -e "    python main.py"
echo ""
echo -e "  ${CYAN}Auto-start on boot:${NC}"
echo -e "    sudo reboot"
echo ""
echo -e "  ${CYAN}First run:${NC}"
echo -e "    Arcanum will ask you to repeat 7 words"
echo -e "    for voice calibration, then ask your name."
echo -e "    After that, say ${BOLD}'Arcanum'${NC} to activate!"
echo ""
echo -e "  ${CYAN}Plug in your USB microphone.${NC}"
echo ""
echo -e "  ${YELLOW}Tip:${NC} Say 'Arcanum, ayuda' for all commands."
echo -e "  ${YELLOW}Tip:${NC} Say 'Arcanum, configurar modo' for automations."
echo -e "  ${YELLOW}Tip:${NC} Say 'Arcanum, teclado' for on-screen keyboard."
echo ""
