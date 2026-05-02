"""
Chilean radio streaming service using VLC.
"""
import vlc
from config.settings import RADIO_STATIONS


class RadioService:
    def __init__(self):
        self.instance = vlc.Instance("--no-video", "--aout=alsa")
        self.player = self.instance.media_player_new()
        self.current_station = None
        self.is_playing = False

    def get_available_stations(self) -> list[str]:
        """Return list of available radio station names."""
        return list(RADIO_STATIONS.keys())

    def find_station(self, query: str) -> str | None:
        """Find a station matching the query."""
        query_lower = query.lower().strip()

        # Exact match
        if query_lower in RADIO_STATIONS:
            return query_lower

        # Partial match
        for station_name in RADIO_STATIONS:
            if query_lower in station_name or station_name in query_lower:
                return station_name

        return None

    def play_station(self, station_name: str) -> bool:
        """Play a radio station by name."""
        station = self.find_station(station_name)

        if not station:
            print(f"[Radio] Station not found: {station_name}")
            print(f"[Radio] Available: {', '.join(self.get_available_stations())}")
            return False

        url = RADIO_STATIONS[station]
        try:
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            self.current_station = station
            self.is_playing = True
            print(f"[Radio] Playing: {station.title()}")
            return True
        except Exception as e:
            print(f"[Radio] Error playing {station}: {e}")
            return False

    def stop(self) -> bool:
        """Stop radio playback."""
        try:
            self.player.stop()
            self.is_playing = False
            self.current_station = None
            print("[Radio] Stopped.")
            return True
        except Exception as e:
            print(f"[Radio] Stop error: {e}")
            return False

    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        volume = max(0, min(100, volume))
        try:
            self.player.audio_set_volume(volume)
            print(f"[Radio] Volume: {volume}%")
            return True
        except Exception as e:
            print(f"[Radio] Volume error: {e}")
            return False
