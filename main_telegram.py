"""
This is the main file for the telegram service. It is responsible for the following:
"""
import os
from dotenv import load_dotenv
from services.telegram import TelegramAPIService
from services.telegram_threads import ThreadsGrabService

class TelegramAPIController(object):
    """
    This class is responsible for the following:
    """
    def __init__(self,
                api_id_para,
                api_hash_para,
                notion_token_para,
                databaseid_para,
                client_id_para,
                client_secret_para,
                tenant_id_para,
                user_id_para,
                drive_id_para,
                groups_name):
        self.api_id = api_id_para
        self.api_hash = api_hash_para
        self.notion_token = notion_token_para
        self.client_id = client_id_para
        self.client_secret = client_secret_para
        self.tenant_id = tenant_id_para
        self.user_id = user_id_para
        self.drive_id = drive_id_para
        self.databaseid = databaseid_para
        self.groups_name = groups_name
        self.grab_tele_group = []
        self.telegram_service = TelegramAPIService(self.api_id,self.api_hash,self.grab_tele_group)
        self.threads_service = ThreadsGrabService(self.api_id,
                                                self.api_hash,
                                                self.groups_name,
                                                self.notion_token,
                                                self.databaseid,
                                                self.client_id,
                                                self.client_secret,
                                                self.tenant_id,
                                                self.user_id,
                                                self.drive_id)

    def main(self):
        """
        Main function to start the service
        """
        self.threads_service.main()
        #self.telegram_service.main()

if __name__ == "__main__":
    try:
        api_id = os.getenv('API_ID')
    except KeyError as e:
        print("API_ID not found in the environment variables")

    try:
        api_hash = os.getenv('API_HASH')
    except KeyError as e:
        print("API_HASH not found in the environment variables")

    try:
        notion_token = os.getenv('NOTION_TOKEN')
    except KeyError as e:
        print("NOTION_TOKEN not found in the environment variables")

    try:
        databaseid = os.getenv('NOTION_THREADS_DATABASE_ID')
    except KeyError as e:
        print("NOTION_THREADS_DATABASE_ID not found in the environment variables")

    try:
        client_id = os.getenv('ONEDRIVE_SERVICE_CLIENT_ID')
    except KeyError as e:
        print("ONEDRIVE_SERVICE_CLIENT_ID not found in the environment variables")

    try:
        client_secret = os.getenv('ONEDRIVE_SERVICE_CLIENT_SECRET')
    except KeyError as e:
        print("ONEDRIVE_SERVICE_CLIENT_SECRET not found in the environment variables")

    try:
        tenant_id = os.getenv('ONEDRIVE_SERVICE_TENANT_ID')
    except KeyError as e:
        print("ONEDRIVE_SERVICE_TENANT_ID not found in the environment variables")

    try:
        user_id = os.getenv('ONEDRIVE_USERID')
    except KeyError as e:
        print("ONEDRIVE_USERID not found in the environment variables")

    try:
        drive_id = os.getenv('ONEDRIVE_DRIVE_ID')
    except KeyError as e:
        print("ONEDRIVE_DRIVE_ID not found in the environment variables")

    try:
        groups_name = os.getenv('TELEGRAM_THREAD_GROUP').split()
    except KeyError as e:
        print("TELEGRAM_THREAD_GROUP not found in the environment variables")

    '''load_dotenv("utils/.env")
    api_id = os.getenv("api_id")
    api_hash = os.getenv("api_hash")
    notion_token = os.getenv("notion_token")
    databaseid = os.getenv("notion_threads_database_id")
    client_id = os.getenv("onedrive_service_client_id")
    client_secret = os.getenv("onedrive_service_client_secret")
    tenant_id = os.getenv("onedrive_service_tenant_id")
    user_id = os.getenv("onedrive_userid")
    drive_id = os.getenv("onedrive_drive_id")
    '''
    TelegramAPIController(
                        api_id,
                        api_hash,
                        notion_token,
                        databaseid,
                        client_id,
                        client_secret,
                        tenant_id,
                        user_id,
                        drive_id,
                        groups_name
                        ).main()
