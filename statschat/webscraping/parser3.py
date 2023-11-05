import os
import json
from bs4 import BeautifulSoup


class WebPageProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.ensure_directories()

    def ensure_directories(self):
        if not os.path.exists(self.input_directory):
            raise FileNotFoundError(
                f"The input directory '{self.input_directory}' does not exist."
            )
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def clean_html(self, html_content):
        # Parse HTML content using BeautifulSoup to extract relevant data
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title, URL, URL keywords, and content
        title = soup.title.string if soup.title else ""
        url = soup.find("meta", {"property": "og:url"})
        url = url.get("content") if url else ""
        url_keywords = soup.find("meta", {"name": "keywords"})
        url_keywords = url_keywords.get("content") if url_keywords else ""
        content = soup.get_text()

        return {
            "title": title,
            "url": url,
            "url_keywords": url_keywords,
            "content": content,
        }

    def process_web_pages(self):
        # Delete existing files in the output directory
        for file in os.listdir(self.output_directory):
            file_path = os.path.join(self.output_directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Process each web page in the input directory
        for file in os.listdir(self.input_directory):
            input_file_path = os.path.join(self.input_directory, file)
            output_file_path = os.path.join(
                self.output_directory, f"{os.path.splitext(file)[0]}.json"
            )

            with open(input_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            cleaned_data = self.clean_html(html_content)

            # Save cleaned data as a JSON file
            with open(output_file_path, "w", encoding="utf-8") as json_file:
                json.dump(cleaned_data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_directory = "web_pages"
    output_directory = "preprocessed_data"

    web_page_processor = WebPageProcessor(input_directory, output_directory)
    web_page_processor.process_web_pages()
