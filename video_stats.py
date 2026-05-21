# YouTube Data API client for retrieving channel video statistics
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")
API_KEY = os.getenv("API_KEY")  # YouTube Data API key
CHANNEL_HANDLE = "MrBeast"  # Target YouTube channel handle
maxResults = 50  # Maximum number of results per API request

def get_playlist_id():
    """
    Retrieves the uploads playlist ID for a YouTube channel.
    
    Returns:
        str: The playlist ID containing all uploaded videos for the channel
    """
    try:
        # Construct API URL to get channel details by handle
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        # Make API request to YouTube Data API
        response = requests.get(url)
        
        response.raise_for_status()  # Check if the request was successful
        
        # Parse JSON response
        data = response.json()
        #print(json.dumps(data, indent=4))
        
        # Extract the uploads playlist ID from the response
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        #print(uploads_playlist_id)
        return uploads_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)



def get_video_ids(playlistid):
    """
    Retrieves all video IDs from a YouTube playlist using pagination.
    
    Args:
        playlistid (str): The playlist ID to fetch videos from
        
    Returns:
        list: A list of video IDs from the playlist
    """
    video_ids = []
    pagetoken = None  # Used for pagination through API results
    
    # Construct base API URL for playlist items
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistid}&key={API_KEY}"
    
    try:
        # Loop through all pages of results
        while True:
            # Start with base URL
            url = base_url
            # Add page token if we're on a subsequent page
            if pagetoken:
                url += f"&pageToken={pagetoken}"
            
            # Make API request for current page
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            data = response.json()
            
            # Extract video IDs from current page
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
                
            # Check if there are more pages to fetch
            pagetoken = data.get('nextPageToken')
            if not pagetoken:
                break  # No more pages, exit loop
                
        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
  


if __name__ == "__main__":
    """
    Main execution block:
    1. Gets the uploads playlist ID for the specified channel
    2. Retrieves all video IDs from that playlist
    """
    #print("get_playlist_id will be executed")
    playlistid = get_playlist_id()  # Get the uploads playlist ID
    get_video_ids(playlistid)  # Fetch all video IDs from the playlist

