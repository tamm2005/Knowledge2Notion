import json
import time
import datetime
from typing import Dict
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright
import requests


class ThreadsGrabber:
    """
    A class for scraping Threads posts and replies.
    """

    @staticmethod
    def clean_url(url: str) -> str:
        """
        Clean the given Threads URL to remove query parameters.

        Args:
            url (str): URL of the Threads post.

        Returns:
            str: Cleaned URL without query parameters.
        """
        if '?' in url:
            return url.split('?')[0]
        return url

    @staticmethod
    def safe_get(data, path, default=None):
        """
        Safely extract a value from a nested dictionary using JMESPath.

        Args:
            data (dict): The data dictionary to search.
            path (str): JMESPath search string.
            default: Default value if the path doesn't exist.

        Returns:
            Any: The value found or the default.
        """
        try:
            return jmespath.search(path, data) or default
        except Exception:
            return default

    @staticmethod
    def parse_thread(data: Dict) -> Dict:
        """
        Parse Threads JSON dataset for the most important fields.

        Args:
            data (Dict): JSON dataset containing Threads post data.

        Returns:
            Dict: Parsed data containing the most important fields.
        """
        if ThreadsGrabber.safe_get(data, "post.carousel_media[].image_versions2.candidates[1].url", []) == []:
            images = ThreadsGrabber.safe_get(data, "post.image_versions2.candidates[1].url", [])
        else:
            images = ThreadsGrabber.safe_get(data, "post.carousel_media[].image_versions2.candidates[1].url", [])

        if ThreadsGrabber.safe_get(data, "post.carousel_media[].video_versions[1].url", []) == []:
            videos = ThreadsGrabber.safe_get(data, "post.video_versions[1].url", [])
        else:
            videos = ThreadsGrabber.safe_get(data, "post.carousel_media[].video_versions[1].url", [])

        result = {
            "text": ThreadsGrabber.safe_get(data, "post.caption.text"),
            "published_on": ThreadsGrabber.safe_get(data, "post.taken_at"),
            "id": ThreadsGrabber.safe_get(data, "post.id"),
            "pk": ThreadsGrabber.safe_get(data, "post.pk"),
            "code": ThreadsGrabber.safe_get(data, "post.code"),
            "username": ThreadsGrabber.safe_get(data, "post.user.username"),
            "user_pic": ThreadsGrabber.safe_get(data, "post.user.profile_pic_url"),
            "user_verified": ThreadsGrabber.safe_get(data, "post.user.is_verified"),
            "like_count": ThreadsGrabber.safe_get(data, "post.like_count"),
            "reply_count": ThreadsGrabber.safe_get(data, "view_replies_cta_string"),
            "images": images,
            "videos": videos,
        }

        # Ensure images and videos are lists
        if not isinstance(result["images"], list):
            result["images"] = [result["images"]]
        if not isinstance(result["videos"], list):
            result["videos"] = [result["videos"]]

        # Format reply count if it's a string
        if result["reply_count"] and not isinstance(result["reply_count"], int):
            try:
                result["reply_count"] = int(result["reply_count"].split(" ")[0])
            except ValueError:
                result["reply_count"] = 0

        # Generate post URL
        result["url"] = f"https://www.threads.net/@{result['username']}/post/{result['code']}"
        return result

    @staticmethod
    def validate_thread_data(expected_username: str, expected_post_id: str, data: Dict) -> bool:
        """
        Validate if the loaded thread data matches the expected username and post ID.

        Args:
            expected_username (str): Expected username in the thread.
            expected_post_id (str): Expected post ID.

        Returns:
            bool: True if the thread data matches expectations, False otherwise.
        """
        return (data.get("username") == expected_username and
                data.get("code") == expected_post_id)

    @staticmethod
    def scrape_thread(url: str) -> Dict:
        """
        Scrape Threads post and replies from a given URL.

        Args:
            url (str): URL of the Threads post.

        Returns:
            Dict: Dictionary containing the main post and replies.
        """
        cleaned_url = ThreadsGrabber.clean_url(url)
        expected_username = cleaned_url.split('/')[3].replace('@', '')
        expected_post_id = cleaned_url.split('/')[-1]

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Navigate to the URL
            page.goto(cleaned_url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Screenshot for debugging
            name_file = cleaned_url.split('/')[3].replace('@', '')
            page.screenshot(
                path=f"data\\threads_capture\\{name_file}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                full_page=True)

            # Extract content from the page
            selector = Selector(page.content())
            hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()

            threads = []
            for hidden_dataset in hidden_datasets:
                if '"ScheduledServerJS"' not in hidden_dataset or "thread_items" not in hidden_dataset:
                    continue

                data = json.loads(hidden_dataset)
                thread_items = nested_lookup("thread_items", data)
                if not thread_items:
                    continue

                threads = [ThreadsGrabber.parse_thread(t) for thread in thread_items for t in thread]

                # Validate that the scraped data matches the expected username and ID
                if threads and ThreadsGrabber.validate_thread_data(expected_username, expected_post_id, threads[0]):
                    break

            if not threads:
                raise ValueError("Could not find the correct thread data.")

            page.close()
            context.close()
            browser.close()

            return {
                "thread": threads[0],
                "replies": threads[1:],
            }

    @staticmethod
    def download_media(url: str, save_path: str) -> None:
        """
        Download media from a given URL.

        Args:
            url (str): URL of the media.
            save_path (str): Path where the media will be saved.
        """
        response = requests.get(url, timeout=20)
        with open(save_path, "wb") as file:
            file.write(response.content)


#Example usage:
#if __name__ == "__main__":
#    thread_url = 'https://www.threads.net/@yeuow_/post/DGEGJtzBeXP'
#    result = ThreadsGrabber.scrape_thread(thread_url)
#    print(json.dumps(result, indent=2))
