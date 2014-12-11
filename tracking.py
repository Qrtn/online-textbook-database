import sys
import traceback
import pprint
from datetime import datetime

import flask

import httpagentparser

class Tracker:
    def __init__(self, collection, insert=True):
        self.collection = collection
        self.insert = insert

    def track_event(self, event, properties={}):
        document = {
            'event': event,
            'time': datetime.utcnow(),
        }
        document.update(properties)

        if self.insert:
            try:
                self.collection.insert(document)
            except Exception as e:
                traceback.print_exc()

        pprint.pprint(document)

    def track_http_event(self, event, properties={}):
        ua = httpagentparser.detect(flask.request.user_agent.string) 
        ua['string'] = flask.request.user_agent.string

        document = {
            'time': datetime.utcfromtimestamp(flask.g.start),
            'http': {
                'method': flask.request.method,
                'path': flask.request.path,
                'remote_addr': flask.request.remote_addr,
                'referrer': flask.request.headers.get('Referer'),
                'user_agent': ua,
                'form': flask.request.form.to_dict(),
                'args': flask.request.args.to_dict(),
            },
        }
        document.update(properties)

        self.track_event(event, document)

    def track_error(self, properties={}):
        document = {
            'traceback': traceback.format_exc(),
        }
        document.update(properties)

        self.track_http_event('error', document)
