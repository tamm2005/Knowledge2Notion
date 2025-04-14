"""
This module contains the Notion_API class which is used to interact with the Notion API.
"""
import os
from typing import Tuple
import requests

class Notion_API(object):
    """
    Class representing a Notion API service.
    """

    def __init__(self,token:str,database_id:str,payload:dict,json_data_page_children:dict):
        self.token = token
        self.database_id = database_id
        self.payload = payload
        self.json_data_page_children = json_data_page_children

    def notion_information(self,notion_version:str) -> dict:
        """
        Get the Notion API information.

        Parameters:
        notion_version (str): The version of the Notion API to use.

        Returns:
        dict: The Notion API information.
        """

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": notion_version #"2022-06-22"
        }


    def notion_payload_createpage(self) -> dict:
        """
        Create the payload for the Notion API.

        Returns:
        dict: The payload for the Notion API.
        """

        return {
            "parent": {
            "database_id": self.database_id
            },
            'properties': self.payload
        }
    
    def check_notion_db_record(self,id_name:list,id_list:list) -> Tuple[int, dict]:
        # Set the URL for the request
        url = f'https://api.notion.com/v1/databases/{self.database_id}/query'
        # Set the request headers
        headers = self.notion_information("2021-08-16")
        #headers = self.notion_information("2022-06-28")
        val_list = []
        for i in range(len(id_name)):
            val_list.append(            
                    {
                        "property": id_name[i],
                        "text": {
                            "equals": id_list[i]
                        }
                    }
                )
        data = {
            "filter": {
                "and": val_list
                    }
                
            }
        # Send a GET request to retrieve the database information
        response = requests.post(url, headers=headers, json=data, timeout=20)
        data = response.json()
        # Access the retrieved information
        results = data['results']
        subject = []
        name = []
        for item in results:
            for i in range(len(id_name)):
                title = item['properties'][id_name[i]]['rich_text'][0]['text']['content']
                name.append(item['properties']['Name']['title'][0]['plain_text'])
                subject.append(title)
        return name,subject

    def read_notion_response(self,id_value,id_name) -> Tuple[int, dict]:
        """
        Read the response from the Notion API.

        Parameters:
        id_value (str): The value of the ID.
        id_name (str): The name of the ID.

        Returns:
        Tuple[int, dict]: The status code and the response from the Notion API.
        """

        # Set the URL for the request
        url = f'https://api.notion.com/v1/databases/{self.database_id}/query'
        # Set the request headers
        headers = self.notion_information("2021-08-16")
        #headers = self.notion_information("2022-06-28")
        data = {
            "filter": {
                    "property": id_name,
                    "text": {
                        "equals": id_value
                    }
            }
        }
        # Send a GET request to retrieve the database information
        response = requests.post(url, headers=headers, json=data, timeout=20)
        return response.status_code, response.json()

    def update_num_of_applicants(self, page_id: str, payload: dict) -> Tuple[int, dict]:
        url = f'https://api.notion.com/v1/pages/{page_id}'
        headers = self.notion_information("2021-08-16")
        response = requests.patch(url, headers=headers, json=payload, timeout=20)
        return response.status_code, response.json()

    def write_to_notion_page(self) -> Tuple[int, dict]:
        """
        Write the JSON data to the Notion page.

        Returns:
        Tuple[int, dict]: The status code and the response from the Notion API.
        """

        url = "https://api.notion.com/v1/pages"
        headers = self.notion_information("2021-05-13")
        payload = self.notion_payload_createpage()
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        return response.status_code, response.json()

    def read_notion_database(self,id_value,id_name) -> Tuple[list, list]:
        """
        Read the Notion database.

        Parameters:
        id_value (str): The value of the ID.
        id_name (str): The name of the ID.

        Returns:
        Tuple[list, list]: The subject and name of the database.
        """

        _,data = self.read_notion_response(id_value,id_name)
        # Access the retrieved information
        results = data['results']
        subject = []
        name = []
        for item in results:
            title = item['properties'][id_name]['rich_text'][0]['text']['content']
            name.append(item['properties']['Name']['title'][0]['plain_text'])
            subject.append(title)
        return subject,name

    def delete_notion_page(self,page_id:str, headers:dict) -> None:
        """
        Delete the Notion page.

        Parameters:
        page_id (str): The ID of the page.
        headers (dict): The headers for the request.
        """

        url = f"https://api.notion.com/v1/blocks/{page_id}"
        response = requests.delete(url, headers=headers, timeout=20)
        if response.status_code == 200:
            print("Page deleted successfully!")
        else:
            print(f"An error occurred while deleting the page. Status code: {response.status_code}")

    def headingone_json(self,heading_string:str) -> list:
        """
        Create the JSON for the heading.

        Parameters:
        heading_string (str): The heading string.

        Returns:
        list: The JSON for the heading.
        """

        return [{
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": heading_string
                            }
                        }
                    ]
                }
                }]

    def rich_text_json(self,chunks:str)->list:
        """
        Create the JSON for the rich text.

        Parameters:
        chunks (str): The text chunks.

        Returns:
        list: The JSON for the rich text.
        """

        return [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": chunks#.strip()
                                                },
                                            }
                                        ]
                                    },
                                }
                                #for chunk in chunks
                            ]

    def image_json(self,images:list)->list:
        """
        Create the JSON for the image.

        Parameters:
        images (list): The list of images.

        Returns:
        list: The JSON for the image.
        """

        return [
            {
                "object": "block",
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": image
                        }
                    }
                }
                for image in images
        ]

    def video_json(self,videos:list) -> list:
        """
        Create the JSON for the video.

        Parameters:
        videos (list): The list of videos.

        Returns:
        list: The JSON for the video.
        """

        return [
            {
                "object": "block",

                    "type": "video",
                    "video": {
                        "type": "external",
                        "external": {
                            "url": video
                        }
                    }
                }
                for video in videos
        ]

    def pdf_json(self, pdf_links, caption_strings):
        """
        Create the JSON for the PDF.

        Parameters:
        pdf_links (list): The list of PDF links.
        caption_strings (list): The list of caption strings.

        Returns:
        list: The JSON for the PDF.
        """

        children=[]
        for index in range(len(pdf_links)):
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": caption_strings[index]
                            }
                        }
                    ]
                }
            })
            children.append({
                "object": "block",
                "type": "file",
                "file": {
                        "type": "external",
                        "external": {
                            "url": pdf_links[index]
                                        }
                        }#,
                            #"text": {
                            #    "content": caption_strings[index]
                            #}
                        }
            )
        return children

    def image_withcaption_json(self,images:list,caption_strings)->list:
        """
        Create the JSON for the image with caption.

        Parameters:
        images (list): The list of images.
        caption_strings (list): The list of caption strings.

        Returns:
        list: The JSON for the image with caption.
        """

        children=[]
        for index in range(len(images)):
            children.append({
                                "object": "block",
                                    "type": "bookmark",
                                    "bookmark": {
                                        "caption": [],
                                        "url": caption_strings[index]
                                    }
                                })
            children.append({
                                "object": "block",
                                    "type": "image",
                                    "image": {
                                        "type": "external",
                                        "external": {
                                            "url": images[index]
                                        }
                                    }
                                }
            )
        return children

    def video_withcaption_json(self,videos:list,caption_strings)->list:
        """
        Create the JSON for the video with caption.

        Parameters:
        videos (list): The list of images.
        caption_strings (list): The list of caption strings.

        Returns:
        list: The JSON for the video with caption.
        """

        children=[]
        for index in range(len(videos)):
            children.append({
                                "object": "block",
                                    "type": "bookmark",
                                    "bookmark": {
                                        "caption": [],
                                        "url": caption_strings[index]
                                    }
                                })
            children.append({
                                "object": "block",
                                    "type": "video",
                                    "video": {
                                        "type": "external",
                                        "external": {
                                            "url": videos[index]
                                        }
                                    }
                                }
            )
        return children

    def web_bookmarks_json(self,web_bookmarks_json) -> list:
        """
        Create the JSON for the web bookmarks.

        Parameters:
        web_bookmarks_json (list): The list of web bookmarks.
        
        Returns:
        list: The JSON for the web bookmarks.
        """

        return [
                            {
                                "object": "block",
                                    "type": "bookmark",
                                    "bookmark": {
                                        "caption": [],
                                        "url": web_bookmark_json
                                    }
                                }
                                for web_bookmark_json in web_bookmarks_json
                        ]

    def split_string_by_length(self, text, max_length):
        """
        Split the string by length.

        Parameters:
        text (str): The text to split.
        max_length (int): The maximum length.

        Returns:
        list: The list of chunks.
        """

        chunks = []
        current_chunk = ""
        lines = text.split("\n")
        for line in lines:
            if len(current_chunk) + len(line) <= max_length:
                current_chunk += line + "\n"
            else:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def write_to_notion_content(self,page_id: str,json_type: str, heading_string:str) -> None:
        """
        Write the JSON data to the Notion content.

        Parameters:
        page_id (str): The ID of the page.
        json_type (str): The type of JSON data.
        heading_string (str): The heading string.
        """

        headers = self.notion_information("2022-06-28")
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        try:
            if len(self.json_data_page_children[json_type]) > 0:
                for content_string in self.json_data_page_children[json_type]:
                    print(content_string['text'])
                    if content_string['text'] is None:
                        flag = 1
                        content = ''
                    else:
                        flag = 0
                        content = content_string['text']
                    images = content_string['images']
                    videos = content_string['videos']
                    pdf_links = content_string['pdf_links']
                    caption_strings = content_string['caption_strings']
                    web_bookmarks = content_string['web_bookmarks']
                    image_messages = content_string['image_messages']
                    video_messages = content_string['video_messages']

                    if flag == 0:
                        for index,chunk in enumerate(self.split_string_by_length(content,1500)):

                            input_string = ''.join(chunk)

                            if index == 0:
                                payload = {
                                    "children": 
                                        self.headingone_json(heading_string) +
                                        self.rich_text_json(input_string)
                                    }
                            else:
                                payload = {
                                    "children": 
                                        self.rich_text_json(input_string)
                                    }

                            response = requests.patch(
                                            url,
                                            headers=headers,
                                            json=payload,
                                            timeout=20
                                        )
                            if response.status_code == 200:
                                print("Json Post successfully to Notion!")
                                print(response.status_code)
                            else:
                                print("Error uploading String to Notion. Status code:",
                                        response.status_code)
                                print(response.status_code)
                                self.delete_notion_page(page_id,headers)
                    else:
                        payload = {"children": self.headingone_json(heading_string)}

                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Page to Notion. Status code:",
                                    response.status_code)
                            print(response.status_code)
                            self.delete_notion_page(page_id,headers)

                    if images is not None and image_messages is not None:
                        payload = {"children": self.image_withcaption_json(images,image_messages)}

                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Image to Notion. Status code:",
                                    response.status_code)
                            print(response.json())
                            self.delete_notion_page(page_id,headers)
                    elif images is not None:
                        payload = {"children": self.image_json(images)}

                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Image to Notion. Status code:",
                                    response.status_code)
                            print(response.status_code)
                            self.delete_notion_page(page_id,headers)
                    if videos is not None and video_messages is not None:
                        payload = {"children": self.video_withcaption_json(videos,video_messages)}

                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Video to Notion. Status code:",
                                    response.status_code)
                            print(response.status_code)
                            self.delete_notion_page(page_id,headers)
                    elif videos is not None:
                        payload = {"children": self.video_json(videos)}

                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Video to Notion. Status code:",
                                    response.status_code)
                            print(response.status_code)
                            self.delete_notion_page(page_id,headers)

                    if pdf_links is not None:
                        payload = {"children": self.pdf_json(pdf_links,caption_strings)}
                        headers = self.notion_information('2021-05-13')
                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading PDF to Notion. Status code:",
                                    response.status_code)
                            print(response.json())
                            self.delete_notion_page(page_id,headers)

                    if web_bookmarks is not None:
                        payload = {"children": self.web_bookmarks_json(web_bookmarks)}
                        headers = self.notion_information('2021-05-13')
                        response = requests.patch(url, headers=headers, json=payload, timeout=20)
                        if response.status_code == 200:
                            print("Json Post successfully to Notion!")
                            print(response.status_code)
                        else:
                            print("Error uploading Bookmark to Notion. Status code:",
                                    response.status_code)
                            print(response.json())
                            self.delete_notion_page(page_id,headers)

        except Exception as e:
            self.delete_notion_page(page_id,headers)
            print(str(e))

    def upload_to_notion(self):
        """
        Upload the JSON data to Notion.
        """

        status_code,response_content = self.write_to_notion_page()
        if status_code == 200:
            print("Page successfully Create to Notion!")
            page_id = response_content['id']
            for key, _ in self.json_data_page_children.items():
                self.write_to_notion_content(page_id,key,key)
        else:
            page_id = None
            print(response_content)
            print("Error uploading JSON data to Notion. Status code:", status_code)
        return page_id
