import base64
import os
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE_URL = "https://api.spotify.com/v1"


class SpotifyAPIError(Exception):
    """Raised when Spotify returns an unexpected response."""


class SpotifyClient:
    def __init__(self) -> None:
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise ValueError(
                "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in environment."
            )

        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        raw = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(raw.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=20)

        if response.status_code != 200:
            raise SpotifyAPIError(
                f"Token request failed: {response.status_code} {response.text}"
            )

        payload = response.json()
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)

        if not access_token:
            raise SpotifyAPIError("Spotify token response did not include access_token.")

        self._access_token = access_token
        self._token_expires_at = time.time() + int(expires_in) - 30
        return self._access_token

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
        }

        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            params=params,
            timeout=20,
        )

        if response.status_code != 200:
            raise SpotifyAPIError(
                f"GET {endpoint} failed: {response.status_code} {response.text}"
            )

        return response.json()

    def search(
        self,
        query: str,
        search_type: str = "track",
        limit: int = 10,
        offset: int = 0,
        market: Optional[str] = None,
    ) -> Dict[str, Any]:
        if limit > 10:
            limit = 10
        if limit < 1:
            limit = 1

        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
            "offset": offset,
        }

        if market:
            params["market"] = market

        return self._get("/search", params=params)

    def search_artist_by_name(self, artist_name: str) -> Optional[Dict[str, Any]]:
        results = self.search(
            query=f'artist:"{artist_name}"',
            search_type="artist",
            limit=1,
        )
        artists = results.get("artists", {}).get("items", [])
        return artists[0] if artists else None

    def get_artist_id(self, artist_name: str) -> Optional[str]:
        artist = self.search_artist_by_name(artist_name)
        if not artist:
            return None
        return artist.get("id")

    def search_tracks_by_artist(
        self,
        artist_name: str,
        limit: int = 10,
        year: Optional[int] = None,
        album: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> Dict[str, Any]:
        parts = [f'artist:"{artist_name}"']

        if album:
            parts.append(f'album:"{album}"')
        if year:
            parts.append(f"year:{year}")
        if genre:
            parts.append(f'genre:"{genre}"')

        query = " ".join(parts)
        return self.search(query=query, search_type="track", limit=limit)

    # ===== OFFICIAL ENDPOINTS =====

    def get_artist_top_tracks(
        self,
        artist_id: str,
        market: str = "US",
    ) -> Dict[str, Any]:
        return self._get(f"/artists/{artist_id}/top-tracks", params={"market": market})

    def get_recommendations(
        self,
        seed_artists: Optional[str] = None,
        seed_tracks: Optional[str] = None,
        seed_genres: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        if limit > 10:
            limit = 10
        if limit < 1:
            limit = 1

        params: Dict[str, Any] = {"limit": limit}

        if seed_artists:
            params["seed_artists"] = seed_artists
        if seed_tracks:
            params["seed_tracks"] = seed_tracks
        if seed_genres:
            params["seed_genres"] = seed_genres

        return self._get("/recommendations", params=params)

    # ===== FALLBACK METHODS =====

    def get_artist_top_tracks_fallback(
        self,
        artist_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        fallback = self.search_tracks_by_artist(
            artist_name=artist_name,
            limit=limit,
        )
        return {
            "source": "search_fallback",
            "tracks": fallback.get("tracks", {}).get("items", []),
        }

    def get_recommendations_fallback(
        self,
        artist_name: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        parts = []

        if artist_name:
            parts.append(f'artist:"{artist_name}"')
        if genre:
            parts.append(f'genre:"{genre}"')
        if year:
            parts.append(f"year:{year}")

        if not parts:
            parts.append('genre:"pop"')

        query = " ".join(parts)
        fallback = self.search(query=query, search_type="track", limit=limit)

        return {
            "source": "search_fallback",
            "tracks": fallback.get("tracks", {}).get("items", []),
        }