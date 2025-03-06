"""
This module is used to interact with the Gmail API. 
It is used to fetch emails from the Gmail account and upload them to the Notion database.
"""
import base64
import re
from typing import Tuple,Any
import emoji
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class gmail_IMAP:
    """Class representing a gmail api service"""

    def __init__(self,token:str,email_id:str,label:str) -> None:
        self.token = token
        self.email_id = email_id
        self.label = label
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    def remove_emojis(self,text:str) -> str:
        """
        Remove emojis from the input text.

        Parameters:
        text (str): The input text containing emojis.

        Returns:
        str: The text with emojis removed.
        """

        emoji_pattern = re.compile(emoji.get_emoji_regexp())
        return emoji_pattern.sub(r'', text)

    def google_auth(self) -> Any:
        """
        Authenticate the user and build the Gmail service.

        Returns:
        Any: service.
        """

        creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)
        # Retrieve a list of Gmail messages
        #results = service.users().messages().list(
        #    userId=self.email_id,
        #    q=f'label:{self.label}'
        #).execute()
        #messages = results.get('messages', [])
        return service

    def get_gmail_message(self, service, message) -> Tuple[dict, dict, list]:
        """
        Get the Gmail message.
        
        Parameters:
        service (Any): The Gmail service.

        message (dict): The message to get.

        Returns:
        Tuple[dict, dict, list]: A tuple containing the message, headers, and content.
        """

        msg = service.users().messages().get(
                userId=self.email_id,
                id=message['id'],
                format='full'
            ).execute()
        headers = msg.get('payload', {}).get('headers', [])
        parts = msg.get('payload', {}).get('parts', [])
        content = []
        for part in parts:
            if part['mimeType'] == 'text/plain':
                content_string = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                #content_without_emoji = gmail_operation.remove_emojis(content_string)
                content += [{"text":content_string,'images':None,'videos':None}]
        return msg,headers,content
    