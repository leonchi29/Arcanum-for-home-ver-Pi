"""
Custom widgets for Arcanum's premium UI.
Rounded cards, gradient backgrounds, animated buttons.
"""
import tkinter as tk


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend(c1: str, c2: str, t: float) -> str:
    """Blend two hex colors. t=0 returns c1, t=1 returns c2."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex((r, g, b))


class RoundedCard(tk.Canvas):
    """A canvas-based card with rounded corners and optional gradient."""

    def __init__(self, parent, *, bg_outer: str, bg_card: str, border: str,
                 radius: int = 18, padding: int = 22, height: int = 0,
                 accent: str | None = None, **kwargs):
        super().__init__(
            parent, bg=bg_outer, highlightthickness=0, bd=0,
            height=height if height else None, **kwargs,
        )
        self._bg_outer = bg_outer
        self._bg_card = bg_card
        self._border = border
        self._radius = radius
        self._padding = padding
        self._accent = accent

        # Inner Frame for content
        self.body = tk.Frame(self, bg=bg_card)
        self._body_id = self.create_window(
            padding, padding, anchor="nw", window=self.body,
        )

        self.bind("<Configure>", self._redraw)

    def set_accent(self, color: str | None) -> None:
        self._accent = color
        self._redraw()

    def _redraw(self, event=None) -> None:
        self.delete("bg")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return

        r = self._radius
        # Card background (rounded rectangle approximated with arcs + rectangles)
        self._rounded_rect(0, 0, w, h, r, fill=self._bg_card,
                           outline=self._accent or self._border, width=2 if self._accent else 1)

        # Resize body
        self.itemconfig(self._body_id, width=w - 2 * self._padding,
                        height=h - 2 * self._padding)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        # Use polygon for smoother result
        pts = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        self.create_polygon(pts, smooth=True, tags="bg", **kw)


class CircleButton(tk.Canvas):
    """A round flat button with hover/press states."""

    def __init__(self, parent, *, size: int, bg: str, fg: str,
                 active_bg: str, text: str, font: tuple, command=None,
                 outer_bg: str = "#000000"):
        super().__init__(
            parent, width=size, height=size, bg=outer_bg,
            highlightthickness=0, bd=0,
        )
        self._size = size
        self._bg = bg
        self._fg = fg
        self._active_bg = active_bg
        self._command = command
        self._is_hover = False
        self._is_pressed = False

        self._circle = self.create_oval(2, 2, size - 2, size - 2,
                                        fill=bg, outline="")
        self._label = self.create_text(size // 2, size // 2,
                                       text=text, fill=fg, font=font)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.config(cursor="hand2")

    def _on_enter(self, _e):
        self._is_hover = True
        if not self._is_pressed:
            self.itemconfig(self._circle, fill=self._active_bg)

    def _on_leave(self, _e):
        self._is_hover = False
        if not self._is_pressed:
            self.itemconfig(self._circle, fill=self._bg)

    def _on_press(self, _e):
        self._is_pressed = True
        self.itemconfig(self._circle, fill=self._active_bg)

    def _on_release(self, _e):
        self._is_pressed = False
        self.itemconfig(self._circle, fill=self._active_bg if self._is_hover else self._bg)
        if self._command:
            self._command()

    def set_text(self, text: str) -> None:
        self.itemconfig(self._label, text=text)

    def set_color(self, bg: str, active_bg: str) -> None:
        self._bg = bg
        self._active_bg = active_bg
        self.itemconfig(self._circle, fill=bg)


class WaveformAnimation(tk.Canvas):
    """Animated audio waveform-style bars for listening state."""

    def __init__(self, parent, *, width: int, height: int, bg: str,
                 color: str, num_bars: int = 5):
        super().__init__(
            parent, width=width, height=height, bg=bg,
            highlightthickness=0, bd=0,
        )
        self._width = width
        self._height = height
        self._color = color
        self._num_bars = num_bars
        self._tick = 0
        self._anim_id = None
        self._running = False
        self._bars = []
        self._setup_bars()

    def _setup_bars(self):
        self.delete("bar")
        bar_w = max(4, (self._width - (self._num_bars + 1) * 6) // self._num_bars)
        gap = 6
        total = self._num_bars * bar_w + (self._num_bars - 1) * gap
        start_x = (self._width - total) // 2
        cy = self._height // 2

        self._bars = []
        for i in range(self._num_bars):
            x = start_x + i * (bar_w + gap)
            bar = self.create_rectangle(
                x, cy - 4, x + bar_w, cy + 4,
                fill=self._color, outline="", tags="bar",
            )
            self._bars.append((bar, x, bar_w))

    def start(self):
        if self._running:
            return
        self._running = True
        self._animate()

    def stop(self):
        self._running = False
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        # Reset to flat bars
        cy = self._height // 2
        for bar, x, bw in self._bars:
            self.coords(bar, x, cy - 3, x + bw, cy + 3)

    def set_color(self, color: str) -> None:
        self._color = color
        for bar, _, _ in self._bars:
            self.itemconfig(bar, fill=color)

    def _animate(self):
        if not self._running:
            return
        import math
        self._tick += 1
        cy = self._height // 2
        for i, (bar, x, bw) in enumerate(self._bars):
            phase = (self._tick * 0.18) + (i * 0.7)
            amplitude = (math.sin(phase) + 1) / 2  # 0..1
            amplitude = 0.2 + amplitude * 0.8  # 0.2..1.0
            half = int((self._height * 0.42) * amplitude)
            self.coords(bar, x, cy - half, x + bw, cy + half)
        self._anim_id = self.after(60, self._animate)
