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
        self.flag = flag
        self.job_description_list = fetch_linkedin_jobs(self.keywords,
                                 self.start,
                                 self.stop_sec)
        self.notion_service = Notion_API(self.notion_token, self.databaseid)
    
    def main(self):
        notionAPIservice = Notion_API(
                                self.notion_token,
                                self.databaseid,
                                self.job_description_list,
                                []
                            )
        status_code,response_content = notionAPIservice.write_to_notion_page()