import os
import flask

from pymongo import MongoClient
from bson.objectid import ObjectId

from fuzzywuzzy import process

import resolve

app = flask.Flask(__name__)
app.db = MongoClient(os.getenv('MONGOLAB_URI')).otd

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

def is_list(value):
    return isinstance(value, list)
app.jinja_env.tests['list'] = is_list

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/link/<objectid>/<access>', methods=['GET'])
@app.route('/link/<objectid>/<access>/<int:index>', methods=['GET'])
def textbook(objectid, access, index=0):
    document = app.db.books.find_one(ObjectId(objectid))
    try:
        page = resolve.convert[access](document=document, index=index)
    except KeyError:
        return 'No such method.'
    except resolve.InvalidFormat:
        return 'Invalid method for specified book.'
    except IndexError:
        return 'Invalid index for specified method.'
    return page

@app.route('/cover/<objectid>', methods=['GET'])
def cover(objectid):
    image = app.db.books.find_one(ObjectId(objectid))['image']
    return flask.Response(image['data'], mimetype=image['content_type'])

def extract(query=None, start=None, stop=None):
    if query is None:
        yield from app.db.books.find({}, {'image': 0})[start:stop]
    else:
        for match in process.extract(query, queries, limit=None)[start:stop]:
            yield app.db.books.find_one(match[2], {'image': 0})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
