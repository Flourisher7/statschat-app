import os
import json
from bs4 import BeautifulSoup


class HTMLPageProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

        # Ensure the output directory exists and is empty
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        else:
            for filename in os.listdir(output_directory):
                file_path = os.path.join(output_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def process_html_page(self, page_filename):
        with open(
            os.path.join(self.input_directory, page_filename), "r", encoding="utf-8"
        ) as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract web page title, URL, URL keywords
        page_title = soup.title.string if soup.title else ""
        page_url = (
            soup.find("link", rel="canonical")["href"]
            if soup.find("link", rel="canonical")
            else ""
        )
        page_keywords = (
            soup.find("meta", attrs={"name": "keywords"})["content"]
            if soup.find("meta", attrs={"name": "keywords"})
            else ""
        )

        # Extract content sections
        content_sections = []
        for content in soup.find_all("div", class_="content-section"):
            section_url = content.find("a")["href"] if content.find("a") else ""
            section_header = content.h2.text if content.h2 else ""
            section_text = content.p.text if content.p else ""
            section_figures = [figure["src"] for figure in content.find_all("img")]
            content_sections.append(
                {
                    "section_url": section_url,
                    "section_header": section_header,
                    "section_text": section_text,
                    "section_figures": section_figures,
                }
            )

        # Create an Element object
        element = {
            "page_title": page_title,
            "page_url": page_url,
            "page_keywords": page_keywords,
            "content_sections": content_sections,
        }

        return element

    def process_all_pages(self):
        processed_data = []

        for page_filename in os.listdir(self.input_directory):
            if page_filename.endswith(".html"):
                element = self.process_html_page(page_filename)
                processed_data.append(element)

                output_filename = page_filename.replace(".html", ".json")
                output_path = os.path.join(self.output_directory, output_filename)
                with open(output_path, "w", encoding="utf-8") as output_file:
                    json.dump(element, output_file, ensure_ascii=False, indent=4)

        return processed_data


if __name__ == "__main__":
    input_directory = "web_pages"
    output_directory = "preprocessed_data"

    processor = HTMLPageProcessor(input_directory, output_directory)
    processed_data = processor.process_all_pages()
