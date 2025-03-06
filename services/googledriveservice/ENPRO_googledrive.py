"""
This module is used to extract the URL from the email body and 
extract the PDF links and caption strings from the Google Drive
"""
import re
import json
import requests
from bs4 import BeautifulSoup

class ENPROgoogledriveETL(object):
    """
    This class is used to extract the URL from the email body and 
    extract the PDF links and caption strings from the Google Drive
    """
    def __init__(self,email_body:str) -> str:
        self.email_body = email_body

    def get_email_url(self) -> str:
        """
        This function is used to extract the URL from the email body

        Returns:
        website_content: str: The content of the website
        """

        start_index = self.email_body.index("You can view the newsletter by clicking here:")
        start_index += len("You can view the newsletter by clicking here:")
        sub_string = "You're receiving this newsletter because you have shown interest in Englishgram IGPRO."
        end_index = self.email_body.index(
                        sub_string,
                        start_index)
        url = self.email_body[start_index:end_index].strip()

        # Send a GET request to the URL and retrieve the content
        response = requests.get(url,timeout=20)

        # Get the content of the website
        website_content = response.text

        return website_content

    def fix_encoding(self,misencoded_string:str) -> str:
        """
        This function is used to fix the encoding of the string

        Args:
        misencoded_string: str: The misencoded string
        
        Returns:
        corrected_str: str: The corrected string
        """

        # Decode the string assuming it was incorrectly decoded as ISO-8859-1
        bytes_str = misencoded_string.encode('iso-8859-1')
        # Re-decode it correctly as UTF-8
        corrected_str = bytes_str.decode('utf-8')
        corrected_str = corrected_str.replace(' ','\xa0')
        return corrected_str

    def grab_google_drive_file_link(self,website_content:str) -> list:
        """
        This function is used to extract the PDF links and caption strings from the Google Drive

        Args:
        website_content: str: The content of the website

        Returns:
        pdf_links: list: The list of PDF links
        caption_strings: list: The list of caption strings
        """

        # Print the content of the website
        #print(website_content)
        soup = BeautifulSoup(website_content, 'html.parser')
        # Extract the URL
        url_element = soup.find_all('a')[1]
        url = url_element['href'] if url_element else None
        response = requests.get(url,timeout=20)
        # Get the content of the website
        website_content = response.text
        # Parse the HTML document
        soup = BeautifulSoup(website_content, 'html.parser')
        # Find the script tag with the desired JavaScript code
        script_tag = soup.find('script', text=re.compile(r"window\['_DRIVE_ivd'\]")).string.strip()
        #.encode('utf8').decode('unicode_escape')
        script_tag = re.search(r"window\['_DRIVE_ivd'\] = '(.+?)'", script_tag).group(1)
        script_tag = json.loads(script_tag.encode('utf8').decode('unicode_escape'))
        pdf_links = []
        caption_strings = []
        for items in script_tag:
            if items is not None and isinstance(items, list):
                for item in items:
                    if not isinstance(item[0], list):
                        try:
                            response = requests.get(
                                'https://drive.google.com/drive/folders/' + item[0],
                                timeout=20)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            script_tag = soup.find(
                                            'script',
                                            text=re.compile(r"window\['_DRIVE_ivd'\]")
                                            ).string.strip()
                            script_tag = re.search(
                                            r"window\['_DRIVE_ivd'\] = '(.+?)'",
                                            script_tag
                                            ).group(1)
                            script_tag = json.loads(
                                            script_tag.encode('utf8').decode('unicode_escape')
                                            )
                            for itemss in script_tag:
                                if itemss is not None and isinstance(itemss, list):
                                    for itemsss in itemss:
                                        pdf_links.append(
                                            'https://drive.google.com/file/d/' + itemsss[0]
                                            )
                                        caption_strings.append(self.fix_encoding(itemsss[2]))
                        except Exception as e:
                            print(str(e))
        return pdf_links,caption_strings
