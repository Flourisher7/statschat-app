import os
import json
from bs4 import BeautifulSoup


class WebPageProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.cleanup_output_directory()

    def cleanup_output_directory(self):
        # Delete all files in the output directory
        if os.path.exists(self.output_directory):
            file_list = os.listdir(self.output_directory)
            for file_name in file_list:
                file_path = os.path.join(self.output_directory, file_name)
                os.remove(file_path)

    def clean_and_format_page(self, page_file):
        with open(page_file, "r", encoding="utf-8") as file:
            page_content = file.read()

        soup = BeautifulSoup(page_content, "html.parser")

        # Extract title, URL, and keywords
        title = soup.title.text if soup.title else ""
        url = page_file.split(os.sep)[-1]
        url_keywords = [
            meta.get("content")
            for meta in soup.find_all("meta", attrs={"name": "keywords"})
        ]

        # Extract content as a list of sections
        sections = []
        for section in soup.find_all("section"):
            section_url = (
                section.find("a", href=True)["href"]
                if section.find("a", href=True)
                else ""
            )
            section_header = section.find("h1").text if section.find("h1") else ""
            section_text = section.get_text()
            section_figures = [img["src"] for img in section.find_all("img")]
            sections.append(
                {
                    "section_url": section_url,
                    "section_header": section_header,
                    "section_text": section_text,
                    "figures": section_figures,
                }
            )

        # Create a JSON representation of the data
        data = {
            "title": title,
            "url": url,
            "url_keywords": url_keywords,
            "content": sections,
        }

        return data

    def process_web_pages(self):
        # List all HTML files in the input directory
        html_files = [
            os.path.join(self.input_directory, file)
            for file in os.listdir(self.input_directory)
            if file.endswith(".html")
        ]

        for page_file in html_files:
            formatted_data = self.clean_and_format_page(page_file)

            # Save the formatted data as JSON
            output_file = os.path.join(
                self.output_directory,
                os.path.basename(page_file).replace(".html", ".json"),
            )
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(formatted_data, outfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_directory = "web_pages"
    output_directory = "preprocessed_data"

    processor = WebPageProcessor(input_directory, output_directory)
    processor.process_web_pages()
