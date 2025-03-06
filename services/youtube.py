"""
This module is used to extract the YouTube links from 
the playlist and upload them to Notion
"""
import os
from integrations.youtube.youtube_API import YouTube_API
from integrations.notion.notion_API import Notion_API

class YoutubeService(object):
    """
    This class is used to extract the YouTube links from
    """
    def __init__(self,playlist_ids,notion_token,databaseid,youtubeapikey):
        self.playlist_ids = playlist_ids
        self.notion_token = notion_token
        self.databaseid = databaseid
        self.youtubeapikey = youtubeapikey

    def json_to_notion_page(self,json_data:dict) -> dict:
        """
        This function is used to convert the JSON data to the Notion page

        Args:
        json_data: dict: The JSON data

        Returns:
        payload: dict: The Notion page payload
        """

        return {
                'ID': {'rich_text': [{'text': {'content': json_data["video_id"]}}]},
                'Tags': {'select': {'name': json_data["playlist_title"]}},
                'Name': {'title': [{'text': {'content': json_data["video_title"]}}]},
                'VideoURL': {'url':  json_data["video_link"]}
            }

    def json_data_notion_page_children(self,json_data:dict,json_data_page_children:dict={}) -> dict:
        """
        This function is used to convert the JSON data to the Notion page children

        Args:
        json_data: dict: The JSON data
        json_data_page_children: dict: The JSON data page children

        Returns:
        json_data_page_children: dict: The Notion page children
        """

        json_data_page_children["YouTube Content"] = [
                                        {
                                            "text":json_data['video_description'],
                                            'images':None,
                                            'videos':None,
                                            'pdf_links':None,
                                            'caption_strings':None,
                                            'web_bookmarks':[json_data['video_link']],
                                            'image_messages':None,
                                            'video_messages':None
                                        }
            ]
        return json_data_page_children

    def main(self):
        """
        Main function to start the service
        """

        for playlist_id in self.playlist_ids:
            ytapiser = YouTube_API(self.youtubeapikey)
            playlist_title,youtubelinks = ytapiser.get_playlist_info(playlist_id)
            video_links, video_ids, video_titles,video_descriptions =  \
                                            ytapiser.get_video_info(youtubelinks)
            video_links = video_links[::-1]
            video_ids = video_ids[::-1]
            video_titles = video_titles[::-1]
            video_descriptions = video_descriptions[::-1]

            for video_link, video_id, video_title,video_description in \
                        zip(video_links, video_ids, video_titles,video_descriptions):
                video_dict = {
                    'playlist_title': playlist_title,
                    'video_link': video_link,
                    'video_id': video_id,
                    'video_title': video_title,
                    'video_description': video_description
                }
                payload = self.json_to_notion_page(video_dict)
                json_data_page_children = self.json_data_notion_page_children(video_dict)
                notionAPIservice = Notion_API(
                                        self.notion_token,
                                        self.databaseid,
                                        payload,
                                        json_data_page_children
                                    )
                subject,_ = notionAPIservice.read_notion_database(
                                            video_dict["video_id"],
                                            "ID"
                                        )
                if video_dict["video_id"] in subject:
                    print("Email already exists in Notion")
                    break
                else:
                    notionAPIservice.upload_to_notion()
