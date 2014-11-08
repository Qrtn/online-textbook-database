import os
import flask

from pymongo import MongoClient

from fuzzywuzzy import process

import config
import resolve

app = flask.Flask(__name__, static_folder=None)
app.config.from_object(config)
app.db = MongoClient(config.MONGOLAB_URI).otd

queries = {document['_id']: document['query'] for document in app.db.books.aggregate([
    {'$project': {'query': {'$concat': [
        '$title', ' ',
        {'$ifNull': ['$volume', '']}, ' ',
        {'$ifNull': ['$edition', '']},
        '$publisher', ' ',
        '$copyright', ' ',
        '$isbn_10', ' ',
        '$isbn_13',
    ]}}}
])['result']}

@app.template_test('list')
def is_list(value):
    return isinstance(value, list)

@app.route('/favicon.ico')
def favicon():
    return flask.redirect('http://otd-io.s3.amazonaws.com/favicon.ico')

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

def extract(query=None, start=None, stop=None):
    if query is None:
        yield from app.db.books.find()[start:stop]
    else:
        for match in process.extract(query, queries, limit=None)[start:stop]:
            yield app.db.books.find_one(match[2])

@app.route('/')
def search():
    SEARCH_QUERY = '/?query={}&start={}&num={}'

    query = flask.request.args.get('query', '')

    total = len(queries)
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

    prev_href = None if start == 0 else SEARCH_QUERY.format(query, start - (start % num or num), num)
    next_href = None if start + num >= total else SEARCH_QUERY.format(query, start + (num - start % num or num), num)

    genresults = extract(query or None, start, stop)

    return flask.render_template('index.html',
        documents=genresults,
        from_n=(start + 1), to_n=min(start + num, total), prev_href=prev_href, next_href=next_href,
        query=query, num=num, total=total)

@app.route('/help')
def help():
    return flask.send_file('static/help.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
