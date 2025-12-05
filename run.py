import csv
from config import URLs, HEADERS
from scraper import Scraper
import helper
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


csv_output = "kdrama_list.csv"
with open(csv_output, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["title", "release_year", "num_episodes", "rating_type", "rating_score", "cast", "short_description"]
    )

    # 1) Scrape 2000s and 2020s with the requests-based Scraper
    for period, URL in URLs.items():
        if period == "2010s":
            continue

        scraper_obj = Scraper(URL, HEADERS)
        drama_list = scraper_obj.get_drama_list()

        for drama in drama_list:
            print(
                f"{drama['title']} {drama['release_year']} {drama['num_episodes']} "
                f"{drama['rating_type']} {drama['rating_score']} {drama['cast']} {drama['short_description']}"
            )
            writer.writerow(
                [
                    drama["title"],
                    drama["release_year"],
                    drama["num_episodes"],
                    drama["rating_type"],
                    drama["rating_score"],
                    ", ".join(drama["cast"]),
                    drama["short_description"],
                ]
            )

    # 2) Scrape 2010s with Selenium and append to CSV
    dramas_2010s = scrape_2010s_with_selenium(URLs["2010s"])
    for drama in dramas_2010s:
        print(
            f"{drama['title']} {drama['release_year']} {drama['num_episodes']} "
            f"{drama['rating_type']} {drama['rating_score']} {drama['cast']} {drama['short_description']}"
        )
        writer.writerow(
            [
                drama["title"],
                drama["release_year"],
                drama["num_episodes"],
                drama["rating_type"],
                drama["rating_score"],
                ", ".join(drama["cast"]),
                drama["short_description"],
            ]
        )