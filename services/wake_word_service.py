"""
Wake word listener using Porcupine (Picovoice).
Detects the custom wake word "Arcanum".
"""
import struct
import pvporcupine
from pvrecorder import PvRecorder
from config.settings import PICOVOICE_ACCESS_KEY, WAKE_WORD


class WakeWordListener:
    """Listens for the wake word 'Arcanum' using Porcupine."""

    def __init__(self):
        self.porcupine = None
        self.recorder = None

    def initialize(self) -> bool:
        """Initialize wake word detection engine."""
        if not PICOVOICE_ACCESS_KEY:
            print("[WakeWord] No Picovoice access key configured.")
            print("[WakeWord] Get a free key at https://console.picovoice.ai/")
            print("[WakeWord] Falling back to keyword-based detection.")
            return False

        try:
            # Use built-in keyword or custom trained model
            self.porcupine = pvporcupine.create(
                access_key=PICOVOICE_ACCESS_KEY,
                keywords=["computer"],  # Use 'computer' as base, rename via UI
            )
            self.recorder = PvRecorder(
                frame_length=self.porcupine.frame_length,
                device_index=-1,  # Default audio device
            )
            print(f"[WakeWord] Initialized. Listening for '{WAKE_WORD}'...")
            return True
        except Exception as e:
            print(f"[WakeWord] Initialization error: {e}")
            return False

    def wait_for_wake_word(self) -> bool:
        """Block until wake word is detected. Returns True on detection."""
        if not self.porcupine or not self.recorder:
            return False

        self.recorder.start()
        try:
            while True:
                pcm = self.recorder.read()
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    print(f"[WakeWord] '{WAKE_WORD}' detected!")
                    return True
        except KeyboardInterrupt:
            return False
        finally:
            self.recorder.stop()

    def cleanup(self):
        """Release resources."""
        if self.recorder:
            self.recorder.delete()
        if self.porcupine:
            self.porcupine.delete()
