import os
import json
from bs4 import BeautifulSoup
import re


class WebPageProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

    def clean_text(self, text):
        # Remove extra white spaces and newlines
        return re.sub(r"\s+", " ", text).strip()

    def process_page(self, page_path):
        with open(page_path, "r", encoding="utf-8") as file:
            page_content = file.read()

        soup = BeautifulSoup(page_content, "html.parser")

        # Extract title
        title = soup.title.string if soup.title else ""

        # Extract URL
        url = soup.find("meta", attrs={"property": "og:url"})
        url = url["content"] if url else ""

        # Extract URL keywords (meta keywords)
        keywords = soup.find("meta", attrs={"name": "keywords"})
        keywords = keywords["content"] if keywords else ""

        # Extract content, section_url, section_header, section_text, figure (as list)
        content = []

        # You may need to adapt the logic below to your specific HTML structure
        # Here, we assume that content is divided into sections with a header
        for section in soup.find_all("section"):
            section_url = url  # Assuming section URL is the same as the main URL
            section_header = section.find("h2").get_text() if section.find("h2") else ""
            section_text = self.clean_text(section.get_text())
            figure_tags = section.find_all("img")
            figures = [img["src"] for img in figure_tags]

            section_data = {
                "section_url": section_url,
                "section_header": section_header,
                "section_text": section_text,
                "figure": figures,
            }

            content.append(section_data)

        # Create a dictionary to store the extracted data
        data = {
            "title": title,
            "url": url,
            "url_keywords": keywords,
            "content": content,
        }

        # Save the data as JSON in the output directory
        output_filename = os.path.splitext(os.path.basename(page_path))[0] + ".json"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=4, ensure_ascii=False)

    def preprocess_pages(self):
        # Remove existing files in the output directory
        if os.path.exists(self.output_directory):
            for file in os.listdir(self.output_directory):
                file_path = os.path.join(self.output_directory, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Process all HTML pages in the input directory
        for file in os.listdir(self.input_directory):
            if file.endswith(".html"):
                page_path = os.path.join(self.input_directory, file)
                self.process_page(page_path)


if __name__ == "__main__":
    input_directory = "web_pages"
    output_directory = "preprocessed_data"

    processor = WebPageProcessor(input_directory, output_directory)
    processor.preprocess_pages()
