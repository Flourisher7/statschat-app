import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import time


class WebCrawler:
    """
    A web crawler class for scraping web pages.
    """

    def __init__(self, seed_url, max_pages=100, save_dir="web_pages"):
        """
        Initialize the WebCrawler.

        Args:
            seed_url (str): The starting URL for web crawling.
            max_pages (int): The maximum number of pages to crawl.
            save_dir (str): The directory to save the crawled pages.
        """
        self.seed_url = seed_url
        self.max_pages = max_pages
        self.save_dir = save_dir
        self.visited = set()
        self.to_visit = [seed_url]

    def download_page(self, url):
        """
        Download a web page.

        Args:
            url (str): The URL of the web page to download.

        Returns:
            str: The HTML content of the web page, or None if download fails.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to download {url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading {url}: {str(e)}")
        return None

    def save_page(self, url, html_content):
        """
        Save a web page to a local directory.

        Args:
            url (str): The URL of the web page.
            html_content (str): The HTML content of the web page.
        """
        parsed_url = urlparse(url)
        page_name = parsed_url.netloc + parsed_url.path.replace("/", "_") + ".html"
        file_name = os.path.join(self.save_dir, page_name)

        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved {url} as {file_name}")

    def crawl(self):
        """
        Perform web crawling.
        """
        collected_pages = 0

        while self.to_visit and collected_pages < self.max_pages:
            url = self.to_visit.pop(0)
            if url not in self.visited:
                print(f"Crawling: {url}")

                html_content = self.download_page(url)
                if html_content:
                    self.save_page(url, html_content)

                    # Extract links and add to the to-visit list
                    soup = BeautifulSoup(html_content, "html.parser")
                    for a_tag in soup.find_all("a", href=True):
                        href = a_tag.get("href")
                        full_url = urljoin(url, href)
                        self.to_visit.append(full_url)

                    self.visited.add(url)
                    collected_pages += 1
                    time.sleep(1)  # Be polite and avoid overloading the server


if __name__ == "__main__":
    seed_url = "https://abs.gov.au"  # Replace with your starting URL
    max_pages = 100  # Maximum number of pages to crawl
    save_dir = "web_pages"  # Directory to save crawled pages

    crawler = WebCrawler(seed_url, max_pages, save_dir)
    crawler.crawl()
