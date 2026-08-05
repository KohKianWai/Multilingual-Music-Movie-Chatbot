import os
import requests
from dotenv import load_dotenv

load_dotenv()

class NetflixAPI:
    def __init__(self):
        self.api_key = os.getenv("NETFLIXAPI_KEY")
        self.host = "netflix54.p.rapidapi.com"
        self.base_url = f"https://{self.host}"

        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }

    def search(self, query):
        url = f"{self.base_url}/search"
        
        params = {
            "query": query
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            print("Error:", response.status_code)
            print(response.text)
            return None

        return response.json()