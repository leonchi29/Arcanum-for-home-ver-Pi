"""
Text-to-speech service for Arcanum.
Uses pyttsx3 for offline TTS on Raspberry Pi.
"""
import threading
import pyttsx3
from config.settings import TTS_RATE


class TTSService:
    def __init__(self):
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", TTS_RATE)

        # Try to set Spanish voice if available
        voices = self._engine.getProperty("voices")
        for voice in voices:
            if "spanish" in voice.name.lower() or "es" in voice.id.lower():
                self._engine.setProperty("voice", voice.id)
                break

        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        """Speak text aloud in a separate thread."""
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str) -> None:
        """Synchronous speech (runs in thread)."""
        with self._lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                print(f"[TTS] Error: {e}")

    def speak_and_wait(self, text: str) -> None:
        """Speak text and block until done."""
        self._speak_sync(text)
