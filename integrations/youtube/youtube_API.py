"""
This module is used to interact with the YouTube API.
"""
import os
from typing import Tuple
from googleapiclient.discovery import build
from googleapiclient.http import HttpError

class YouTube_API:
    """
    YouTube_API class is responsible for interacting with the YouTube API.
    """
    def __init__(self,youtubeapikey:str) -> None:
        self.API_KEY = youtubeapikey
        # Create a YouTube API client
        self.client = build('youtube', 'v3', developerKey=self.API_KEY)

    def get_playlist_info(self,playlist_id:str) -> Tuple[str,dict]:
        """
        Get the playlist information from the YouTube API.

        Args:
        """
        # Make a request to retrieve the playlist information
        request = self.client.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            # Extract the relevant information from the response
            try:
                playlist_title = response['items'][0]['snippet']['title']
            except:
                playlist_title = ""

            # Make a request to retrieve the playlist items (videos)
            request = self.client.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=1000  # Adjust the number of results to retrieve
            )
            try:
                response = request.execute()
                response = response['items']
            except HttpError as error:
                # Check if the error is a 404 (playlist not found)
                response = {}
                if error.resp.status == 404:
                    print(f'Playlist not found for the given ID: {playlist_id}')
                else:
                    print(f'An HTTP error occurred: {error}')
        else:
            playlist_title = ""
            response = {}

        return playlist_title,response

    def get_video_info(self,info: dict) -> Tuple[list, list, list, list]:
        """
        Get the video links from the playlist.

        Args:
            playlist (Playlist): The playlist object.

        Returns:
            Tuple[str, list, list, list]: A tuple containing the 
                playlist title, video links, video IDs, and video titles.
        """


        video_links = [f"https://www.youtube.com/watch?v={data['contentDetails']['videoId']}" for data in info]
        video_ids = [data['contentDetails']['videoId'] for data in info]
        video_titles = [data['snippet']['title'] for data in info]
        video_descriptions = [data['snippet']['description'] for data in info]

        return video_links, video_ids, video_titles,video_descriptions