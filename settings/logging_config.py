import os
import logging
import logging.handlers

from settings.constants import LOG_FOLDER


LOG_LEVEL = logging.INFO

LOG_CONFIG_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-8s %(name)s.%(funcName)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)-8s %(name)s.%(funcName)s - %(message)s'
        },
    },
    'handlers': {
        'logfile': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, 'app_logs.log'),
            'formatter': 'default',
        },

        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['logfile', 'console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    }
}
