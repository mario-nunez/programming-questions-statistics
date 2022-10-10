import asyncio
import logging
import logging.config
import platform
import queue
from time import perf_counter, process_time

import aiohttp
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from gui import Gui
from transform import Parser
from extract import Collector
from settings.logging_config import LOG_CONFIG_DICT
from settings.constants import (
    URL_TEMPLATE, PAGE_TEMPLATE, WORKERS, STATUS_CODE_OK, REQUEST_LIMIT
)


# Logging configuration
logging.config.dictConfig(LOG_CONFIG_DICT)
logger = logging.getLogger(__name__)


class MainClass:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.data_parsed_df = None
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
            # Store results in pandas dataframe in main class
            self.data_parsed_df = pd.DataFrame.from_records(p.data_parsed)

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
        logger.info(f'Starting program...')

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
        asyncio.run(self.get_pages_info(base_url, pages_num))

        self.stop()

        stop_time = perf_counter()
        cpu_stop_time = process_time()

        logger.info(f'Wall time: {stop_time - start_time} seconds')
        logger.info(f'CPU time: {cpu_stop_time - cpu_start_time} seconds')

        # Visualise results with seaborn

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(11,9))
        fig.subplots_adjust(hspace=0.3, wspace=0.3)
        fig.suptitle('Stackoverflow visualizations', fontsize=20)

        # Top 5 questions with most views
        data_most_views = self.data_parsed_df\
            .sort_values("views", ascending=False).head(5)
        ax1 = sns\
            .barplot(x="question_id", y="views", data=data_most_views,
                     orient="v", ax=axes[0,0], order=data_most_views\
                        .sort_values("views", ascending=False).question_id)\
            .set(title="Top 5 questions with most views",
                 xlabel="Question ID", ylabel="Views")


        # Top 5 questions with most answers
        data_most_answers = self.data_parsed_df\
            .sort_values("num_answers", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="num_answers", data=data_most_answers,
                     orient="v", ax=axes[0,1], order=data_most_answers\
                        .sort_values("num_answers", ascending=False).question_id)\
            .set(title="Top 5 questions with most answers",
                 xlabel="Question ID", ylabel="Number of answers")

        # Top 5 questions with most votes
        data_most_votes = self.data_parsed_df\
            .sort_values("votes", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="votes", data=data_most_votes,
                     orient="v", ax=axes[1,0], order=data_most_votes\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Votes")

        # Number of answers of the top 5 questions with most votes
        sns\
            .barplot(x="question_id", y="num_answers", data=data_most_votes,
                     orient="v", ax=axes[1,1], order=data_most_votes\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Number of answers of the top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Number of answers")

        fig2, axes = plt.subplots(nrows=2, ncols=2, figsize=(11,9))
        fig2.subplots_adjust(hspace=0.3, wspace=0.3)
        fig2.suptitle('Other visualizations', fontsize=20)
        
        plt.show()

        logger.info('Program finished.')


if __name__ == "__main__":
    s = MainClass()
    try:
        s.main()
    except KeyboardInterrupt:
        logger.warning('Ctrl-c was pressed. Keyboard interruption ocurred.')
        s.stop()
