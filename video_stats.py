import requests
import json
import os
from dotenv import load_dotenv


load_dotenv(".env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"


def get_playlist_id():
    
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)
        
        response.raise_for_status()  # Check if the request was successful
        
        data = response.json()
        #print(json.dumps(data, indent=4))
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        print(uploads_playlist_id)
        return uploads_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


if __name__ == "__main__":
    print("get_playlist_id will be executed")
    get_playlist_id()
