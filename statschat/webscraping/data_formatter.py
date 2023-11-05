import os
import json
from bs4 import BeautifulSoup
import time


class DataFormatter:
    """
    A class for formatting and preprocessing web page data.
    """

    def __init__(self, collected_data, save_dir="collected_data"):
        """
        Initialize the DataFormatter.

        Args:
            collected_data (list): List of dictionaries representing collected data.
            save_dir (str): The directory to save formatted data.
        """
        self.collected_data = collected_data
        self.save_dir = save_dir

    @staticmethod
    def extract_page_content(html_content):
        """
        Extract page title and text content from HTML.

        Args:
            html_content (str): HTML content of the web page.

        Returns:
            tuple: A tuple containing page title and text content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        page_title = soup.title.string if soup.title else ""
        page_text = soup.get_text()
        return page_title, page_text

    @staticmethod
    def extract_metadata(html_content):
        """
        Extract metadata including section URL, section header, section text, and
        figures.

        Args:
            html_content (str): HTML content of the web page.

        Returns:
            list: A list of dictionaries containing metadata for each section.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metadata_list = []

        # Loop through sections or elements containing metadata
        for section in soup.find_all(
            "section"
        ):  # Modify this selector based on the HTML structure
            section_url = "https://example.com"  # Replace with the actual section URL
            section_header = section.find("h2").text if section.find("h2") else ""
            section_text = section.get_text()

            # Extract figs (you can customize this part based on your HTML structure)
            figures = []
            for figure in section.find_all("img"):
                src = figure.get("src")
                alt = figure.get("alt")
                if src:
                    figure_data = {"src": src, "alt": alt}
                    figures.append(figure_data)

            metadata = {
                "section_url": section_url,
                "section_header": section_header,
                "section_text": section_text,
                "figures": figures,
            }
            metadata_list.append(metadata)

        return metadata_list

    def format_data(self, url, title, html_content):
        """
        Format collected data including metadata.

        Args:
            url (str): The URL of the web page.
            title (str): Page title.
            html_content (str): HTML content of the web page.

        Returns:
            dict: Formatted data as a dictionary.
        """
        metadata = DataFormatter.extract_metadata(html_content)

        return {"url": url, "title": title, "metadata": metadata}

    def remove_duplicates(self):
        """
        Remove duplicate entries in the collected data based on URLs.
        """
        unique_data = []
        unique_urls = set()

        for entry in self.collected_data:
            url = entry["url"]
            if url not in unique_urls:
                unique_data.append(entry)
                unique_urls.add(url)

        self.collected_data = unique_data

    def save_data(self):
        """
        Save the collected and formatted data in a structured format (e.g., JSON).
        """
        os.makedirs(self.save_dir, exist_ok=True)
        timestamp = int(time.time())
        file_name = os.path.join(self.save_dir, f"data_{timestamp}.json")
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(self.collected_data, f, indent=4)
        print(f"Saved collected data as {file_name}")


if __name__ == "__main__":
    collected_data = []  # Replace with your collected data
    save_dir = "collected_data"  # Directory to save formatted data

    formatter = DataFormatter(collected_data, save_dir)
    formatter.remove_duplicates()
    formatter.save_data()
