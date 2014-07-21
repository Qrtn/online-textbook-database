import os
import flask

from pymongo import MongoClient
from bson.objectid import ObjectId

import resolve

app = flask.Flask(__name__)
app.db = MongoClient(os.getenv('MONGOLAB_URI')).otd

def is_list(value):
    return isinstance(value, list)
app.jinja_env.tests['list'] = is_list

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def index():
    return flask.render_template('index.html', documents=app.db.books.find())

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
