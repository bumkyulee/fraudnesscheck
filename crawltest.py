import requests
import json
from BeautifulSoup import BeautifulSoup

url = 'https://play.google.com/store/getreviews'
data = {'reviewType':'0','pageNum':'100','id':'com.sampleapp','reviewSortOrder':'0','xhr':'1'}
headers = {
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'user-agent': 'Mozilla/5.0'
}
r = requests.post(url, data=data, headers=headers)
data = json.loads(r.text[5:])
soup = BeautifulSoup(data[0][2])
print soup.html
for review in soup.select('.single-review'):
    title = review.select('.review-title')[0].text
    body = review.select('.review-body')[0].text
    rating = int(review.select('.current-rating')[0]['style'].split(':')[1].strip()[:-2])/20
    print title + ' / ' + body + ' / ' + rating


