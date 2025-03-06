"""
This module is used to extract the messages from the telegram group
"""
from telethon.sync import TelegramClient
from integrations.telegram.telegram_API import Telegram_API

class TelegramAPIService(object):
    """
    This class is used to extract the messages from the telegram group
    """

    def __init__(self,api_id,api_hash,groups_name):
        self.api_id = api_id
        self.api_hash = api_hash
        self.groups_name = groups_name

    def main(self):
        """
        Main function to start the service
        """

        for group_name in self.groups_name:
            with TelegramClient('grabbed', self.api_id, self.api_hash) as client:
                _,_,video_messages,image_messages = client.loop.run_until_complete(
                                                        Telegram_API(
                                                                self.api_id,
                                                                self.api_hash,
                                                                group_name,
                                                                client
                                                                ).take_messages()
                                                        )
            with TelegramClient('grabbed', self.api_id, self.api_hash) as client:
                for message in video_messages:
                    client.loop.run_until_complete(
                                    Telegram_API(
                                        self.api_id,
                                        self.api_hash,
                                        group_name,
                                        client
                                        ).download_media(message,'video')
                                )
                for message in image_messages:
                    client.loop.run_until_complete(
                                    Telegram_API(
                                        self.api_id,
                                        self.api_hash,
                                        group_name,
                                        client
                                        ).download_media(message,'image')
                                )
