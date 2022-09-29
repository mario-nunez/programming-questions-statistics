import re
import queue
import logging
import threading

from settings.constants import (QUESTIONS_TAG, DATE_POSTED_TAG, TITLE_TAG, STATS_TAG,
                       VIEWS_STATS_POSITION, TAGS_TAG, PAGE_TAG)


logger = logging.getLogger(__name__)


class Parser(threading.Thread):

    def __init__(self, thread_name, task_queue):
        self.thread_name = thread_name
        self.task_queue = task_queue
        self.data_parsed = []
        threading.Thread.__init__(self, name=thread_name)

    def run(self):
        """
        Main loop for a Parser. It will keep reading from the queue until it
        gets some task. If the task is a tuple like (None, None), the Parser
        stops.
        """
        print(f'Parser {self.name} has started')
        logger.info(f'Parser {self.name} has started')

        while True:
            try:
                html_response = self.task_queue.get(True, timeout=0.5)
            except queue.Empty:
                continue

            msg = f'Parser {self.name} got data from queue'
            print(msg)

            # When a None arrives to the queue, means that collectors
            # have stopped sending items
            if html_response is None:
                # This is needed so any other parser threads stop as well
                self.task_queue.put(None)
                break

            data_error = self.parse_html_response(html_response)
            self.task_queue.task_done()

            if data_error is True:
                self.task_queue.put(None)
                break

        print(f'Data parsed elements: {len(self.data_parsed)}')

    # Data source: Stackoverflow web page
    def parse_html_response(self, html_response):
        """
        Parse data and structure it

        Parameters
        ----------
        html_response: str
            Data in HTML format
        
        Returns
        -------
        data_error: bool
            True if correct data, False otherwise.
        """
        questions = html_response.find_all(
            'div', {'id' : re.compile(rf'^{QUESTIONS_TAG}\d+')})

        data_error = False
        try:
            for item in questions:
                # get all the elements
                question_id = int(item.attrs['id'].split(QUESTIONS_TAG)[1])
                title = item.find('h3', {'class' : TITLE_TAG}).find('a').text
                date_posted = item.find('span', {'class' : DATE_POSTED_TAG})
                if date_posted is not None:
                    date_posted = date_posted.attrs['title']
                
                stats_spans = item.find_all('span', {'class' : STATS_TAG})
                stats = []
                for index, stat in enumerate(stats_spans):
                    # Get the exact amount of views from a specific location
                    if index == VIEWS_STATS_POSITION:
                        stats.append(int(stat.parent['title'].split(' ')[0]))
                    else:
                        stats.append(int(stat.text))

                question_tags = item.find_all('a', {'rel' : TAGS_TAG})
                tags = [qt.text for qt in question_tags]

                # Store the data of each question in a single dict
                q = {
                    'question_id': question_id,
                    'title': title,
                    'date_posted': date_posted,
                    'votes': stats[0],
                    'num_answers': stats[1],
                    'views': stats[2],
                    'tags': tags
                }
                self.data_parsed.append(q)
        except (KeyError, IndexError, AttributeError) as e:
            print('\n' + e.__class__.__name__ + ':', e)
            print('\nPlease report to the project owner.' ,
                'The HTML structure of Stack Overflow may have changed.')
            data_error = True

        return data_error

    
    def parse_questions_num(html_response):
        """
        Get the total number of questions to search

        Parameters
        ----------
        html_response: str
            Data in HTML format

        Returns
        -------
        questions_num: int
            Number of questions that match the search parameters selected
        """
        # Get total number of questions - Interesting to do a progress bar
        total_questions = html_response.find('div', {'class' : 'fs-body3'})
        if total_questions is not None:
            questions_num = int(
                total_questions.text.split('\n')[1].replace(',', '')
            )
        else:
            questions_num = 0
        
        return questions_num

    def parse_pages_num(html_response):
        """
        Get the total number of pages to search through

        Parameters
        ----------
        html_response: str
            Data in HTML format

        Returns
        -------
        pages_num: int
            Number of pages with data that match the search parameters selected
        """
        total_pages = html_response.find_all('a', {'class' : PAGE_TAG})
        if total_pages:
            pages_num = int(total_pages[-2].text)
        else:
            pages_num = 1
        
        return pages_num
