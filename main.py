import re

import requests
from bs4 import BeautifulSoup

from gui import Gui
from constants import (
    HEADERS, URL_TEMPLATE, QUESTIONS_TAG, DATE_POSTED_TAG, TITLE_TAG,
    STATS_TAG, VIEWS_STATS_POSITION, TAGS_TAG
    
)


def select_search_parameters():
    """
    Let the user choose the language and the programming language of the
    offers to search using an interactive GUI

    Returns
    -------
    search_lang: str
        language option selected by the user
    search_prog_lang: str
        programming language option selected by the user
    """
    gui = Gui()
    gui.mainloop()

    return gui.search_lang, gui.search_prog_lang

def get_info(url):
    """
    Collect data from a URL

    Parameters
    ----------
    url: str
        URL to get information from

    Returns
    -------
    questions_data: list
        Data collected and structured
    """
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract data, the results are stored in cards inside a div container
    questions = soup.find_all(
        'div', {'id' : re.compile(rf'^{QUESTIONS_TAG}\d+')})
    print('Total questions in the request ' + str(len(questions)))

    questions_data = []
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

    return questions_data

def main():
    """
    Main function
    """
    # Ask the user to select the search parameters
    lang, prog_lang = select_search_parameters()
    url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang)
    data = get_info(url)
    for d in data:
        print(d)
        print('\n')

    print('\nProgram finished.')
    

if __name__ == "__main__":
    main()
