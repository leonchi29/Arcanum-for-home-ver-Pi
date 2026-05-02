#!/usr/bin/env python3
"""
Arcanum - Voice Assistant for Raspberry Pi 5
=============================================
Main entry point with fullscreen GUI.
Listens for wake word "Arcanum", shows conversation on screen,
speaks responses via TTS, and manages streaming services.

Commands:
  - "Arcanum, reproduce [song]"       -> Spotify Web
  - "Arcanum, radio [station]"        -> Chilean FM radio
  - "Arcanum, modo comer"             -> Zapping TV news
  - "Arcanum, netflix / disney / youtube" -> Open streaming
  - "Arcanum, qué hora es"            -> Tell current time
  - "Arcanum, clima"                  -> Weather info
  - "Arcanum, alarma [HH:MM]"        -> Set alarm
  - "Arcanum, busca [topic]"          -> Search internet
  - "Arcanum, disponible"             -> List services
  - "Arcanum, cierra"                 -> Close current service
  - "Arcanum, para todo"              -> Stop everything
"""
import sys
import threading
import tkinter as tk
from services.speech_service import SpeechService
from services.tts_service import TTSService
from services.command_router import CommandRouter
from services.wake_word_service import WakeWordListener
from services.audio_manager import AudioManager
from ui.app_window import AppWindow


class Arcanum:
    def __init__(self):
        self.running = False
        self.speech = None
        self.tts = None
        self.router = None
        self.wake_word = None
        self.audio = None
        self.window = None
        self.use_porcupine = False
        self._service_was_active = False

    def start(self):
        """Initialize and start the assistant with GUI."""
        # Create Tkinter root
        root = tk.Tk()

        # Build GUI
        self.window = AppWindow(root)
        self.window.add_system_message("Initializing Arcanum...")

        # Initialize services in a background thread (so GUI doesn't freeze)
        self.running = True
        init_thread = threading.Thread(target=self._init_services, daemon=True)
        init_thread.start()

        # Handle window close
        root.protocol("WM_DELETE_WINDOW", self._shutdown)

        # Start Tkinter main loop
        root.mainloop()

    def _init_services(self):
        """Initialize all services (runs in background thread)."""
        try:
            self._ui_msg("system", "Setting up USB microphone...")
            self.speech = SpeechService()

            self._ui_msg("system", "Setting up text-to-speech...")
            self.tts = TTSService()

            self._ui_msg("system", "Setting up audio manager...")
            self.audio = AudioManager()

            self._ui_msg("system", "Setting up command router...")
            self.router = CommandRouter(on_alarm_callback=self._on_alarm)

            # Try Porcupine wake word
            self._ui_msg("system", "Setting up wake word detection...")
            self.wake_word = WakeWordListener()
            self.use_porcupine = self.wake_word.initialize()

            if not self.use_porcupine:
                self._ui_msg("system", "Using speech recognition for wake word (no Picovoice key).")

            self._ui_msg("system", "✓ All systems ready!")
            self._ui_status("Ready - Say 'Arcanum'")
            self.tts.speak("Arcanum listo. Dime Arcanum para activarme.")

            # Start listening loop
            self._main_loop()

        except Exception as e:
            self._ui_msg("system", f"Initialization error: {e}")

    def _main_loop(self):
        """Main loop - listen for wake word, then process commands."""
        while self.running:
            try:
                if self.use_porcupine:
                    detected = self.wake_word.wait_for_wake_word()
                    if detected:
                        self._on_wake_word()
                else:
                    self._listen_with_speech_fallback()

            except Exception as e:
                self._ui_msg("system", f"Error: {e}")
                import time
                time.sleep(1)

    def _listen_with_speech_fallback(self):
        """Fallback: listen via speech recognition for wake word + command."""
        text = self.speech.listen_continuous()
        if text and "arcanum" in text:
            # Remove wake word from text
            command = text.replace("arcanum", "").strip()
            if command:
                self._on_wake_word()
                self._process(command)
            else:
                self._on_wake_word()
                self._listen_for_command()

    def _on_wake_word(self):
        """Handle wake word detection."""
        # If a service is running, mute it and bring Arcanum to front
        if self.router and self.router.web.is_active:
            self._service_was_active = True
            self.audio.mute()
            self.router.web.minimize_service()
            self.window.bring_to_front()
        elif self.router and self.router.radio.is_playing:
            self._service_was_active = True
            self.router.radio.set_volume(10)

        # Dismiss screensaver
        self._safe_ui(lambda: self.window.dismiss_screensaver())
        self._safe_ui(lambda: self.window.set_listening(True))

        self.tts.speak("Sí?")
        self._listen_for_command()

    def _listen_for_command(self):
        """Listen for the actual command after wake word."""
        command = self.speech.listen_for_command()
        self._safe_ui(lambda: self.window.set_listening(False))

        if command:
            self._process(command)
        else:
            self._ui_msg("bot", "I didn't hear anything. Try again.")
            self.tts.speak("No escuché nada.")
            self._restore_service()

    def _process(self, command: str):
        """Process a voice command: show on screen, execute, respond."""
        # Show what the user said
        self._ui_msg("user", command)

        # Route the command
        response = self.router.process_command(command)

        # Show and speak the response
        self._ui_msg("bot", response)
        self.tts.speak(response)

        # Update service info in UI
        if self.router.web.is_active:
            from config.settings import STREAMING_SERVICES
            svc = self.router.web.current_service
            name = STREAMING_SERVICES.get(svc, {}).get("name", svc)
            self._safe_ui(lambda: self.window.set_service_info(f"Active: {name}"))
        elif self.router.radio.is_playing:
            station = self.router.radio.current_station or ""
            self._safe_ui(lambda: self.window.set_service_info(f"Radio: {station.title()}"))
        else:
            self._safe_ui(lambda: self.window.set_service_info(""))

        # If we muted a service, check if we should restore it
        # Only restore if the command didn't close/stop it
        is_close = any(kw in command for kw in ["cierra", "para", "stop", "apaga"])
        if self._service_was_active and not is_close:
            self._restore_service()
        self._service_was_active = False

        self._ui_status("Ready - Say 'Arcanum'")

    def _restore_service(self):
        """Restore the previously active service (unmute, bring back)."""
        if self.router.web.is_active:
            self.audio.unmute()
            self.router.web.restore_service()
        elif self.router.radio.is_playing:
            self.router.radio.set_volume(80)

    def _on_alarm(self, message: str):
        """Callback when an alarm/timer triggers."""
        self._ui_msg("system", f"⏰ {message}")
        self.tts.speak(message)

    # --- Thread-safe UI helpers ---

    def _ui_msg(self, msg_type: str, text: str):
        """Add a message to the UI from any thread."""
        if msg_type == "user":
            self._safe_ui(lambda: self.window.add_user_message(text))
        elif msg_type == "bot":
            self._safe_ui(lambda: self.window.add_bot_message(text))
        else:
            self._safe_ui(lambda: self.window.add_system_message(text))

    def _ui_status(self, text: str):
        """Update status from any thread."""
        self._safe_ui(lambda: self.window.set_status(text))

    def _safe_ui(self, func):
        """Run a function on the Tkinter main thread."""
        try:
            if self.window and self.window.root:
                self.window.root.after(0, func)
        except Exception:
            pass

    def _shutdown(self):
        """Clean up resources and exit."""
        self.running = False
        if self.wake_word:
            self.wake_word.cleanup()
        if self.router:
            self.router.cleanup()
        if self.window and self.window.root:
            self.window.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = Arcanum()
    app.start()
