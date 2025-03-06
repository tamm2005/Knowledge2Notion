"""
This module is used to interact with the YouTube API.
"""
import os
from typing import Tuple
from pytube import Playlist, YouTube

class pytube_API:
    """
    YouTube_API class is responsible for interacting with the YouTube API.
    """

    @staticmethod
    def get_paylist_links(playlist_id:str) -> str:
        """
        Get the playlist links from the YouTube API.

        Args:
            playlist_id (str): The ID of the playlist.

        Returns:
            str: The playlist link.
        """

        return Playlist(f"https://www.youtube.com/playlist?list={playlist_id}")

    @staticmethod
    def get_video_links(playlist: Playlist) -> Tuple[str, list, list, list]:
        """
        Get the video links from the playlist.

        Args:
            playlist (Playlist): The playlist object.

        Returns:
            Tuple[str, list, list, list]: A tuple containing the 
                playlist title, video links, video IDs, and video titles.
        """
        # Print the video information
        playlist_title = playlist.title
        video_links = [video.watch_url for video in playlist.videos]
        video_ids = [video.video_id for video in playlist.videos]
        video_titles = [video.title for video in playlist.videos]
        return playlist_title, video_links, video_ids, video_titles
