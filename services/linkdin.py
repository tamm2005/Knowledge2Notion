import os
import time
from integrations.linkdin.linkdin import fetch_linkedin_jobs
from integrations.notion.notion_API import Notion_API
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        self.job_description_list, self.job_id_data, self.num_applicants, self.page_content = fetch_linkedin_jobs(self.keywords,
                                 self.start,
                                 self.stop_sec)

    def main(self):
        for index,notion_data in enumerate(self.job_description_list):
            notion_service = Notion_API(
                                    self.notion_token,
                                    self.databaseid,
                                    notion_data,
                                    self.page_content
                                )
            job_id = self.job_id_data[index]
            status, notion_resp = notion_service.read_notion_response(job_id, "job_id")
            results = notion_resp.get("results", [])

            if not results:
                print(f"[NEW] job_id {job_id} not found in Notion.")
                status_code,response_content = notion_service.write_to_notion_page()
                
                if status_code == 200:
                    print("Page successfully Create to Notion!")
                    page_id = response_content['id']
                    for key, _ in self.page_content[index].items():
                        notion_service.write_to_notion_content(page_id,key,key)
                else:
                    page_id = None
                    print(response_content)
                    print("Error uploading JSON data to Notion. Status code:", status_code)

                print(status_code)
                print(notion_data)
                print(json.dumps(response_content, ensure_ascii=False, indent=2))
                continue  # Or insert logic

            page_id = results[0]["id"]
            rich_texts = results[0]["properties"]["num_applicants"]["rich_text"][0]["text"]["content"]
            if self.num_applicants[index] != rich_texts:
                print(f"[UPDATE] job_id {job_id}")
                payload = {
                    "properties": {
                        'num_applicants': {'rich_text': [{'text': {'content': self.num_applicants[index]}}]}
                    }
                }
                print(payload)
                print(rich_texts)
                notion_service.update_num_of_applicants(page_id, payload)
            else:
                print(f"[SKIP] job_id {job_id} unchanged.")
