import csv
from config import URLs, HEADERS
from scraper import Scraper

csv_output = "kdrama_list.csv"
with open(csv_output, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "release_year", "num_episodes", "rating_type", "rating_score", "cast", "short_description"])

    for URL in URLs.values():
        scraper_obj = Scraper(URL, HEADERS)
        drama_list = scraper_obj.get_drama_list()

        for drama in drama_list:
            print(
                f"{drama['title']} {drama['release_year']} {drama['num_episodes']} "
                f"{drama['rating_type']} {drama['rating_score']} {drama['cast']} {drama['short_description']}"
            )
            writer.writerow([
                drama["title"],
                drama["release_year"],
                drama["num_episodes"],
                drama["rating_type"],
                drama["rating_score"],
                ", ".join(drama["cast"]),
                drama["short_description"],
            ])
        