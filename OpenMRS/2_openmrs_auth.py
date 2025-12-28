#!/usr/bin/env python3
"""
OpenMRS Authentication Script
1. Registers a new OAuth2 Client (if needed)
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

    REDIRECT_URI = "http://127.0.0.1:3000/callback"
    REDIRECT_URIS = ["http://localhost:3000/callback", "http://127.0.0.1:3000/callback"]
    CALLBACK_PORT = 3000
    SCOPES = "openid fhirUser patient/Patient.read patient/Patient.write patient/Encounter.read patient/Encounter.write"

    APP_TYPE = "public"  # OpenMRS typically uses public clients with PKCE
    AUTH_METHOD = "none"  # For public clients using PKCE

    # Application Registration
    APP_NAME = "OpenMRS POC Testing App"

    # Credentials (will be populated)
    CODE_VERIFIER = None
    CLIENT_ID = None
    CLIENT_SECRET = None

# Global variable to store authorization code
auth_code = None

def generate_pkce_pair():
    """Generate PKCE code verifier and challenge."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

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
            # Ignore non-auth callback requests (favicon, etc.)
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress default logging

class OpenMRSAuth:
    def __init__(self):
        self.config = Config()
        self.load_env()
        self.config.CODE_VERIFIER, code_challenge = generate_pkce_pair()
        self.code_challenge = code_challenge

    def load_env(self):
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if '=' in line:
                            k, v = line.strip().split('=', 1)
                            if k == 'CLIENT_ID':
                                self.config.CLIENT_ID = v
                            elif k == 'CLIENT_SECRET':
                                self.config.CLIENT_SECRET = v
                            elif k == 'OPENMRS_BASE_URL':
                                self.config.BASE_URL = v
        except Exception:
            pass

    def get_authorization_code(self):
        print(f"\n{'='*80}\nSTEP 1: Get Authorization Code (Browser)\n{'='*80}")

        # Start local server to listen for callback
        server = HTTPServer(('127.0.0.1', self.config.CALLBACK_PORT), CallbackHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # Construct Authorization URL
        # Generate State
        state = secrets.token_hex(16)

        params = {
            "response_type": "code",
            "client_id": "fhir-client-app",  # Default OpenMRS OAuth2 client ID
            "redirect_uri": self.config.REDIRECT_URI,
            "scope": self.config.SCOPES,
            "state": state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256"
        }

        auth_url = f"{self.config.BASE_URL}/oauth2/authorize?{urllib.parse.urlencode(params)}"
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
        print(f"\n{'='*80}\nSTEP 2: Exchange Code for Token\n{'='*80}")

        url = f"{self.config.BASE_URL}/oauth2/token"

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.REDIRECT_URI,
            "code_verifier": self.config.CODE_VERIFIER,
            "client_id": "fhir-client-app"  # Default OpenMRS OAuth2 client ID
        }

        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(url, data=payload, headers=headers, verify=False)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("Body: " + json.dumps(data, indent=2))
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token", "")
                print("✅ Access Token Received")
                return access_token, refresh_token
            else:
                print("Body: " + json.dumps(response.json(), indent=2))
                print("❌ Error: Token exchange failed")
                return None, None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None, None

    def save_to_env(self, access_token, refresh_token=""):
        print(f"\n{'='*80}\nSTEP 3: Save Credentials to .env\n{'='*80}")

        env_content = f"""OPENMRS_BASE_URL={self.config.BASE_URL}
CLIENT_ID=fhir-client-app
ACCESS_TOKEN={access_token}
REFRESH_TOKEN={refresh_token}
"""
        with open(".env", "w") as f:
            f.write(env_content)

        import os
        print(f"✅ Credentials saved to {os.path.abspath('.env')}")

def main():
    print("Starting OpenMRS Authentication...")
    auth = OpenMRSAuth()

    code = auth.get_authorization_code()
    if code:
        token, refresh_token = auth.exchange_code_for_token(code)
        if token:
            auth.save_to_env(token, refresh_token)

if __name__ == "__main__":
    main()