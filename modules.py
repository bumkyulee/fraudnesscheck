#-*- coding: utf-8 -*-
import requests
import json
import time
import re
import mechanize
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient
from konlpy.tag import Twitter

## Delete Reviews from MongoDB
def deleteReview(id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    collection.remove({'appid':id})
    print 'Deleted: ' + id

## Get Google Reviews By Page
def saveReview(limit, id, title):
    #appInfo
    try:
        appInfoResult = getAppInfo(id)
    except:
        print 'appInfoError - ' + id
    #appReview
    print 'begin: ' + id
    url = 'https://play.google.com/store/getreviews'
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }

    pageNum = 0
    reviewNo = 1
    whileFlag = True

    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app

    while whileFlag:
        data = {'reviewType':'0','pageNum':pageNum,'id':id,'reviewSortOrder':'0','xhr':'1'}
        r = requests.post(url, data=data, headers=headers)
        try:
            data = json.loads(r.text[5:])
            soup = BeautifulSoup(data[0][2])
        except:
            break
        reviews = soup.findAll('div',attrs={'class':'single-review'})
        if len(reviews) == 0:
            break
        for review in reviews:
            result = dict()
            author = review.find('span',attrs={'class':'author-name'}).text
            date = review.find('span',attrs={'class':'review-date'}).text.encode('utf-8').replace('년','.').replace('월','.').replace('일','').decode('utf-8')
            body_title = review.find('span',attrs={'class':'review-title'}).text
            body_content = body_title + ' ' + review.find('div',attrs={'class':'review-body'}).text[len(body_title):-5]
            rating = int(review.find('div',attrs={'class':'current-rating'})['style'].split(':')[1].strip()[:-2])/20
            user = review.find('span',attrs={'class':'author-name'}).find('a')
            user = user['href'].split('id=')[1] if user is not None else ''
            result['apptitle'] = title
            result['appgenre'] = appInfoResult['genre']
            result['appid'] = id
            result['no'] = reviewNo
            result['author'] = author
            result['date'] = date
            result['rating'] = rating
            result['body'] = body_content
            result['user'] = user
            collection.insert(result)
            if reviewNo >= limit:
                whileFlag = False
                break
            else:
                reviewNo+=1
        print 'page: ' + str(pageNum)
        pageNum+=1
        time.sleep(5)

    print 'saved: ' + str(collection.find({"appid":id}).count())

def getAppInfo(id):
    url = 'https://play.google.com/store/apps/details?id='+id
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }
    r = requests.post(url, headers=headers)
    soup = BeautifulSoup(r.text)

    appInfoResult = dict()
    appInfoResult['title'] = soup.find('div',attrs={'class':'id-app-title'}).text
    appInfoResult['genre'] = soup.find('a',attrs={'class':'document-subtitle category'}).text
    return appInfoResult

## function - Load Review from MongoDB
def setReviewData(id):
    print 'analyze begin - '+id
    client = MongoClient('mongodb://localhost:27017/')
    db = client.reviews
    collection = db.app
    if id == 'all':
        data = collection.find({})
    else:
        data = collection.find({"appid":id})

    for row in data:
        collection.remove({'_id':row['_id']})
        row['wordset'] = getTokenizedWords(row['body'])
        row['shortness'] = checkWithRating(checkShortness(row['wordset']),row['rating'])
        row['exaggeration'] = checkWithRating(checkExaggeration(row['wordset']),row['rating'])
        row['reward'] = checkWithRating(checkReward(row['body']),row['rating'])
        collection.insert(row)

## function - tokenize
def getTokenizedWords(text):
    twitter = Twitter()
    tokens = twitter.pos(text, norm=True, stem=True)
    results = list()
    for token in tokens:
        if token[1] in ['Noun','KoreanParticle','Adjective']:
            results.append(token[0])
    results = list(set(results))
    return results

## FraudCheck1 - Shortness
def checkShortness(tokens):
    lengthLimit = 5
    result = len(tokens) < lengthLimit
    return result

## FraudCheck2 - Exaggeration
def checkExaggeration(tokens):
    mots = [u'최고',u'좋다',u'짱',u'별루']
    intersectLimit = 0
    result = len(mots) - len(list(set(mots) - set(tokens))) > intersectLimit
    return result

## FraudCheck3 - Reward
def checkReward(body):
    # 1 - mots check
    result = False
    mots = [u'쿠폰',u'이벤트',u'아이템',u'이모티콘',u'아이디',u'계정']
    for mot in mots:
        if mot in body:
            result = True
            break
    # 2 - has email?
    result = result or bool(re.search(r"(\w+[\w\.]*)@(\w+[\w\.]*)\.([A-Za-z]+)", body))
    # 3 - has website? has id?
    result = result or bool(re.match(r'([a-zA-Z]|[0-9]|[$-_@.&+]){5}', body))
    return result

## FraudCheck - With Rating
def checkWithRating(result,rating):
    if rating in [1,5] and result:
        return 'High'
    elif rating in [2,4] and result:
        return 'Medium'
    elif rating in [3] and result:
        return 'Low'
    else:
        return ''

## AppId Collecting
def saveTopAppIds(limit):
    print 'Top App Id Crawling - Begin'
    url = 'https://play.google.com/store/apps/collection/topselling_free'
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }
    whileFlag = True
    count = 1
    start = 0
    num = 60
    apps = list()
    while whileFlag:
        data = {'start':start,'num':num}
        r = requests.post(url, data=data, headers=headers)
        soup = BeautifulSoup(r.text)
        for div in soup.findAll('div',attrs={'class':'card-content id-track-click id-track-impression'}):
            title = div.find('a',attrs={'class':'title'}).text
            id = div.find('span',attrs={'class':'preview-overlay-container'})['data-docid']
            appinfos = dict()
            appinfos['title'] = title
            appinfos['id'] = id
            apps.append(appinfos)
            count+=1
            if count > limit:
                whileFlag = False
                break
        start += num
        time.sleep(2)
    print 'Top App Id Crawling - Done: ' + str(len(apps))
    return apps

# Generate Total Data
def genData(endRank,reviewNum,beginRank = 0):
    for rank, app in enumerate(saveTopAppIds(endRank),start=1):
        print 'Processing Rank: '+str(rank) + ' / ' + str(endRank)
        if beginRank > rank:
            print '> Do nothing'
            continue
        id = app['id']
        title = app['title']
        deleteReview(id)
        saveReview(reviewNum,id,title)
        setReviewData(id)
