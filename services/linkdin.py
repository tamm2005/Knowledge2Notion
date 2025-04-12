import os
import time
from integrations.linkdin.linkdin import fetch_linkedin_jobs
from integrations.notion.notion_API import Notion_API

class LinkdinGrabService(object):
    def __init__(self,
                 notion_token:str,
                 databaseid:str,
                 keywords:str = "DataEngineer",
                 start:int = 0,
                 stop_sec:int = 10):
        self.notion_token = notion_token
        self.databaseid = databaseid
        self.keywords = keywords
        self.start = start
        self.stop_sec = stop_sec
        self.job_description_list = fetch_linkedin_jobs(self.keywords,
                                 self.start,
                                 self.stop_sec)
        import sys
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(self.job_description_list)
        self.notion_service = Notion_API(
                                self.notion_token,
                                self.databaseid,
                                self.job_description_list,
                                []
                            )
    
    def main(self):
        status_code,response_content = self.notion_service.write_to_notion_page()