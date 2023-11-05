import os
import json
from bs4 import BeautifulSoup


class ABSPagesParser:
    def __init__(self, pages_directory, output_directory):
        self.pages_directory = pages_directory
        self.output_directory = output_directory

    def clean_output_directory(self):
        if os.path.exists(self.output_directory):
            for file in os.listdir(self.output_directory):
                file_path = os.path.join(self.output_directory, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def parse_page(self, page_filename):
        with open(
            os.path.join(self.pages_directory, page_filename), "r", encoding="utf-8"
        ) as file:
            page_content = file.read()

        soup = BeautifulSoup(page_content, "html.parser")

        # Extract data fields
        title = soup.title.string if soup.title else "No Title Found"
        url = f"https://www.abs.gov.au/{page_filename}"
        url_keyword = os.path.splitext(page_filename)[0]

        sections_data = []
        for section in soup.find_all(["p", "ul", "ol"]):
            section_url = None
            section_header = None
            section_text = section.get_text(separator=" ")

            if section.find("a"):
                anchor = section.find("a")
                section_url = anchor.get("href")
                section_header = anchor.text

            figure_data = None
            if section.find("img"):
                figure_data = {
                    "figure_title": section.find("img").get("alt", ""),
                    "figure_subtitle": None,
                    "figure_url": section.find("img").get("src", ""),
                    "figure_type": "image",
                }

            sections_data.append(
                {
                    "section_url": section_url,
                    "section_header": section_header,
                    "section_text": section_text,
                    "figure": figure_data,
                }
            )

        page_data = {
            "title": title,
            "url": url,
            "url_keyword": url_keyword,
            "content": sections_data,
        }

        # Save the data as a JSON file
        output_filename = f"{url_keyword}.json"
        output_path = os.path.join(self.output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(page_data, json_file, ensure_ascii=False, indent=4)

        print(f"Page '{url_keyword}' has been processed.")

    def process_pages(self):
        self.clean_output_directory()
        for filename in os.listdir(self.pages_directory):
            if filename.endswith(".html"):
                self.parse_page(filename)


if __name__ == "__main__":
    pages_parser = ABSPagesParser(
        "web_pages", "preprocessed_data"
    )  # Replace 'web_pages' with the actual directory containing the scraped pages
    pages_parser.process_pages()
