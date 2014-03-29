import os
from flask import Flask, g
from pymongo import MongoClient

app = Flask(__name__)
app.client = MongoClient(os.getenv('MONGOHQ_URL'))

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/covers/<id>', methods=['GET'])
def covers():
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
