from flask import Flask, render_template, request
from pymongo import MongoClient

#Korean Analyzer
from konlpy.tag import Twitter
import json
from bson import json_util

app = Flask(__name__)

@app.route("/")
def enter():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    data = list()
    for appid in collection.distinct('appid'):
        appInfo = dict()
        appInfo['appid'] = appid
        appInfo['apptitle'] = collection.find_one({'appid':appid})['apptitle']
        data.append(appInfo)
    result = render_template('enter.html',data = data)
    return result

## html - main.html
@app.route("/main")
def main():
    id = request.args.get('id')
    result = render_template('main.html',data=loadReview(id),id=id)
    return result

## test - tokenizer
@app.route("/test1")
def test1():
    id = request.args.get('id')
    return json.dumps(list(loadReview(id)), default=json_util.default)

## test - tokenizer
@app.route("/test2")
def test2():
    text = request.args.get('text')
    twitter = Twitter()
    return json.dumps(twitter.pos(text, norm=True, stem=True))

## function - Load Review from MongoDB
def loadReview(id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    if id == 'all':
        return collection.find({}).sort('no', 1).sort('appid',1)
    else:
        return collection.find({"appid":id}).sort('no', 1)

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')