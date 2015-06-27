import time
from collections import OrderedDict

import flask
from werkzeug.contrib.fixers import ProxyFix

from pymongo import MongoClient

from fuzzywuzzy import process

import config
import resolve
import tracking

app = flask.Flask(__name__, static_folder=config.STATIC_FOLDER)
app.config.from_object(config)
db = MongoClient(config.MONGOLAB_URI).otd

if not app.debug:
    tracker = tracking.Tracker(db.log)
else:
    tracker = tracking.Tracker(db.log, insert=False)

# OTD (for now) runs behind Heroku reverse proxies, changing remote_addr
app.wsgi_app = ProxyFix(app.wsgi_app)

queries_items_descending = [(document['_id'], document['query']) for document in db.books.aggregate([
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
])]

queries = {-1: OrderedDict(queries_items_descending), 1: OrderedDict(reversed(queries_items_descending))}

@app.template_test('list')
def is_list(value):
    return isinstance(value, list)

@app.template_filter('dictprioritize')
def dictprioritize(value):
    # template will pass in doc['access']; dictprioritize returns access
    # methods and data sorted by priority

    # each access method function in resolve.convert requires a corresponding
    # access method priority int in resolve.priority, or KeyError will be
    # raised here when template sorts document access dictionary

    # also called in /link without access method to route to canonical access

    return sorted(value.items(), key=lambda x: resolve.priority[x[0]])

@app.before_request
def before_request():
    flask.g.start = time.time()

@app.after_request
def after_request(response):
    flask.g.status = response.status
    return response

@app.teardown_request
def teardown_request(exception=None):
    diff = time.time() - flask.g.start
    tracker.track_http_event('request', {
        'execution_time': diff,
        'status': flask.g.status,
    })

@app.errorhandler(Exception)
def errorhandler(error):
    tracker.track_error()
    raise

@app.route('/favicon.ico')
def favicon():
    return flask.redirect(config.ASSETS_BASE + 'favicon.ico')

@app.route('/robots.txt')
def robots():
    return flask.send_file('static/robots.txt')

@app.route('/help')
def help():
    return flask.send_file('static/help.html')

@app.route('/<int:id_>')
@app.route('/link/<int:id_>')
@app.route('/link/<int:id_>/<access>')
@app.route('/link/<int:id_>/<access>/<int:index>')
def link(id_, access=None, index=0):
    document = db.books.find_one(id_)
    if document is None:
        return 'No such book.'

    if access is None:
        access = dictprioritize(document['access'])[0][0]

    tracker.track_http_event('access', {
        'access': {
            'book': id_,
            'method': access,
            'index': index,
        },
    })

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
        yield from db.books.find().sort('_id', order)[start:stop]
    else:
        for match in process.extract(query, queries[order], limit=None)[start:stop]:
            yield db.books.find_one(match[2])

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

    tracker.track_http_event('search', {
        'search': {
            'query': query,
            'start': start,
            'num': num,
            'order': order,
        },
    })

    prev_href = None if start == 0 else SEARCH_QUERY.format(query, start - (start % num or num), num, order)
    next_href = None if start + num >= total else SEARCH_QUERY.format(query, start + (num - start % num or num), num, order)

    genresults = extract(query or None, start, stop, order)

    return flask.render_template('search.html',
        documents=genresults,
        from_n=(start + 1), to_n=min(start + num, total), prev_href=prev_href, next_href=next_href,
        query=query, order=order, num=num, total=total)

@app.route('/shelf/<int:id_>')
def shelf(id_):
    tracker.track_http_event('shelf', {
        'shelf': id_,
    })

    shelf = db.shelves.find_one(id_)
    if shelf is None:
        return 'No such shelf.'

    documents = (db.books.find_one(bookid) for bookid in shelf['books'])

    return flask.render_template('shelf.html',
        documents=documents, shelfid=id_)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
