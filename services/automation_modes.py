"""
Automation modes service for Arcanum.
Users configure named modes with sequences of voice commands.
Example: "Modo Santi" = [abre YouTube, busca Super Wings, reproduce primer resultado]
Example: "Modo Relax" = [radio Concierto, baja volumen]
"""
import os
import json
from config.settings import MODES_FILE


class AutomationModes:
    """Manages user-defined automation modes (macro sequences)."""

    def __init__(self):
        self._modes: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        """Load modes from disk."""
        if os.path.exists(MODES_FILE):
            try:
                with open(MODES_FILE, "r", encoding="utf-8") as f:
                    self._modes = json.load(f)
            except Exception:
                self._modes = {}

    def _save(self) -> None:
        """Save modes to disk."""
        try:
            with open(MODES_FILE, "w", encoding="utf-8") as f:
                json.dump(self._modes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Modes] Save error: {e}")

    def create_mode(self, name: str, actions: list[str]) -> str:
        """
        Create or overwrite a mode.
        name: mode name (e.g. "Santi", "Relax")
        actions: list of voice command strings to execute in sequence
        Returns confirmation message.
        """
        name_key = name.strip().lower()
        self._modes[name_key] = {
            "name": name.strip().title(),
            "actions": actions,
        }
        self._save()
        actions_text = ", ".join(f'"{a}"' for a in actions)
        return (
            f"Modo {name.strip().title()} creado con {len(actions)} acciones: "
            f"{actions_text}"
        )

    def get_mode(self, name: str) -> dict | None:
        """Get a mode by name. Returns {'name': str, 'actions': [str]} or None."""
        name_key = name.strip().lower()
        return self._modes.get(name_key)

    def delete_mode(self, name: str) -> str:
        """Delete a mode by name."""
        name_key = name.strip().lower()
        if name_key in self._modes:
            display_name = self._modes[name_key]["name"]
            del self._modes[name_key]
            self._save()
            return f"Modo {display_name} eliminado."
        return f"No existe un modo llamado {name}."

    def list_modes(self) -> str:
        """List all available modes with their actions."""
        if not self._modes:
            return "No hay modos configurados. Di 'configurar modo' para crear uno."

        lines = ["Modos disponibles:"]
        for key, mode in self._modes.items():
            actions_summary = ", ".join(mode["actions"][:3])
            if len(mode["actions"]) > 3:
                actions_summary += f" (+{len(mode['actions']) - 3} más)"
            lines.append(f"  • {mode['name']}: {actions_summary}")
        return "\n".join(lines)

    def get_mode_names(self) -> list[str]:
        """Get list of all mode names (lowercase keys)."""
        return list(self._modes.keys())

    def find_mode(self, command: str) -> dict | None:
        """
        Try to find a mode referenced in a command.
        E.g. "modo santi" → finds mode "santi"
        """
        cmd_lower = command.lower().strip()

        # Remove "modo" prefix
        for prefix in ["modo ", "activar modo ", "ejecutar modo ", "pon modo "]:
            if cmd_lower.startswith(prefix):
                name = cmd_lower[len(prefix):].strip()
                if name in self._modes:
                    return self._modes[name]

        # Direct match
        for key in self._modes:
            if key in cmd_lower:
                return self._modes[key]

        return None
