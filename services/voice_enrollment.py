"""
Voice enrollment service for Arcanum.
First-run calibration: user repeats 7 phrases, then says their name.
Stores user profiles for personalized responses.
Supports multiple users.
"""
import os
import json
from config.settings import PROFILES_FILE, ENROLLMENT_PHRASES


class VoiceEnrollment:
    """Manages user profiles and first-run voice calibration."""

    def __init__(self):
        self._profiles: list[dict] = []
        self._active_user: str | None = None
        self._load()

    def _load(self) -> None:
        """Load profiles from disk."""
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._profiles = data.get("profiles", [])
                self._active_user = data.get("active_user")
                # Validate — if profiles is empty or corrupted, reset
                if not self._profiles or not isinstance(self._profiles, list):
                    self._profiles = []
                    self._active_user = None
            except Exception:
                self._profiles = []
                self._active_user = None

    def _save(self) -> None:
        """Save profiles to disk."""
        try:
            data = {
                "profiles": self._profiles,
                "active_user": self._active_user,
            }
            with open(PROFILES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Enrollment] Save error: {e}")

    @property
    def needs_enrollment(self) -> bool:
        """True if no users have been enrolled yet."""
        return len(self._profiles) == 0

    @property
    def active_user_name(self) -> str:
        """Current active user name, or 'Usuario' as fallback."""
        return self._active_user or "Usuario"

    @property
    def profiles(self) -> list[dict]:
        """All enrolled profiles."""
        return self._profiles

    def get_enrollment_phrases(self) -> list[str]:
        """Get the 7 calibration phrases the user must repeat."""
        return ENROLLMENT_PHRASES

    def complete_enrollment(self, name: str) -> None:
        """
        Complete enrollment for a user.
        Called after the user has repeated all 7 phrases successfully.
        """
        name = name.strip().title()

        # Check if user already exists
        for profile in self._profiles:
            if profile["name"].lower() == name.lower():
                self._active_user = profile["name"]
                self._save()
                return

        profile = {
            "name": name,
            "enrolled": True,
        }
        self._profiles.append(profile)
        self._active_user = name
        self._save()

    def set_active_user(self, name: str) -> bool:
        """Set the active user by name."""
        for profile in self._profiles:
            if profile["name"].lower() == name.lower():
                self._active_user = profile["name"]
                self._save()
                return True
        return False

    def get_user_names(self) -> list[str]:
        """Get list of all enrolled user names."""
        return [p["name"] for p in self._profiles]

    def remove_user(self, name: str) -> bool:
        """Remove a user profile."""
        for i, profile in enumerate(self._profiles):
            if profile["name"].lower() == name.lower():
                self._profiles.pop(i)
                if self._active_user and self._active_user.lower() == name.lower():
                    self._active_user = (
                        self._profiles[0]["name"] if self._profiles else None
                    )
                self._save()
                return True
        return False

    def personalized_response(self, base_response: str) -> str:
        """
        Add personalization to a response.
        E.g.: "Claro Carlos, aquí tienes" instead of just "Claro".
        """
        name = self.active_user_name
        # Add name naturally into short responses
        prefixes = [
            f"Claro {name}, ",
            f"Listo {name}, ",
            f"Dale {name}, ",
            f"Por supuesto {name}, ",
        ]
        import random
        prefix = random.choice(prefixes)
        return f"{prefix}{base_response[0].lower()}{base_response[1:]}"
