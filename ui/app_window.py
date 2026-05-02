"""
Main GUI window for Arcanum.
Fullscreen Tkinter app with Alexa/Google Home style dashboard.
Shows: clock, date, location, weather, live speech, conversation.
"""
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
from PIL import Image, ImageTk
from config.settings import (
    COLOR_BG, COLOR_BG_CARD, COLOR_BG_HEADER, COLOR_TEXT, COLOR_ACCENT,
    COLOR_USER, COLOR_BOT, COLOR_DIM, COLOR_LISTENING, COLOR_LISTENING_BG,
    APP_NAME, APP_AUTHOR, SCREENSAVER_TIMEOUT, HOME_LOCATION,
)
from ui.screensaver import Screensaver
from ui.help_overlay import HelpOverlay


class AppWindow:
    """Main application window with home dashboard and conversation."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.configure(bg=COLOR_BG)
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")  # Hide cursor on Pi

        # Allow ESC to exit fullscreen / show cursor (dev mode)
        self.root.bind("<Escape>", self._toggle_dev_mode)
        self.root.bind("<F11>", lambda e: self.root.attributes("-fullscreen", True))

        # Reset screensaver on any activity
        self.root.bind("<Motion>", self._reset_screensaver_timer)
        self.root.bind("<Key>", self._reset_screensaver_timer)

        self._screensaver_timer_id = None
        self._weather_text = "Loading weather..."
        self._qr_photo = None  # Keep reference for Tkinter
        self._listening_anim_id = None
        self._listening_dots = 0

        self._build_ui()

        # Overlays
        self.screensaver = Screensaver(self.main_frame)
        self.help_overlay = HelpOverlay(self.main_frame)
        self._reset_screensaver_timer()

    def _build_ui(self) -> None:
        """Build the home dashboard UI."""
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.pack(fill="both", expand=True)

        # ===== TOP BAR =====
        top_bar = tk.Frame(self.main_frame, bg=COLOR_BG_HEADER, height=40)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        self.status_dot = tk.Label(
            top_bar, text="●", font=("Helvetica", 14),
            fg=COLOR_BOT, bg=COLOR_BG_HEADER, padx=10,
        )
        self.status_dot.pack(side="left")

        self.status_label = tk.Label(
            top_bar, text="Initializing...", font=("Helvetica", 11),
            fg=COLOR_DIM, bg=COLOR_BG_HEADER,
        )
        self.status_label.pack(side="left")

        self.service_label = tk.Label(
            top_bar, text="", font=("Helvetica", 11),
            fg=COLOR_ACCENT, bg=COLOR_BG_HEADER, padx=15,
        )
        self.service_label.pack(side="right")

        # ===== MAIN CONTENT AREA =====
        content = tk.Frame(self.main_frame, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=15, pady=5)

        # --- Left column: Clock + Weather + Location ---
        left_col = tk.Frame(content, bg=COLOR_BG, width=340)
        left_col.pack(side="left", fill="y", padx=(5, 10))
        left_col.pack_propagate(False)

        # Clock card
        clock_card = tk.Frame(left_col, bg=COLOR_BG_CARD, padx=15, pady=15)
        clock_card.pack(fill="x", pady=(5, 5))

        self.time_label = tk.Label(
            clock_card, text="00:00", font=("Helvetica", 56, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
        )
        self.time_label.pack()

        self.seconds_label = tk.Label(
            clock_card, text=":00", font=("Helvetica", 20),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        )
        self.seconds_label.place(relx=0.82, rely=0.35)

        self.date_label = tk.Label(
            clock_card, text="", font=("Helvetica", 14),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD,
        )
        self.date_label.pack(pady=(5, 0))

        self.day_label = tk.Label(
            clock_card, text="", font=("Helvetica", 11),
            fg=COLOR_DIM, bg=COLOR_BG_CARD,
        )
        self.day_label.pack()

        # Weather card
        weather_card = tk.Frame(left_col, bg=COLOR_BG_CARD, padx=15, pady=12)
        weather_card.pack(fill="x", pady=5)

        tk.Label(
            weather_card, text="🌤  Clima", font=("Helvetica", 12, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD, anchor="w",
        ).pack(fill="x")

        self.weather_label = tk.Label(
            weather_card, text=self._weather_text, font=("Helvetica", 11),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD, anchor="w", wraplength=300,
            justify="left",
        )
        self.weather_label.pack(fill="x", pady=(5, 0))

        # Location card
        location_card = tk.Frame(left_col, bg=COLOR_BG_CARD, padx=15, pady=10)
        location_card.pack(fill="x", pady=5)

        tk.Label(
            location_card, text="📍  Ubicación", font=("Helvetica", 12, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD, anchor="w",
        ).pack(fill="x")

        tk.Label(
            location_card, text=HOME_LOCATION, font=("Helvetica", 11),
            fg=COLOR_TEXT, bg=COLOR_BG_CARD, anchor="w",
        ).pack(fill="x", pady=(3, 0))

        # QR area (hidden until requested)
        self.qr_card = tk.Frame(left_col, bg=COLOR_BG_CARD, padx=15, pady=10)
        # Not packed by default — shown when QR is generated

        self.qr_title_label = tk.Label(
            self.qr_card, text="📶  WiFi QR", font=("Helvetica", 12, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_CARD, anchor="w",
        )
        self.qr_title_label.pack(fill="x")

        self.qr_image_label = tk.Label(self.qr_card, bg=COLOR_BG_CARD)
        self.qr_image_label.pack(pady=5)

        self.qr_info_label = tk.Label(
            self.qr_card, text="", font=("Helvetica", 9),
            fg=COLOR_DIM, bg=COLOR_BG_CARD, wraplength=280,
        )
        self.qr_info_label.pack()

        # --- Right column: Conversation + Listening ---
        right_col = tk.Frame(content, bg=COLOR_BG)
        right_col.pack(side="right", fill="both", expand=True)

        # Listening / live speech area
        self.listening_frame = tk.Frame(right_col, bg=COLOR_LISTENING_BG, height=80)
        self.listening_frame.pack(fill="x", pady=(5, 5))
        self.listening_frame.pack_propagate(False)

        self.listening_icon = tk.Label(
            self.listening_frame, text="", font=("Helvetica", 28),
            fg=COLOR_LISTENING, bg=COLOR_LISTENING_BG,
        )
        self.listening_icon.pack(side="left", padx=(15, 5))

        self.listening_text = tk.Label(
            self.listening_frame, text=f'Say "{APP_NAME}" to activate',
            font=("Helvetica", 16), fg=COLOR_DIM, bg=COLOR_LISTENING_BG,
            anchor="w", wraplength=500, justify="left",
        )
        self.listening_text.pack(side="left", fill="both", expand=True, padx=10)

        # Conversation area
        chat_container = tk.Frame(right_col, bg=COLOR_BG)
        chat_container.pack(fill="both", expand=True)

        self.chat_canvas = tk.Canvas(chat_container, bg=COLOR_BG, highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(
            chat_container, orient="vertical", command=self.chat_canvas.yview,
        )
        self.chat_inner = tk.Frame(self.chat_canvas, bg=COLOR_BG)

        self.chat_inner.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")),
        )
        self.chat_canvas.create_window((0, 0), window=self.chat_inner, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_scrollbar.pack(side="right", fill="y")

        # ===== BOTTOM BAR =====
        bottom = tk.Frame(self.main_frame, bg=COLOR_BG_HEADER, height=30)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)

        tk.Label(
            bottom, text=f"◆ {APP_NAME} by {APP_AUTHOR}",
            font=("Helvetica", 9), fg=COLOR_DIM, bg=COLOR_BG_HEADER, padx=10,
        ).pack(side="left")

        self.bottom_time = tk.Label(
            bottom, text="", font=("Helvetica", 9),
            fg=COLOR_DIM, bg=COLOR_BG_HEADER, padx=10,
        )
        self.bottom_time.pack(side="right")

        # Start clock
        self._update_clock()

    def _update_clock(self) -> None:
        """Update all time displays every second."""
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.seconds_label.configure(text=f":{now.strftime('%S')}")

        # Date with Spanish day names
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        day_name = days_es[now.weekday()]
        month_name = months_es[now.month - 1]
        self.date_label.configure(text=f"{now.day} de {month_name}, {now.year}")
        self.day_label.configure(text=day_name)

        self.bottom_time.configure(text=now.strftime("%H:%M:%S"))

        self.root.after(1000, self._update_clock)

    # ===== PUBLIC METHODS =====

    def add_user_message(self, text: str) -> None:
        """Show what the user said."""
        self._add_message(f"🎤  Tú:  {text}", COLOR_USER)
        self._scroll_to_bottom()

    def add_bot_message(self, text: str) -> None:
        """Show Arcanum's response."""
        self._add_message(f"◆  {APP_NAME}:  {text}", COLOR_BOT)
        self._scroll_to_bottom()

    def add_system_message(self, text: str) -> None:
        """Show a system/info message."""
        self._add_message(f"ℹ  {text}", COLOR_DIM)
        self._scroll_to_bottom()

    def set_status(self, text: str, color: str = COLOR_BOT) -> None:
        """Update the top status bar."""
        self.status_label.configure(text=text)
        self.status_dot.configure(fg=color)

    def set_listening(self, active: bool) -> None:
        """Show/hide the listening state with animation."""
        if active:
            self.listening_frame.configure(bg=COLOR_BG_CARD)
            self.listening_icon.configure(text="🔴", bg=COLOR_BG_CARD)
            self.listening_text.configure(
                text="Escuchando...", fg=COLOR_LISTENING, bg=COLOR_BG_CARD,
                font=("Helvetica", 18, "bold"),
            )
            self.set_status("Escuchando", COLOR_LISTENING)
            self._start_listening_animation()
        else:
            self._stop_listening_animation()
            self.listening_frame.configure(bg=COLOR_LISTENING_BG)
            self.listening_icon.configure(text="", bg=COLOR_LISTENING_BG)
            self.listening_text.configure(
                text=f'Di "{APP_NAME}" para activar',
                fg=COLOR_DIM, bg=COLOR_LISTENING_BG,
                font=("Helvetica", 16),
            )
            self.set_status("Listo", COLOR_BOT)

    def set_live_speech(self, text: str) -> None:
        """Update the listening area with what's being heard in real time."""
        display = text if text else "Escuchando..."
        self.listening_text.configure(
            text=f'🗣️  "{display}"',
            fg=COLOR_USER, bg=COLOR_BG_CARD,
            font=("Helvetica", 16, "bold"),
        )

    def set_processing(self) -> None:
        """Show that we're processing the command."""
        self.listening_icon.configure(text="⚙️")
        self.listening_text.configure(
            text="Procesando...", fg=COLOR_ACCENT,
            font=("Helvetica", 16, "bold"),
        )
        self.set_status("Procesando", COLOR_ACCENT)

    def set_not_understood(self) -> None:
        """Show that we didn't understand."""
        self.listening_icon.configure(text="❌")
        self.listening_text.configure(
            text="No te entendí, intenta de nuevo.",
            fg=COLOR_LISTENING, font=("Helvetica", 16, "bold"),
        )

    def update_weather(self, text: str) -> None:
        """Update the weather card."""
        self._weather_text = text
        self.weather_label.configure(text=text)

    def show_qr(self, image_path: str, wifi_text: str) -> None:
        """Show the WiFi QR code in the left panel."""
        try:
            img = Image.open(image_path)
            img = img.resize((180, 180), Image.LANCZOS)
            self._qr_photo = ImageTk.PhotoImage(img)
            self.qr_image_label.configure(image=self._qr_photo)
            self.qr_info_label.configure(text=wifi_text)
            self.qr_card.pack(fill="x", pady=5)
        except Exception as e:
            print(f"[UI] QR display error: {e}")

    def hide_qr(self) -> None:
        """Hide the WiFi QR code."""
        self.qr_card.pack_forget()

    def set_service_info(self, text: str) -> None:
        """Update the service info in top bar."""
        self.service_label.configure(text=text)

    def show_help(self) -> None:
        """Show the help overlay."""
        self.help_overlay.show()

    def hide_help(self) -> None:
        """Hide the help overlay."""
        self.help_overlay.hide()

    def clear_chat(self) -> None:
        """Clear all messages."""
        for widget in self.chat_inner.winfo_children():
            widget.destroy()

    def dismiss_screensaver(self) -> None:
        """Force dismiss the screensaver."""
        self.screensaver.hide()
        self._reset_screensaver_timer()

    def bring_to_front(self) -> None:
        """Bring the Arcanum window to the front."""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    # ===== PRIVATE METHODS =====

    def _add_message(self, text: str, color: str) -> None:
        """Add a message to the chat area."""
        timestamp = datetime.now().strftime("%H:%M")

        msg_frame = tk.Frame(self.chat_inner, bg=COLOR_BG, pady=3)
        msg_frame.pack(fill="x", anchor="w")

        time_lbl = tk.Label(
            msg_frame, text=timestamp, font=("Helvetica", 8),
            fg=COLOR_DIM, bg=COLOR_BG, anchor="w",
        )
        time_lbl.pack(anchor="w")

        text_lbl = tk.Label(
            msg_frame, text=text, font=("Helvetica", 13),
            fg=color, bg=COLOR_BG, anchor="w",
            wraplength=550, justify="left",
        )
        text_lbl.pack(anchor="w")

        sep = tk.Frame(msg_frame, bg="#112240", height=1)
        sep.pack(fill="x", pady=(3, 0))

    def _scroll_to_bottom(self) -> None:
        """Scroll to latest message."""
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _start_listening_animation(self) -> None:
        """Animate the listening indicator."""
        self._listening_dots = 0
        self._animate_listening()

    def _animate_listening(self) -> None:
        """Pulsing dot animation while listening."""
        if self.listening_icon.cget("text") != "🔴":
            return
        self._listening_dots = (self._listening_dots + 1) % 4
        dots = "." * self._listening_dots
        base_text = self.listening_text.cget("text")
        if base_text.startswith("Escuchando"):
            self.listening_text.configure(text=f"Escuchando{dots}")
        self._listening_anim_id = self.root.after(400, self._animate_listening)

    def _stop_listening_animation(self) -> None:
        """Stop the listening animation."""
        if self._listening_anim_id:
            self.root.after_cancel(self._listening_anim_id)
            self._listening_anim_id = None

    def _toggle_dev_mode(self, event=None) -> None:
        """Toggle fullscreen and cursor for development."""
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)
        self.root.config(cursor="" if is_full else "none")

    def _reset_screensaver_timer(self, event=None) -> None:
        """Reset the screensaver inactivity timer."""
        if self._screensaver_timer_id:
            self.root.after_cancel(self._screensaver_timer_id)

        if self.screensaver.active:
            self.screensaver.hide()

        self._screensaver_timer_id = self.root.after(
            SCREENSAVER_TIMEOUT * 1000, self._activate_screensaver
        )

    def _activate_screensaver(self) -> None:
        """Show screensaver after inactivity."""
        if not self.help_overlay.active:
            self.screensaver.show()
