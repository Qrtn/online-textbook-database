import os
import flask

from pymongo import MongoClient
from bson.objectid import ObjectId

import resolve

app = flask.Flask(__name__)
app.db = MongoClient(os.getenv('MONGOHQ_URL')).otd

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def index():
    return '<html><body>Try <a href="/resolve/5334c81a8f51ef1966b82cd6/hrw">Earth Science</a>! (<a href="/covers/5334c81a8f51ef1966b82cd6">Here\'s</a> a picture.) We\'re getting there!</body></html>'

@app.route('/resolve/<objectid>/<access>')
def textbook(objectid, access):
    document = app.db.books.find_one(ObjectId(objectid))
    return resolve.convert[access](document)

@app.route('/covers/<objectid>', methods=['GET'])
def covers(objectid):
    image = app.db.books.find_one(ObjectId(objectid))['image']
    return flask.Response(image['data'], mimetype=image['content_type'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
