from flask import Flask, render_template, request
from modules import *

app = Flask(__name__)

@app.route("/")
def enter():
    result = render_template('enter.html')
    return result

## html - main.html
@app.route("/main")
def main():
    id = request.args.get('id')
    result = render_template('main.html',data=id)
    #result = render_template('main.html',data=getReview(0, id))
    return result

## ajax - Get Google Play Reviews By PageNum, Id
@app.route("/review", methods=["POST"])
def review():
    pageNum = request.form.get('pageNum')
    id = request.form.get('id')
    return json.dumps(getReview(pageNum, id))

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')