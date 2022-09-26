import requests
from bs4 import BeautifulSoup

from constants import HEADERS


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
            response = self.s.get(url, headers=HEADERS)
            response_html = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError as e:
            print(e.__doc__, e)
            print('\nTry again later.')
            response_html = ''
        
        return response_html
