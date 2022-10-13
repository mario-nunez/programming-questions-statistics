import asyncio
import logging
import logging.config
import platform
import queue
from time import perf_counter, process_time

from bs4 import BeautifulSoup
import pandas as pd

from extract import Collector
from graph_maker import GraphMaker
from gui import Gui
from transform import Parser
from settings.logging_config import LOG_CONFIG_DICT
from settings.constants import (
    URL_TEMPLATE, PAGE_TEMPLATE, WORKERS, REQUEST_LIMIT
)


# Logging configuration
logging.config.dictConfig(LOG_CONFIG_DICT)
logger = logging.getLogger(__name__)


class MainClass:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.data_parsed_df = pd.DataFrame()
        self.scraper = Collector(self.task_queue)
        self.graph_maker = GraphMaker()
        self.parsers = []
        self._create_parser_workers(WORKERS)

    def stop(self):
        """
        Stop parsers
        """
        logger.info('Stopping parsers...')

        self.task_queue.put(None)
        dfs = []
        for p in self.parsers:
            p.join()
            dfs.append(pd.DataFrame.from_records(p.data_parsed))

        self.data_parsed_df = pd.concat(dfs)

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

    def get_pages_num(self, base_url):
        """
        Get the number of pages that match the search parameters
        """
        url = base_url + PAGE_TEMPLATE.format(page=1)
        resp = self.scraper.scrape(url)
        if resp:
            pages_num = Parser.parse_pages_num(BeautifulSoup(resp, 'html.parser'))
            logger.info(f'{pages_num} pages to request in total')
        else:
            pages_num = 0

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
        # Ask the user to select the search parameters
        lang, prog_lang = self.select_search_parameters()
        if lang is None and prog_lang is None:
            logger.warning('No search parameters selected')
            self.stop()
            return None

        base_url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang)

        pages_num = self.get_pages_num(base_url)
        if pages_num == 0:
            logger.warning('No pages to request')
            self.stop()
            return None
        elif pages_num > REQUEST_LIMIT:
            logger.info(f'{pages_num} pages limited to {REQUEST_LIMIT} pages')
            pages_num = REQUEST_LIMIT

        start_time = perf_counter()
        cpu_start_time = process_time()

        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.scraper.get_pages_info(base_url, pages_num))

        self.stop()

        stop_time = perf_counter()
        cpu_stop_time = process_time()

        logger.info(f'Wall time: {stop_time - start_time} seconds')
        logger.info(f'CPU time: {cpu_stop_time - cpu_start_time} seconds')

        if self.data_parsed_df.empty:
            logger.info('No data to display')
        else:
            self.graph_maker.create_graphs('stackoverflow', self.data_parsed_df)


if __name__ == "__main__":
    s = MainClass()
    try:
        logger.info(f'Starting program...')
        s.main()
    except KeyboardInterrupt:
        logger.warning('Ctrl-c was pressed. Keyboard interruption ocurred.')
        s.stop()
    logger.info('Program finished.')
