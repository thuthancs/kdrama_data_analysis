import requests
import helper
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def fetch_page(self):
        """Fetch the IMDb list page using requests (no JS)."""
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def get_drama_list(self, rating_type: str = "imdb"):
        """Parse the IMDb list page into a list of drama dictionaries."""
        soup = self.fetch_page()
        lst = soup.find(
            "ul",
            class_="ipc-metadata-list ipc-metadata-list--dividers-between "
            "sc-d24d5d37-0 hDHQeM detailed-list-view ipc-metadata-list--base",
        )
        if lst is None:
            raise RuntimeError("Could not find drama list container in HTML response")

        dramas = []
        for item in lst.find_all("li", class_="ipc-metadata-list-summary-item"):
            drama_object = {}

            # Extract h3, which is the title of the drama
            raw_title = item.find("h3", class_="ipc-title__text").get_text(strip=True)
            preprocessed_title = helper.preprocess_title(raw_title)
            drama_object["title"] = preprocessed_title

            # Extract the year of release and number of episodes
            spans = item.find_all(
                "span", class_="sc-b4f120f6-7 hoOxkw dli-title-metadata-item"
            )
            release_year = spans[0].get_text(strip=True)
            num_episodes = spans[1].get_text(strip=True)
            drama_object["release_year"] = release_year
            drama_object["num_episodes"] = helper.preprocess_episodes(num_episodes)

            # Extract rating score
            rating = item.find("span", class_="ipc-rating-star--rating")
            drama_object["rating_type"] = rating_type
            drama_object["rating_score"] = rating.get_text(strip=True) if rating else ""

            # Extract cast
            cast = item.find_all(
                "span", class_="sc-9d52d06f-2 cWCmUf title-description-credit"
            )
            cast_list = [actor.get_text(strip=True) for actor in cast]
            drama_object["cast"] = cast_list

            # Extract short description
            description = item.find("div", class_="ipc-html-content-inner-div")
            drama_object["short_description"] = (
                description.get_text(strip=True) if description else ""
            )

            # Append the drama object to the list
            dramas.append(drama_object)

        return dramas
