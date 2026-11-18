#Scrapper to add deck data for certain

import logging

from config import BASE_URLS, HEADERS

from scraper.request_handler import RequestHandler
from scraper.parser import HTMLParser
from processing.cleaning import DataProcessor
from database.database_handler import DatabaseHandler

from urllib.parse import urlencode

def build_search_url(base_url, search_term):

    params = {
        "q": search_term
    }

    #example:
    #"decks?name=Krenko&orderBy=-updatedAt&page=1"
    # "https://archidekt.com/search/decks?name=Krenko&orderBy=-updatedAt&page=1"
    return f"{base_url}/search?{urlencode(params)}"

#TODO
#Write Scrapper
#Write Processing
#Write Database sub script


#Fine tuned control over log data.
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

#Currently only looking at one base version of a deck/website.


def main():

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting deck web scraper")

    try:
        # 1. Initialize components
        request_handler = RequestHandler(
            headers=HEADERS
        )

        parser = HTMLParser()
        processor = DataProcessor()
        database = DatabaseHandler()

        # 2. Request website
        logger.info("Requesting website")

        #Start with Archideckt only.
        html = request_handler.get(BASE_URLS["archideckt"])

        # 3. Parse website
        logger.info("Parsing website")

        raw_data = parser.parse(html)

        # 4. Process extracted data
        logger.info("Processing data")

        clean_data = processor.clean(raw_data)

        # 5. Store data
        logger.info("Storing data")

        database.insert_data(clean_data)

        logger.info("Scraping completed successfully")

    except Exception:
        logger.exception("Scraping failed")
        raise


if __name__ == "__main__":
    main()