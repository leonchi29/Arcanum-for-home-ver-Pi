"""
Premium screensaver for Arcanum.
Cinematic dark canvas with floating particles, glowing time, and aurora bands.
"""
import tkinter as tk
import math
import random
from datetime import datetime
from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_ACCENT_2, COLOR_ACCENT_3,
    COLOR_DIM, COLOR_TEXT, COLOR_TEXT_SOFT,
    APP_AUTHOR, APP_NAME, HOME_LOCATION,
)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "r", "color", "life")

    def __init__(self, w, h, color):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.4, -0.1)
        self.r = random.uniform(1, 2.6)
        self.color = color
        self.life = random.uniform(0.6, 1.0)


class Screensaver:
    """Premium screensaver overlay with particles and glow."""

    SCREENSAVER_BG = "#04060d"

    def __init__(self, parent, font: str = "Helvetica"):
        self.parent = parent
        self.font = font
        self.active = False
        self._frame = None
        self._canvas = None
        self._anim_id = None
        self._tick = 0
        self._particles: list[Particle] = []

    def show(self) -> None:
        if self.active:
            return
        self.active = True

        self._frame = tk.Frame(self.parent, bg=self.SCREENSAVER_BG)
        self._frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._canvas = tk.Canvas(
            self._frame, bg=self.SCREENSAVER_BG, highlightthickness=0,
        )
        self._canvas.pack(fill="both", expand=True)

        self._tick = 0
        self._init_particles()
        self._animate()

    def hide(self) -> None:
        if not self.active:
            return
        self.active = False
        if self._anim_id:
            self.parent.after_cancel(self._anim_id)
            self._anim_id = None
        if self._frame:
            self._frame.destroy()
            self._frame = None

    def _init_particles(self):
        w = self.parent.winfo_width() or 1200
        h = self.parent.winfo_height() or 700
        accents = [COLOR_ACCENT, COLOR_ACCENT_2, COLOR_ACCENT_3]
        self._particles = [
            Particle(w, h, random.choice(accents)) for _ in range(60)
        ]

    def _animate(self):
        if not self.active or not self._canvas:
            return

        self._tick += 1
        self._canvas.delete("all")

        w = self._canvas.winfo_width() or 1200
        h = self._canvas.winfo_height() or 700
        cx, cy = w // 2, h // 2

        # Aurora bands (concentric soft circles)
        pulse = (math.sin(self._tick * 0.018) + 1) / 2  # 0..1
        for i, (color, base_r) in enumerate([
            (COLOR_ACCENT, 380),
            (COLOR_ACCENT_3, 280),
            (COLOR_ACCENT_2, 200),
        ]):
            r = base_r + int(pulse * 30) + i * 6
            self._canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=color, width=1, stipple="gray25",
            )

        # Particles drift upward
        for p in self._particles:
            p.x += p.vx
            p.y += p.vy
            if p.y < -10:
                p.y = h + 10
                p.x = random.uniform(0, w)
            if p.x < -10:
                p.x = w + 10
            elif p.x > w + 10:
                p.x = -10
            self._canvas.create_oval(
                p.x - p.r, p.y - p.r, p.x + p.r, p.y + p.r,
                fill=p.color, outline="",
            )

        # Center orb (logo)
        orb_r = 56 + int(pulse * 6)
        for i in range(4, 0, -1):
            rr = orb_r + i * 8
            shade = ["#1a1538", "#241a4a", "#2e1f5c", "#382470"][i - 1]
            self._canvas.create_oval(
                cx - rr, cy - 130 - rr, cx + rr, cy - 130 + rr,
                fill=shade, outline="",
            )
        # Inner gradient
        self._canvas.create_oval(
            cx - orb_r, cy - 130 - orb_r,
            cx + orb_r, cy - 130 + orb_r,
            fill=COLOR_ACCENT, outline="",
        )
        self._canvas.create_oval(
            cx - orb_r // 2, cy - 130 - orb_r // 2,
            cx + orb_r // 2, cy - 130 + orb_r // 2,
            fill=COLOR_ACCENT_3, outline="",
        )
        self._canvas.create_oval(
            cx - 6, cy - 130 - 6, cx + 6, cy - 130 + 6,
            fill="#ffffff", outline="",
        )

        # APP NAME with subtle glow
        self._canvas.create_text(
            cx + 2, cy - 30 + 2,
            text=APP_NAME.upper(),
            font=(self.font, 64, "bold"),
            fill="#1a1538",
        )
        self._canvas.create_text(
            cx, cy - 30,
            text=APP_NAME.upper(),
            font=(self.font, 64, "bold"),
            fill=COLOR_TEXT,
        )

        # Subtitle
        self._canvas.create_text(
            cx, cy + 22,
            text=f"by {APP_AUTHOR}",
            font=(self.font, 14, "bold"),
            fill=COLOR_ACCENT,
        )

        # Time block
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        sec_str = now.strftime("%S")

        self._canvas.create_text(
            cx, cy + 110,
            text=time_str,
            font=(self.font, 96, "bold"),
            fill=COLOR_TEXT,
        )
        self._canvas.create_text(
            cx + 130, cy + 95,
            text=sec_str,
            font=(self.font, 22, "bold"),
            fill=COLOR_ACCENT_3,
            anchor="w",
        )

        # Date
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves",
                   "Viernes", "Sábado", "Domingo"]
        months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre",
                     "Noviembre", "Diciembre"]
        day_name = days_es[now.weekday()]
        month_name = months_es[now.month - 1]
        date_str = f"{day_name}, {now.day} de {month_name} {now.year}"

        self._canvas.create_text(
            cx, cy + 188,
            text=date_str.upper(),
            font=(self.font, 13, "bold"),
            fill=COLOR_TEXT_SOFT,
        )

        # Location bottom
        self._canvas.create_text(
            cx, h - 60,
            text=f"📍  {HOME_LOCATION}",
            font=(self.font, 11),
            fill=COLOR_DIM,
        )

        # Hint
        self._canvas.create_text(
            cx, h - 35,
            text=f'Toca o di "{APP_NAME}" para activar',
            font=(self.font, 10),
            fill=COLOR_DIM,
        )

        self._anim_id = self.parent.after(50, self._animate)
