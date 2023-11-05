import unittest
import os
from web_crawler import WebCrawler
from data_formatter import DataFormatter


class TestWebCrawler(unittest.TestCase):
    def test_download_page(self):
        crawler = WebCrawler("https://example.com", 10, "test_pages")
        page_content = crawler.download_page("https://example.com")
        self.assertIsNotNone(page_content)
        self.assertTrue("Example Domain" in page_content)

    def test_save_page(self):
        crawler = WebCrawler("https://example.com", 10, "test_pages")
        page_content = crawler.download_page("https://example.com")
        crawler.save_page("https://example.com", page_content)
        self.assertTrue(os.path.isfile("test_pages/example.com.html"))


class TestDataFormatter(unittest.TestCase):
    def test_extract_metadata(self):
        html_content = """<html><body>
            <section>
                <h2>Section 1</h2>
                <p>Text for section 1</p>
                <img src="figure1.jpg" alt="Figure 1">
            </section>
            <section>
                <h2>Section 2</h2>
                <p>Text for section 2</p>
            </section>
        </body></html>"""

        metadata = DataFormatter.extract_metadata(html_content)
        self.assertEqual(len(metadata), 2)
        self.assertEqual(metadata[0]["section_header"], "Section 1")
        self.assertEqual(metadata[0]["figures"][0]["alt"], "Figure 1")
        self.assertEqual(metadata[1]["section_text"], "Text for section 2")

    def test_format_data(self):
        formatter = DataFormatter([], "test_collected_data")
        url = "https://example.com"
        title = "Example Domain"
        html_content = "<html><body><p>Some text</p></body></html>"
        formatted_data = formatter.format_data(url, title, html_content)
        self.assertEqual(formatted_data["url"], url)
        self.assertEqual(formatted_data["title"], title)
        self.assertEqual(len(formatted_data["metadata"]), 0)


if __name__ == "__main__":
    unittest.main()
