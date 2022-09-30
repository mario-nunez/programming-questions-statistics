import logging

import requests
from bs4 import BeautifulSoup

from settings.constants import HEADERS


logger = logging.getLogger(__name__)


class Collector:
    """
    A class to represent a web scraper.
    """
    def __init__(self):
        self.s = requests.Session() 

    def scrape(self, url):
        """
        Get data from web page in HTML format

        Parameters
        ----------
        url: str
            URL to get the data

        Returns
        -------
        response_html: str
            Data in HTML format
        """
        try:
            response = requests.get(url, headers=HEADERS)
            response_html = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError as e:
            logger.error(f'{e.__doc__}, {e}')
            response_html = ''
        
        return response_html
