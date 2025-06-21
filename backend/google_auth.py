import os
import json
import sqlite3
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def init_db():
    conn = sqlite3.connect('gmail_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, 
                  name TEXT,
                  picture TEXT,
                  tokens TEXT,
                  created_at TIMESTAMP,
                  last_login TIMESTAMP)''')
    conn.commit()
    conn.close()

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5001/oauth2callback'

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def get_oauth_flow():
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)

def get_user_info(credentials):
    service = build('oauth2', 'v2', credentials=credentials)
    return service.userinfo().get().execute()

def save_user(email, name, picture, credentials):
    conn = sqlite3.connect('gmail_users.db')
    c = conn.cursor()
    
    creds_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    c.execute("""INSERT OR REPLACE INTO users 
                 (email, name, picture, tokens, created_at, last_login) 
                 VALUES (?, ?, ?, ?, 
                         COALESCE((SELECT created_at FROM users WHERE email = ?), ?),
                         ?)""",
              (email, name, picture, json.dumps(creds_dict), 
               email, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect('gmail_users.db')
    c = conn.cursor()
    c.execute("SELECT name, picture, tokens FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name, picture, tokens = row
        creds_dict = json.loads(tokens)
        credentials = Credentials(**creds_dict)
        return {
            'email': email,
            'name': name,
            'picture': picture,
            'credentials': credentials
        }
    return None

def send_email(user_email, to, subject, body):
    user = get_user(user_email)
    if not user:
        return {"error": "User not found"}
    
    creds = user['credentials']
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_user(user_email, user['name'], user['picture'], creds)
    
    service = build('gmail', 'v1', credentials=creds)
    
    try:
        sent = service.users().messages().send(
            userId='me', 
            body={'raw': create_message(user_email, to, subject, body)}
        ).execute()
        return {"success": True, "messageId": sent['id']}
    except Exception as e:
        return {"error": str(e)}

def create_message(from_email, to, subject, body):
    import base64
    from email.mime.text import MIMEText
    
    message = MIMEText(body)
    message['to'] = to
    message['from'] = from_email
    message['subject'] = subject
    return base64.urlsafe_b64encode(message.as_bytes()).decode()

init_db() 