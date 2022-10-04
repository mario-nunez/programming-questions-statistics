import logging

import requests

from settings.constants import HEADERS


logger = logging.getLogger(__name__)


class Collector:

    def scrape(self, url):
        """
        Get data from web page in HTML format

        Parameters
        ----------
        url: str
            URL to get the data

        Returns
        -------
        html_resp: bs4.BeautifulSoup
            HTML res
        """
        try:
            with requests.Session() as s:
                resp = s.get(url, headers=HEADERS)
                resp = resp.text
        except requests.exceptions.ConnectionError as e:
            logger.error(f'{e.__doc__}, {e}')
            resp = ''
        
        return resp
