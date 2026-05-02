"""
Screensaver for Arcanum.
Shows animated 'Arcanum by Carlos' text with current time and date.
Dark blue theme matching the app.
"""
import tkinter as tk
import math
from datetime import datetime
from config.settings import COLOR_BG, COLOR_ACCENT, COLOR_DIM, APP_AUTHOR, APP_NAME, HOME_LOCATION


class Screensaver:
    """Floating screensaver overlay on the main window."""

    SCREENSAVER_BG = "#060f1a"

    def __init__(self, parent_frame: tk.Frame):
        self.parent = parent_frame
        self.active = False
        self._frame = None
        self._canvas = None
        self._animation_id = None
        self._tick = 0

    def show(self) -> None:
        """Show the screensaver overlay."""
        if self.active:
            return

        self.active = True
        self._frame = tk.Frame(self.parent, bg=self.SCREENSAVER_BG)
        self._frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._canvas = tk.Canvas(
            self._frame, bg=self.SCREENSAVER_BG, highlightthickness=0
        )
        self._canvas.pack(fill="both", expand=True)

        self._tick = 0
        self._animate()

    def hide(self) -> None:
        """Hide the screensaver."""
        if not self.active:
            return

        self.active = False
        if self._animation_id:
            self.parent.after_cancel(self._animation_id)
            self._animation_id = None

        if self._frame:
            self._frame.destroy()
            self._frame = None

    def _animate(self) -> None:
        """Animation loop for the screensaver."""
        if not self.active or not self._canvas:
            return

        self._canvas.delete("all")
        self._tick += 1

        w = self._canvas.winfo_width() or 800
        h = self._canvas.winfo_height() or 480

        # Floating position using sine waves
        cx = w // 2 + int(math.sin(self._tick * 0.015) * (w * 0.2))
        cy = h // 2 + int(math.cos(self._tick * 0.012) * (h * 0.15))

        # Pulsing glow
        pulse = abs(math.sin(self._tick * 0.025))
        glow_color = f"#{0:02x}{int(180 * pulse):02x}{int(216 * (0.5 + pulse * 0.5)):02x}"

        # Background particles
        for i in range(12):
            angle = (self._tick * 0.03) + (i * math.pi / 6)
            radius = 120 + math.sin(self._tick * 0.02 + i) * 40
            px = cx + int(math.cos(angle) * radius)
            py = cy + int(math.sin(angle) * radius * 0.5) - 20
            r = 2 + int(pulse * 2)
            self._canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill=COLOR_ACCENT, outline="",
            )

        # Main title
        self._canvas.create_text(
            cx, cy - 40,
            text=APP_NAME.upper(),
            font=("Helvetica", 52, "bold"),
            fill=COLOR_ACCENT,
        )

        # Subtitle
        self._canvas.create_text(
            cx, cy + 20,
            text=f"by {APP_AUTHOR}",
            font=("Helvetica", 18),
            fill=COLOR_DIM,
        )

        # Current time (large)
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        # Spanish date
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        day_name = days_es[now.weekday()]
        month_name = months_es[now.month - 1]
        date_str = f"{day_name} {now.day} de {month_name}, {now.year}"

        self._canvas.create_text(
            cx, cy + 70,
            text=time_str,
            font=("Helvetica", 42, "bold"),
            fill=glow_color,
        )

        self._canvas.create_text(
            cx, cy + 115,
            text=date_str,
            font=("Helvetica", 14),
            fill=COLOR_DIM,
        )

        # Location
        self._canvas.create_text(
            cx, cy + 145,
            text=f"📍 {HOME_LOCATION}",
            font=("Helvetica", 12),
            fill="#3a5a7a",
        )

        self._animation_id = self.parent.after(50, self._animate)
