from flask import Flask,request,jsonify
from pymongo import MongoClient

client = MongoClient('localhost', 27017)


db = client.flask_db
todos = db.todos




app = Flask(__name__)

@app.route('/api/validate', methods=['POST'])
def validate_request():
    # Validate the incoming request

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"status": "error", "message": "Missing username or password"}, 400

    return {"status": "success"}

@app.route('/api/scrape',methods=['POST'])
def scrape():
    #scrapes
    data = request.get_json()
    url = data.get('url')
    scraped_data = "poopoo"
    if not url:
        return {"status": "error", "message": "Missing URL"}, 400

    # Perform scraping logic here
    # ...

    return {"status": "success", "data": scraped_data}

@app.route('/', methods=['GET'])
def index():
    return "MHAHAHAHAHA BACKEND"

if __name__ == '__main__':
    app.run(debug=True, port=5000)