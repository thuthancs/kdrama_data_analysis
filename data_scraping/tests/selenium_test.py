from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

URL = "https://www.imdb.com/list/ls565286034/"

options = Options()
# Temporarily run *with* UI so you can see what happens:
# comment this out while debugging
# options.add_argument("--headless=new")

options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service("/opt/homebrew/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(URL)
    print("Current URL:", driver.current_url)

    # Wait until the list container is present
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[data-testid='list-page-mc-list-content'] ul.ipc-metadata-list")
        )
    )

    # (Optional) scroll to bottom to trigger any lazy-loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    html = driver.page_source
finally:
    driver.quit()

with open("imdb_2010s_debug.html", "w", encoding="utf-8") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
items = soup.select("li.ipc-metadata-list-summary-item")
print("Found items:", len(items))