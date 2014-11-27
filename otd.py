import os
from collections import OrderedDict
import flask

from pymongo import MongoClient

from fuzzywuzzy import process

import config
import resolve

app = flask.Flask(__name__, static_folder=config.STATIC_FOLDER)
app.config.from_object(config)
app.db = MongoClient(config.MONGOLAB_URI).otd

queries_items_descending = [(document['_id'], document['query']) for document in app.db.books.aggregate([
    {'$project': {'query': {'$concat': [
        '$title', ' ',
        {'$ifNull': ['$volume', '']}, ' ',
        {'$ifNull': ['$edition', '']},
        '$publisher', ' ',
        '$copyright', ' ',
        '$isbn_10', ' ',
        '$isbn_13',
    ]}}},
    {'$sort': {'_id': -1}},
])['result']]

queries = {-1: OrderedDict(queries_items_descending), 1: OrderedDict(reversed(queries_items_descending))}

@app.template_test('list')
def is_list(value):
    return isinstance(value, list)

@app.route('/favicon.ico')
def favicon():
    return flask.redirect(config.ASSETS_BASE + 'favicon.ico')

@app.route('/link/<int:id_>/<access>', methods=['GET'])
@app.route('/link/<int:id_>/<access>/<int:index>', methods=['GET'])
def link(id_, access, index=0):
    document = app.db.books.find_one(id_)
    try:
        page = resolve.convert[access](document=document, index=index)
    except KeyError:
        return 'No such method.'
    except resolve.InvalidFormat:
        return 'Invalid method for specified book.'
    except IndexError:
        return 'Invalid index for specified method.'
    return page

def extract(query=None, start=None, stop=None, order=-1):
    # order -1 is descending or newest
    # order 1 is ascending or oldest
    if query is None:
        yield from app.db.books.find().sort('_id', order)[start:stop]
    else:
        for match in process.extract(query, queries[order], limit=None)[start:stop]:
            yield app.db.books.find_one(match[2])

SEARCH_QUERY = '/?query={}&start={}&num={}&order={}'
ORDER_NAMES = {'-1': -1, '1': 1}

@app.route('/')
def search():
    query = flask.request.args.get('query', '')

    total = len(queries_items_descending)
    try:
        start = int(flask.request.args.get('start'))
    except TypeError:
        start = 0
    if start < 0 or start >= total:
        start = 0
    try:
        num = int(flask.request.args.get('num'))
    except TypeError:
        num = 10
    stop = None if num < 0 else start + num

    order = ORDER_NAMES.get(flask.request.args.get('order'), -1)

    prev_href = None if start == 0 else SEARCH_QUERY.format(query, start - (start % num or num), num, order)
    next_href = None if start + num >= total else SEARCH_QUERY.format(query, start + (num - start % num or num), num, order)

    genresults = extract(query or None, start, stop, order)

    return flask.render_template('index.html',
        documents=genresults,
        from_n=(start + 1), to_n=min(start + num, total), prev_href=prev_href, next_href=next_href,
        query=query, order=order, num=num, total=total)

@app.route('/help')
def help():
    return flask.send_file('static/help.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
