import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_TTS_API_KEY")
BASE_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

# Voice map per language — uses best available free voice
VOICE_MAP = {
    "en-US": {"name": "en-US-Standard-C", "ssmlGender": "FEMALE"},  # Standard — 4M free chars
    "ms-MY": {"name": "ms-MY-Wavenet-A", "ssmlGender": "FEMALE"},   # WaveNet — 1M free chars
}


def text_to_speech(text: str, output_file: str = "output.mp3", language_code: str = "en-US") -> str:
    """
    Convert text to speech using free tier voices.
    - English: Standard voice (4M chars/month free)
    - Malay: WaveNet voice (1M chars/month free)
    """
    # Get the correct voice for the language, fallback to English if not found
    voice = VOICE_MAP.get(language_code, VOICE_MAP["en-US"])

    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": language_code,
            "name": voice["name"],
            "ssmlGender": voice["ssmlGender"]
        },
        "audioConfig": {
            "audioEncoding": "MP3"
        }
    }

    response = requests.post(BASE_URL, params={"key": API_KEY}, json=payload)
    data = response.json()

    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    audio_content = base64.b64decode(data["audioContent"])

    with open(output_file, "wb") as f:
        f.write(audio_content)

    print(f"✅ Audio saved to {output_file} (language: {language_code}, voice: {voice['name']})")
    return output_file