"""
This module contains the Gmail_IMAP class, 
which is used to connect to the Gmail IMAP server and fetch emails with a given label.
"""
from datetime import datetime
from typing import Tuple
import email
import imaplib
from email.header import decode_header

class gmail_IMAP(object):
    """
    Class representing a Gmail IMAP service.
    """

    def __init__(self,#token:str,database_id:str,
                    username:str,password:str,mailbox) -> None:
        #self.token = token #'secret_HubXVEuvnD68G2wVSsUUnbQKkFl5nJ43xHyrq7wvmnO'
        #self.database_id = database_id #'3c45d0d84b0649a7b01038cca1167a90'
        self.username = username #tamm2005@gmail.com
        self.password = password #'miie cmvo zqdz pplc'
        self.mailbox = mailbox

    def gmail_IMAP_setting(self,label:str) -> list:
        """
        Connect to the Gmail IMAP server and fetch the emails with the given label.

        Parameters:
        label (str): The label to search for.

        Returns:
        list: A list of messages.
        """

        imap_server = imaplib.IMAP4_SSL(host='imap.gmail.com',port='993')

        # Log in to your Gmail account
        imap_server.login(self.username, self.password)

        # Select the mailbox (e.g., 'INBOX') from which you want to fetch emails
        imap_server.select(self.mailbox)

        # Search for email messages with the label "enpro"
        _, messages = imap_server.search(None, f'X-GM-LABELS "{label}"')

        imap_server.logout()

        return messages

    def decode_mime_word(self,encoded_word:str) -> str:
        """
        Decode a MIME word to a Unicode string.
        
        Parameters:
        encoded_word (str): The MIME word to decode.

        Returns:
        str: The decoded Unicode string.
        """

        decoded_bytes, charset = decode_header(encoded_word)[0]
        if charset:
            return decoded_bytes.decode(charset)
        return decoded_bytes

    def get_email(self,message_id:str,label:str) -> Tuple[dict,dict]:
        """
        Get the email with the given message ID.
        
        Parameters:
        message_id (str): The message ID of the email to get.
        label (str): The label of the email.
        
        Returns:
        Tuple[dict,dict]: A tuple containing the email data and the email content.
        """

        imap_server = imaplib.IMAP4_SSL(host='imap.gmail.com',port='993')

        imap_server.login(self.username, self.password)

        imap_server.select(self.mailbox)

        # Fetch the email for the given message ID
        _, email_data = imap_server.fetch(message_id, '(RFC822)')

        # The email data is returned as a tuple, with the actual email content in the second element
        raw_email = email_data[0][1]

        # Parse the raw email data
        msg = email.message_from_bytes(raw_email)
        new_datetime = msg['Date'].split('+')[0] + ' +' + msg['Date'].split('+')[1].split(' (')[0]
        json_data = {}
        json_data['id'] = msg['Message-ID']
        json_data['label'] = label
        json_data['subject'] = self.decode_mime_word(msg['Subject'])
        json_data['date'] = datetime.strptime(new_datetime, "%a, %d %b %Y %H:%M:%S %z")\
                    .strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        json_data["from"] = msg['From']
        json_data["to"] = msg['To']
        #json_data["content"] = ''
        json_data_page_children = {}
        # Extract the email body
        if msg.is_multipart():
            content = []
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    email_body = part.get_payload(decode=True).decode('utf-8')
                    content += [
                        {
                            "text": email_body,
                            'images': None,
                            'videos': None,
                            'pdf_links': None,
                            'caption_strings': None,
                            'web_bookmarks': None,
                            'image_messages': None,
                            'video_messages': None
                        }
                    ]
                    break
            json_data_page_children["Post"] = content
        else:
            email_body = msg.get_payload(decode=True).decode('utf-8')
            json_data_page_children["Post"] = [
                {
                    "text": email_body,
                    'images': None,
                    'videos': None,
                    'pdf_links': None,
                    'caption_strings': None,
                    'web_bookmarks': None,
                    'image_messages': None,
                    'video_messages': None
                }
            ]
        imap_server.logout()
        return json_data,json_data_page_children
