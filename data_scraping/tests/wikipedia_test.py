from data_scraping.scrapers.wikipedia_scraper import WikipediaScraper
import json
from pathlib import Path
from data_scraping.config import HEADERS

with open(Path(__file__).parent.parent / "data" / "wikipedia_list.json", encoding="utf-8") as f:
    wlist = json.load(f)

def test_wikipedia_scraper():
    for entry in wlist[:5]:
        title, url = next(iter(entry.items()))  # unpack {title: url}
        wscraper = WikipediaScraper(url, HEADERS)
        info = wscraper.get_info_list()
        print(f"Title: {title}")
        print(f"URL:   {url}")
        print(f"Info:  {info}")

if __name__ == "__main__":
    test_wikipedia_scraper()