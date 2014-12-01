import logging
import traceback
from datetime import datetime

import flask

import httpagentparser

class MongoHandler(logging.Handler):
    def __init__(self, collection, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.collection = collection

    def emit(self, record):
        level = record.levelname

        document = {
            # Include log level
            'level': level,
            # Convert timestamp to datetime
            'time': datetime.utcfromtimestamp(flask.g.start),
            'remote_addr': flask.request.remote_addr,
            'user_agent_string': flask.request.user_agent.string,
            'user_agent': httpagentparser.detect(flask.request.user_agent.string),
            'method': flask.request.method,
            'path': flask.request.path,
        }

        document.update(record.msg)

        if level == 'ERROR':
            # Convert record.exc_info to string traceback
            document.update({
                'traceback': ''.join(traceback.format_exception(*record.exc_info)),
            })

        print(document)

        try:
            self.collection.insert(document)
        except Exception as e:
            traceback.print_exc()
