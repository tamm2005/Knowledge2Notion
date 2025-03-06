"""
This module is used to extract the email from the gmail account 
and upload it to the Notion database.
"""
from integrations.gmail.gmail_IMAP import gmail_IMAP
from integrations.notion.notion_API import Notion_API
from services.googledriveservice.ENPRO_googledrive import ENPROgoogledriveETL

class gmailIMAPReceivedService(object):
    """
    This class is used to extract the email from the gmail account 
    and upload it to the Notion database
    """
    def __init__(self,email_id,gmail_password,labels,notion_token,databaseid):
        self.email_id = email_id
        self.gmail_password = gmail_password
        self.labels = labels
        self.notion_token = notion_token
        self.databaseid = databaseid
        self.mailbox = 'INBOX'
        self.gmailIMAPservice = gmail_IMAP(self.email_id,self.gmail_password,self.mailbox)

    def json_to_notion_page(self,json_data):
        """
        This function converts the json data into the notion page format
        """
        return {
                        'ID': {'rich_text': [{'text': {'content': json_data["id"]}}]},
                        'Classification': {'select': {'name': json_data["label"]}},
                        'Name': {'title': [{'text': {'content': json_data["subject"]}}]},
                        'Date Received': {'date': {'start': json_data["date"]}},
                        'From': {'email': json_data["from"]},
                        'To': {'rich_text': [{'text': {'content': json_data["to"]}}]}
                    }

    def main(self):
        """
        Main function to start the service
        """
        for label in self.labels:
            messages = self.gmailIMAPservice.gmail_IMAP_setting(label)
            messages = messages[::-1]
            for message in messages[0].split():
                json_data,json_data_page_children = self.gmailIMAPservice.get_email(message,label)
                if label == 'ENPRO':
                    ENPROgooglddrive = ENPROgoogledriveETL(
                                            json_data_page_children['Post'][0]['text'])
                    website_content = ENPROgooglddrive.get_email_url()
                    pdf_links,caption_strings = ENPROgooglddrive.grab_google_drive_file_link(
                                                    website_content)
                    json_data_page_children['Post'][0]['pdf_links'] = pdf_links
                    json_data_page_children['Post'][0]['caption_strings'] = caption_strings

                payload = self.json_to_notion_page(json_data)

                notionAPIservice = Notion_API(
                                        self.notion_token,
                                        self.databaseid,
                                        payload,
                                        json_data_page_children)
                subject, _ = notionAPIservice.read_notion_database(json_data["id"],"ID")
                if json_data["id"] in subject:
                    print("Email already exists in Notion")
                    break
                else:
                    notionAPIservice.upload_to_notion()
