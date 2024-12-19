from pathlib import Path
from bs4 import BeautifulSoup
import unicodedata
import re

indir = Path("Incels_html_Dateien/")
outdir = Path("incels_extracted/")

outdir.mkdir(exist_ok=True)

# list all files in a directory
files = indir.glob("*.html")


for file in files:
    text = file.read_text()
    soup = BeautifulSoup(text, "html.parser")


    # extract the title
    try:
        title = soup.find("h1", {"class": "p-title-value"}).text

        # normalize weird unicode characters
        title = unicodedata.normalize("NFKD", title)

        # remove newlines and superfluous whitespace
        title = re.sub("\s+", " ", title).strip()

    except (TypeError, AttributeError):
        print("Issue while parsing title in file: ", file)
        pass

    # extract the post
    try:
        first_post = soup.find("article", {"class": "message-body"}).text

        first_post = unicodedata.normalize("NFKD", first_post)
        first_post = re.sub("\s+", " ", first_post).strip()

    except (TypeError, AttributeError):
        print("Issue while parsing body in file: ", file)
        pass


    # write the title and post to a text file
    f_out = outdir / (file.stem + ".txt")
    with open(f_out, "w") as f:
        f.write(title + "\n")
        f.write(first_post + "\n")
