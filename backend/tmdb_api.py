import os
import requests
from dotenv import load_dotenv
import pycountry
import country_converter as coco

load_dotenv()

class TMDBAPI:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        token = os.getenv("TMDB_ACCESS_TOKEN")
        if not token:
            raise ValueError("TMDB_ACCESS_TOKEN not found in .env file")

        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def search_movie(self, query, language="en-US", page=1):
        return self._get(
            "/search/movie",
            params={
                "query": query,
                "language": language,
                "page": page
            }
        )

    def get_movie_details(self, movie_id, language="en-US"):
        return self._get(
            f"/movie/{movie_id}",
            params={
                "language": language
            }
        )

    def discover_movies(self, 
                        genre=None, 
                        year=None, 
                        country=None, 
                        original_language=None, 
                        actor=None,
                        director=None,
                        sort_by="popularity.desc", 
                        page=1):
        if original_language:
            original_language = self.get_language_code(original_language)
        country = self.get_country_code(country)
        genre_id = self.get_genre_id(genre)
        actor = self.get_person_id(actor)
        director = self.get_person_id(director)
        return self._get(
            "/discover/movie",
            params={
                "with_genres": genre_id,
                "with_original_language": original_language,
                "primary_release_year": year,
                "with_origin_country": country,
                "with_cast": actor,
                "with_crew": director,
                "sort_by": sort_by,
                "page": page
            }
        )
    
    def search_person(self, query, language="en-US", page=1):
        return self._get(
            "/search/person",
            params={
                "query": query,
                "language": language,
                "page": page
            }
        )

    def get_movie_genres(self, language="en"):
        return self._get(
            "/genre/movie/list",
            params={
                "language": language
            }
        )

    def get_similar_movies(self, movie_id, language="en-US", page=1):
        return self._get(
            f"/movie/{movie_id}/similar",
            params={
                "language": language,
                "page": page
            }
        )
    
    def get_language_code(self, language):
        manual_map = {
            "malay": "ms",
            "chinese": "zh",
            "mandarin": "zh",
            "korean": "ko",
            "japanese": "ja",
            "english": "en",
        }
        key = language.lower().strip()

        if key in manual_map:
            return manual_map[key]
        try:
            # Search for the language by name
            language = pycountry.languages.get(name=language.title())
            
            # Return the 2-letter ISO 639-1 code
            return language.alpha_2
        except (AttributeError, LookupError):
            # Return english as default
            return None
        
    def get_country_code(self, country_name):
        try:
            # search_fuzzy handles minor naming variations
            code = coco.convert(names=country_name.title(), to="ISO2")
            # Returns the alpha_2 code (e.g., 'US')
            return code
        except:
            return None
        
    def get_genre_id(self, genre_name):
        if not genre_name:
            return None

        # First letter capital, others lowercase for each word
        genre_name = genre_name.title()

        genre_list = self.get_movie_genres().get("genres", [])

        for genre in genre_list:
            if genre["name"] == genre_name:
                return genre["id"]

        return None
    
    def get_person_id(self, person_name):
        if not person_name:
            return None
        
        person_name = person_name.title()

        result = self.search_person(query=person_name).get("results", [])

        if not result:
            return None

        return result[0].get("id")
     