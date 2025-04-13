import requests
from bs4 import BeautifulSoup
import os
import time
from typing import List, Dict
import json

def fetch_linkedin_jobs(keywords: str = "DataEngineer", start: int=0, stop_sec:int=10, flag:int=1) -> List[Dict]:
    notion_data,job_id_data,num_applicants_data = [], [], []
    while start < 1000 and flag == 1:
        job_id_list = []
        print(start)
        url = f"https://hk.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&start={start}"
        response = requests.get(url)
        list_data = response.text
        list_soup = BeautifulSoup(list_data, "html.parser")
        page_jobs = list_soup.find_all("li")

        for job in page_jobs:
            try:
                base_card_div = job.find("div",{"class":"base-card"})
                job_id = base_card_div.get("data-entity-urn").split(":")[3]
                job_id_list.append(job_id)
            except:
                flag = 0
                break
        if flag == 1:
            for job_id in job_id_list:
                job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                job_response = requests.get(job_url)
                job_soup = BeautifulSoup(job_response.text, "html.parser")
                job_post = {}
                job_id_total = job_id
                # Try to extract and store the job title
                try:
                    job_title = job_soup.find("h2", {"class":"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip()
                except:
                    job_title = ''
                    
                # Try to extract and store the company name
                try:
                    company_name=job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
                except:
                    company_name=''

                # Try to extract and store the job title
                try:
                    div = job_soup.find(
                        'div',
                        class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden'
                    )

                    contents = div.get_text(separator=' ', strip=True) if div else ''
                except:
                    contents=''
                    
                # Try to extract and store the time posted
                try:
                    time_posted=job_soup.find("span", {"class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip()
                except:
                    time_posted=''
                    
                # Try to extract and store the number of applicants
                try:
                    num_applicants=job_soup.find("span", {"class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"}).text.strip()
                except:
                    num_applicants=''

                notion_data.append({
                    'job_id': {'title': [{'text': {'content': job_id_total}}]},
                    'job_title': {'rich_text': [{'text': {'content': job_title}}]},
                    'company_name': {'rich_text': [{'text': {'content': company_name}}]},
                    'contents': {'rich_text': [{'text': {'content': contents}}]},
                    'time_posted': {'rich_text': [{'text': {'content': time_posted}}]},
                    'num_applicants': {'rich_text': [{'text': {'content': num_applicants}}]}
                    }
                )

                job_id_data.append(job_id)
                num_applicants_data.append(num_applicants)

            start += len(page_jobs)
            time.sleep(stop_sec)  # Sleep for 1 second to avoid hitting the server too hard
    return notion_data, job_id_data, num_applicants_data