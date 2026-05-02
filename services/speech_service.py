"""
Wake word detection and speech recognition service.
Listens for "Arcanum" then captures the voice command.
Supports USB microphone auto-detection on Raspberry Pi.
"""
import speech_recognition as sr
from config.settings import SPEECH_LANGUAGE, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT


class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic_index = self._find_usb_microphone()
        self.microphone = sr.Microphone(device_index=self.mic_index)

        # Adjust for ambient noise on startup
        with self.microphone as source:
            print("[Speech] Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("[Speech] Microphone ready.")

    def _find_usb_microphone(self) -> int | None:
        """Auto-detect USB microphone. Returns device index or None for default."""
        print("[Speech] Searching for USB microphone...")
        mic_list = sr.Microphone.list_microphone_names()

        for i, name in enumerate(mic_list):
            print(f"  [{i}] {name}")

        # Look for USB mic keywords
        usb_keywords = ["usb", "USB", "external", "External"]
        for i, name in enumerate(mic_list):
            if any(kw in name for kw in usb_keywords):
                print(f"[Speech] Found USB mic: [{i}] {name}")
                return i

        # Look for common USB mic brands
        brand_keywords = ["Blue", "Yeti", "Fifine", "Rode", "HyperX", "Samson",
                          "Audio-Technica", "Maono", "Tonor", "Boya"]
        for i, name in enumerate(mic_list):
            if any(kw.lower() in name.lower() for kw in brand_keywords):
                print(f"[Speech] Found USB mic (brand): [{i}] {name}")
                return i

        # On Raspberry Pi, card 1+ is usually USB (card 0 is built-in audio)
        for i, name in enumerate(mic_list):
            if "card 1" in name.lower() or "hw:1" in name.lower():
                print(f"[Speech] Assuming USB mic: [{i}] {name}")
                return i

        print("[Speech] No USB mic found, using default device.")
        return None

    def listen_for_command(self) -> str | None:
        """Listen for a voice command after wake word is detected."""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )

            # Use Google Speech Recognition (free, supports es-CL)
            text = self.recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
            return text.lower().strip()

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[Speech] Recognition error: {e}")
            return None

    def listen_continuous(self) -> str | None:
        """
        Continuously listen for any speech (used for wake word fallback).
        Returns the recognized text or None.
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )

            text = self.recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
            return text.lower().strip()

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except sr.RequestError:
            return None
