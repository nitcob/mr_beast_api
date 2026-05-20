import requests
import json
import os
from dotenv import load_dotenv


load_dotenv(".env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

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



def get_video_ids(playlistid):
    
    video_ids = []
    pagetoken = None
    
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistid}&key={API_KEY}"
    
    try:
        while True:
            
            url = base_url
            if pagetoken:
                url += f"&pageToken={pagetoken}"
            
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
                
            pagetoken = data.get('nextPageToken')
            if not pagetoken:
                break
        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
  


if __name__ == "__main__":
    #print("get_playlist_id will be executed")
    playlistid = get_playlist_id()
    get_video_ids(playlistid)

