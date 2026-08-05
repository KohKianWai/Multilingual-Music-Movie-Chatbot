import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFMError(Exception):
    """Raised when Last.fm returns an API error."""


class LastFMClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 20) -> None:
        self.api_key = api_key or os.getenv("LASTFM_API_KEY")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("Missing LASTFM_API_KEY in your .env file")

    def call(self, method: str, **params: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": method,
            "api_key": self.api_key,
            "format": "json",
            **{k: v for k, v in params.items() if v is not None},
        }

        response = requests.get(BASE_URL, params=payload, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            raise LastFMError(
                f"Last.fm error {data['error']}: {data.get('message')}\nPayload: {payload}"
            )
        return data


# Public-only methods useful for chatbot search and recommendation.
METHOD_CATALOG: Dict[str, Dict[str, Any]] = {
    # Search
    "artist.search": {
        "required_params": ["artist"],
        "optional_params": ["limit", "page"],
        "description": "Search artists by name",
    },
    "track.search": {
        "required_params": ["track"],
        "optional_params": ["artist", "limit", "page"],
        "description": "Search tracks by title, optionally with artist",
    },
    "album.search": {
        "required_params": ["album"],
        "optional_params": ["limit", "page"],
        "description": "Search albums by title",
    },

    # Similar / recommendation
    "artist.getSimilar": {
        "required_params": ["artist"],
        "optional_params": ["limit", "autocorrect"],
        "description": "Get similar artists",
    },
    "track.getSimilar": {
        "required_params": ["artist", "track"],
        "optional_params": ["limit", "autocorrect"],
        "description": "Get similar tracks",
    },

    # Details / follow-up metadata
    "artist.getTopTracks": {
        "required_params": ["artist"],
        "optional_params": ["limit", "page", "autocorrect"],
        "description": "Get an artist's top tracks",
    },
    "artist.getTopTags": {
        "required_params": ["artist"],
        "optional_params": ["autocorrect"],
        "description": "Get top tags for an artist",
    },
    "album.getInfo": {
        "required_params": ["artist", "album"],
        "optional_params": ["autocorrect"],
        "description": "Get album details and track list",
    },
    "album.getTopTags": {
        "required_params": ["artist", "album"],
        "optional_params": ["autocorrect"],
        "description": "Get top tags for an album",
    },
    "track.getInfo": {
        "required_params": ["artist", "track"],
        "optional_params": ["autocorrect", "username"],
        "description": "Get track details",
    },
    "track.getTopTags": {
        "required_params": ["artist", "track"],
        "optional_params": ["autocorrect"],
        "description": "Get top tags for a track",
    },

    # Tag / genre discovery
    "tag.getInfo": {
        "required_params": ["tag"],
        "optional_params": [],
        "description": "Get info about a tag or genre",
    },
    "tag.getTopArtists": {
        "required_params": ["tag"],
        "optional_params": ["limit", "page"],
        "description": "Get top artists for a tag",
    },
    "tag.getTopTracks": {
        "required_params": ["tag"],
        "optional_params": ["limit", "page"],
        "description": "Get top tracks for a tag",
    },
    "tag.getTopAlbums": {
        "required_params": ["tag"],
        "optional_params": ["limit", "page"],
        "description": "Get top albums for a tag",
    },
    "tag.getTopTags": {
        "required_params": [],
        "optional_params": ["limit", "page"],
        "description": "Get globally popular tags",
    },

    # Trending fallback
    "chart.getTopArtists": {
        "required_params": [],
        "optional_params": ["limit", "page"],
        "description": "Get globally trending artists",
    },
    "chart.getTopTracks": {
        "required_params": [],
        "optional_params": ["limit", "page"],
        "description": "Get globally trending tracks",
    },
    "chart.getTopTags": {
        "required_params": [],
        "optional_params": ["limit", "page"],
        "description": "Get globally trending tags",
    },

    # Regional discovery
    "geo.getTopArtists": {
        "required_params": ["country"],
        "optional_params": ["limit", "page"],
        "description": "Get top artists by country",
    },
    "geo.getTopTracks": {
        "required_params": ["country"],
        "optional_params": ["limit", "page"],
        "description": "Get top tracks by country",
    },
}


def list_methods() -> List[str]:
    return sorted(METHOD_CATALOG.keys())


def get_method_info(method_name: str) -> Dict[str, Any]:
    if method_name not in METHOD_CATALOG:
        raise KeyError(f"Unknown method: {method_name}")
    return METHOD_CATALOG[method_name]


# if __name__ == "__main__":
#     print("Loaded Last.fm chatbot client")
#     print(f"Methods available: {len(METHOD_CATALOG)}")
#     for method_name in list_methods():
#         spec = METHOD_CATALOG[method_name]
#         print(f"- {method_name} | required={spec.get('required_params', [])} | optional={spec.get('optional_params', [])}")