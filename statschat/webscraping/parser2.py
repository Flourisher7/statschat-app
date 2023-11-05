import os
import json
from bs4 import BeautifulSoup


class WebPagePreprocessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

    def clear_output_directory(self):
        if os.path.exists(self.output_directory):
            for filename in os.listdir(self.output_directory):
                file_path = os.path.join(self.output_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def preprocess_web_pages(self):
        self.clear_output_directory()

        for filename in os.listdir(self.input_directory):
            if filename.endswith(".html"):
                input_path = os.path.join(self.input_directory, filename)
                output_path = os.path.join(
                    self.output_directory, f"{os.path.splitext(filename)[0]}.json"
                )
                self.process_and_save_page(input_path, output_path)

    def process_and_save_page(self, input_path, output_path):
        with open(input_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, "html.parser")

            title = soup.title.string if soup.title else ""
            url = (
                soup.find("meta", {"property": "og:url"})["content"]
                if soup.find("meta", {"property": "og:url"})
                else ""
            )
            keywords = [
                meta["content"] for meta in soup.find_all("meta", {"name": "keywords"})
            ]
            content = soup.get_text()

            page_data = {
                "title": title,
                "url": url,
                "keywords": keywords,
                "content": content,
            }

            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(page_data, output_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_directory = "web_pages"
    output_directory = "preprocessed_data"
    preprocessor = WebPagePreprocessor(input_directory, output_directory)
    preprocessor.preprocess_web_pages()
