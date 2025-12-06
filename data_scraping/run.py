import csv
import json
from pathlib import Path

from .config import URLs, HEADERS
from .scrapers.imdb_scraper import IMDBScraper
from .scrapers.wikipedia_scraper import WikipediaScraper
from . import helper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_2010s_with_selenium(url: str):
    """Return a list of drama dicts for the 2010s list using Selenium."""
    options = Options()
    # Uncomment to run headless once everything is stable:
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service("/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        print("2010s current URL:", driver.current_url)

        # Wait until the list container is present (same as in test.py)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='list-page-mc-list-content'] ul.ipc-metadata-list")
            )
        )

        # Optional: scroll to bottom in case of lazy-load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div[data-testid='list-page-mc-list-content'] ul.ipc-metadata-list")
    if container is None:
        raise RuntimeError("Could not find list container for 2010s page")

    dramas = []
    for item in container.select("li.ipc-metadata-list-summary-item"):
        drama_object = {}

        # Title
        raw_title = item.find("h3", class_="ipc-title__text").get_text(strip=True)
        drama_object["title"] = helper.preprocess_title(raw_title)

        # Year + episodes
        spans = item.find_all("span", class_="sc-b4f120f6-7 hoOxkw dli-title-metadata-item")
        release_year = spans[0].get_text(strip=True)
        num_episodes = spans[1].get_text(strip=True)
        drama_object["release_year"] = release_year
        drama_object["num_episodes"] = helper.preprocess_episodes(num_episodes)

        # Rating
        rating = item.find("span", class_="ipc-rating-star--rating")
        drama_object["rating_type"] = "imdb"
        drama_object["rating_score"] = rating.get_text(strip=True) if rating else ""

        # Cast
        cast = item.find_all("span", class_="sc-9d52d06f-2 cWCmUf title-description-credit")
        drama_object["cast"] = [actor.get_text(strip=True) for actor in cast]

        # Short description
        description = item.find("div", class_="ipc-html-content-inner-div")
        drama_object["short_description"] = description.get_text(strip=True) if description else ""

        dramas.append(drama_object)

    return dramas


def build_wikipedia_map(wikipedia_list_path: Path) -> dict[str, str]:
    """Load wikipedia_list.json and return {title: url} mapping."""
    with open(wikipedia_list_path, encoding="utf-8") as f:
        raw_list = json.load(f)

    title_to_url: dict[str, str] = {}
    for entry in raw_list:
        title, url = next(iter(entry.items()))
        title_to_url[title] = url
    return title_to_url


def main():
    # 1) Collect all dramas from IMDb (2000s + 2020s via requests, 2010s via Selenium)
    all_dramas: list[dict] = []

    for period, URL in URLs.items():
        if period == "2010s":
            dramas = scrape_2010s_with_selenium(URL)
        else:
            scraper_obj = IMDBScraper(URL, HEADERS)
            dramas = scraper_obj.get_drama_list()

        all_dramas.extend(dramas)

    # 2) Enrich with Wikipedia info where available
    wikipedia_list_path = Path(__file__).parent / "data" / "wikipedia_list.json"
    title_to_url = build_wikipedia_map(wikipedia_list_path)

    for drama in all_dramas:
        title = drama["title"]
        wiki_url = title_to_url.get(title)
        if not wiki_url:
            continue

        wscraper = WikipediaScraper(wiki_url, HEADERS)
        info_list = wscraper.get_info_list()
        if not info_list:
            continue

        info = info_list[0]
        # Map Wikipedia fields into our schema
        drama["network_provider"] = info.get("network", "")
        drama["screenwriter"] = ", ".join(info.get("screenwriter", []))
        drama["director"] = ", ".join(info.get("director", []))
        drama["plot"] = info.get("plot", "")
        drama["source"] = wiki_url

    # 3) Write final CSV with IMDb + Wikipedia fields
    csv_output = "kdrama_list.csv"
    fieldnames = [
        "title",
        "release_year",
        "num_episodes",
        "rating_type",
        "rating_score",
        "cast",
        "short_description",
        "network_provider",
        "screenwriter",
        "director",
        "plot",
        "source",
    ]

    with open(csv_output, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)

        for drama in all_dramas:
            print(
                f"{drama['title']} {drama['release_year']} {drama['num_episodes']} "
                f"{drama['rating_type']} {drama['rating_score']} {drama['cast']} {drama['short_description']}"
            )
            writer.writerow(
                [
                    drama.get("title", ""),
                    drama.get("release_year", ""),
                    drama.get("num_episodes", ""),
                    drama.get("rating_type", ""),
                    drama.get("rating_score", ""),
                    ", ".join(drama.get("cast", [])),
                    drama.get("short_description", ""),
                    drama.get("network_provider", ""),
                    drama.get("screenwriter", ""),
                    drama.get("director", ""),
                    drama.get("plot", ""),
                    drama.get("source", ""),
                ]
            )


if __name__ == "__main__":
    main()