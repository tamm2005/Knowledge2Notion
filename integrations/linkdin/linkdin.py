import requests
from bs4 import BeautifulSoup
import os
import time
from typing import List, Dict
import json

def fetch_linkedin_jobs(keywords: str = "DataEngineer", start: int=0, stop_sec:int=10, flag:int=1) -> List[Dict]:
    job_id_total,job_title,company_name,contents,time_posted,num_applicants = [],[],[],[],[],[]
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
                print(job_url)
                job_response = requests.get(job_url)
                print(job_response)
                job_soup = BeautifulSoup(job_response.text, "html.parser")
                job_post = {}
                job_id_total.append(job_id)
                # Try to extract and store the job title
                try:
                    job_title.append(job_soup.find("h2", {"class":"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip())
                except:
                    job_title.append('')
                    
                # Try to extract and store the company name
                try:
                    company_name.append(job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip())
                except:
                    company_name.append('')

                # Try to extract and store the job title
                try:
                    contents.append(job_soup.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden').text.strip())
                except:
                    contents.append('')
                    
                # Try to extract and store the time posted
                try:
                    time_posted.append(job_soup.find("span", {"class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip())
                except:
                    time_posted.append('')
                    
                # Try to extract and store the number of applicants
                try:
                    num_applicants.append(job_soup.find("span", {"class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"}).text.strip())
                except:
                    num_applicants.append('')

            start += len(page_jobs)
            time.sleep(stop_sec)  # Sleep for 1 second to avoid hitting the server too hard
    return {
                'job_id': {'title': [{'text': {'content': job_id_total}}]},
                'job_title': {'rich_text': [{'text': {'content': job_title}}]},
                'company_name': {'rich_text': [{'text': {'company_name': company_name}}]},
                'contents': {'rich_text': [{'text': {'content': contents}}]},
                'time_posted': {'date': {'start': time_posted}},
                'num_applicants': {'rich_text': [{'text': {'content': num_applicants}}]}
                }
    
    '''{
        "job_id": job_id_total,
        "job_title": job_title,
        "company_name": company_name,
        "contents": contents,
        "time_posted": time_posted,
        "num_applicants": num_applicants
    }'''