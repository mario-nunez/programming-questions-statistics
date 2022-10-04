import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# Configuration settings
WORKERS = 1

# Info associated with the request to Stack Overflow
HEADERS = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"}
URL_TEMPLATE = "https://{lang}stackoverflow.com/questions/tagged/{prog_lang}?sort=MostVotes&page={page}&pagesize=50"
STATUS_OK_CODE = 200

# Info associated with Stack Overflow HTML structure
PAGE_TAG = "s-pagination--item js-pagination-item"
QUESTIONS_TAG = "question-summary-"
DATE_POSTED_TAG = "relativetime"
TITLE_TAG = "s-post-summary--content-title"
STATS_TAG = "s-post-summary--stats-item-number"
VIEWS_STATS_POSITION = 2
TAGS_TAG = "tag"
