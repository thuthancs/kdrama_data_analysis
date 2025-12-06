import requests
from .. import helper
from bs4 import BeautifulSoup

class WikipediaScraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
    
    def fetch_page(self):
        """Fetch the IMDb list page using requests (no JS)."""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException:
            # If the page is missing or any network error occurs, signal failure to the caller
            return None

        return BeautifulSoup(response.content, "html.parser")

    def get_info_list(self):
        info_list = []
        soup = self.fetch_page()
        # If the page could not be fetched (404, network error, etc.), just return empty
        if soup is None:
            return info_list
        # Try several common infobox variants; Wikipedia markup can change between pages
        table = (
            soup.find("table", class_="infobox ib-tv vevent")
            or soup.find("table", class_="infobox vevent")
            or soup.find("table", class_="infobox")
        )

        # If we still can't find an infobox, just return an empty list so the caller can skip this title
        if table is None:
            # Optional: you could log/print the URL here for debugging
            return info_list

        # Get the tbody element inside the table (if missing, operate directly on the table)
        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")
        
        # Find the row that has <th> with class_= "infobox-label" Extract screenwriter & director
        # <th> and <td> are on the same level
        obj = {}
        for row in rows:
            header = row.find("th", class_="infobox-label")
            if header:
                label = header.get_text(strip=True)
                if label == "Written by":
                    screenwriter_td = row.find("td", class_="infobox-data")
                    # There might be more than 1 screenwriter. If that's the case, get the div with the class "plainlist" and inside the dive, get the li elements inside the ul element
                    # If the <li> has a <a> tag, get the text inside the <a> tag
                    screenwriter = []
                    plainlist_div = screenwriter_td.find("div", class_="plainlist")
                    if plainlist_div:
                        for li in plainlist_div.find_all("li"):
                            a_tag = li.find("a")
                            if a_tag:
                                screenwriter.append(a_tag.get_text(strip=True))
                            else:
                                screenwriter.append(li.get_text(strip=True))
                    else:
                        screenwriter.append(screenwriter_td.get_text(strip=True))
                    obj["screenwriter"] = screenwriter
                
                # Get the director   
                elif label == "Directed by":
                    director_td = row.find("td", class_="infobox-data")
                    director = []
                    plainlist_div = director_td.find("div", class_="plainlist")
                    if plainlist_div:
                        for li in plainlist_div.find_all("li"):
                            a_tag = li.find("a")
                            if a_tag:
                                director.append(a_tag.get_text(strip=True))
                            else:
                                director.append(li.get_text(strip=True))
                    else:
                        director.append(director_td.get_text(strip=True))
                    obj["director"] = director
                
                # Get the network
                elif label == "Network":
                    network_td = row.find("td", class_="infobox-data")
                    network = network_td.get_text(strip=True)
                    obj["network"] = network
                
        # Extract the plot
        # Find the heading with an id of Synopsis or Plot
        plot_heading = soup.find(id="Synopsis") or soup.find(id="Plot")
        # Extract all the text of the <p> elements until the next heading
        plot = ""
        if plot_heading:
            for sibling in plot_heading.parent.find_next_siblings():
                if sibling.name and sibling.name.startswith("h"):
                    break
                if sibling.name == "p":
                    plot += sibling.get_text(strip=True) + " "
            obj["plot"] = plot.strip()
        
        info_list.append(obj)
        return info_list