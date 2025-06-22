#TASKS:
#(FINISHED) connect frontend to backend - Everyone
#(FINISHED) build company list page - Alex
#(FINISHED) build dashboard webpage skeleton (features: different platform options, analytics?) - Vincent
#(FINISHED) build page to input what type of users you want to reach out to + what type of msg you wanna send (after selecting a platform) - Alex
#(FINISHED) scrape/crawl platforms for user data - Matthew
#(FINISHED) build RAG architecture (how the LLM uses user data to make msgs personalized) - Vincent
#(FINISHED) ensure RAG updates fast - Vincent
#(FINISHED) plug RAG data into an LLM (should be gemini for one of the prize categories iirc) - Matthew
#(FINISHED) plug scraped data into RAG architecture - Vincent
#(FINISHED) authentication and emails - Alex
#(FINISHED) analytics - Alex & Matthew
#(FINISHED) outreach overview - Alex
#(FINISHED) fix linkedin account security
#(FINISHED) presentation/pitch & deliverables - Frank & Everyone


from flask import Flask, render_template, request, redirect, session, jsonify
from livereload import Server
from pymongo.mongo_client import MongoClient 
from pymongo.server_api import ServerApi
from datetime import datetime
import queryDB
import outreach

import google.generativeai as genai
from dotenv import load_dotenv
import os
import asyncio


load_dotenv() #import environment variables 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


import secrets

import importlib.util
spec = importlib.util.spec_from_file_location("google_auth", "google-auth.py")
google_auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_auth)

get_oauth_flow = google_auth.get_oauth_flow
get_user_info = google_auth.get_user_info
save_user = google_auth.save_user
get_user = google_auth.get_user
send_email = google_auth.send_email













app = Flask(__name__)
app.debug = True  

app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
#setup
uri = ""
client = MongoClient(uri, server_api=ServerApi('1'))
genai.configure(api_key="")
#we can worry about the open api keys later.
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.flask_db
users = db.users
companies = db.companies
optimal_companies = db.optimal_companies





#routing
@app.route("/")
def home():
    return render_template("dashboard.html", user=session.get('user'))

@app.route("/register")
def register():
    return render_template("register.html")

# Google OAuth routes
@app.route("/login")
def login():
    flow = get_oauth_flow()
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = get_oauth_flow()
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    user_info = get_user_info(credentials)
    
    # Save user to database
    save_user(user_info['email'], user_info['name'], 
              user_info.get('picture'), credentials)
    
    # Store user info in session
    session['user'] = {
        'email': user_info['email'],
        'name': user_info['name'],
        'picture': user_info.get('picture'),
        'authenticated': True
    }
    
    # Redirect back to where they came from or dashboard
    return redirect(session.get('next_url', '/'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

# @app.route("/analytics")
# def analytics():
#     return render_template("analytics.html")

#requests
@app.route('/search', methods=['POST'])
def search():
    genre = request.form['genre']
    query = request.form['template']
    effective_companies = []

    #vector db search for relevant companies
    company_data = queryDB.query_db_outreach(10, genre)

    #MONGODb search for effective companies
    for company in company_data:
        result = optimal_companies.find_one({
            "name": company["name"],
            "willing_to_outreach": True
        })

        if result:
            # Mark highlighted and put company at front
            company["highlighted"] = True
            effective_companies.insert(0, company)

            # Query the other collection for this company
            company_doc = companies.find_one({"name": company["name"]})

            if company_doc:
                # Assuming posts is a list of dicts with e.g. a timestamp or _id
                # Find the most recent post - example using 'created_at' field
                most_recent_post = company_doc["element"][len(company_doc["element"]) - 1]
                
                # Attach it to your company dict or do something else
                company["most_recent_post"] = most_recent_post
        else:
            # Append others to the end
            effective_companies.append(company)
        
        

    return render_template(
        'companies.html',
        company_data = effective_companies,
        query = query
    )


@app.route('/api/message-history', methods=['POST'])
def get_message_history():
#     """Get the message history for the given user email"""
#     data = request.get_json()
#     email = data.get("email")
#     if not email:
#         return jsonify({"error": "Email is required"}), 400

#     user = users.find_one({"email": email})
#     if not user or "emails" not in user:
#         return jsonify({"emails": []})

#     return jsonify({"emails": user["emails"]})


# @app.route('/api/message-history', methods=['POST'])
# def get_message_history():
#     """Get the message history for the logged-in user"""



    # For now, return mock data
    # In production, this would fetch from your database
    mock_data = [
        {
            "company": "TechStartup Inc.",
            "email": "hello@techstartup.com",
            "subject": "Partnership Opportunity",
            "dateSent": "2024-01-15",
            "status": "sent"
        },
        {
            "company": "Digital Agency Co.",
            "email": "contact@digitalagency.com", 
            "subject": "Design Services Proposal",
            "dateSent": "2024-01-14",
            "status": "sent"
        },
        {
            "company": "Innovation Labs",
            "email": "info@innovationlabs.com",
            "subject": "Collaboration Request",
            "dateSent": "2024-01-13",
            "status": "sent"
        }
    ]
    
    return jsonify(mock_data)

@app.route('/generate', methods=['POST'])
def generate():
    # Check if user is authenticated
    if not session.get('user') or not session['user'].get('authenticated'):
        # Store the intended destination
        session['next_url'] = request.url
        return redirect('/login')
        
    query = request.form['transfer-info']
    from_email = request.form['email-info']
    selected_ids = request.form.getlist('selected_companies')

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    user_email = session['user']['email']
    json_data = []
    for company_name in selected_ids:
        response = model.generate_content(f"Give ONLY the email and no extra text. What is the business inquiry email for the company f{company_name}? Give ONLY the email and no extra text.")

        email = response.text.strip()
        print(email)

        email = "alex.tan.toronto2@gmail.com"
        overview = request.form[f'overview_{company_name}']
        industry = request.form[f'industry_{company_name}']
        employees = request.form[f'employees_{company_name}']

        # Generate personalized message
        message = outreach.message_generator(company_name, overview, industry, employees, query)
        
        # Send email using Google OAuth
        result = send_email(user_email, email, f"Partnership Opportunity with {company_name}", message)
        json_data.append({
            "company": company_name,
            "email": email,
            "subject": "Collaboration Request",
            "dateSent": datetime.today().strftime('%Y-%m-%d'),
            "status": "sent"
        })
    users.update_one(
    { "email": from_email },
    # { "email" : "alex.tan.toronto2@gmail.com"},
    { "$push": { "emails": {
        "company": company_name,
        "email": email,
        "subject": "Collaboration Request",
        "dateSent": datetime.today().strftime('%Y-%m-%d'),
        "status": "sent"
    }}},
    upsert=True
)

    return render_template(
        'dashboard.html',
    )













server = Server(app.wsgi_app)
server.watch("templates")
server.watch("static")
server.serve(port=5002)
