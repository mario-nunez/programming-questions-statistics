import re

from constants import (QUESTIONS_TAG, DATE_POSTED_TAG, TITLE_TAG, STATS_TAG,
                       VIEWS_STATS_POSITION, TAGS_TAG)
class Parser:

    # Data source: Stackoverflow web page
    def parse_stackoverflow_questions_num(self, html_response):
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
            questions_num = int(total_questions.text.split('\n')[1].replace(',', ''))
        else:
            questions_num = 0
        
        return questions_num

    def parse_stackoverflow_data(self, html_response):
        """
        Parse data and structure it

        Parameters
        ----------
        html_response: str
            Data in HTML format
        
        Returns
        -------
        questions_data: list
            List of dicts containing each question
        data_error: bool
            True if correct data, False otherwise.
        """
        if not html_response:
            questions_data, data_error = [], False
            return questions_data, data_error
        # Extract data, the results are stored in cards inside a div container
        questions = html_response.find_all(
            'div', {'id' : re.compile(rf'^{QUESTIONS_TAG}\d+')})

        questions_data = []
        try:
            data_error = False
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
                    # Special location to get the exact amount of views
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
                questions_data.append(q)
        except (KeyError, IndexError, AttributeError) as e:
            print('\n' + e.__class__.__name__ + ':', e)
            print('\nPlease report to the project owner.' ,
                'The HTML structure of Stack Overflow may have changed.')
            data_error = True

        return questions_data, data_error
