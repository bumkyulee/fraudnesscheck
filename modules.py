#-*- coding: utf-8 -*-
import requests
import json
from BeautifulSoup import BeautifulSoup

## Get Google Reviews By Page
def getReview(limit, id):
    url = 'https://play.google.com/store/getreviews'
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }

    results = list()
    pageNum = 0
    reviewNo = 1
    whileFlag = True

    while whileFlag:
        data = {'reviewType':'0','pageNum':pageNum,'id':id,'reviewSortOrder':'0','xhr':'1'}
        r = requests.post(url, data=data, headers=headers)
        try:
            data = json.loads(r.text[5:])
            soup = BeautifulSoup(data[0][2])
        except:
            break
        for review in soup.findAll('div',attrs={'class':'single-review'}):
            result = dict()
            author = review.find('span',attrs={'class':'author-name'}).text
            date = review.find('span',attrs={'class':'review-date'}).text.encode('utf-8').replace('년','.').replace('월','.').replace('일','').decode('utf-8')
            title = review.find('span',attrs={'class':'review-title'}).text
            body = title + ' ' + review.find('div',attrs={'class':'review-body'}).text[len(title):-5]
            rating = int(review.find('div',attrs={'class':'current-rating'})['style'].split(':')[1].strip()[:-2])/20
            result['no'] = reviewNo
            result['author'] = author
            result['date'] = date
            result['rating'] = rating
            result['body'] = body
            result['warning1'] = 'none'
            result['warning2'] = 'none'
            result['warning3'] = 'none'
            result['warning4'] = 'none'
            results.append(result)
            if reviewNo >= limit:
                whileFlag = False
                break
            else:
                reviewNo+=1
        pageNum+=1

    return results