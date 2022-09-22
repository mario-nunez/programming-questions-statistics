import re

import requests
from bs4 import BeautifulSoup

from gui import Gui
from constants import (HEADERS, URL_TEMPLATE, QUESTIONS_TAG, DATE_POSTED_TAG,
                       TITLE_TAG, STATS_TAG, VIEWS_STATS_POSITION, TAGS_TAG,
                       PAGE_SIZE)


def select_search_parameters():
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

def get_total_questions(response_html):
    """
    Get the total number of questions to search

    Parameters
    ----------
    response_html: str
        Data in HTML format

    Returns
    -------
    questions_num: int
        Number of questions that match the search parameters selected
    """
    # Get total number of questions - Interesting to do a progress bar
    total_questions = response_html.find('div', {'class' : 'fs-body3'})
    if total_questions is not None:
        questions_num = int(total_questions.text.split('\n')[1].replace(',', ''))
    else:
        questions_num = 0
    
    return questions_num

def parse_html(response_html):
    """
    Parse data and structure it

    Parameters
    ----------
    response_html: str
        Data in HTML format
    
    Returns
    -------
    questions_data: list
        List of dicts containing each question
    data_error: bool
        True if correct data, False otherwise.
    """
    if not response_html:
        questions_data, data_error = [], False
        return questions_data, data_error
    # Extract data, the results are stored in cards inside a div container
    questions = response_html.find_all(
        'div', {'id' : re.compile(rf'^{QUESTIONS_TAG}\d+')})
    print('Total questions obtained in the request: ' + str(len(questions)))

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

def get_info_html(url):
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
        response = requests.get(url, headers=HEADERS)
        response_html = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.ConnectionError as e:
        print(e.__doc__, e)
        print('\nTry again later.')
        response_html = ''
    
    return response_html

def main():
    """
    Main function
    """
    # Ask the user to select the search parameters
    lang, prog_lang = select_search_parameters()
    if lang is None and prog_lang is None:
        print('\nNo search parameters selected.')
        return None
    
    # Get the total number of questions that match the search parameters
    url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang,
                              page=1, page_size=PAGE_SIZE)
    response_html = get_info_html(url)
    questions_num = get_total_questions(response_html)
    print(f'There are approximately {questions_num} questions in total\n')
    # TODO: A progress bar with estimated time

    page = 1
    end = False
    all_questions = []
    while end is not True:
        url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang,
                                  page=page, page_size=PAGE_SIZE)
        print(url)
        response_html = get_info_html(url)
        data, data_error = parse_html(response_html)

        if data_error is True:
            break

        if data:
            page += 1
            all_questions.extend(data)
        else:
            end = True

    print('\nNumber of questions stored:', len(all_questions))
    
    
if __name__ == "__main__":
    main()
    print('\nProgram finished.')
