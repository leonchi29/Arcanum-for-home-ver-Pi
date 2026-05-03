"""
Wake word listener for Arcanum.
Uses Google Speech Recognition to detect "Arcanum" in continuous audio.
No external API keys or Porcupine needed.
"""
import speech_recognition as sr
from config.settings import WAKE_WORD, SPEECH_LANGUAGE


class WakeWordListener:
    """Listens for the wake word 'Arcanum' using speech recognition."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic_index = None
        self.microphone = None

    def initialize(self, mic_index: int | None = None) -> bool:
        """Initialize wake word detection with given mic index."""
        try:
            self.mic_index = mic_index
            self.microphone = sr.Microphone(device_index=mic_index)

            # Make wake word detection very sensitive
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.8

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"[WakeWord] Initialized. Energy threshold: {self.recognizer.energy_threshold}")
            print(f"[WakeWord] Listening for '{WAKE_WORD}'...")
            return True
        except Exception as e:
            print(f"[WakeWord] Initialization error: {e}")
            return False

    def wait_for_wake_word(self) -> bool:
        """
        Listen for the wake word. Returns True when detected.
        Blocks until wake word is heard or timeout.
        """
        if not self.microphone:
            return False

        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, timeout=10, phrase_time_limit=5,
                )

            text = self.recognizer.recognize_google(
                audio, language=SPEECH_LANGUAGE
            )
            text_lower = text.lower().strip()
            print(f"[WakeWord] Heard: '{text_lower}'")

            # Check if wake word is in the recognized text
            if WAKE_WORD in text_lower or "arcano" in text_lower or "arcana" in text_lower:
                print(f"[WakeWord] WAKE WORD DETECTED!")
                return True

            return False

        except sr.WaitTimeoutError:
            return False
        except sr.UnknownValueError:
            return False
        except sr.RequestError as e:
            print(f"[WakeWord] Network error (need internet): {e}")
            return False

    def cleanup(self):
        """Release resources."""
        pass  # No special cleanup needed for speech recognition
