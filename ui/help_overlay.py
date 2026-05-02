"""
Help overlay screen for Arcanum.
Shows all available commands grouped by category.
"""
import tkinter as tk
from config.settings import (
    COLOR_BG, COLOR_BG_CARD, COLOR_ACCENT, COLOR_TEXT, COLOR_DIM,
    COLOR_HELP_BG, COMMAND_CATALOG, APP_NAME,
)


class HelpOverlay:
    """Fullscreen overlay showing command reference."""

    def __init__(self, parent_frame: tk.Frame):
        self.parent = parent_frame
        self.active = False
        self._frame = None

    def show(self) -> None:
        """Show the help overlay."""
        if self.active:
            return

        self.active = True
        self._frame = tk.Frame(self.parent, bg=COLOR_HELP_BG)
        self._frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Header
        header = tk.Frame(self._frame, bg=COLOR_BG_CARD, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text=f"📋  {APP_NAME} — Comandos Disponibles",
            font=("Helvetica", 20, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
            anchor="w", padx=20,
        ).pack(side="left", fill="y")

        tk.Label(
            header, text="Di 'Arcanum, cierra ayuda' para volver",
            font=("Helvetica", 12), fg=COLOR_DIM, bg=COLOR_BG_CARD,
            anchor="e", padx=20,
        ).pack(side="right", fill="y")

        # Scrollable content
        container = tk.Frame(self._frame, bg=COLOR_HELP_BG)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container, bg=COLOR_HELP_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLOR_HELP_BG)

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Group commands by category
        categories = {}
        for cmd in COMMAND_CATALOG:
            cat = cmd["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd)

        # Category icons
        cat_icons = {
            "Música": "🎵",
            "Streaming": "📺",
            "Control": "🎛️",
            "Info": "ℹ️",
            "Utilidades": "🔧",
            "Sistema": "⚙️",
        }

        for category, commands in categories.items():
            icon = cat_icons.get(category, "•")

            # Category header
            cat_frame = tk.Frame(inner, bg=COLOR_BG_CARD, pady=5)
            cat_frame.pack(fill="x", padx=10, pady=(10, 2))

            tk.Label(
                cat_frame, text=f"  {icon}  {category}",
                font=("Helvetica", 16, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG_CARD,
                anchor="w", padx=10, pady=5,
            ).pack(fill="x")

            # Commands in this category
            for cmd in commands:
                row = tk.Frame(inner, bg=COLOR_HELP_BG, pady=2)
                row.pack(fill="x", padx=20)

                # Command name
                tk.Label(
                    row, text=f'  "{cmd["command"]}"',
                    font=("Helvetica", 13, "bold"), fg=COLOR_TEXT, bg=COLOR_HELP_BG,
                    anchor="w",
                ).pack(anchor="w")

                # Description
                tk.Label(
                    row, text=f"    {cmd['description']}",
                    font=("Helvetica", 11), fg=COLOR_DIM, bg=COLOR_HELP_BG,
                    anchor="w",
                ).pack(anchor="w")

                # Example
                tk.Label(
                    row, text=f'    Ejemplo: {cmd["example"]}',
                    font=("Helvetica", 10, "italic"), fg="#3a8a5a", bg=COLOR_HELP_BG,
                    anchor="w",
                ).pack(anchor="w")

    def hide(self) -> None:
        """Hide the help overlay."""
        if not self.active:
            return
        self.active = False
        if self._frame:
            self._frame.destroy()
            self._frame = None

    def toggle(self) -> None:
        """Toggle help overlay."""
        if self.active:
            self.hide()
        else:
            self.show()
