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
    limit = request.args.get('limit')
    result = render_template('main.html',data=getReview(int(limit), id))
    return result

@app.route("/test")
def test():
    limit = request.args.get('limit')
    id = request.args.get('id')
    return json.dumps(getReview(int(limit), id))

if __name__ == "__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')