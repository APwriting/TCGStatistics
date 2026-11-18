
import logging
import requests

#Class for deck web scrapper focused on archideckt and Moxfield
#Handles getting URL data
#And closing
#Called by Deck_scrapper_main.py

class RequestHandler:

    def __init__(self, headers=None, timeout=15):

        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()
        self.session.headers.update(headers or {})

        self.timeout = timeout


    def get(self, url):

        self.logger.info("Sending GET request: %s", url)

        try:
            response = self.session.get(
                url,
                timeout=self.timeout
            )

            response.raise_for_status()

            self.logger.info(
                "Request successful: HTTP %s",
                response.status_code
            )

            return response

        except requests.RequestException:

            self.logger.exception(
                "Request failed: %s",
                url
            )

            raise


    def close(self):

        self.session.close()
