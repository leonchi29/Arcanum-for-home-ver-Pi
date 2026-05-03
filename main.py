#!/usr/bin/env python3
"""
Arcanum — Voice Assistant for Raspberry Pi 5
=============================================
Zero API keys. Voice enrollment. Automation modes.
On-screen keyboard. 10s listen timeout.
"""
import sys
import threading
import time
import tkinter as tk

from services.speech_service import SpeechService
from services.tts_service import TTSService
from services.command_router import (
    CommandRouter,
    SENTINEL_SHOW_HELP, SENTINEL_HIDE_HELP,
    SENTINEL_SHOW_QR, SENTINEL_HIDE_QR,
    SENTINEL_SHUTDOWN, SENTINEL_RESTART,
    SENTINEL_SHOW_KEYBOARD, SENTINEL_HIDE_KEYBOARD,
    SENTINEL_CONFIGURE_MODE, SENTINEL_LOGIN_PROMPT,
)
from services.wake_word_service import WakeWordListener
from services.audio_manager import AudioManager
from services.voice_enrollment import VoiceEnrollment
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
        self.enrollment = None
        self._service_was_active = False
        self._weather_update_interval = 600  # 10 minutes

    def start(self):
        """Initialize and start the assistant with GUI."""
        root = tk.Tk()
        self.window = AppWindow(root)
        self.window.add_system_message("Inicializando Arcanum...")

        self.running = True
        init_thread = threading.Thread(target=self._init_services, daemon=True)
        init_thread.start()

        root.protocol("WM_DELETE_WINDOW", self._shutdown)
        root.mainloop()

    def _init_services(self):
        """Initialize all services (runs in background thread)."""
        try:
            self._ui_msg("system", "Configurando micrófono USB...")
            self.speech = SpeechService()

            self._ui_msg("system", "Configurando voz...")
            self.tts = TTSService()

            self._ui_msg("system", "Configurando audio...")
            self.audio = AudioManager()

            self._ui_msg("system", "Configurando servicios...")
            self.router = CommandRouter(
                on_alarm_callback=self._on_alarm,
                prompt_callback=self._voice_prompt,
            )

            # Initialize enrollment
            self.enrollment = VoiceEnrollment()

            # Wake word listener (uses speech recognition, no API keys)
            self._ui_msg("system", "Configurando detección de voz...")
            self.wake_word = WakeWordListener()
            self.wake_word.initialize(mic_index=self.speech.mic_index)

            self._ui_msg("system", "✓ Todos los sistemas listos!")

            # Check if first run — enrollment needed
            if self.enrollment.needs_enrollment:
                self._run_enrollment()
            else:
                name = self.enrollment.active_user_name
                self._ui_status(f"Listo — Di 'Arcanum', {name}")
                self.tts.speak(f"Hola {name}! Arcanum listo. Dime Arcanum para activarme.")

            # Connect push-to-talk button
            self._safe_ui(lambda: self.window.set_talk_callback(self._on_talk_button))

            # Start weather updates
            weather_thread = threading.Thread(target=self._weather_loop, daemon=True)
            weather_thread.start()

            # Start listening loop
            self._main_loop()

        except Exception as e:
            self._ui_msg("system", f"Error de inicialización: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # VOICE ENROLLMENT (first run)
    # ============================================================

    def _run_enrollment(self):
        """First-run voice calibration: 7 phrases + ask name."""
        self._ui_msg("system", "🎙️ Primera vez — Configuración de voz")
        self.tts.speak_and_wait(
            "Hola! Soy Arcanum, tu asistente de voz. "
            "Vamos a configurar tu voz. Repite después de mí cada frase."
        )

        phrases = self.enrollment.get_enrollment_phrases()
        success_count = 0

        for i, phrase in enumerate(phrases, 1):
            self._ui_msg("bot", f"({i}/{len(phrases)}) Repite: \"{phrase}\"")
            self.tts.speak_and_wait(f"Repite: {phrase}")

            self._safe_ui(lambda: self.window.set_listening(True))
            heard = self.speech.listen_for_command(timeout=10)
            self._safe_ui(lambda: self.window.set_listening(False))

            if heard:
                self._ui_msg("user", heard)
                success_count += 1
                self._ui_msg("bot", "✓ Perfecto!")
                self.tts.speak_and_wait("Perfecto!")
            else:
                self._ui_msg("bot", "No te escuché, pero seguimos.")
                self.tts.speak_and_wait("No te escuché, pero seguimos.")

            time.sleep(0.5)

        # Ask name
        self._ui_msg("bot", "¿Cómo te llamas?")
        self.tts.speak_and_wait("Excelente! Ahora dime, ¿cómo te llamas?")

        self._safe_ui(lambda: self.window.set_listening(True))
        name = self.speech.listen_for_command(timeout=10)
        self._safe_ui(lambda: self.window.set_listening(False))

        if not name:
            name = "Usuario"
            self._ui_msg("bot", "No entendí tu nombre, te llamaré Usuario.")
            self.tts.speak_and_wait("No entendí tu nombre, te llamaré Usuario por ahora.")
        else:
            self._ui_msg("user", name)
            # Clean up name (remove common filler words)
            clean_name = name.strip().title()
            for filler in ["me llamo ", "mi nombre es ", "soy ", "yo soy "]:
                if clean_name.lower().startswith(filler):
                    clean_name = clean_name[len(filler):].strip().title()
            name = clean_name

        self.enrollment.complete_enrollment(name)
        user_name = self.enrollment.active_user_name

        self._ui_msg("bot", f"✓ Listo {user_name}! Tu voz está configurada.")
        self.tts.speak_and_wait(
            f"Perfecto {user_name}! Tu voz está configurada. "
            f"Di Arcanum cuando necesites algo."
        )
        self._ui_status(f"Listo — Di 'Arcanum', {user_name}")

    # ============================================================
    # MAIN LOOP
    # ============================================================

    def _main_loop(self):
        """Main loop — listen for wake word, then process commands."""
        while self.running:
            try:
                detected = self.wake_word.wait_for_wake_word()
                if detected:
                    self._on_wake_word()
            except Exception as e:
                print(f"[Main] Loop error: {e}")
                time.sleep(1)

    def _weather_loop(self):
        """Periodically update the weather display."""
        while self.running:
            try:
                weather_text = self.router.weather.get_weather()
                self._safe_ui(lambda: self.window.update_weather(weather_text))
            except Exception:
                pass
            time.sleep(self._weather_update_interval)

    def _on_talk_button(self):
        """Handle push-to-talk button press from GUI."""
        thread = threading.Thread(target=self._on_wake_word, daemon=True)
        thread.start()

    def _on_wake_word(self):
        """Handle wake word detection — mute services, show listening UI."""
        if self.router and self.router.web.is_active:
            self._service_was_active = True
            self.audio.mute()
            self.router.web.minimize_service()
            self.window.bring_to_front()
        elif self.router and self.router.radio.is_playing:
            self._service_was_active = True
            self.router.radio.set_volume(10)

        self._safe_ui(lambda: self.window.dismiss_screensaver())
        self._safe_ui(lambda: self.window.hide_help())
        self._safe_ui(lambda: self.window.set_listening(True))

        name = self.enrollment.active_user_name if self.enrollment else ""
        self.tts.speak_and_wait(f"Sí, {name}?" if name else "Sí?")
        self._listen_for_command()

    def _listen_for_command(self):
        """Listen for the command with 10s timeout."""
        self._safe_ui(lambda: self.window.set_listening(True))

        command = self.speech.listen_for_command(timeout=10)
        self._safe_ui(lambda: self.window.set_listening(False))

        if command:
            self._safe_ui(lambda: self.window.set_live_speech(command))
            time.sleep(0.5)
            self._safe_ui(lambda: self.window.set_processing())
            self._process(command)
        else:
            # 10s timeout — cancel and go back to idle
            self._safe_ui(lambda: self.window.set_not_understood())
            self._ui_msg("bot", "No escuché nada, volviendo a esperar.")
            self.tts.speak("No escuché nada.")
            time.sleep(1)
            self._safe_ui(lambda: self.window.set_listening(False))
            self._restore_service()

    def _voice_prompt(self, question: str) -> str | None:
        """Ask the user a follow-up question via voice. Returns answer or None."""
        self._ui_msg("bot", question)
        self.tts.speak_and_wait(question)
        self._safe_ui(lambda: self.window.set_listening(True))
        answer = self.speech.listen_for_command(timeout=10)
        self._safe_ui(lambda: self.window.set_listening(False))
        if answer:
            self._ui_msg("user", answer)
        return answer

    # ============================================================
    # PROCESS COMMAND
    # ============================================================

    def _process(self, command: str):
        """Process a voice command: show on screen, execute, respond."""
        self._ui_msg("user", command)

        response = self.router.process_command(command)

        # Handle special sentinel responses
        if response == SENTINEL_SHOW_HELP:
            self._safe_ui(lambda: self.window.show_help())
            self._ui_msg("bot", "Mostrando comandos disponibles.")
            self.tts.speak("Aquí tienes todos los comandos.")
            self._ui_status_ready()
            return

        if response == SENTINEL_HIDE_HELP:
            self._safe_ui(lambda: self.window.hide_help())
            self.tts.speak("Listo.")
            self._ui_status_ready()
            return

        if response.startswith(SENTINEL_SHOW_QR):
            parts = response.replace(SENTINEL_SHOW_QR, "").split("__|__")
            qr_path = parts[0]
            wifi_text = parts[1] if len(parts) > 1 else ""
            self._safe_ui(lambda: self.window.show_qr(qr_path, wifi_text))
            self._ui_msg("bot", f"QR del WiFi generado. {wifi_text}")
            self.tts.speak("Código QR del WiFi generado. Escanea con tu teléfono.")
            self._ui_status_ready()
            return

        if response == SENTINEL_HIDE_QR:
            self._safe_ui(lambda: self.window.hide_qr())
            self.tts.speak("Listo.")
            self._ui_status_ready()
            return

        if response == SENTINEL_SHUTDOWN:
            self._ui_msg("bot", "Apagando el sistema...")
            self.tts.speak_and_wait("Apagando. Hasta pronto!")
            self._shutdown()
            return

        if response == SENTINEL_RESTART:
            self._ui_msg("bot", "Reiniciando el sistema...")
            self.tts.speak_and_wait("Reiniciando. Un momento.")
            import subprocess
            subprocess.run(["sudo", "reboot"], check=False)
            return

        if response == SENTINEL_SHOW_KEYBOARD:
            self._safe_ui(lambda: self.window.show_keyboard())
            self._ui_msg("bot", "Teclado en pantalla activado.")
            self.tts.speak("Teclado en pantalla.")
            self._ui_status_ready()
            return

        if response == SENTINEL_HIDE_KEYBOARD:
            self._safe_ui(lambda: self.window.hide_keyboard())
            self.tts.speak("Teclado cerrado.")
            self._ui_status_ready()
            return

        if response == SENTINEL_CONFIGURE_MODE:
            self._configure_mode_flow()
            self._ui_status_ready()
            return

        if response.startswith(SENTINEL_LOGIN_PROMPT):
            service_key = response.replace(SENTINEL_LOGIN_PROMPT, "")
            self._login_flow(service_key)
            self._ui_status_ready()
            return

        # Normal response — personalize with user name
        if self.enrollment and not self.enrollment.needs_enrollment:
            # Add personalization to action responses
            action_intents = {"play_media", "open_spotify", "open_netflix", "open_youtube",
                              "open_disney", "radio", "recommend", "alarm", "timer"}
            from services.intents import detect_intent
            intent, _ = detect_intent(command)
            if intent in action_intents:
                response = self.enrollment.personalized_response(response)

        self._ui_msg("bot", response)
        self.tts.speak(response)

        # Update service info in UI
        if self.router.web.is_active:
            from config.settings import STREAMING_SERVICES
            svc = self.router.web.current_service
            name = STREAMING_SERVICES.get(svc, {}).get("name", svc)
            self._safe_ui(lambda: self.window.set_service_info(f"▶ {name}"))
        elif self.router.radio.is_playing:
            station = self.router.radio.current_station or ""
            self._safe_ui(lambda: self.window.set_service_info(f"📻 {station.title()}"))
        else:
            self._safe_ui(lambda: self.window.set_service_info(""))

        # Restore muted service
        is_close = any(kw in command for kw in ["cierra", "para", "stop", "apaga"])
        if self._service_was_active and not is_close:
            self._restore_service()
        self._service_was_active = False

        self._ui_status_ready()

    # ============================================================
    # MODE CONFIGURATION FLOW
    # ============================================================

    def _configure_mode_flow(self):
        """Interactive flow to create an automation mode via voice."""
        # Ask for mode name
        name = self._voice_prompt("¿Cómo se llama el modo?")
        if not name:
            self._ui_msg("bot", "No entendí el nombre. Cancelado.")
            self.tts.speak("No entendí. Cancelado.")
            return

        self._ui_msg("bot", f"Modo: {name.title()}")
        self.tts.speak_and_wait(
            f"Modo {name.title()}. Ahora dime las acciones una por una. "
            f"Cuando termines, di 'listo'."
        )

        actions = []
        max_actions = 10

        while len(actions) < max_actions:
            self._ui_msg("bot", f"Acción {len(actions) + 1} (o di 'listo' para terminar):")
            self._safe_ui(lambda: self.window.set_listening(True))
            action = self.speech.listen_for_command(timeout=10)
            self._safe_ui(lambda: self.window.set_listening(False))

            if not action:
                self.tts.speak("No te escuché. ¿Otra acción o di listo?")
                continue

            self._ui_msg("user", action)

            # Check if done
            if any(w in action.lower() for w in ["listo", "terminar", "fin", "ya", "eso es todo"]):
                break

            actions.append(action)
            self._ui_msg("bot", f"✓ Acción guardada: {action}")
            self.tts.speak_and_wait(f"Guardada. ¿Siguiente acción o di listo?")

        if not actions:
            self._ui_msg("bot", "No se agregaron acciones. Cancelado.")
            self.tts.speak("No se agregaron acciones. Cancelado.")
            return

        result = self.router.modes.create_mode(name, actions)
        self._ui_msg("bot", result)
        self.tts.speak(f"Modo {name.title()} creado con {len(actions)} acciones. "
                       f"Di 'modo {name}' para ejecutarlo.")

    # ============================================================
    # LOGIN FLOW
    # ============================================================

    def _login_flow(self, service_key: str):
        """Ask for credentials via voice and save them."""
        from config.settings import STREAMING_SERVICES
        service_name = STREAMING_SERVICES.get(service_key, {}).get("name", service_key)

        # Ask for username/email
        user = self._voice_prompt(f"¿Cuál es tu usuario o correo para {service_name}?")
        if not user:
            self._ui_msg("bot", "No entendí el usuario. Puedes usar el teclado en pantalla.")
            self.tts.speak("No entendí. Di 'teclado' para usar el teclado en pantalla.")
            return

        # Ask for password
        password = self._voice_prompt(f"¿Cuál es la contraseña para {service_name}?")
        if not password:
            self._ui_msg("bot", "No entendí la contraseña. Usa el teclado en pantalla.")
            self.tts.speak("No entendí. Di 'teclado' para usar el teclado en pantalla.")
            return

        # Save and autofill
        self.router.credentials.save_credentials(service_key, user, password)
        self.router.credentials.autofill_login(service_key, self.router.browser)

        self._ui_msg("bot", f"Credenciales guardadas e iniciando sesión en {service_name}.")
        self.tts.speak(f"Credenciales guardadas. Iniciando sesión en {service_name}.")

    # ============================================================
    # SERVICE RESTORE
    # ============================================================

    def _restore_service(self):
        """Restore the previously active service (unmute, bring back)."""
        if self.router.web.is_active:
            self.audio.unmute()
            self.router.web.restore_service()
        elif self.router.radio.is_playing:
            self.router.radio.set_volume(80)

    def _on_alarm(self, message: str):
        """Callback when an alarm/timer triggers."""
        self._safe_ui(lambda: self.window.dismiss_screensaver())
        self._ui_msg("system", f"⏰ {message}")
        self.tts.speak(message)

    # ============================================================
    # UI HELPERS
    # ============================================================

    def _ui_msg(self, msg_type: str, text: str):
        if msg_type == "user":
            self._safe_ui(lambda: self.window.add_user_message(text))
        elif msg_type == "bot":
            self._safe_ui(lambda: self.window.add_bot_message(text))
        else:
            self._safe_ui(lambda: self.window.add_system_message(text))

    def _ui_status(self, text: str):
        self._safe_ui(lambda: self.window.set_status(text))

    def _ui_status_ready(self):
        name = self.enrollment.active_user_name if self.enrollment else ""
        status = f"Listo — Di 'Arcanum', {name}" if name else "Listo — Di 'Arcanum'"
        self._ui_status(status)

    def _safe_ui(self, func):
        try:
            if self.window and self.window.root:
                self.window.root.after(0, func)
        except Exception:
            pass

    def _shutdown(self):
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
