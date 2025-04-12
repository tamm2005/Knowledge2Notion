import os
from dotenv import load_dotenv
from services.linkdin import LinkdinGrabService

class LinkdinAPIController(object):
    """
    This class is responsible for the following:
    """
    def __init__(self,
                notion_token,
                databaseid):
        self.notion_token = notion_token
        self.databaseid = databaseid
        self.linkdin_service = LinkdinGrabService(
                                                self.notion_token,
                                                self.databaseid,
                                                )

    def main(self):
        """
        Main function to start the service
        """
        self.linkdin_service.main()
        #self.telegram_service.main()

if __name__ == "__main__":
    try:
        notion_token = os.getenv('NOTION_TOKEN')
    except KeyError as e:
        print("NOTION_TOKEN not found in the environment variables")

    try:
        databaseid = os.getenv('NOTION_LINKDIN_DATABASE_ID')
    except KeyError as e:
        print("NOTION_THREADS_DATABASE_ID not found in the environment variables")
    
    LinkdinAPIController(notion_token,databaseid).main()