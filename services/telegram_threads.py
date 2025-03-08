"""
This module is used to extract the messages from the telegram group
"""
import os
import time
from telethon.sync import TelegramClient
from integrations.telegram.telegram_API import Telegram_API
from integrations.notion.notion_API import Notion_API
from integrations.onedrive.onedrive_API import OneDrive_API
from integrations.threads.threads import ThreadsGrabber

class ThreadsGrabService(object):
    """
    This class is used to extract the messages from the telegram group
    """
    def __init__(
            self,
            api_id,
            api_hash,
            groups_name,
            notion_token,
            databaseid,
            client_id,
            client_secret,
            tenant_id,
            userid,
            drive_id
            ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.groups_name = groups_name
        self.notion_token = notion_token
        self.databaseid = databaseid
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.userid = userid
        self.drive_id = drive_id
        self.oneapiservice = OneDrive_API(
                                self.client_id,
                                self.client_secret,
                                self.tenant_id,
                                self.userid,
                                self.drive_id)

    def json_to_notion_page(self,json_data):
        """
        This function is used to convert the JSON data to Notion page

        Args:
        json_data: dict: The JSON data

        Returns:
        payload: dict: The Notion page payload
        """

        return {
                'chat_id': {'rich_text': [{'text': {'content': json_data["chat_id"]}}]},
                'message_id': {'rich_text': [{'text': {'content': json_data["message_id"]}}]},
                'Threads_ID': {'rich_text': [{'text': {'content': json_data["id"]}}]},
                'Classification': {'select': {'name': json_data["label"]}},
                'tag': {'select': {'name': json_data["tag"]}},
                'Name': {'title': [{'text': {'content': json_data["subject"]}}]},
                'Date': {'date': {'start': json_data["date"]}},
                'ThreadsURL': {'url':  json_data["ThreadsURL"]}
                }

    def main(self):
        """
        Main function to start the service
        """

        for group_name in self.groups_name:
            with TelegramClient('grabbed', self.api_id, self.api_hash) as client:
                created_date,link,video_messages,image_messages,message_ids,chat_ids = \
                                                client.loop.run_until_complete(
                                                            Telegram_API(
                                                                    self.api_id,
                                                                    self.api_hash,
                                                                    group_name,
                                                                    client
                                                                    ).take_messages()
                                                        )
            failed = []
            link = link[::-1]
            video_messages = video_messages[::-1]
            image_messages = image_messages[::-1]
            message_ids =  message_ids[::-1]
            chat_ids = chat_ids[::-1]
            for index,item in enumerate(link):
                print(message_ids[index],chat_ids[index])
                if item is not None and "https://www.threads.net" in item and \
                    item.split('/')[3].replace('@','') != '3049346217':
                    if item.split('/')[3].replace('@','') == '3184274590':
                        item = item.replace('3184274590', 'rice.9547')
                    elif item.split('/')[3].replace('@','') == '321242492':
                        item = item.replace('321242492', 'koshuang')
                    notionAPIserviceb4 = Notion_API(self.notion_token,self.databaseid, '', '')
                    try:
                        _,subject = notionAPIserviceb4.check_notion_db_record(
                                                                ["chat_id","message_id"],
                                                                [str(chat_ids[index]),str(message_ids[index])]
                                                                )
                    except Exception as e:
                        print(str(e))
                        subject = []

                    if len(subject) != 0:
                        print("Already exists in Notion")
                    else:
                        data = ThreadsGrabber.scrape_thread(item)
                        if data['thread'] is not None:
                            json_data = {}
                            json_data['id'] = data['thread']['pk']
                            json_data['label'] = item.split('/')[3].replace('@','')
                            json_data['subject'] = item
                            if group_name == 'threadsssssssgir':
                                json_data['tag'] = 'girls'
                            elif group_name == 'tammmmmmmmmmmmmmyself':
                                json_data['tag'] = 'IT'
                            json_data['ThreadsURL'] = data['thread']['url']
                            json_data['date'] = created_date
                            json_data['chat_id'] = str(chat_ids[index])
                            json_data['message_id'] = str(message_ids[index])
                            #print([i for i in data['replies'] if data['replies'] is not None])
                            notionAPIserviceb4 = Notion_API(
                                            self.notion_token,
                                            self.databaseid,
                                            '',
                                            '')

                            payload = self.json_to_notion_page(json_data)
                            if item.split('?')[0] == data['thread']['url'] or item == data['thread']['url']:
                                json_data_page_children = {}
                                image_messages = []
                                video_messages = []
                                if data['thread']['images'] is not None:
                                    for index,image in enumerate(data['thread']['images']):
                                        ThreadsGrabber.download_media(
                                                        image,
                                                        #data/threads/
                                                        f"D:\\{json_data['id']}_{index} \
                                                            .jpg"
                                                    )
                                        time.sleep(5)
                                        _ = self.oneapiservice.upload_onedrive_file(
                                                        f"D:\\{json_data['id']}_{index} \
                                                            .jpg",
                                                        f"{json_data['id']}_{index}.jpg",
                                                        'Notion/Threads'
                                                    )
                                        time.sleep(5)
                                        sharelink = self.oneapiservice.get_onedrive_sharelink(
                                                        "Notion/Threads",
                                                        f"{json_data['id']}_{index}.jpg"
                                                    )
                                        image_messages.append(sharelink)
                                if data['thread']['videos'] is not None:
                                    for index,video in enumerate(data['thread']['videos']):
                                        ThreadsGrabber.download_media(
                                                        video,
                                                        f"D:\\{json_data['id']}_{index}.mp4"
                                                    )
                                        time.sleep(5)
                                        _ = self.oneapiservice.upload_onedrive_file(
                                                        f"D:\\{json_data['id']}_{index}.mp4",
                                                        f"{json_data['id']}_{index}.mp4",
                                                        'Notion/Threads'
                                                    )
                                        time.sleep(5)
                                        sharelink = self.oneapiservice.get_onedrive_sharelink(
                                                        "Notion/Threads",
                                                        f"{json_data['id']}_{index}.mp4"
                                                    )
                                        video_messages.append(sharelink)
                                if not image_messages:
                                    image_messages = None
                                if not video_messages:
                                    video_messages = None

                                json_data_page_children["Post"] = [
                                                        {
                                                            "text":data['thread']['text'],
                                                            'images':data['thread']['images'],
                                                            'videos':data['thread']['videos'],
                                                            'pdf_links':None,
                                                            'caption_strings':None,
                                                            'web_bookmarks':None,
                                                            'image_messages':image_messages,
                                                            'video_messages':video_messages
                                                        }
                                        ]
                                json_data_page_children["Replies"] = []
                                if 'replies' in data: # pylint: disable=unsubscriptable-object
                                    for perdata in data['replies']: # pylint: disable=unsubscriptable-object
                                        image_messages = []
                                        video_messages = []
                                        if perdata.get('images') is not None:
                                            for index,image in enumerate(perdata['images']): # pylint: disable=unsubscriptable-object
                                                ThreadsGrabber.download_media(
                                                            image,
                                                            f"D:\\ \
                                                                {json_data['id']}_{index} \
                                                                .jpg"
                                                        )
                                                time.sleep(2)
                                                _ = self.oneapiservice.upload_onedrive_file(
                                                            f"D:\\ \
                                                                {json_data['id']}_{index} \
                                                                .jpg",
                                                            f"{json_data['id']}_{index}.jpg",
                                                            'Notion/Threads'
                                                        )
                                                time.sleep(1)
                                                sharelink = \
                                                        self.oneapiservice.get_onedrive_sharelink(
                                                            "Notion/Threads",
                                                            f"{json_data['id']}_{index}.jpg"
                                                        )
                                                image_messages.append(sharelink)
                                        if perdata.get('videos') is not None: # pylint: disable=unsubscriptable-object
                                            for index,video in enumerate(perdata['videos']): # pylint: disable=unsubscriptable-object
                                                ThreadsGrabber.download_media(
                                                            video,
                                                            f"D:\\{json_data['id']}_{index}.mp4"
                                                        )
                                                time.sleep(5)
                                                _ = self.oneapiservice.upload_onedrive_file(
                                                            f"D:\\{json_data['id']}_{index}.mp4",
                                                            f"{json_data['id']}_{index}.mp4",
                                                            'Notion/Threads'
                                                        )
                                                time.sleep(5)
                                                sharelink = \
                                                        self.oneapiservice.get_onedrive_sharelink(
                                                            "Notion/Threads",
                                                            f"{json_data['id']}_{index}.mp4"
                                                        )
                                                video_messages.append(sharelink)

                                        self.oneapiservice.close_onedrive_connection()
                                        if not image_messages:
                                            image_messages = None
                                        if not video_messages:
                                            video_messages = None

                                        json_data_page_children["Replies"].append(
                                                                {
                                                                    "text":perdata['text'], # pylint: disable=unsubscriptable-object
                                                                    'images':perdata['images'], # pylint: disable=unsubscriptable-object
                                                                    'videos':perdata['videos'], # pylint: disable=unsubscriptable-object
                                                                    'pdf_links':None,
                                                                    'caption_strings':None,
                                                                    'web_bookmarks':None,
                                                                    'image_messages':image_messages,
                                                                    'video_messages':video_messages
                                                                }
                                                )

                                notionAPIservice = Notion_API(
                                                        self.notion_token,
                                                        self.databaseid,
                                                        payload,
                                                        json_data_page_children
                                                    )

                                notionAPIservice.upload_to_notion()
                            else:
                                grabbed_link = data['thread']['url']
                                print(f'The search link: {grabbed_link}')
                                print(f'The thread real link: {item}')
                                failed.append(chat_ids[index])
                                failed.append(item)
                                #os.system('pause')
                        else:
                            print(item)
                            failed.append(message_ids[index])
                            failed.append(item)
            print(failed)
            #os.system('pause')
