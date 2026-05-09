"""
Premium GUI window for Arcanum.
Smart-display style dashboard with rounded cards, waveform animation,
gradient accents, and smooth transitions.
"""
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
from PIL import Image, ImageTk

from config.settings import (
    COLOR_BG, COLOR_BG_CARD, COLOR_BG_HEADER, COLOR_BG_ELEVATED, COLOR_BORDER,
    COLOR_TEXT, COLOR_TEXT_SOFT, COLOR_DIM,
    COLOR_ACCENT, COLOR_ACCENT_2, COLOR_ACCENT_3,
    COLOR_USER, COLOR_BOT, COLOR_SYSTEM,
    COLOR_LISTENING, COLOR_LISTENING_BG, COLOR_PROCESSING,
    APP_NAME, APP_AUTHOR, SCREENSAVER_TIMEOUT, HOME_LOCATION,
    FONT_FAMILY,
)
from ui.screensaver import Screensaver
from ui.help_overlay import HelpOverlay
from ui.widgets import RoundedCard, CircleButton, WaveformAnimation, blend


def _pick_font(root: tk.Tk, preferred: str, fallbacks: list[str]) -> str:
    available = set(tkfont.families(root))
    for name in [preferred] + fallbacks:
        if name in available:
            return name
    return "Helvetica"


class AppWindow:
    """Premium home dashboard for Arcanum."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.configure(bg=COLOR_BG)
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="")

        self.font = _pick_font(
            root, FONT_FAMILY,
            ["Inter", "SF Pro Display", "Segoe UI Variable", "Segoe UI",
             "Ubuntu", "Helvetica"],
        )
        self.font_mono = _pick_font(
            root, "JetBrains Mono",
            ["Fira Code", "Cascadia Code", "Consolas", "Courier"],
        )

        # Hotkeys
        self.root.bind("<Escape>", self._toggle_dev_mode)
        self.root.bind("<Control-q>", lambda e: self.root.destroy())
        self.root.bind("<F11>", lambda e: self.root.attributes("-fullscreen", True))
        self.root.bind("<Motion>", self._reset_screensaver_timer)
        self.root.bind("<Key>", self._reset_screensaver_timer)

        # State
        self._screensaver_timer_id = None
        self._weather_text = "Cargando…"
        self._qr_photo = None
        self._talk_callback = None
        self._keyboard_frame = None
        self._keyboard_active = False
        self._keyboard_text = ""
        self._kb_shift = False
        self._mode = "idle"  # idle, listening, processing, error
        self._talk_pulse_id = None
        self._talk_pulse_step = 0

        self._build_ui()

        # Overlays
        self.screensaver = Screensaver(self.root, font=self.font)
        self.help_overlay = HelpOverlay(self.root, font=self.font)
        self._reset_screensaver_timer()

    # ============================================================
    # UI BUILD
    # ============================================================

    def _build_ui(self) -> None:
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.pack(fill="both", expand=True)

        self._build_top_bar()

        # Main content with proper grid
        content = tk.Frame(self.main_frame, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=22, pady=12)

        content.columnconfigure(0, weight=0, minsize=400)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=COLOR_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        right = tk.Frame(content, bg=COLOR_BG)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_clock_card(left)
        self._build_weather_card(left)
        self._build_now_playing_card(left)
        self._build_qr_card(left)

        self._build_listening_hero(right)
        self._build_chat_card(right)

        self._build_bottom_bar()
        self._update_clock()

    def _build_top_bar(self) -> None:
        bar = tk.Frame(self.main_frame, bg=COLOR_BG_HEADER, height=58)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Brand
        brand = tk.Frame(bar, bg=COLOR_BG_HEADER)
        brand.pack(side="left", padx=24)

        # Logo orb
        orb = tk.Canvas(brand, width=32, height=32, bg=COLOR_BG_HEADER,
                        highlightthickness=0, bd=0)
        orb.pack(side="left", padx=(0, 12))
        orb.create_oval(2, 2, 30, 30, fill=COLOR_ACCENT, outline="")
        orb.create_oval(8, 8, 24, 24, fill=COLOR_ACCENT_3, outline="")
        orb.create_oval(13, 13, 19, 19, fill="#ffffff", outline="")

        tk.Label(
            brand, text=APP_NAME, font=(self.font, 18, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_HEADER,
        ).pack(side="left")

        tk.Label(
            brand, text="·  Voice Assistant",
            font=(self.font, 11), fg=COLOR_DIM, bg=COLOR_BG_HEADER,
            padx=10,
        ).pack(side="left")

        # Right cluster
        right = tk.Frame(bar, bg=COLOR_BG_HEADER)
        right.pack(side="right", padx=24)

        # Service indicator
        self.service_label = tk.Label(
            right, text="", font=(self.font, 12, "bold"),
            fg=COLOR_ACCENT_3, bg=COLOR_BG_HEADER,
        )
        self.service_label.pack(side="right", padx=(12, 0))

        # Status pill
        pill = tk.Frame(
            right, bg=COLOR_BG_ELEVATED,
            highlightthickness=1, highlightbackground=COLOR_BORDER,
        )
        pill.pack(side="right")

        self.status_dot = tk.Canvas(
            pill, width=12, height=12, bg=COLOR_BG_ELEVATED,
            highlightthickness=0, bd=0,
        )
        self.status_dot.pack(side="left", padx=(12, 8), pady=8)
        self._status_dot_id = self.status_dot.create_oval(
            0, 0, 12, 12, fill=COLOR_ACCENT_2, outline="",
        )

        self.status_label = tk.Label(
            pill, text="Inicializando", font=(self.font, 11, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_ELEVATED,
        )
        self.status_label.pack(side="left", padx=(0, 14), pady=8)

    # ---------- LEFT COLUMN ----------

    def _build_clock_card(self, parent) -> None:
        card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_BG_CARD,
            border=COLOR_BORDER, radius=20, padding=24, height=200,
        )
        card.pack(fill="x", pady=(0, 16))
        card.pack_propagate(False)

        body = card.body

        # Top label
        tk.Label(
            body, text="HORA ACTUAL", font=(self.font, 9, "bold"),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(anchor="w")

        # Clock with seconds
        clock_row = tk.Frame(body, bg=COLOR_BG_CARD)
        clock_row.pack(fill="x", pady=(8, 6))

        self.time_label = tk.Label(
            clock_row, text="00:00", font=(self.font, 70, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD,
        )
        self.time_label.pack(side="left")

        sec_col = tk.Frame(clock_row, bg=COLOR_BG_CARD)
        sec_col.pack(side="left", padx=(12, 0), pady=(20, 0), anchor="s")

        self.seconds_label = tk.Label(
            sec_col, text="00", font=(self.font, 22, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
        )
        self.seconds_label.pack(anchor="w")

        tk.Label(
            sec_col, text="seg", font=(self.font, 10),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(anchor="w", pady=(2, 0))

        # Day/Date row
        date_row = tk.Frame(body, bg=COLOR_BG_CARD)
        date_row.pack(fill="x", pady=(6, 0))

        self.day_label = tk.Label(
            date_row, text="", font=(self.font, 13, "bold"),
            fg=COLOR_ACCENT_2, bg=COLOR_BG_CARD,
        )
        self.day_label.pack(side="left")

        self.date_label = tk.Label(
            date_row, text="", font=(self.font, 13),
            fg=COLOR_TEXT_SOFT, bg=COLOR_BG_CARD,
        )
        self.date_label.pack(side="right")

    def _build_weather_card(self, parent) -> None:
        card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_BG_CARD,
            border=COLOR_BORDER, radius=20, padding=22, height=160,
        )
        card.pack(fill="x", pady=(0, 16))
        card.pack_propagate(False)

        body = card.body

        # Header
        header = tk.Frame(body, bg=COLOR_BG_CARD)
        header.pack(fill="x")

        tk.Label(
            header, text="CLIMA", font=(self.font, 9, "bold"),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(side="left")

        tk.Label(
            header, text="🌤", font=(self.font, 22),
            fg=COLOR_ACCENT_3, bg=COLOR_BG_CARD,
        ).pack(side="right")

        tk.Label(
            body, text=HOME_LOCATION, font=(self.font, 10),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(anchor="w", pady=(2, 8))

        self.weather_label = tk.Label(
            body, text=self._weather_text, font=(self.font, 12),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD,
            anchor="w", justify="left", wraplength=340,
        )
        self.weather_label.pack(fill="x", expand=True, anchor="nw")

    def _build_now_playing_card(self, parent) -> None:
        # Hidden by default; appears when a service is active
        self._now_playing_card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_BG_CARD,
            border=COLOR_BORDER, radius=20, padding=22, height=130,
            accent=None,
        )

        body = self._now_playing_card.body

        tk.Label(
            body, text="REPRODUCIENDO", font=(self.font, 9, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
        ).pack(anchor="w")

        row = tk.Frame(body, bg=COLOR_BG_CARD)
        row.pack(fill="x", pady=(8, 0))

        self.np_icon = tk.Label(
            row, text="▶", font=(self.font, 24),
            fg=COLOR_ACCENT_2, bg=COLOR_BG_CARD,
        )
        self.np_icon.pack(side="left", padx=(0, 12))

        col = tk.Frame(row, bg=COLOR_BG_CARD)
        col.pack(side="left", fill="both", expand=True)

        self.np_title = tk.Label(
            col, text="", font=(self.font, 14, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD, anchor="w",
        )
        self.np_title.pack(fill="x")

        self.np_subtitle = tk.Label(
            col, text="", font=(self.font, 11),
            fg=COLOR_DIM, bg=COLOR_BG_CARD, anchor="w",
        )
        self.np_subtitle.pack(fill="x")

    def _build_qr_card(self, parent) -> None:
        # Hidden by default
        self._qr_parent = parent
        self.qr_card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_BG_CARD,
            border=COLOR_BORDER, radius=20, padding=20, height=300,
        )

        body = self.qr_card.body

        tk.Label(
            body, text="WIFI · ESCANEA CON TU TELÉFONO",
            font=(self.font, 9, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
        ).pack(anchor="w")

        self.qr_image_label = tk.Label(body, bg=COLOR_BG_CARD)
        self.qr_image_label.pack(pady=(10, 8))

        self.qr_info_label = tk.Label(
            body, text="", font=(self.font_mono, 10),
            fg=COLOR_TEXT_SOFT, bg=COLOR_BG_CARD, wraplength=320,
        )
        self.qr_info_label.pack()

    # ---------- RIGHT COLUMN ----------

    def _build_listening_hero(self, parent) -> None:
        card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_LISTENING_BG,
            border=COLOR_BORDER, radius=22, padding=24, height=180,
        )
        card.pack(fill="x", pady=(0, 16))
        card.pack_propagate(False)
        self._listening_card = card

        body = card.body

        # Top row: status hint + waveform
        top_row = tk.Frame(body, bg=COLOR_LISTENING_BG)
        top_row.pack(fill="x")

        self.listening_hint = tk.Label(
            top_row, text="LISTO", font=(self.font, 10, "bold"),
            fg=COLOR_ACCENT_2, bg=COLOR_LISTENING_BG,
        )
        self.listening_hint.pack(side="left")

        # Waveform (compact)
        self.waveform = WaveformAnimation(
            top_row, width=120, height=28,
            bg=COLOR_LISTENING_BG, color=COLOR_DIM, num_bars=7,
        )
        self.waveform.pack(side="right")

        # Main message
        self.listening_text = tk.Label(
            body, text=f'Di "{APP_NAME}" o toca el botón',
            font=(self.font, 22, "bold"),
            fg=COLOR_TEXT, bg=COLOR_LISTENING_BG,
            anchor="w", justify="left",
        )
        self.listening_text.pack(fill="x", pady=(14, 4))

        # Sub hint
        self.listening_sub = tk.Label(
            body, text='Comandos por voz · Modos · Streaming',
            font=(self.font, 11),
            fg=COLOR_DIM, bg=COLOR_LISTENING_BG,
            anchor="w",
        )
        self.listening_sub.pack(fill="x")

        # Bottom: actions row
        actions = tk.Frame(body, bg=COLOR_LISTENING_BG)
        actions.pack(fill="x", side="bottom", pady=(10, 0))

        # Big talk button
        self.talk_btn = CircleButton(
            actions, size=64, bg=COLOR_ACCENT, fg="#ffffff",
            active_bg=COLOR_ACCENT_3, text="🎤",
            font=(self.font, 26), command=self._on_talk_pressed,
            outer_bg=COLOR_LISTENING_BG,
        )
        self.talk_btn.pack(side="right")

        # Helper text near button
        tk.Label(
            actions, text="Pulsar para hablar",
            font=(self.font, 11), fg=COLOR_DIM, bg=COLOR_LISTENING_BG,
        ).pack(side="right", padx=(0, 14))

    def _build_chat_card(self, parent) -> None:
        card = RoundedCard(
            parent, bg_outer=COLOR_BG, bg_card=COLOR_BG_CARD,
            border=COLOR_BORDER, radius=22, padding=2,
        )
        card.pack(fill="both", expand=True)

        body = card.body

        # Header
        header = tk.Frame(body, bg=COLOR_BG_CARD)
        header.pack(fill="x", padx=18, pady=(16, 8))

        tk.Label(
            header, text="CONVERSACIÓN", font=(self.font, 10, "bold"),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(side="left")

        # Clear-all chip
        self.clear_chip = tk.Label(
            header, text="•", font=(self.font, 10),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        )
        self.clear_chip.pack(side="right")

        # Subtle separator
        sep = tk.Frame(body, bg=COLOR_BORDER, height=1)
        sep.pack(fill="x", padx=18, pady=(0, 8))

        # Scrollable canvas
        chat_container = tk.Frame(body, bg=COLOR_BG_CARD)
        chat_container.pack(fill="both", expand=True, padx=10, pady=(0, 14))

        self.chat_canvas = tk.Canvas(
            chat_container, bg=COLOR_BG_CARD, highlightthickness=0,
        )
        self.chat_scrollbar = tk.Scrollbar(
            chat_container, orient="vertical",
            command=self.chat_canvas.yview,
            bg=COLOR_BG_CARD, troughcolor=COLOR_BG_CARD,
            activebackground=COLOR_ACCENT, bd=0, relief="flat",
            highlightthickness=0, width=8,
        )
        self.chat_inner = tk.Frame(self.chat_canvas, bg=COLOR_BG_CARD)

        self.chat_inner.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            ),
        )
        self._chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.chat_inner, anchor="nw",
        )
        self.chat_canvas.bind(
            "<Configure>",
            lambda e: self.chat_canvas.itemconfig(
                self._chat_window, width=e.width
            ),
        )
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_scrollbar.pack(side="right", fill="y")

        # Empty state
        self._empty_state = tk.Frame(self.chat_inner, bg=COLOR_BG_CARD)
        self._empty_state.pack(fill="x", pady=40)

        tk.Label(
            self._empty_state, text="◆", font=(self.font, 48),
            fg=COLOR_BORDER, bg=COLOR_BG_CARD,
        ).pack()

        tk.Label(
            self._empty_state,
            text="La conversación aparecerá aquí",
            font=(self.font, 13), fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(pady=(8, 0))

        tk.Label(
            self._empty_state,
            text='Di "Arcanum, ayuda" para ver todos los comandos',
            font=(self.font, 11), fg=COLOR_DIM, bg=COLOR_BG_CARD,
        ).pack(pady=(4, 0))

    def _build_bottom_bar(self) -> None:
        bar = tk.Frame(self.main_frame, bg=COLOR_BG_HEADER, height=34)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(
            bar, text=f"◆ {APP_NAME}  ·  by {APP_AUTHOR}",
            font=(self.font, 10), fg=COLOR_DIM, bg=COLOR_BG_HEADER,
            padx=20,
        ).pack(side="left")

        self.bottom_time = tk.Label(
            bar, text="", font=(self.font_mono, 10),
            fg=COLOR_DIM, bg=COLOR_BG_HEADER, padx=20,
        )
        self.bottom_time.pack(side="right")

        tk.Label(
            bar, text="Ctrl+Q salir  ·  ESC fullscreen",
            font=(self.font, 10), fg=COLOR_DIM, bg=COLOR_BG_HEADER,
        ).pack(side="right", padx=12)

    # ============================================================
    # CLOCK
    # ============================================================

    def _update_clock(self) -> None:
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.seconds_label.configure(text=now.strftime("%S"))

        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        day_name = days_es[now.weekday()]
        month_name = months_es[now.month - 1]
        self.date_label.configure(text=f"{now.day} {month_name} {now.year}")
        self.day_label.configure(text=day_name.upper())
        self.bottom_time.configure(text=now.strftime("%H:%M:%S"))

        self.root.after(1000, self._update_clock)

    # ============================================================
    # PUBLIC API
    # ============================================================

    def add_user_message(self, text: str) -> None:
        self._hide_empty_state()
        self._add_bubble(text, sender="user")
        self._scroll_to_bottom()

    def add_bot_message(self, text: str) -> None:
        self._hide_empty_state()
        self._add_bubble(text, sender="bot")
        self._scroll_to_bottom()

    def add_system_message(self, text: str) -> None:
        self._hide_empty_state()
        self._add_bubble(text, sender="system")
        self._scroll_to_bottom()

    def _hide_empty_state(self) -> None:
        if self._empty_state and self._empty_state.winfo_exists():
            try:
                self._empty_state.destroy()
                self._empty_state = None
            except Exception:
                pass

    def set_status(self, text: str, color: str = COLOR_ACCENT_2) -> None:
        self.status_label.configure(text=text)
        self.status_dot.itemconfig(self._status_dot_id, fill=color)

    def set_listening(self, active: bool) -> None:
        if active:
            self._mode = "listening"
            self.listening_hint.configure(text="ESCUCHANDO", fg=COLOR_LISTENING)
            self.listening_text.configure(text="Te escucho…", fg=COLOR_TEXT)
            self.listening_sub.configure(text="Habla con naturalidad")
            self.waveform.set_color(COLOR_LISTENING)
            self.waveform.start()
            self._listening_card.set_accent(COLOR_LISTENING)
            self.talk_btn.set_color(COLOR_LISTENING, blend(COLOR_LISTENING, "#ffffff", 0.2))
            self.talk_btn.set_text("●")
            self.set_status("Escuchando", COLOR_LISTENING)
        else:
            self._mode = "idle"
            self.waveform.stop()
            self.waveform.set_color(COLOR_DIM)
            self.listening_hint.configure(text="LISTO", fg=COLOR_ACCENT_2)
            self.listening_text.configure(
                text=f'Di "{APP_NAME}" o toca el botón', fg=COLOR_TEXT,
            )
            self.listening_sub.configure(text='Comandos por voz · Modos · Streaming')
            self._listening_card.set_accent(None)
            self.talk_btn.set_color(COLOR_ACCENT, COLOR_ACCENT_3)
            self.talk_btn.set_text("🎤")
            self.set_status("Listo", COLOR_ACCENT_2)

    def set_live_speech(self, text: str) -> None:
        display = text if text else "Escuchando…"
        self.listening_text.configure(text=f'"{display}"', fg=COLOR_USER)
        self.listening_sub.configure(text="Procesando lo que dijiste…")

    def set_processing(self) -> None:
        self._mode = "processing"
        self.listening_hint.configure(text="PROCESANDO", fg=COLOR_PROCESSING)
        self.listening_text.configure(text="Pensando…", fg=COLOR_TEXT)
        self.listening_sub.configure(text="Resolviendo tu solicitud")
        self.waveform.set_color(COLOR_PROCESSING)
        self.waveform.start()
        self._listening_card.set_accent(COLOR_PROCESSING)
        self.talk_btn.set_color(COLOR_PROCESSING, blend(COLOR_PROCESSING, "#ffffff", 0.2))
        self.talk_btn.set_text("◐")
        self.set_status("Procesando", COLOR_PROCESSING)

    def set_not_understood(self) -> None:
        self.listening_hint.configure(text="NO ENTENDÍ", fg=COLOR_LISTENING)
        self.listening_text.configure(text="¿Puedes repetir?", fg=COLOR_LISTENING)
        self.listening_sub.configure(text="Habla más cerca del micrófono")
        self._listening_card.set_accent(COLOR_LISTENING)

    def update_weather(self, text: str) -> None:
        self._weather_text = text
        self.weather_label.configure(text=text)

    def show_qr(self, image_path: str, wifi_text: str) -> None:
        try:
            img = Image.open(image_path)
            img = img.resize((220, 220), Image.LANCZOS)
            self._qr_photo = ImageTk.PhotoImage(img)
            self.qr_image_label.configure(image=self._qr_photo)
            self.qr_info_label.configure(text=wifi_text)
            self.qr_card.pack(fill="x", pady=(0, 16))
        except Exception as e:
            print(f"[UI] QR display error: {e}")

    def hide_qr(self) -> None:
        self.qr_card.pack_forget()

    def set_service_info(self, text: str) -> None:
        self.service_label.configure(text=text)
        # Update Now Playing card
        if text:
            self._show_now_playing(text)
        else:
            self._hide_now_playing()

    def _show_now_playing(self, text: str) -> None:
        # Parse "▶ ServiceName" or "📻 Station"
        if text.startswith("▶"):
            icon = "▶"
            title = text[1:].strip()
            subtitle = "Streaming activo"
        elif text.startswith("📻"):
            icon = "📻"
            title = text[1:].strip()
            subtitle = "Radio en vivo"
        else:
            icon = "♫"
            title = text
            subtitle = "Reproduciendo"

        self.np_icon.configure(text=icon)
        self.np_title.configure(text=title)
        self.np_subtitle.configure(text=subtitle)
        self._now_playing_card.set_accent(COLOR_ACCENT_2)
        self._now_playing_card.pack(fill="x", pady=(0, 16), after=None)
        # Re-pack to position after weather
        try:
            self._now_playing_card.pack_forget()
            self._now_playing_card.pack(fill="x", pady=(0, 16))
        except Exception:
            pass

    def _hide_now_playing(self) -> None:
        self._now_playing_card.pack_forget()

    def show_help(self) -> None:
        self.help_overlay.show()

    def hide_help(self) -> None:
        self.help_overlay.hide()

    def clear_chat(self) -> None:
        for widget in self.chat_inner.winfo_children():
            widget.destroy()

    def dismiss_screensaver(self) -> None:
        self.screensaver.hide()
        self._reset_screensaver_timer()

    def bring_to_front(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def set_talk_callback(self, callback) -> None:
        self._talk_callback = callback

    # ============================================================
    # ON-SCREEN KEYBOARD
    # ============================================================

    def show_keyboard(self) -> None:
        if self._keyboard_active:
            return
        self._keyboard_active = True
        self._keyboard_text = ""
        self._kb_shift = False

        self._keyboard_frame = tk.Frame(
            self.root, bg=COLOR_BG_HEADER,
            highlightthickness=1, highlightbackground=COLOR_BORDER,
        )
        self._keyboard_frame.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)

        # Display row
        display_row = tk.Frame(self._keyboard_frame, bg=COLOR_BG_HEADER)
        display_row.pack(fill="x", padx=18, pady=(18, 10))

        display_card = tk.Frame(
            display_row, bg=COLOR_BG_CARD,
            highlightthickness=2, highlightbackground=COLOR_ACCENT,
        )
        display_card.pack(side="left", fill="both", expand=True, ipady=10)

        tk.Label(
            display_card, text="✎", font=(self.font, 16),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD, padx=14,
        ).pack(side="left")

        self._kb_display = tk.Label(
            display_card, text="|",
            font=(self.font_mono, 18, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD,
            anchor="w",
        )
        self._kb_display.pack(side="left", fill="both", expand=True)

        send_btn = tk.Button(
            display_row, text="ENVIAR  ↵",
            font=(self.font, 12, "bold"),
            fg="#ffffff", bg=COLOR_ACCENT_2,
            activebackground=COLOR_ACCENT_3, activeforeground="#ffffff",
            relief="flat", bd=0, padx=20, pady=12, cursor="hand2",
            command=self._kb_send,
        )
        send_btn.pack(side="right", padx=(10, 0))

        close_btn = tk.Button(
            display_row, text="✕",
            font=(self.font, 14, "bold"),
            fg=COLOR_LISTENING, bg=COLOR_BG_CARD,
            activebackground=COLOR_BG_ELEVATED, activeforeground=COLOR_LISTENING,
            relief="flat", bd=0, padx=14, pady=12, cursor="hand2",
            command=self.hide_keyboard,
        )
        close_btn.pack(side="right", padx=(10, 0))

        # Keys
        keys_frame = tk.Frame(self._keyboard_frame, bg=COLOR_BG_HEADER)
        keys_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        rows = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "@", "."],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "/"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ñ", "_"],
            ["⇧", "z", "x", "c", "v", "b", "n", "m", ",", "-", "⌫"],
            ["SPACE"],
        ]

        for row_keys in rows:
            row_frame = tk.Frame(keys_frame, bg=COLOR_BG_HEADER)
            row_frame.pack(fill="x", pady=3)
            for key in row_keys:
                self._make_key(row_frame, key)

    def _make_key(self, parent, key: str) -> None:
        special = key in ("⇧", "⌫", "SPACE")
        bg = COLOR_BG_ELEVATED if special else COLOR_BG_CARD
        fg = COLOR_ACCENT if special else COLOR_TEXT

        if key == "SPACE":
            label = "ESPACIO"
            width = 30
        elif key == "⇧":
            label = "⇧"
            width = 5
        elif key == "⌫":
            label = "⌫"
            width = 5
        else:
            label = key.upper() if self._kb_shift else key
            width = 4

        btn = tk.Button(
            parent, text=label,
            font=(self.font, 14, "bold" if special else "normal"),
            fg=fg, bg=bg,
            activebackground=COLOR_ACCENT, activeforeground="#ffffff",
            relief="flat", bd=0, width=width, height=2,
            cursor="hand2",
            command=lambda k=key: self._kb_press(k),
        )
        btn.pack(side="left", padx=3, expand=(key == "SPACE"),
                 fill="x" if key == "SPACE" else None)

    def hide_keyboard(self) -> None:
        if not self._keyboard_active:
            return
        self._keyboard_active = False
        if self._keyboard_frame:
            self._keyboard_frame.destroy()
            self._keyboard_frame = None

    def _kb_press(self, key: str) -> None:
        if key == "⌫":
            self._keyboard_text = self._keyboard_text[:-1]
        elif key == "⇧":
            self._kb_shift = not self._kb_shift
        elif key == "SPACE":
            self._keyboard_text += " "
        else:
            char = key.upper() if self._kb_shift else key
            self._keyboard_text += char
            self._kb_shift = False
        self._kb_display.configure(text=self._keyboard_text + "|")

    def _kb_send(self) -> None:
        if not self._keyboard_text:
            return
        try:
            from services.browser_control import BrowserControl
            browser = BrowserControl()
            browser.type_text(self._keyboard_text)
            browser.click_or_select()
        except Exception as e:
            print(f"[Keyboard] Send error: {e}")
        self._keyboard_text = ""
        self._kb_display.configure(text="|")
        self.hide_keyboard()

    # ============================================================
    # CHAT BUBBLES
    # ============================================================

    def _add_bubble(self, text: str, sender: str) -> None:
        timestamp = datetime.now().strftime("%H:%M")

        outer = tk.Frame(self.chat_inner, bg=COLOR_BG_CARD)
        outer.pack(fill="x", pady=8, padx=10)

        if sender == "user":
            avatar_text = "Tú"
            avatar_bg = COLOR_USER
            bubble_bg = COLOR_BG_ELEVATED
            text_color = COLOR_TEXT
            anchor_side = "right"
            label_color = COLOR_USER
        elif sender == "bot":
            avatar_text = "◆"
            avatar_bg = COLOR_BOT
            bubble_bg = COLOR_BG_ELEVATED
            text_color = COLOR_TEXT
            anchor_side = "left"
            label_color = COLOR_BOT
        else:  # system
            avatar_text = "ℹ"
            avatar_bg = COLOR_DIM
            bubble_bg = COLOR_BG_CARD
            text_color = COLOR_SYSTEM
            anchor_side = "left"
            label_color = COLOR_DIM

        # Row container
        row = tk.Frame(outer, bg=COLOR_BG_CARD)
        row.pack(fill="x")

        if anchor_side == "right":
            spacer = tk.Frame(row, bg=COLOR_BG_CARD)
            spacer.pack(side="left", fill="x", expand=True)

        # Bubble side
        bubble_side = tk.Frame(row, bg=COLOR_BG_CARD)
        bubble_side.pack(side=anchor_side)

        # Header (sender + time)
        header = tk.Frame(bubble_side, bg=COLOR_BG_CARD)
        header.pack(fill="x", anchor="e" if anchor_side == "right" else "w")

        if anchor_side == "right":
            tk.Label(
                header, text=timestamp, font=(self.font, 9),
                fg=COLOR_DIM, bg=COLOR_BG_CARD,
            ).pack(side="right", padx=(8, 6))
            tk.Label(
                header, text=avatar_text,
                font=(self.font, 10, "bold"),
                fg=label_color, bg=COLOR_BG_CARD,
            ).pack(side="right")
        else:
            tk.Label(
                header, text=avatar_text,
                font=(self.font, 10, "bold"),
                fg=label_color, bg=COLOR_BG_CARD,
            ).pack(side="left", padx=(6, 0))
            tk.Label(
                header, text=timestamp, font=(self.font, 9),
                fg=COLOR_DIM, bg=COLOR_BG_CARD,
            ).pack(side="left", padx=(8, 0))

        # Bubble itself with subtle border
        bubble = tk.Frame(
            bubble_side, bg=bubble_bg,
            highlightthickness=1,
            highlightbackground=label_color if sender != "system" else COLOR_BORDER,
        )
        bubble.pack(fill="x", pady=(4, 0), padx=4)

        tk.Label(
            bubble, text=text, font=(self.font, 13),
            fg=text_color, bg=bubble_bg,
            anchor="w", justify="left",
            wraplength=540, padx=16, pady=12,
        ).pack(fill="both")

        if anchor_side == "left":
            spacer = tk.Frame(row, bg=COLOR_BG_CARD)
            spacer.pack(side="left", fill="x", expand=True)

    def _scroll_to_bottom(self) -> None:
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    # ============================================================
    # MISC
    # ============================================================

    def _on_talk_pressed(self) -> None:
        if self._talk_callback:
            self._talk_callback()

    def _toggle_dev_mode(self, event=None) -> None:
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)

    def _reset_screensaver_timer(self, event=None) -> None:
        if self._screensaver_timer_id:
            self.root.after_cancel(self._screensaver_timer_id)
        if self.screensaver.active:
            self.screensaver.hide()
        self._screensaver_timer_id = self.root.after(
            SCREENSAVER_TIMEOUT * 1000, self._activate_screensaver
        )

    def _activate_screensaver(self) -> None:
        if not self.help_overlay.active:
            self.screensaver.show()
