"""
Alarm and timer service for Arcanum.
"""
import threading
import time
from datetime import datetime, timedelta


class AlarmService:
    def __init__(self, on_alarm_callback=None):
        self._alarms = []
        self._timers = []
        self._running = True
        self._callback = on_alarm_callback
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def set_alarm(self, hour: int, minute: int) -> str:
        """Set an alarm for a specific time today (or tomorrow if passed)."""
        now = datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if alarm_time <= now:
            alarm_time += timedelta(days=1)

        self._alarms.append(alarm_time)
        time_str = alarm_time.strftime("%H:%M")
        return f"Alarm set for {time_str}."

    def set_timer(self, minutes: int) -> str:
        """Set a countdown timer."""
        end_time = datetime.now() + timedelta(minutes=minutes)
        self._timers.append(end_time)
        return f"Timer set for {minutes} minutes."

    def get_active_alarms(self) -> list[str]:
        """Return list of active alarms as formatted strings."""
        now = datetime.now()
        self._alarms = [a for a in self._alarms if a > now]
        return [a.strftime("%H:%M") for a in self._alarms]

    def cancel_alarms(self) -> str:
        """Cancel all alarms and timers."""
        self._alarms.clear()
        self._timers.clear()
        return "All alarms and timers cancelled."

    def _check_loop(self):
        """Background loop checking for triggered alarms/timers."""
        while self._running:
            now = datetime.now()
            triggered = []

            for alarm in self._alarms[:]:
                if now >= alarm:
                    triggered.append(f"Alarm! It's {alarm.strftime('%H:%M')}.")
                    self._alarms.remove(alarm)

            for timer in self._timers[:]:
                if now >= timer:
                    triggered.append("Timer finished!")
                    self._timers.remove(timer)

            for msg in triggered:
                if self._callback:
                    self._callback(msg)

            time.sleep(5)

    def stop(self):
        """Stop the alarm check loop."""
        self._running = False
