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
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import secrets
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import hashlib
import os

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
class Config:
    BASE_URL = "https://localhost:8443"
    
    # OAuth2 Configuration
    REDIRECT_URI = "http://localhost:3000/callback"
    CALLBACK_PORT = 3000
    # Scopes - Requesting System scopes for full access
    SCOPES = "openid offline_access api:oemr api:fhir system/patient.read system/patient.write"
    
    # App Type - "private" (Confidential)
    # Using 'private' to attempt to acquire system scopes
    APP_TYPE = "private" 
    
    # Token Endpoint Auth Method - "client_secret_post"
    AUTH_METHOD = "client_secret_post"
    
    # Application Registration
    APP_NAME = "POC Testing App"
    
    # Credentials (will be populated)
    CODE_VERIFIER = None
    CLIENT_ID = None
    CLIENT_SECRET = None

# Global variable to store authorization code
auth_code = None

def generate_jwks():
    """Generates an RSA key pair and returns the JWKS."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    public_key = private_key.public_key()
    
    # Get public numbers
    pn = public_key.public_numbers()
    
    def to_b64url(val):
        """Helper to convert int to base64url string"""
        bytes_val = val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')
        return base64.urlsafe_b64encode(bytes_val).decode('utf-8').rstrip('=')

    jwk = {
        "kty": "RSA",
        "use": "sig",
        "kid": "1", # Key ID
        "alg": "RS256",
        "n": to_b64url(pn.n),
        "e": to_b64url(pn.e)
    }
    
    return {"keys": [jwk]}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authentication Successful!</h1><p>You can close this window and return to the terminal.</p></body></html>")
            print("\n✅ Code Received")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code parameter")
            print("\n❌ Error: Callback received but missing 'code'")
            
    def log_message(self, format, *args):
        return  # Suppress default logging

class OpenEMRAuth:
    def __init__(self):
        self.config = Config()
        self.jwks = generate_jwks()

    def register_application(self):
        print(f"\n{'='*80}\nSTEP 1: Register Application\n{'='*80}")
        
        url = f"{self.config.BASE_URL}/oauth2/default/registration"
        
        payload = {
            "application_type": self.config.APP_TYPE,
            "redirect_uris": [self.config.REDIRECT_URI],
            "client_name": self.config.APP_NAME,
            "token_endpoint_auth_method": self.config.AUTH_METHOD,
            "scope": self.config.SCOPES,
            "jwks": self.jwks, # Include JWKS for confidential client
            "response_types": ["code"],
            "grant_types": ["authorization_code", "refresh_token"]
        }
        
        print(f"POST {url}")
        try:
            response = requests.post(url, json=payload, verify=False)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                print("Body: " + json.dumps(data, indent=2))
                self.config.CLIENT_ID = data.get("client_id")
                self.config.CLIENT_SECRET = data.get("client_secret")
                print("✅ Registration Successful")
                return True
            else:
                print("Body: " + json.dumps(response.json(), indent=2))
                print("❌ Error: Registration failed")
                return False
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    def get_authorization_code(self):
        print(f"\n{'='*80}\nSTEP 2: Get Authorization Code (Browser)\n{'='*80}")
        
        # Start local server to listen for callback
        server = HTTPServer(('localhost', self.config.CALLBACK_PORT), CallbackHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        # Construct Authorization URL
        # Generate State
        state = secrets.token_hex(16)
        
        params = {
            "response_type": "code",
            "client_id": self.config.CLIENT_ID,
            "redirect_uri": self.config.REDIRECT_URI,
            "scope": self.config.SCOPES,
            "state": state,
            "aud": f"{self.config.BASE_URL}/oauth2/default"
        }
        
        auth_url = f"{self.config.BASE_URL}/oauth2/default/authorize?{urllib.parse.urlencode(params)}"
        print(f"Authorization URL: {auth_url}")
        print("📌 Opening browser...")
        
        webbrowser.open(auth_url)
        
        # Wait for code (timeout after 120 seconds)
        for _ in range(120):
            if auth_code:
                break
            time.sleep(1)
            
        server.shutdown()
        
        if not auth_code:
            print("❌ Error: Timeout waiting for authorization code")
            return None
            
        return auth_code

    def exchange_code_for_token(self, code):
        print(f"\n{'='*80}\nSTEP 3: Exchange Code for Token\n{'='*80}")
        
        url = f"{self.config.BASE_URL}/oauth2/default/token"
        
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.REDIRECT_URI,
            "client_id": self.config.CLIENT_ID,
        }
        
        # Add client secret (since we are confidential client)
        if self.config.CLIENT_SECRET:
             payload["client_secret"] = self.config.CLIENT_SECRET

        try:
            # Use data=payload for form-urlencoded content type
            response = requests.post(url, data=payload, verify=False)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Body: " + json.dumps(data, indent=2))
                access_token = data.get("access_token")
                print("✅ Access Token Received")
                return access_token
            else:
                print("Body: " + json.dumps(response.json(), indent=2))
                print("❌ Error: Token exchange failed")
                return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def save_to_env(self, access_token):
        print(f"\n{'='*80}\nSTEP 4: Save Credentials to .env\n{'='*80}")
        
        env_content = f"""OPENEMR_BASE_URL={self.config.BASE_URL}
CLIENT_ID={self.config.CLIENT_ID}
CLIENT_SECRET={self.config.CLIENT_SECRET}
ACCESS_TOKEN={access_token}
"""
        with open(".env", "w") as f:
            f.write(env_content)
            
        import os
        print(f"✅ Credentials saved to {os.path.abspath('.env')}")

def main():
    print("starting OpenEMR Authentication...")
    auth = OpenEMRAuth()
    
    if auth.register_application():
        code = auth.get_authorization_code()
        if code:
            token = auth.exchange_code_for_token(code)
            if token:
                auth.save_to_env(token)

if __name__ == "__main__":
    main()
