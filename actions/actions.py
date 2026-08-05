from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from word2number import w2n

language_to_country = {
    "korean": "korea",
    "japanese": "japan",
    "thai": "thailand",
    "turkish": "turkey",

    "malay": "malaysia",
    "indonesian": "indonesia",
    "filipino": "philippines",
    "tagalog": "philippines",

    "hindi": "india",
    "tamil": "india",
    "telugu": "india",
    "malayalam": "india",
    "kannada": "india",
    "marathi": "india",
    "bengali": "india",
    "punjabi": "india",
    "gujarati": "india",

    "cantonese": "hong kong"
}

country_normalization = {
    "india": "india",
    "indian": "india",

    "canada": "canada",
    "canadian": "canada",

    "korea": "south korea",
    "south korea": "south korea",
    
    "japan": "japan",
    "japanese": "japan",

    "usa": "us",
    "us": "us",
    "american": "us",

    "uk": "uk",
    "british": "uk",

    "france": "france",
    "french": "france"
}

class ActionCallBackend(Action):

    def name(self) -> Text:
        return "action_call_backend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            response = requests.get("http://localhost:8000/testing")
            data = response.json()

            dispatcher.utter_message(text=f"Backend says: {data['testing']}")

        except Exception as e:
            dispatcher.utter_message(text="Error connecting to backend.")

        return []

class ActionCallMusicApp(Action):
    def name(self) -> str:
        return "action_call_music_app"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> List[Dict]:

        # --- Extract entities ---
        artist_name = None
        genre = None
        language = None
        number = None

        entities = tracker.latest_message.get("entities", [])
        print("Entities extracted:", entities)

        # Try to intelligently combine multi-word artist names
        temp_artist_parts = []

        for e in entities:
            entity_name = e.get("entity")
            value = e.get("value")

            if entity_name == "artist":
                temp_artist_parts.append(value)
            elif entity_name == "genre":
                genre = value
            elif entity_name == "language":
                language = value
            elif entity_name == "number":
                number = value

        if temp_artist_parts:
            artist_name = " ".join(temp_artist_parts).strip()

        # --- Normalize text fields ---
        if artist_name:
            artist_name = artist_name.strip()
        if genre:
            genre = genre.lower()
        if language:
            language = language.lower()

        user_specified_number = number is not None
        # --- Handle number safely ---
        try:
            if number:
                if isinstance(number, str) and not number.isnumeric():
                    number = w2n.word_to_num(number)  # converts "three" → 3
                number = int(number)
            else:
                number = 10  # default to 10 if not provided
        except ValueError:
            number = 10  # default to 10 if conversion fails
            user_specified_number = False

        # --- Debug print ---
        print("Params to backend:", {
            "artist": artist_name,
            "genre": genre,
            "language": language,
            "number": number
        })

        # --- Call backend ---
        try:
            # Decide which endpoint to call
            if not (artist_name or genre or language):
                # Random music
                response = requests.get(
                    "http://localhost:8000/random-music",
                    params={"number": number}
                )
            else:
                # Search by criteria
                response = requests.get(
                    "http://localhost:8000/music/by-search-criteria",
                    params={
                        "artist": artist_name,
                        "genre": genre,
                        "language": language,
                        "number": number
                    }
                )

            response.raise_for_status()
            data = response.json()

            if not data:
                dispatcher.utter_message(text="Sorry, I couldn't find any songs.")
                return []

            # --- Build response message ---
            return_message = ""
            if user_specified_number and len(data) < number:
                return_message += f"Sorry, only {len(data)} songs were found matching your criteria.\n"

            return_message += "Here's a song for you:" if len(data) == 1 else "Here are some songs for you:"
            for idx, song in enumerate(data, start=1):
                if not song['artist']:
                    return_message += f"\n{idx}) {song['title']}"
                else:
                    return_message += f"\n{idx}) {song['title']} - {song['artist']}"

            dispatcher.utter_message(text=return_message + '\n')
            
        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                dispatcher.utter_message(text=error_data.get("detail", "Sorry, something went wrong."))
            except Exception:
                dispatcher.utter_message(text="Sorry, the chatbot service is currently experiencing issues.")
            print("Error calling backend:", e)

        except Exception as e:
            dispatcher.utter_message(text="Sorry, the chatbot service is currently experiencing issues.")
            print("Unexpected error:", e)

        return []

   
class ActionCallMovieApp(Action):

    def name(self) -> Text:
        return "action_call_movie_app"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message.get("entities", [])

        category = None
        actor = None
        director = None
        language = None
        year = None
        country = None
        number = None

        actor_parts = []
        director_parts = []

        for e in entities:
            entity_name = e.get("entity")
            value = e.get("value")

            if entity_name == "actor":
                actor_parts.append(value)

            elif entity_name == "category":
                category = value

            elif entity_name == "language":
                language = value

            elif entity_name == "year":
                year = value

            elif entity_name == "country":
                country = value

            elif entity_name == "number":
                number = value

            elif entity_name == "director":
                director_parts.append(value)

        if actor_parts:
            actor = " ".join(actor_parts)

        if director_parts:
            director = " ".join(director_parts)

        # 2. Normalize values
        if category:
            category = category.lower()

        if language:
            language = language.lower()

        if actor:
            actor = actor.strip()

        if director:
            director = director.strip()

        if country:
            country = country.lower()
            country = country_normalization.get(country, country)
            
        # if language and not country:
        #     mapped_country = language_to_country.get(language)
        #     if mapped_country:
        #         country = mapped_country

        print("Entities extracted:", entities)
        print(country)

        user_specified_number = number is not None
        # Normalize number
        try:
            if number:
                if isinstance(number, str) and not number.isnumeric():
                    number = w2n.word_to_num(number)  # converts "three" → 3
                number = int(number)
            else:
                number = 10  # default to 10 if not provided
        except ValueError:
            number = 10  # default to 10 if conversion fails

        # Normalize year
        if year:
            try:
                if isinstance(year, str) and not year.isnumeric():
                    year = w2n.word_to_num(year)
                year = int(year)
            except:
                year = None


        try:
            # 4. Decide endpoint # TODO handle for title
            if not any([category, actor, director, language, year, country]):
                response = requests.get(
                    "http://localhost:8000/random-movies",
                    params={"number": number}
                )

            else:  
                response = requests.get(
                    "http://localhost:8000/movie/by-search-criteria",
                    params={
                        "genre": category,
                        "language": language,
                        "year": year,
                        "country": country,
                        "actor": actor,
                        "director": director,
                        "number": number
                    }
                )

            response.raise_for_status()
            data = response.json()

            # 5. Handle empty response
            if not data:
                dispatcher.utter_message(text="Sorry, I couldn't find any movies.")
                return []

            # 6. Build response
            return_message = ""

            if user_specified_number and len(data) < number:
                return_message += f"Sorry, only {len(data)} movies were found matching your criteria.\n"

            if len(data) == 1:
                return_message += "Here's a movie for you:"
            else:
                return_message += f"Here are {len(data)} movies for you:"

            for i, movie in enumerate(data, start=1):
                return_message += f"\n{i}) {movie['title']} ({movie.get('release_date', 'N/A')})"
            
            dispatcher.utter_message(text=return_message+ '\n')

        except requests.exceptions.HTTPError as e:
            try:
                error_data = response.json()
                dispatcher.utter_message(text=error_data.get("detail", "Sorry, something went wrong."))
            except Exception:
                dispatcher.utter_message(text="Sorry, the chatbot service is currently experiencing issues.")
            print("Error calling backend:", e)

        except Exception as e:
            print("Error:", e)
            dispatcher.utter_message(text="Error connecting to movie service.")

        return []