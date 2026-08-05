import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
BASE_URL = "https://translation.googleapis.com/language/translate/v2"


def translate_to_english(text: str) -> dict:
    """
    Translate any language to English.
    Auto-detects the source language (optimized for Malay input).
    """
    response = requests.post(BASE_URL, params={"key": API_KEY}, json={
        "q": text,
        "target": "en",
        "format": "text"
    })

    data = response.json()

    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    translation = data["data"]["translations"][0]
    return {
        "original": text,
        "translated": translation["translatedText"],
        "detected_source_language": translation.get("detectedSourceLanguage"),
    }

def translate_english_to_malay(text: str) -> dict:
    """
    Translate English text to Malay.
    Forces source language to English.
    """

    response = requests.post(
        BASE_URL,
        params={"key": API_KEY},
        json={
            "q": text,
            "source": "en",
            "target": "ms",
            "format": "text"
        }
    )

    data = response.json()

    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    translation = data["data"]["translations"][0]

    return {
        "original": text,
        "translated": translation["translatedText"],
        "source_language": "en",
        "target_language": "ms"
    }

def detect_language(text: str) -> dict:
    """Detect the language of the given text."""
    response = requests.post(
        f"{BASE_URL}/detect",
        params={"key": API_KEY},
        json={"q": text}
    )

    data = response.json()

    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    result = data["data"]["detections"][0][0]
    return {
        "language": result["language"],
        "confidence": result["confidence"],
    }