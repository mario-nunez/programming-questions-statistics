import logging

import aiohttp
from bs4 import BeautifulSoup
import requests

from settings.constants import HEADERS, PAGE_TEMPLATE, STATUS_CODE_OK


logger = logging.getLogger(__name__)


class Collector:

    def __init__(self, task_queue):
        self.task_queue = task_queue

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

    async def fetch(self, session, url):
        """
        Async function that makes a request and returns its html response.
        """
        async with session.get(url) as resp:
            if resp.status != STATUS_CODE_OK:
                logger.error(
                    f'Error in response with status code: {resp.status}. '
                    f'{resp.reason}')
                return None
            return await resp.text()

    async def get_pages_info(self, base_url, pages_num):
        """
        Async function that gets the information of certain urls and 
        insert them in the parser queue.
        """
        print(f'Requests made of the {pages_num}:')
        async with aiohttp.ClientSession() as session:
            for i in range(1, pages_num+1):
                url = base_url + PAGE_TEMPLATE.format(page=i)
                html_resp = await self.fetch(session, url)
                if html_resp is None:
                    return None
                print(f'{i},', end="", flush=True)
                self.task_queue.put(BeautifulSoup(html_resp, 'html.parser'))
