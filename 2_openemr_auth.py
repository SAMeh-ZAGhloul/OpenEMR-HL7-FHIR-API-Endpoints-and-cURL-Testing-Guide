#!/usr/bin/env python3
"""
OpenEMR Authentication Script
1. Registers a new OAuth2 Client
2. Authenticates via Browser (OAuth2 Code Flow with PKCE)
3. Saves credentials to .env file
"""

import requests
import json
import base64
import time
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import secrets
import hashlib
import os

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Config:
    """Configuration for OpenEMR API"""
    BASE_URL = "https://localhost:8443"
    OAUTH_BASE = f"{BASE_URL}/oauth2/default"
    
    # OAuth2 Configuration
    REDIRECT_URI = "http://localhost:3000/callback"
    CALLBACK_PORT = 3000
    
    # Application Registration
    APP_NAME = "POC Testing App"
    APP_TYPE = "native"
    SCOPES = "openid offline_access api:oemr api:fhir"
    
    # Credentials (will be populated)
    CODE_VERIFIER = None
    CLIENT_ID = None
    CLIENT_SECRET = None
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None

class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth2 callback"""
    auth_code = None
    
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>window.close();</script>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.wfile.write(b"No code received")
    
    def log_message(self, format, *args):
        pass

class AuthClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False 
    
    def print_step(self, step: str, description: str):
        print(f"\n{'='*80}\nSTEP {step}: {description}\n{'='*80}")
    
    def print_response(self, response):
        print(f"Status: {response.status_code}")
        try:
            print(f"Body: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Body: {response.text[:500]}")

    def register_application(self):
        self.print_step("1", "Register Application")
        url = f"{Config.OAUTH_BASE}/registration"
        payload = {
            "application_type": Config.APP_TYPE,
            "redirect_uris": [Config.REDIRECT_URI],
            "post_logout_redirect_uris": [f"{Config.REDIRECT_URI}/logout"],
            "client_name": Config.APP_NAME,
            "token_endpoint_auth_method": "client_secret_post",
            "contacts": ["admin@example.com"],
            "scope": Config.SCOPES
        }
        
        print(f"POST {url}")
        response = self.session.post(url, json=payload)
        self.print_response(response)
        
        if response.status_code in [200, 201]:
            data = response.json()
            Config.CLIENT_ID = data['client_id']
            Config.CLIENT_SECRET = data.get('client_secret', '')
            print("✅ Registration Successful")
            return Config.CLIENT_ID
        else:
            raise Exception("Registration failed")

    def get_authorization_code(self):
        self.print_step("2", "Get Authorization Code (Browser)")
        
        # PKCE
        verifier = secrets.token_urlsafe(64)
        Config.CODE_VERIFIER = verifier
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        
        params = {
            'response_type': 'code',
            'client_id': Config.CLIENT_ID,
            'redirect_uri': Config.REDIRECT_URI,
            'scope': Config.SCOPES,
            'state': secrets.token_hex(16),
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
        auth_url = f"{Config.OAUTH_BASE}/authorize?{urllib.parse.urlencode(params)}"
        
        print(f"Authorization URL: {auth_url}")
        print("📌 Opening browser...")
        
        server = HTTPServer(('localhost', Config.CALLBACK_PORT), CallbackHandler)
        thread = threading.Thread(target=server.handle_request)
        thread.daemon = True
        thread.start()
        
        webbrowser.open(auth_url)
        thread.join(timeout=120)
        
        if CallbackHandler.auth_code:
            print("✅ Code Received")
            return CallbackHandler.auth_code
        else:
            raise Exception("No code received")

    def exchange_code_for_token(self, code):
        self.print_step("3", "Exchange Code for Token")
        url = f"{Config.OAUTH_BASE}/token"
        payload = {
            'grant_type': 'authorization_code',
            'redirect_uri': Config.REDIRECT_URI,
            'code': code,
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'code_verifier': Config.CODE_VERIFIER
        }
        
        response = self.session.post(url, data=payload)
        self.print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            Config.ACCESS_TOKEN = data['access_token']
            print("✅ Access Token Received")
        else:
            raise Exception("Token exchange failed")

    def save_to_env(self):
        self.print_step("4", "Save Credentials to .env")
        lines = [
            f"OPENEMR_BASE_URL={Config.BASE_URL}",
            f"CLIENT_ID={Config.CLIENT_ID}",
            f"CLIENT_SECRET={Config.CLIENT_SECRET}",
            f"ACCESS_TOKEN={Config.ACCESS_TOKEN}"
        ]
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Credentials saved to {os.path.abspath('.env')}")

def main():
    print("starting OpenEMR Authentication...")
    auth = AuthClient()
    try:
        auth.register_application()
        code = auth.get_authorization_code()
        auth.exchange_code_for_token(code)
        auth.save_to_env()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
