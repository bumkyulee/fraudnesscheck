from flask import Flask
import requests
import json
from BeautifulSoup import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def main():

    url = 'https://play.google.com/store/getreviews'
    data = {'reviewType':'0','pageNum':'0','id':'com.sampleapp','reviewSortOrder':'0','xhr':'1'}
    headers = {
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'user-agent': 'Mozilla/5.0'
    }
    r = requests.post(url, data=data, headers=headers)
    data = json.loads(r.text[5:])
    soup = BeautifulSoup(data[0][2])
    for review in soup.findAll('div',attrs={'class':'single-review'}):
        author = review.find('span',attrs={'class':'author-name'}).text
        date = review.find('span',attrs={'class':'review-date'}).text
        title = review.find('span',attrs={'class':'review-title'}).text
        body = review.find('div',attrs={'class':'review-body'}).text[len(title):-5]
        rating = int(review.find('div',attrs={'class':'current-rating'})['style'].split(':')[1].strip()[:-2])/20
        break

    return author + ' / ' + date + ' / ' + title + ' / ' + body + ' / ' + str(rating)

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')