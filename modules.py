import requests
import json
from BeautifulSoup import BeautifulSoup

## Get Google Reviews By Page
def getReview(pageNum, id):
    url = 'https://play.google.com/store/getreviews'
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }

    result = list()

    data = {'reviewType':'0','pageNum':pageNum,'id':id,'reviewSortOrder':'0','xhr':'1'}
    r = requests.post(url, data=data, headers=headers)
    data = json.loads(r.text[5:])
    try:
        soup = BeautifulSoup(data[0][2])
    except:
        return result
    for review in soup.findAll('div',attrs={'class':'single-review'}):
        author = review.find('span',attrs={'class':'author-name'}).text
        date = review.find('span',attrs={'class':'review-date'}).text
        title = review.find('span',attrs={'class':'review-title'}).text
        body = title + ' ' + review.find('div',attrs={'class':'review-body'}).text[len(title):-5]
        rating = int(review.find('div',attrs={'class':'current-rating'})['style'].split(':')[1].strip()[:-2])/20
        result.append(author + ' / ' + date + ' / ' + body + ' / ' + str(rating))

    return result