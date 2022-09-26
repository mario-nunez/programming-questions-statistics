import asyncio

from gui import Gui
from extract import Collector
from transform import Parser
from constants import URL_TEMPLATE, PAGE_SIZE


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

def main():
    """
    Main function
    """
    # Tools
    scraper = Collector()
    parser = Parser()

    # Ask the user to select the search parameters
    lang, prog_lang = select_search_parameters()
    if lang is None and prog_lang is None:
        print('\nNo search parameters selected.')
        return None
   
    # Get the total number of questions that match the search parameters
    url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang,
                              page=1, page_size=PAGE_SIZE)
    html_response = scraper.scrape(url)
    questions_num = parser.parse_stackoverflow_questions_num(html_response)
    print(f'There are approximately {questions_num} questions in total\n')
    # TODO: A progress bar with estimated time

    page = 1
    end = False
    all_questions = []
    while end is not True:
        url = URL_TEMPLATE.format(lang=lang, prog_lang=prog_lang,
                                  page=page, page_size=PAGE_SIZE)
        print(url)
        html_response = scraper.scrape(url)
        data, data_error = parser.parse_stackoverflow_data(html_response)

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
