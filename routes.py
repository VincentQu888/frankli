from flask import Flask, request, jsonify, redirect, session, url_for
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv
from google_auth import get_oauth_flow, save_user, get_user_info, send_email, get_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# client = MongoClient('localhost', 27017)
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.flask_db
todos = db.todos


# Test connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connection failed:", e)




app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-this')
CORS(app)
users = db.users




# Create user if they don't exist
def create_user_if_not_exists(email, name):
    user = users.find_one({"email": email})
    if not user:
        new_user = {
            "email": email,
            "name": name,
            "cold_emails_sent": 0,
            "cold_emails_successful": 0,
            "emails": []
        }
        result = users.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        print(f"Created new user: {email}")
        return new_user
    else:
        user["_id"] = str(user["_id"])
        print(f"User already exists: {email}")
        return user

# Endpoint: Get or create user history
@app.route('/api/history', methods=['POST'])
def get_history():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    if not email:
        return jsonify({"status": "error", "message": "Missing email"}), 400
    user_info = create_user_if_not_exists(email, name or "")
    return jsonify(user_info)





# @app.route('/api/validate', methods=['POST'])
# def validate_request():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
    
#     if not username or not password:
#         return {"status": "error", "message": "Missing username or password"}, 400
#     return {"status": "success"}

# @app.route('/api/scrape', methods=['POST'])
# def scrape():
#     data = request.get_json()
#     url = data.get('url')
#     scraped_data = "poopoo"
#     if not url:
#         return {"status": "error", "message": "Missing URL"}, 400
#     return {"status": "success", "data": scraped_data}






@app.route('/api/auth/google/login', methods=['GET'])
def google_login():
    try:
        if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
            return jsonify({'error': 'Missing Google OAuth credentials in .env'}), 500
        
        flow = get_oauth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        session['state'] = state
        return jsonify({'auth_url': authorization_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/oauth2callback')
def oauth2callback():
    flow = get_oauth_flow()
    flow.fetch_token(authorization_response=request.url)
    
    user_info = get_user_info(flow.credentials)
    save_user(
        email=user_info['email'],
        name=user_info['name'],
        picture=user_info.get('picture', ''),
        credentials=flow.credentials
    )
    session['user_email'] = user_info['email']
    
    redirect_url = f"http://localhost:5001/demo.html?email={user_info['email']}&name={user_info['name']}"
    return redirect(redirect_url)

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    email = session.get('user_email') or request.args.get('email')
    if not email:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = get_user(email)
    if user:
        return jsonify({
            "email": user['email'],
            "name": user['name'],
            "picture": user['picture']
        })
    return jsonify({"error": "User not found"}), 404


@app.route('/api/send-email', methods=['POST'])
def send_email_route():
    data = request.get_json()
    user_email = session.get('user_email') or data.get('user_email')
    
    if not user_email:
        return jsonify({"error": "Not authenticated"}), 401
    
    to = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    
    if not all([to, subject, body]):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = send_email(user_email, to, subject, body)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/', methods=['GET'])
def index():
    return "MHAHAHAHAHA BACKEND"

if __name__ == '__main__':
    # Port 5000 conflicts with AirPlay on macOS, using 5001 instead (please)
    app.run(debug=True, port=5001, host='127.0.0.1')