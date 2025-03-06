"""
This is the main file to start the service
"""
import os
from services.gmail import gmailIMAPReceivedService
from dotenv import load_dotenv

class gmailIMAPController:
    """
    Controller class to start the service
    """
    def __init__(self,email_id_para,gmail_password_para,notion_token_para,databaseid_para,labels):
        self.email_id = email_id_para
        self.gmail_password = gmail_password_para
        self.labels = labels
        self.notion_token = notion_token_para
        self.databaseid = databaseid_para
        self.imap_service = gmailIMAPReceivedService(
                                self.email_id,
                                self.gmail_password,
                                self.labels,
                                self.notion_token,
                                self.databaseid
                                )

    def main(self):
        """
        Main function to start the service
        """

        self.imap_service.main()

if __name__ == "__main__":

    try:
        email_id = os.getenv('EMAIL_ID')
    except KeyError as e:
        print("email_id not found in the environment variables")

    try:
        gmail_password = os.getenv('GMAIL_PASSWORD')
    except KeyError as e:
        print("gmail_password not found in the environment variables")

    try:
        notion_token = os.getenv('NOTION_TOKEN')
    except KeyError as e:
        print("NOTION_TOKEN not found in the environment variables")

    try:
        databaseid = os.getenv('NOTION_GMAIL_DATABASE_ID')
    except KeyError as e:
        print("NOTION_THREADS_DATABASE_ID not found in the environment variables")
    
    try:
        labels = os.getenv('GMAIL_LABEL').split()
    except KeyError as e:
        print("NOTION_THREADS_DATABASE_ID not found in the environment variables")

    #load_dotenv("utils/.env")
    #email_id = os.getenv("email_id")
    #gmail_password = os.getenv("gmail_password")
    #notion_token = os.getenv("notion_token")
    #databaseid = os.getenv("notion_gmail_database_id")

    gmailIMAPController(email_id,gmail_password,notion_token,databaseid,labels).main()
