import os
from web_crawler import WebCrawler
from data_formatter import DataFormatter


def main():
    # Web Crawling
    seed_url = "https://abs.gov.au"  # Starting ABS URL
    max_pages = 100  # Maximum number of pages to crawl
    save_dir = "web_pages"  # Directory to save crawled pages

    crawler = WebCrawler(seed_url, max_pages, save_dir)
    crawler.crawl()

    # Data Formatting
    data_dir = "web_pages"  # Directory containing the crawled pages
    collected_data = []

    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                url = "https://abs.gov.au"  # Replace with the actual URL
                html_content = f.read()
                title, text_content = DataFormatter.extract_page_content(html_content)
                data_entry = DataFormatter.format_data(url, title, text_content)
                collected_data.append(data_entry)

    formatter = DataFormatter(collected_data, "collected_data")
    formatter.remove_duplicates()
    formatter.save_data()


if __name__ == "__main__":
    main()
