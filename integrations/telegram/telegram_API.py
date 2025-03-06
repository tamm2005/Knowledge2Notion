"""
This module contains the Telegram_API class which is 
responsible for interacting with the Telegram API.
"""
import os
from typing import Tuple,List,Any
import sys
from telethon.tl.types import MessageMediaDocument,DocumentAttributeFilename

class Telegram_API(object):
    """
    This class is responsible for interacting with the Telegram API.
    """

    def __init__(self,api_id,api_hash,group_name,client):
        self.api_id = api_id
        self.api_hash = api_hash
        self.group_name = group_name
        self.client = client
        self.current_file = None

    def grabbed_chennel_basic_info(self,channel_name:str) -> Tuple[str,int]:
        """
        Get the basic information of the channel.

        Args:
            channel_name (str): The name of the channel.

        Returns:
            Tuple[str,int]: The title and the number of participants of the channel.
        """

        # get all the channels that I can access
        channels = {d.entity.username: d.entity
                    for d in self.client.get_dialogs()
                    if d.is_channel}
        for d in self.client.get_dialogs():
            if d.is_channel:
                pass
                #print(f'{d.entity.title},{d.entity.username}')
        # choose the one that I want list users from
        channel = channels[channel_name]

        return channel.title,channel.participants_count

    async def progress_bar(self,current, total, file_name=None) -> None:
        """
        Display a progress bar in the console.

        Args:
            current (int): The current progress.
            total (int): The total progress.
            file_name (str, optional): The name of the file being downloaded. Defaults to None.
        """

        if not hasattr(self, 'current_file'):
            self.current_file = None

        if file_name and file_name != self.current_file:
            sys.stdout.write('\n')
            sys.stdout.flush()
            self.current_file = file_name

        progress = (current / total) * 100
        bar_length = 30
        filled_length = int(progress / 100 * bar_length)
        bar_size = '█' * filled_length + '-' * (bar_length - filled_length)
        status = f"Progress: |{bar_size}| {progress:.2f}%"

        if file_name:
            status += f" - {file_name}"

        sys.stdout.write(f"\r{status}")
        sys.stdout.flush()

    async def take_messages(self) -> \
            Tuple[str,List[str],List[Any],List[Any],List[int],List[int]]:
        """
        Get the messages from the Telegram group.

        Returns:
            Tuple[str,List[str],List[Message],List[Message],List[int],List[int]]: 
                The created date, the links, the video messages, the image messages, 
                the message IDs, and the chat IDs.
        """
        link = []
        video_messages = []
        image_messages = []
        message_ids = []
        chat_ids = []
        async for message in self.client.iter_messages(self.group_name, limit=None, reverse=True):
            message_ids.append(message.id)
            chat_ids.append(message.chat_id)
            created_date = message.date.strftime("%Y-%m-%dT%H:%M:%S%z")
            link.append(message.message)
            if isinstance(message.media, MessageMediaDocument):
                if message.media.document.mime_type.startswith('video'):
                    video_messages.append(message)
                elif message.media.document.mime_type.startswith('image'):
                    image_messages.append(message)
        return created_date,link,video_messages,image_messages,message_ids,chat_ids

    async def download_media(self, message, ext_name):
        """
        Download the media from the Telegram group.

        Args:
            message (Message): The message object.
            ext_name (str): The extension name of the media.
        """

        #async with TelegramClient('media', self.api_id, self.api_hash) as client:
        if isinstance(message.media, MessageMediaDocument):
            if message.media.document.mime_type.startswith(ext_name):
                for attr in message.media.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        os.makedirs(os.path.join("data", "telegram",self.group_name), exist_ok=True)
                        file_dir = os.path.join("data", "telegram", self.group_name,attr.file_name)
                        if not os.path.exists(file_dir):
                            await self.client.download_media(
                                            message.media,
                                            file_dir,
                                            progress_callback=lambda current,
                                            total: self.progress_bar(
                                                        current,
                                                        total,
                                                        attr.file_name
                                                        )
                                            )
