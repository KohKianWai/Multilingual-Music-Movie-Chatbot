import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_STT_API_KEY")
BASE_URL = "https://speech.googleapis.com/v1/speech:recognize"


def transcribe_audio(audio_file_path: str, language_code: str = "en-US") -> dict:
    """
    Transcribe audio to text using free tier standard model.
    Supports MP3 directly — no conversion needed.
    Primary: Malay (ms-MY). Fallback: English (en-US).
    Handles Manglish/code-switching.
    60 minutes/month free.
    """
    with open(audio_file_path, "rb") as f:
        audio_content = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "config": {
            "encoding": "WEBM_OPUS",
            "languageCode": language_code,
            "alternativeLanguageCodes": ["ms-MY"],
            "model": "default",
            "enableAutomaticPunctuation": True,
            # "audioChannelCount": 2,
        },
        "audio": {
            "content": audio_content
        }
    }

    response = requests.post(BASE_URL, params={"key": API_KEY}, json=payload)
    data = response.json()

    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    if "results" not in data:
        return {"transcript": "", "confidence": 0}

    result = data["results"][0]["alternatives"][0]
    return {
        "transcript": result["transcript"],
        "confidence": result.get("confidence", 0),
    }