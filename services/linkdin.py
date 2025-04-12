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
        #self.notion_list = self.json_to_notion_page(self.job_description_list)

    def json_to_notion_page(self,json_data):
        """
        This function is used to convert the JSON data to Notion page

        Args:
        json_data: dict: The JSON data

        Returns:
        payload: dict: The Notion page payload
        """

        return {
                'job_id': {'title': [{'text': {'content': json_data["job_id"]}}]},
                'job_title': {'rich_text': [{'text': {'content': json_data["job_title"]}}]},
                'company_name': {'rich_text': [{'text': {'company_name': json_data["company_name"]}}]},
                'contents': {'rich_text': [{'text': {'content': json_data["contents"]}}]},
                'time_posted': {'date': {'start': json_data["time_posted"]}},
                'num_applicants': {'rich_text': [{'text': {'content': json_data["num_applicants"]}}]}
                }
    
    def main(self):
        for notion_data in self.job_description_list:
            notion_service = Notion_API(
                                    self.notion_token,
                                    self.databaseid,
                                    notion_data,
                                    {}
                                )
            status_code,response_content = notion_service.write_to_notion_page()