"""
Premium help overlay for Arcanum.
Card-grid layout with category chips and command examples.
"""
import tkinter as tk
from config.settings import (
    COLOR_BG, COLOR_BG_CARD, COLOR_BG_HEADER, COLOR_BG_ELEVATED, COLOR_BORDER,
    COLOR_ACCENT, COLOR_ACCENT_2, COLOR_ACCENT_3,
    COLOR_TEXT, COLOR_TEXT_SOFT, COLOR_DIM,
    COMMAND_CATALOG, APP_NAME,
)


CATEGORY_ICONS = {
    "Música": "🎵",
    "Streaming": "📺",
    "Control": "🎛",
    "Navegación": "🧭",
    "Info": "ℹ",
    "Utilidades": "🔧",
    "Modos": "⚡",
    "Sistema": "⚙",
    "Diversión": "🎉",
    "Juegos": "🎲",
    "Conocimiento": "🧠",
    "Ambiente": "🌿",
    "Bienestar": "🧘",
    "Cocina": "🍳",
    "Notas": "📝",
    "Comunicación": "💬",
    "Identidad": "👤",
}

CATEGORY_COLORS = {
    "Música": "#a78bfa",
    "Streaming": "#22d3ee",
    "Control": "#06d6a0",
    "Navegación": "#fbbf24",
    "Info": "#60a5fa",
    "Utilidades": "#fb7185",
    "Modos": "#f472b6",
    "Sistema": "#94a3b8",
    "Diversión": "#facc15",
    "Juegos": "#34d399",
    "Conocimiento": "#818cf8",
    "Ambiente": "#4ade80",
    "Bienestar": "#f472b6",
    "Cocina": "#fb923c",
    "Notas": "#fcd34d",
    "Comunicación": "#38bdf8",
    "Identidad": "#c084fc",
}


class HelpOverlay:
    """Premium fullscreen overlay showing all commands."""

    def __init__(self, parent, font: str = "Helvetica"):
        self.parent = parent
        self.font = font
        self.active = False
        self._frame = None

    def show(self) -> None:
        if self.active:
            return
        self.active = True

        self._frame = tk.Frame(self.parent, bg=COLOR_BG)
        self._frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_header()
        self._build_content()

    def hide(self) -> None:
        if not self.active:
            return
        self.active = False
        if self._frame:
            self._frame.destroy()
            self._frame = None

    # ==========================================

    def _build_header(self) -> None:
        header = tk.Frame(self._frame, bg=COLOR_BG_HEADER, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=COLOR_BG_HEADER)
        inner.pack(fill="both", expand=True, padx=32, pady=16)

        # Left: title block
        title_block = tk.Frame(inner, bg=COLOR_BG_HEADER)
        title_block.pack(side="left", fill="y")

        tk.Label(
            title_block, text="GUÍA DE COMANDOS",
            font=(self.font, 9, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_BG_HEADER,
        ).pack(anchor="w")

        tk.Label(
            title_block, text=f"Todo lo que puede hacer {APP_NAME}",
            font=(self.font, 18, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_HEADER,
        ).pack(anchor="w")

        # Right: hint
        hint_block = tk.Frame(inner, bg=COLOR_BG_HEADER)
        hint_block.pack(side="right", fill="y")

        tk.Label(
            hint_block, text="✕  Di 'cierra ayuda' para volver",
            font=(self.font, 11), fg=COLOR_DIM, bg=COLOR_BG_HEADER,
        ).pack(side="right", anchor="e")

        tk.Label(
            hint_block, text="Habla con naturalidad — usa sinónimos",
            font=(self.font, 11), fg=COLOR_DIM, bg=COLOR_BG_HEADER,
        ).pack(side="right", anchor="e")

    def _build_content(self) -> None:
        # Scroll container
        container = tk.Frame(self._frame, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=16)

        canvas = tk.Canvas(container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            container, orient="vertical", command=canvas.yview,
            bg=COLOR_BG, troughcolor=COLOR_BG, activebackground=COLOR_ACCENT,
            bd=0, relief="flat", highlightthickness=0, width=10,
        )
        inner = tk.Frame(canvas, bg=COLOR_BG)

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(inner_id, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Group commands
        categories: dict[str, list] = {}
        for cmd in COMMAND_CATALOG:
            cat = cmd["category"]
            categories.setdefault(cat, []).append(cmd)

        # Render each category
        for category, commands in categories.items():
            self._render_category(inner, category, commands)

    def _render_category(self, parent, category: str, commands: list) -> None:
        icon = CATEGORY_ICONS.get(category, "•")
        accent = CATEGORY_COLORS.get(category, COLOR_ACCENT)

        # Category card
        cat_card = tk.Frame(
            parent, bg=COLOR_BG_CARD,
            highlightthickness=1, highlightbackground=COLOR_BORDER,
        )
        cat_card.pack(fill="x", pady=10, padx=4)

        # Header strip with accent
        header = tk.Frame(cat_card, bg=COLOR_BG_CARD)
        header.pack(fill="x", padx=20, pady=(16, 10))

        # Icon chip
        icon_chip = tk.Frame(header, bg=accent)
        icon_chip.pack(side="left", padx=(0, 12))
        tk.Label(
            icon_chip, text=icon, font=(self.font, 18),
            fg="#0a0e1a", bg=accent, padx=10, pady=4,
        ).pack()

        title_col = tk.Frame(header, bg=COLOR_BG_CARD)
        title_col.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_col, text=category.upper(),
            font=(self.font, 16, "bold"),
            fg=accent, bg=COLOR_BG_CARD, anchor="w",
        ).pack(fill="x")

        tk.Label(
            title_col, text=f"{len(commands)} comandos disponibles",
            font=(self.font, 10),
            fg=COLOR_DIM, bg=COLOR_BG_CARD, anchor="w",
        ).pack(fill="x")

        # Commands grid
        grid = tk.Frame(cat_card, bg=COLOR_BG_CARD)
        grid.pack(fill="x", padx=20, pady=(0, 18))

        for cmd in commands:
            self._render_command(grid, cmd, accent)

    def _render_command(self, parent, cmd: dict, accent: str) -> None:
        row = tk.Frame(
            parent, bg=COLOR_BG_ELEVATED,
            highlightthickness=1, highlightbackground=COLOR_BORDER,
        )
        row.pack(fill="x", pady=4)

        # Left accent bar
        bar = tk.Frame(row, bg=accent, width=3)
        bar.pack(side="left", fill="y")

        body = tk.Frame(row, bg=COLOR_BG_ELEVATED)
        body.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        # Command
        tk.Label(
            body, text=f'"{cmd["command"]}"',
            font=(self.font, 13, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG_ELEVATED, anchor="w",
        ).pack(fill="x")

        # Description
        tk.Label(
            body, text=cmd["description"],
            font=(self.font, 11),
            fg=COLOR_TEXT_SOFT, bg=COLOR_BG_ELEVATED,
            anchor="w", justify="left", wraplength=900,
        ).pack(fill="x", pady=(2, 4))

        # Example chip
        example_row = tk.Frame(body, bg=COLOR_BG_ELEVATED)
        example_row.pack(fill="x")

        tk.Label(
            example_row, text="EJEMPLO",
            font=(self.font, 8, "bold"),
            fg=accent, bg=COLOR_BG_ELEVATED,
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            example_row, text=cmd["example"],
            font=(self.font, 11, "italic"),
            fg=COLOR_DIM, bg=COLOR_BG_ELEVATED,
        ).pack(side="left")
