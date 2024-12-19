# %%
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time


# Set the domain and the start and end date
DOMAIN = "https://press.vatican.va"
START_DATE = "01.02.2024"
END_DATE = "20.04.2024"

# Get all Sundays between start and end date
start_date = datetime.strptime(START_DATE, "%d.%m.%Y")
end_date = datetime.strptime(END_DATE, "%d.%m.%Y")
dates = [
    start_date + timedelta(days=i)
    for i in range((end_date - start_date).days + 1)
    if (start_date + timedelta(days=i)).weekday() == 6
]


def get_link_to_article(url):
    """
    Extract the link to the article from the Vatican press release page.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract the link to the article
        links = soup.find_all("a")

        for link in links:
            if "The Pope’s words" in link.text:
                return DOMAIN + link["href"]
        else:
            print("No link found.", url)
            return None


def parse_article(url):
    """
    Parse the article and extract the title and content.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract the title of the article
        title = soup.find("div", {"class": "titolo"}).text.strip()
        # Extract the content of the article
        content = soup.find("div", {"class": "notizia"}).text.strip()
        return title, content
    else:
        print("Error while parsing article.")
        return None, None




# Scrape over the defined dates
for date in dates:
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")
    url = f"https://press.vatican.va/content/salastampa/en/bollettino/pubblico/{year}/{month}/{day}.html"
    article_link = get_link_to_article(url)

    if article_link:
        # parse the article
        title, content = parse_article(article_link)

        print(f"Title: {title} ({date.strftime('%d.%m.%Y')})")
        print("Url:", article_link) 
        print(f"Content: {content[:100]}")
        print("#"* 20)

        # TODO write to file

    # sleep for 1 second to avoid getting blocked
    time.sleep(1)


# %%
