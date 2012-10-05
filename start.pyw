# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
import logging, logging.config
import sys
from main import MainWindow
from PyQt4.QtGui import QApplication

if __name__ == '__main__':


    config = {
        'version': 1,
        'formatters': {
            'standart': {
                'format': '# %(levelname)-8s [%(asctime)-23s]  %(message)s  # %(filename)s [LINE:%(lineno)d]',
                'datefmt': ''
            },
        },
        'handlers': {
            'default': {
                'formatter':'standart',
                'class':'logging.handlers.RotatingFileHandler',
                'filename':'logs/main.log',
                'maxBytes':10485760,
                'backupCount':5
            },
            'can': {
                'formatter':'standart',
                'class':'logging.handlers.RotatingFileHandler',
                'filename':'logs/can.log',
                'maxBytes':10485760,
                'backupCount':5
            },
        },
        'loggers': {
            'main': {
                'handlers': ['default'],
                'level': 'DEBUG' ,
                'propagate': True
            },
            'can': {
                'handlers': ['can'],
                'level': 'DEBUG' ,
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(config)

__author__ = 'Filin'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
