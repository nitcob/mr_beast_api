# YouTube Data API client for retrieving channel video statistics
import requests
import json
#import os
from dotenv import load_dotenv
from datetime import date
from airflow import task
from airflow.models import Variable
#from pprint import pprint

# Load environment variables from .env file
load_dotenv(".env")
API_KEY = Variable.get("API_KEY")  # YouTube Data API key
CHANNEL_HANDLE = Variable.get("MrBeast")  # Target YouTube channel handle
maxResults = 50  # Maximum number of results per API request

@task
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


@task
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
  

@task
def extract_video_data(video_ids):

    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id : video_id + batch_size]

    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e

@task   
def save_to_json(extracted_data):
    file_path: str = f"./data/video_data_{date.today()}.json"
    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    """
    Main execution block:
    1. Gets the uploads playlist ID for the specified channel
    2. Retrieves all video IDs from that playlist
    """
    #print("get_playlist_id will be executed")
    playlistid = get_playlist_id()  # Get the uploads playlist ID
    video_ids = get_video_ids(playlistid)  # Fetch all video IDs from the playlist
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)



