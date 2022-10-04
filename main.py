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
from settings.constants import URL_TEMPLATE, WORKERS, STATUS_OK_CODE


# Logging configuration
logging.config.dictConfig(LOG_CONFIG_DICT)
logger = logging.getLogger(__name__)


class MainClass:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.parsers = []
        self.scraper = Collector()
        self._create_parser_workers(WORKERS)

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

    def _create_parser_workers(self, worker_num):
        """
        Create and start all parsers threads
        """
        self.parsers = [
            Parser(f'Parser-{i}', self.task_queue) for i in range(1, worker_num+1)
        ]

        for t in self.parsers:
            t.start()

    async def fetch(self, session, url):
        """
        Async function that makes a request and returns its html response.
        """
        async with session.get(url) as resp:
            logger.info(url)
            assert resp.status == STATUS_OK_CODE
            return await resp.text() 

    async def get_urls_info(self, urls):
        """
        Async function that gets the information of certain urls and 
        insert them in the parser queue.
        """
        async with aiohttp.ClientSession() as session:
            for url in urls:
                html_resp = await self.fetch(session, url)
                self.task_queue.put(BeautifulSoup(html_resp, 'html.parser'))

    def generate_urls(self, pages_num, lang, prog_lang):
        """
        Create all the URLs that will be requested
        """
        urls = []
        for i in range(1, pages_num+1):
            urls.append(URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=i))

        return urls
    
    def get_pages_num(self, lang, prog_lang):
        """
        Get the number of pages that match the search parameters
        """
        url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=1)
        resp = self.scraper.scrape(url)
        pages_num = Parser.parse_pages_num(BeautifulSoup(resp, 'html.parser'))
        logger.info(f'{pages_num} pages to request in total')

        return pages_num
    
    def select_search_parameters(self):
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

    def main(self):
        """
        Main function
        """
        logger.info(f'Starting program...')

        # Ask the user to select the search parameters
        lang, prog_lang = self.select_search_parameters()
        if lang is None and prog_lang is None:
            logger.warning('No search parameters selected')
            self.stop()
            return None

        pages_num = self.get_pages_num(lang, prog_lang)
        # TODO: A progress bar with estimated time or percentaje of requests done
        
        start_time = perf_counter()
        cpu_start_time = process_time()

        urls = self.generate_urls(pages_num, lang, prog_lang)
        logger.info('Number of URLs to request for: ' +  str(len(urls)))

        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.get_urls_info(urls))

        self.stop()

        stop_time = perf_counter()
        cpu_stop_time = process_time()

        logger.info(f'Wall time: {stop_time - start_time} seconds')
        logger.info(f'CPU time: {cpu_stop_time - cpu_start_time} seconds')
        logger.info('Program finished.')


if __name__ == "__main__":
    s = MainClass()
    try:
        s.main()
    except KeyboardInterrupt:
        logger.warning('Ctrl-c was pressed. Keyboard interruption ocurred.')
        s.stop()
