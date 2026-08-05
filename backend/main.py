from fastapi import FastAPI, UploadFile, File
import tempfile
import os
from pydantic import BaseModel
import random
import requests
import re
from fastapi.middleware.cors import CORSMiddleware
from word2number import w2n
from fastapi import HTTPException
from spotify_api import SpotifyClient, SpotifyAPIError
import billboard
from lastfm_api import LastFMClient
from tmdb_api import TMDBAPI
from translation_api import translate_english_to_malay, translate_to_english, detect_language
from speech_to_text_api import transcribe_audio
import time


spotify = SpotifyClient()
app = FastAPI()
lastfm = LastFMClient()
tmdb = TMDBAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def webhook(req: ChatRequest):
    return process_chat_message(req.message)

@app.post("/voice-chat")
def voice_chat(audio: UploadFile = File(...)):
    # Save uploaded audio temporarily
    suffix = os.path.splitext(audio.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(audio.file.read())
        temp_audio_path = temp_audio.name

    try:
        # 1. Convert speech to text
        transcription = transcribe_audio(
            audio_file_path=temp_audio_path
        )

        transcript = transcription["transcript"]
        print("Transcript:", transcript, flush=True)

        if not transcript:
            return {
                "reply": "Sorry, I could not understand the audio."
            }

        # 2. Send transcript into existing chatbot flow
        chat_result = process_chat_message(transcript)
        print(chat_result)
        # 3. Return result
        return {
            "transcript": transcript,
            **chat_result
        }

    finally:
        # Delete temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

def process_chat_message(user_message: str):
    start_time = time.time()
    print("--> 1. Entering process_chat_message", flush=True)
    
    # Trace the language detection
    detected = detect_language(user_message)
    print(f"--> 2. Language detected: {detected}", flush=True)
    
    detected_language = detected["language"]
    detected_confidence = detected["confidence"] 
    translate_back_to_malay = False

    if detected_language in ["ms", "id"]:
        translated_result = translate_to_english(user_message)
        message_for_rasa = translated_result["translated"].lower()
        translate_back_to_malay = True
    elif detected_language == "en":
        message_for_rasa = user_message.lower()
    else:
        message_for_rasa = "What is the weather today"

    message_for_rasa = message_for_rasa.lower()

    print(f"--> 3. Sending to Rasa: {message_for_rasa}", flush=True)
    
    # ADDED A TIMEOUT HERE! 
    # If Rasa doesn't reply in 15 seconds, it will throw an error instead of hanging forever.
    try:
        response = requests.post(
            RASA_API_URL, 
            json={
                "sender": "user123", 
                "message": message_for_rasa
            },
            timeout=30
        )
        rasa_response = response.json()
        print(f"--> 4. Rasa replied: {rasa_response}", flush=True)
    except requests.exceptions.Timeout:
        print("--> ERROR: Rasa took longer than 30 seconds to reply!", flush=True)
        return {"reply": "Rasa server timed out. Is it running or doing a cold start?"}
    except Exception as e:
        print(f"--> ERROR connecting to Rasa: {e}", flush=True)
        return {"reply": "Could not connect to Rasa server."}

    if rasa_response:
        reply = rasa_response[0].get("text", "No response from bot")
    else:
        reply = "No response from bot"

    if translate_back_to_malay and detected_confidence > 0.55:
        reply = translate_reply_selectively(reply)

    end_time = time.time()
    response_time = round(end_time - start_time, 2)
    print(f"--> Response Time: {response_time} seconds", flush=True)

    print("--> 5. Process complete, returning reply", flush=True)
    return {"reply": reply}

@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.get("/random-music")
def get_random_music(number: int | str | None = None):
    # convert non-numeric number into numeric number
    if number:
        if isinstance(number, str) and not number.isnumeric():
            number = w2n.word_to_num(number)
        number = int(number)

    # limit the user to only search for 10 songs maximum
    if number and number > 10:
        raise HTTPException(
            status_code=400, 
            detail="Sorry, I cannot recommend that many songs. The maximum is 10."
        )

    results = get_random_suggestion(number)
    ret = []
    for result in results:
        info = {
            "title": result.title,
            "artist": result.artist
        }
        ret.append(info)
    return ret

@app.get("/music/by-search-criteria")       # TODO: handle year
def get_music_by_search_criteria(artist: str | None = None, genre: str | None = None, language: str | None = None, number: int | str = 1):
    # convert non-numeric number into numeric number
    if number:
        if isinstance(number, str) and not number.isnumeric():
            number = w2n.word_to_num(number)
        number = int(number)

    # limit the user to only search for 10 songs maximum
    if number and number > 10:
        raise HTTPException(
            status_code=400, 
            detail="Sorry, I cannot recommend that many songs. The maximum is 10."
        )

    # if user only search by artist
    if artist and not (genre or language):

        results = lastfm.call(
            "artist.getTopTracks",
            artist=artist,
            limit=number
        )
        
        results = results.get("toptracks", {}).get("track", [])

        if isinstance(results, dict):  # only one result
            results = [results]

        if not results:
            return []
        
        # limit the suggestion based on the user preference, default is 1
        random.shuffle(results)
        results = results[:number]

        ret = []
        for result in results:
            info = {
                "title": result.get("name"),
                "artist": '' # result.get("artist", {}).get("name")
            }
            ret.append(info)

        ret = remove_duplicate_songs(ret)
        return ret
    
    else:
        query_parts = []

        if artist:
            query_parts.append(f'artist:"{artist}"')

        if genre:
            query_parts.append(f'{genre}')

        if language:
            query_parts.append(language)

        query = " ".join(query_parts)

        if artist:
            offset = random.randint(0, 5)
        else:
            offset = random.randint(0, 50)

        results = spotify.search(
            query=query,
            search_type="track",
            limit=10,
            offset=offset
        )
        
        results = results.get("tracks", {}).get("items", [])

        if not results:
            return []
        
        # limit the suggestion based on the user preference, default is 1
        random.shuffle(results)
        results = results[:number]

        ret = []
        for result in results:
            info = {
                "title": result['name'],
                "artist": ", ".join(a.get("name", "") for a in result.get("artists", []))
            }
            ret.append(info)

        ret = remove_duplicate_songs(ret)
        return ret

def get_random_suggestion(count: int | None):
    if count is None:
        count = 10
    chart = billboard.ChartData('pop-songs')
    count = min(count, len(chart))

    return random.sample(list(chart), count)

@app.get("/random-movies")
def get_random_movies(number: int | str | None = None):
    # convert non-numeric number into numeric number
    if number:
        if isinstance(number, str) and not number.isnumeric():
            number = w2n.word_to_num(number)
        number = int(number)

    # limit the user to only search for 10 movies maximum
    if number and number > 10:
        raise HTTPException(
            status_code=400, 
            detail="Sorry, I cannot recommend that many movies. The maximum is 10."
        )
    page = random.randint(1, 10)
    results = tmdb.discover_movies(page=page)
    results = results.get("results", [])
    results = filter_inappropriate_movies(results)
    number = min(number, len(results))
    results = random.sample(results, number)
    ret = []
    for result in results:
        info = {
            "title": result.get("title"),
            "release_date": extract_year(result.get("release_date"))
        }
        ret.append(info)

    return ret

@app.get("/movie/by-search-criteria")
def movie_by_search_criteria(genre: str | None = None,
                             year: str | int | None = None,
                             country: str | None = None,
                             language: str | None = None,
                             actor: str | None = None,
                             director: str | None = None,
                             number: str | int | None = None
                              ):
    # convert non-numeric number into numeric number
    if number:
        if isinstance(number, str) and not number.isnumeric():
            number = w2n.word_to_num(number)
        number = int(number)

    # limit the user to only search for 10 movies maximum
    if number and number > 10:
        raise HTTPException(
            status_code=400, 
            detail="Sorry, I cannot recommend that many movies. The maximum is 10."
        )
    
    results = tmdb.discover_movies(   
        genre=genre,
        year=year,
        country=country,
        original_language=language,
        actor=actor,
        director=director
    )
    results = results.get("results", [])
    results = filter_inappropriate_movies(results)
    number = min(number, len(results))
    results = random.sample(results, number)
    ret = []
    for result in results:
        info = {
            "title": result.get("title"),
            "release_date": extract_year(result.get("release_date"))
        }
        ret.append(info)

    return ret
    
def translate_reply_selectively(reply: str) -> str:
    """Translate conversational lines to Malay but keep recommendation lines in English."""
    lines = reply.split("\n")
    translated_lines = []

    for line in lines:
        stripped = line.strip()
        # Skip translation for recommendation lines like "1) Song Title - Artist"
        # and empty lines
        if re.match(r'^\d+\)', stripped) or stripped == "":
            translated_lines.append(line)
        else:
            translated = translate_english_to_malay(stripped)
            translated_lines.append(translated["translated"])

    return "\n".join(translated_lines)

def normalize_song_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"\s*-\s*track by track.*$", "", title)
    title = re.sub(r"\s*-\s*.*remix.*$", "", title)

    title = re.sub(r"\(.*?version.*?\)", "", title)
    title = re.sub(r"\(.*?remaster.*?\)", "", title)
    title = re.sub(r"\(.*?live.*?\)", "", title)
    title = re.sub(r"\(.*?feat.*?\)", "", title)
    title = re.sub(r"\(.*?ft.*?\)", "", title)
    title = re.sub(r"\(.*?featuring.*?\)", "", title)

    title = re.sub(r"\s+", " ", title).strip()
    return title


def remove_duplicate_songs(songs: list) -> list:
    seen = set()
    unique_songs = []

    for song in songs:
        title = song.get("title") or song.get("name") or ""
        artist = song.get("artist") or ""

        key = normalize_song_title(title)

        if key not in seen:
            seen.add(key)
            unique_songs.append(song)

    return unique_songs

def extract_year(date_str):
    if not date_str:
        return ""
    return str(date_str).split("-")[0]

def filter_inappropriate_movies(movies: list) -> list:
    blocked_words = ["porn"]

    filtered_movies = []

    for movie in movies:
        title = movie.get("title", "").lower()

        if not any(word in title for word in blocked_words):
            filtered_movies.append(movie)

    return filtered_movies