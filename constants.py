# Info associated with the request to Stack Overflow
HEADERS = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"}
URL_TEMPLATE = "https://{lang}.stackoverflow.com/questions/tagged/{prog_lang}?sort=MostVotes"

# Info associated with Stack Overflow HTML structure
QUESTIONS_TAG = "question-summary-"
DATE_POSTED_TAG = "relativetime"
TITLE_TAG = "s-post-summary--content-title"
STATS_TAG = "s-post-summary--stats-item-number"
VIEWS_STATS_POSITION = 2
TAGS_TAG = "tag"