from flask import Flask, render_template, request
from pymongo import MongoClient
from flask.ext.cache import Cache

#Korean Analyzer
from konlpy.tag import Twitter
import json
from bson import json_util

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
app.cache = Cache(app, config={
         'CACHE_TYPE': 'filesystem',
         'CACHE_DIR': 'cache-dir',
         'CACHE_DEFAULT_TIMEOUT': 922337203685477580,
         'CACHE_THRESHOLD': 922337203685477580
     })

@app.route("/")
def enter():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    data = list()
    appids = collection.distinct('appid')
    apptitles = collection.distinct('apptitle')
    infos = list()
    for idx, appid in enumerate(appids):
        info = (appid,apptitles[idx],int(apptitles[idx].split('.')[0]))
        infos.append(info)
    for row in sorted(infos, key=lambda x: x[2]):
        appInfo = dict()
        appInfo['appid'] = row[0]
        appInfo['apptitle'] = row[1]
        data.append(appInfo)
    result = render_template('enter.html',data = data)
    return result

## html - main.html
@app.route("/main")
def main():
    id = request.args.get('id')
    '''
    cached = app.cache.get('main_'+id)
    if cached:
        print 'cached!'
        return cached
    '''
    result = render_template('main.html',data=loadReview(id),id=id)
    '''
    app.cache.set('main_'+id, result)
    print 'cache saved!'
    '''
    return result

## test - tokenizer
@app.route("/test1")
def test1():
    id = request.args.get('id')
    return json.dumps(list(loadReview(id)), default=json_util.default)

## test - tokenizer
@app.route("/analysis")
def analysis():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app_compare
    data = list(collection.find({}).sort('no', 1).sort('apptitle',1))
    return json.dumps(data, default=json_util.default)

## Clear All Cache
@app.route("/clearcache")
def test2():
    app.cache.clear()
    return 'Cleared'

## function - Load Review from MongoDB
def loadReview(id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    return collection.find({"appid":id}).sort('no', 1)

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')