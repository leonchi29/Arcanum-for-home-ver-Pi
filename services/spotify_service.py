"""
Spotify music playback service.
Handles authentication and music control.
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.settings import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_SCOPE,
)


class SpotifyService:
    def __init__(self):
        self.sp = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with Spotify. Returns True if successful."""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            print("[Spotify] Missing credentials. Configure .env file.")
            return False

        try:
            auth_manager = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SPOTIFY_SCOPE,
                cache_path=os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), ".spotify_cache"
                ),
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            # Test the connection
            self.sp.current_user()
            self.authenticated = True
            print("[Spotify] Authenticated successfully.")
            return True
        except Exception as e:
            print(f"[Spotify] Authentication failed: {e}")
            print("[Spotify] Please log in via the browser link above.")
            self.authenticated = False
            return False

    def play_song(self, query: str) -> bool:
        """Search and play a song on Spotify."""
        if not self.authenticated:
            print("[Spotify] Not authenticated. Please log in first.")
            return False

        try:
            results = self.sp.search(q=query, type="track", limit=1)
            tracks = results.get("tracks", {}).get("items", [])

            if not tracks:
                print(f"[Spotify] No results for: {query}")
                return False

            track = tracks[0]
            track_name = track["name"]
            artist = track["artists"][0]["name"]
            uri = track["uri"]

            # Get active device
            devices = self.sp.devices()
            active_devices = devices.get("devices", [])

            if not active_devices:
                print("[Spotify] No active devices found. Open Spotify on a device.")
                return False

            device_id = active_devices[0]["id"]
            self.sp.start_playback(device_id=device_id, uris=[uri])
            print(f"[Spotify] Playing: {track_name} - {artist}")
            return True

        except Exception as e:
            print(f"[Spotify] Playback error: {e}")
            return False

    def play_playlist(self, query: str) -> bool:
        """Search and play a playlist on Spotify."""
        if not self.authenticated:
            print("[Spotify] Not authenticated. Please log in first.")
            return False

        try:
            results = self.sp.search(q=query, type="playlist", limit=1)
            playlists = results.get("playlists", {}).get("items", [])

            if not playlists:
                print(f"[Spotify] No playlist found for: {query}")
                return False

            playlist = playlists[0]
            playlist_name = playlist["name"]
            uri = playlist["uri"]

            devices = self.sp.devices()
            active_devices = devices.get("devices", [])

            if not active_devices:
                print("[Spotify] No active devices found. Open Spotify on a device.")
                return False

            device_id = active_devices[0]["id"]
            self.sp.start_playback(device_id=device_id, context_uri=uri)
            print(f"[Spotify] Playing playlist: {playlist_name}")
            return True

        except Exception as e:
            print(f"[Spotify] Playlist error: {e}")
            return False

    def pause(self) -> bool:
        """Pause current playback."""
        if not self.authenticated:
            return False
        try:
            self.sp.pause_playback()
            print("[Spotify] Paused.")
            return True
        except Exception as e:
            print(f"[Spotify] Pause error: {e}")
            return False

    def resume(self) -> bool:
        """Resume playback."""
        if not self.authenticated:
            return False
        try:
            self.sp.start_playback()
            print("[Spotify] Resumed.")
            return True
        except Exception as e:
            print(f"[Spotify] Resume error: {e}")
            return False

    def next_track(self) -> bool:
        """Skip to next track."""
        if not self.authenticated:
            return False
        try:
            self.sp.next_track()
            print("[Spotify] Next track.")
            return True
        except Exception as e:
            print(f"[Spotify] Next error: {e}")
            return False
