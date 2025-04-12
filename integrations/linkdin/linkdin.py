import requests
from bs4 import BeautifulSoup
import os
import time
from typing import List, Dict

def fetch_linkedin_jobs(keywords: str = "DataEngineer", start: int=0, stop_sec:int=10, flag:int=1) -> List[Dict]:

    while start < 1000 and flag == 1:
        job_id_list = []
        print(start)
        url = f"https://hk.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&start={start}"
        response = requests.get(url)
        list_data = response.text
        list_soup = BeautifulSoup(list_data, "html.parser")
        page_jobs = list_soup.find_all("li")
        job_info = []

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
                job_post["job_id"] = job_id
                # Try to extract and store the job title
                try:
                    job_post["job_title"] = job_soup.find("h2", {"class":"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip()
                except:
                    job_post["job_title"] = None
                    
                # Try to extract and store the company name
                try:
                    job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
                except:
                    job_post["company_name"] = None

                # Try to extract and store the job title
                try:
                    job_post["contents"] = job_soup.find('div', class_='show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden').text.strip()
                except:
                    job_post["contents"] = None
                    
                # Try to extract and store the time posted
                try:
                    job_post["time_posted"] = job_soup.find("span", {"class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip()
                except:
                    job_post["time_posted"] = None
                    
                # Try to extract and store the number of applicants
                try:
                    job_post["num_applicants"] = job_soup.find("span", {"class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"}).text.strip()
                except:
                    job_post["num_applicants"] = None
                
                job_info.append(job_post)

            start += len(page_jobs)
            time.sleep(stop_sec)  # Sleep for 1 second to avoid hitting the server too hard
    
    return job_info