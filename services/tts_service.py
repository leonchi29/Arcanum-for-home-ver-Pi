"""
Text-to-speech service for Arcanum.
Uses pyttsx3 for offline TTS on Raspberry Pi.
Falls back to espeak command if pyttsx3 fails.
"""
import subprocess
import threading
import os

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except Exception:
    PYTTSX3_AVAILABLE = False

from config.settings import TTS_RATE


class TTSService:
    def __init__(self):
        self._lock = threading.Lock()
        self._engine = None
        self._use_espeak = False

        if PYTTSX3_AVAILABLE:
            try:
                self._engine = pyttsx3.init(driverName="espeak")
                self._engine.setProperty("rate", TTS_RATE)

                # Try to set Spanish voice
                voices = self._engine.getProperty("voices")
                spanish_voice = None
                for voice in voices:
                    vid = voice.id.lower()
                    vname = voice.name.lower()
                    if "spanish" in vname or "es-cl" in vid or "es_cl" in vid:
                        spanish_voice = voice.id
                        break
                    elif "es" in vid and not spanish_voice:
                        spanish_voice = voice.id

                if spanish_voice:
                    self._engine.setProperty("voice", spanish_voice)
                # If no Spanish voice found, just use default — don't crash
            except Exception as e:
                print(f"[TTS] pyttsx3 init failed: {e}, using espeak directly")
                self._engine = None
                self._use_espeak = True
        else:
            self._use_espeak = True

        # Verify espeak is available as fallback
        if self._use_espeak:
            try:
                subprocess.run(["espeak", "--version"], capture_output=True, check=True)
            except Exception:
                print("[TTS] WARNING: Neither pyttsx3 nor espeak available!")

    def speak(self, text: str) -> None:
        """Speak text aloud in a separate thread."""
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str) -> None:
        """Synchronous speech (runs in thread)."""
        with self._lock:
            if self._use_espeak or self._engine is None:
                self._espeak_direct(text)
            else:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] pyttsx3 error: {e}, falling back to espeak")
                    self._espeak_direct(text)

    def _espeak_direct(self, text: str) -> None:
        """Use espeak command directly as fallback."""
        try:
            # -v es = Spanish voice, -s = speed
            subprocess.run(
                ["espeak", "-v", "es", "-s", str(TTS_RATE), text],
                capture_output=True, timeout=30,
            )
        except Exception as e:
            print(f"[TTS] espeak error: {e}")

    def speak_and_wait(self, text: str) -> None:
        """Speak text and block until done."""
        self._speak_sync(text)
