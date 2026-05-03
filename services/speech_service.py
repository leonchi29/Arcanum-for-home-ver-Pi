"""
Speech recognition service for Arcanum.
USB microphone auto-detection on Raspberry Pi.
10-second timeout — cancels listening if no speech detected.
No external API keys required (uses Google free tier).
"""
import speech_recognition as sr
from config.settings import SPEECH_LANGUAGE, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT


class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic_index = self._find_usb_microphone()
        self.microphone = sr.Microphone(device_index=self.mic_index)

        # Very low energy threshold — MUST hear even quiet voices
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = False  # Don't auto-adjust up
        self.recognizer.pause_threshold = 1.0

        # Quick test: verify mic actually captures audio
        print("[Speech] Testing microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        # Force threshold low after calibration (calibration can set it too high)
        if self.recognizer.energy_threshold > 1000:
            print(f"[Speech] Threshold too high ({self.recognizer.energy_threshold}), forcing to 400")
            self.recognizer.energy_threshold = 400
        print(f"[Speech] Microphone ready. Energy threshold: {self.recognizer.energy_threshold}")

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
                          "Audio-Technica", "Maono", "Tonor", "Boya", "Jlab",
                          "Razer", "Logitech", "Corsair", "SteelSeries"]
        for i, name in enumerate(mic_list):
            if any(kw.lower() in name.lower() for kw in brand_keywords):
                print(f"[Speech] Found USB mic (brand): [{i}] {name}")
                return i

        # On Raspberry Pi, card 1+ is usually USB (card 0 is built-in audio)
        for i, name in enumerate(mic_list):
            if "card 1" in name.lower() or "hw:1" in name.lower():
                print(f"[Speech] Assuming USB mic: [{i}] {name}")
                return i

        # Fallback: look for any device with "mic" or "input" or "capture"
        for i, name in enumerate(mic_list):
            name_lower = name.lower()
            if any(kw in name_lower for kw in ["mic", "input", "capture", "record"]):
                print(f"[Speech] Found input device: [{i}] {name}")
                return i

        # Last resort: use first non-default device
        if len(mic_list) > 1:
            print(f"[Speech] Using device [1]: {mic_list[1]}")
            return 1

        print("[Speech] No USB mic found, using default device (index 0).")
        return 0

    def listen_for_command(self, timeout: int | None = None) -> str | None:
        """
        Listen for a voice command after wake word is detected.
        Returns recognized text or None on timeout/failure.
        10-second timeout by default — cancels if silence.
        """
        listen_timeout = timeout or LISTEN_TIMEOUT
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=listen_timeout,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )

            # Use Google Speech Recognition (free, supports es-CL)
            text = self.recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
            return text.lower().strip()

        except sr.WaitTimeoutError:
            print("[Speech] Timeout — no speech detected in {listen_timeout}s.")
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

    def recalibrate(self) -> None:
        """Re-calibrate microphone for ambient noise."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
