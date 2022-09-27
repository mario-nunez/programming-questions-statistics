import asyncio
import queue

from gui import Gui
from extract import Collector
from transform import Parser
from constants import URL_TEMPLATE, WORKERS


class MainClass:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.parsers = []

    def stop(self):
        """
        Do cleanup actions before stopping the program
        """
        print('Stopping program...')

        self.task_queue.put(None) 
        for p in self.parsers:
            p.join()

        msg = f'Task queue length: {self.task_queue.qsize()} - last item: {self.task_queue.get()}'
        print(msg)

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
        gui = Gui()
        gui.mainloop()

        return gui.lang, gui.prog_lang

    def _create_parser_workers(self, worker_num):
        """
        Creates and starts all parsers threads
        """
        self.parsers = [Parser(f'Parser-{i}', self.task_queue) for i in range(worker_num)]

        for t in self.parsers:
            t.start()

    def main_loop(self):
        """
        Main function
        """
        # Tools
        scraper = Collector()
        self._create_parser_workers(WORKERS)

        # Ask the user to select the search parameters
        lang, prog_lang = self._select_search_parameters()
        if lang is None and prog_lang is None:
            print('\nNo search parameters selected.')
            return None
    
        # Get the total number of questions that match the search parameters
        url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=1)
        html_response = scraper.scrape(url)
        questions_num = Parser.parse_questions_num(html_response)
        # TODO: A progress bar with estimated time

        pages_num = Parser.parse_pages_num(html_response)
        print(f'There are approximately {pages_num} pages in total\n')
        print(f'Math: {pages_num}x50={pages_num*50} aprox -> {questions_num}\n')


        for i in range(1, pages_num+1):
            url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang, page=i)
            print(url)
            html_response = scraper.scrape(url)
            if not html_response: break
            self.task_queue.put(html_response)

        self.stop()
        print(f'There are approximately {questions_num} questions in total\n')
        
    
if __name__ == "__main__":
    e = MainClass()
    e.main_loop()
    print('\nProgram finished.')
