import asyncio
import logging
import logging.config
import platform
import queue
from time import perf_counter, process_time

import aiohttp
from bs4 import BeautifulSoup

from gui import Gui
from transform import Parser
from extract import Collector
from settings.logging_config import LOG_CONFIG_DICT
from settings.constants import URL_TEMPLATE, WORKERS


# Logging configuration
logging.config.dictConfig(LOG_CONFIG_DICT)
logger = logging.getLogger(__name__)


class MainClass:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.parsers = []
        self.results = []

    def stop(self):
        """
        Do cleanup actions before stopping the program
        """
        logger.info('Stopping program...')

        self.task_queue.put(None) 
        for p in self.parsers:
            p.join()

        logger.info(
            f'Task queue length: {self.task_queue.qsize()} -> '
            f'last item: {self.task_queue.get()}'
        )

    def _select_search_parameters(self):
        """
        Let the user choose parameters using an interactive GUI

        Returns
        -------
        lang: str
            language option selected by the user
        prog_lang: str
            programming language option selected by the user
        """
        logger.info(f'Opening GUI...')
        gui = Gui()
        gui.mainloop()
        logger.info(f'GUI closed')

        return gui.lang, gui.prog_lang

    def _create_parser_workers(self, worker_num):
        """
        Creates and starts all parsers threads
        """
        self.parsers = [
            Parser(f'Parser-{i}', self.task_queue) for i in range(1, worker_num+1)
        ]

        for t in self.parsers:
            t.start()

    async def fetch(self, session, url):
        async with session.get(url) as resp:
            logger.info(url)
            assert resp.status == 200
            return await resp.text() 

    async def get_info(self, urls):
        async with aiohttp.ClientSession() as session:
            for url in urls:
                resp = await self.fetch(session, url)
                self.task_queue.put(BeautifulSoup(resp, 'html.parser'))

    def main(self):
        """
        Main function
        """

        # TODO: Reduce docstrings
        # TODO: Refactor code with the asyncio approach

        logger.info(f'Starting program...')
        # Tools
        scraper = Collector()
        self._create_parser_workers(WORKERS)

        # Ask the user to select the search parameters
        lang, prog_lang = self._select_search_parameters()
        if lang is None and prog_lang is None:
            logger.warning('No search parameters selected')
            self.stop()
            return None

        # Get the number of pages that match the search parameters
        url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=1)
        html_response = scraper.scrape(url)
        pages_num = Parser.parse_pages_num(html_response)
        logger.info(f'There are {pages_num} pages in total')
        # TODO: A progress bar with estimated time or percentaje of requests done
        
        start_time = perf_counter()
        cpu_start_time = process_time()

        # TODO: Create a function
        urls = []
        for i in range(1, pages_num+1):
            urls.append(URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=i))

        logger.info('Number of URLs: ' +  str(len(urls)))

        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.get_info(urls))

        self.stop()

        stop_time = perf_counter()
        cpu_stop_time = process_time()

        logger.info(f'Wall time: {stop_time - start_time} seconds')
        logger.info(f'CPU time: {cpu_stop_time - cpu_start_time} seconds')
        logger.info('Program finished.')


if __name__ == "__main__":
    e = MainClass()
    try:
        e.main()
    except KeyboardInterrupt:
        logger.warning('Interruption occurred')
        e.stop()
