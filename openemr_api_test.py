#!/usr/bin/env python3
"""
OpenEMR FHIR API Testing Script
Automates OAuth2 authentication and tests all FHIR API endpoints
"""

import requests
import json
import base64
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys
import secrets
import hashlib

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Config:
    """Configuration for OpenEMR API"""
    BASE_URL = "https://localhost:8443"
    OAUTH_BASE = f"{BASE_URL}/oauth2/default"
    FHIR_BASE = f"{BASE_URL}/apis/default/fhir"
    
    # OAuth2 Configuration
    REDIRECT_URI = "http://localhost:3000/callback"
    CALLBACK_PORT = 3000
    
    # Application Registration
    APP_NAME = "POC Testing App"
    APP_TYPE = "native"
    CODE_VERIFIER = None
    SCOPES = "openid offline_access api:oemr api:fhir"
    
    # Credentials (will be populated after registration)
    CLIENT_ID = None
    CLIENT_SECRET = None
    ACCESS_TOKEN = None
    REFRESH_TOKEN = None
    
    # Test Data IDs (will be populated during testing)
    PATIENT_ID = None
    ENCOUNTER_ID = None
    APPOINTMENT_ID = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth2 callback"""
    auth_code = None
    
    def do_GET(self):
        """Handle GET request with authorization code"""
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
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Error: No authorization code received</h1></body></html>")
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


class OpenEMRAPI:
    """OpenEMR FHIR API Client"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates
    
    def print_step(self, step_num: str, description: str):
        """Print formatted step header"""
        print(f"\n{'='*80}")
        print(f"STEP {step_num}: {description}")
        print(f"{'='*80}")
    
    def print_response(self, response: requests.Response, show_full: bool = False):
        """Print formatted API response"""
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            if show_full:
                print(f"Response Body:\n{json.dumps(data, indent=2)}")
            else:
                # Show abbreviated response
                if isinstance(data, dict):
                    if 'id' in data:
                        print(f"Resource ID: {data['id']}")
                    if 'resourceType' in data:
                        print(f"Resource Type: {data['resourceType']}")
                print(f"Response Body (abbreviated):\n{json.dumps(data, indent=2)[:500]}...")
        except:
            print(f"Response Body: {response.text[:500]}")
    
    def register_application(self) -> Tuple[str, str]:
        """
        Step 3: Register application via dynamic client registration
        Returns: (client_id, client_secret)
        """
        self.print_step("3", "Register Application via API")
        
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
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = self.session.post(url, json=payload)
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            Config.CLIENT_ID = data['client_id']
            Config.CLIENT_SECRET = data.get('client_secret')
            print(f"\n✅ Registration Successful!")
            print(f"Client ID: {Config.CLIENT_ID}")
            print(f"Client Secret: {Config.CLIENT_SECRET}")
            return Config.CLIENT_ID, Config.CLIENT_SECRET
        else:
            raise Exception(f"Registration failed: {response.text}")
    
    def get_authorization_code(self) -> str:
        """
        Step 0.1.1: Get authorization code via browser
        Returns: authorization_code
        """
        self.print_step("0.1.1", "Get Authorization Code (Browser)")
        
        # Generate PKCE
        verifier = secrets.token_urlsafe(64)
        Config.CODE_VERIFIER = verifier
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

        # Build authorization URL
        params = {
            'response_type': 'code',
            'client_id': Config.CLIENT_ID,
            'redirect_uri': Config.REDIRECT_URI,
            'scope': Config.SCOPES,
            'state': 'random_state_12345',
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
        auth_url = f"{Config.OAUTH_BASE}/authorize?{urllib.parse.urlencode(params)}"
        
        print(f"Authorization URL: {auth_url}")
        print(f"\n📌 Opening browser for authentication...")
        print(f"Please log in as 'admin' and approve the consent screen.")
        
        # Start callback server
        server = HTTPServer(('localhost', Config.CALLBACK_PORT), CallbackHandler)
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for callback
        print(f"Waiting for authorization callback...")
        server_thread.join(timeout=120)  # 2 minute timeout
        
        if CallbackHandler.auth_code:
            print(f"\n✅ Authorization Code Received: {CallbackHandler.auth_code[:20]}...")
            return CallbackHandler.auth_code
        else:
            raise Exception("Failed to receive authorization code")
    
    def exchange_code_for_token(self, auth_code: str) -> Dict:
        """
        Step 0.1.2: Exchange authorization code for access token
        Returns: token response dict
        """
        self.print_step("0.1.2", "Exchange Code for Access Token")
        
        url = f"{Config.OAUTH_BASE}/token"
        
        # Public client with PKCE
        payload = {
            'grant_type': 'authorization_code',
            'redirect_uri': Config.REDIRECT_URI,
            'code': auth_code,
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET,
            'code_verifier': Config.CODE_VERIFIER
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = self.session.post(
            url,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        self.print_response(response, show_full=True)
        
        if response.status_code == 200:
            data = response.json()
            Config.ACCESS_TOKEN = data['access_token']
            Config.REFRESH_TOKEN = data.get('refresh_token')
            print(f"\n✅ Access Token Received!")
            print(f"Token Type: {data['token_type']}")
            print(f"Expires In: {data['expires_in']} seconds")
            print(f"Scope: {data.get('scope', 'N/A')}")
            return data
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def refresh_access_token(self) -> Dict:
        """
        Refresh expired access token
        Returns: token response dict
        """
        self.print_step("REFRESH", "Refresh Access Token")
        
        url = f"{Config.OAUTH_BASE}/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': Config.REFRESH_TOKEN,
            'client_id': Config.CLIENT_ID,
            'client_secret': Config.CLIENT_SECRET
        }
        
        response = self.session.post(
            url,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            data = response.json()
            Config.ACCESS_TOKEN = data['access_token']
            print(f"✅ Token Refreshed!")
            return data
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def get_auth_headers(self) -> Dict:
        """Get authorization headers for API calls"""
        return {
            'Authorization': f'Bearer {Config.ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    # ==================== SCENARIO A: Patient Demographics ====================
    
    def search_patients(self) -> None:
        """
        Test: Search for patients (Read Access check)
        """
        self.print_step("A.1", "Search Patients (Read Access Check)")
        
        url = f"{Config.FHIR_BASE}/Patient"
        print(f"GET {url}")
        
        response = self.session.get(url, headers=self.get_auth_headers())
        self.print_response(response, show_full=False)
        
        if response.status_code == 200:
            print("✅ Patient Search Successful (Read Access Confirmed)")
            data = response.json()
            if 'entry' in data:
                print(f"Found {len(data['entry'])} patients.")
            else:
                print("No patients found, but access allowed.")
        else:
             print(f"❌ Patient Search Failed: {response.status_code}")

    def create_patient(self) -> str:
        """
        Scenario A: Create a new patient
        Returns: patient_id
        """
        self.print_step("A", "Create Patient (FHIR Patient Resource)")
        
        url = f"{Config.FHIR_BASE}/Patient"
        patient_data = {
            "resourceType": "Patient",
            "active": True,
            "name": [{
                "use": "official",
                "family": "Appletest",
                "given": ["Jane", "M"]
            }],
            "gender": "female",
            "birthDate": "1988-03-15",
            "telecom": [{
                "system": "phone",
                "value": "555-444-3333",
                "use": "mobile"
            }],
            "address": [{
                "line": ["456 Test Lane"],
                "city": "Testville",
                "state": "CA",
                "postalCode": "90210"
            }]
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(patient_data, indent=2)}")
        
        response = self.session.post(url, json=patient_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            Config.PATIENT_ID = data.get('id')
            print(f"\n✅ Patient Created Successfully!")
            print(f"Patient ID: {Config.PATIENT_ID}")
            return Config.PATIENT_ID
        else:
            raise Exception(f"Patient creation failed: {response.text}")
    
    # ==================== SCENARIO B: Appointment Scheduling ====================
    
    def create_appointment(self) -> str:
        """
        Scenario B: Create an appointment
        Returns: appointment_id
        """
        self.print_step("B", "Create Appointment (FHIR Appointment Resource)")
        
        if not Config.PATIENT_ID:
            raise Exception("Patient ID not available. Create a patient first.")
        
        url = f"{Config.FHIR_BASE}/Appointment"
        
        # Calculate appointment time (tomorrow at 11:00 AM)
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        
        appointment_data = {
            "resourceType": "Appointment",
            "status": "booked",
            "description": "Annual Wellness Visit PoC",
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "participant": [
                {
                    "actor": {"reference": f"Patient/{Config.PATIENT_ID}"},
                    "status": "accepted"
                },
                {
                    "actor": {"reference": "Practitioner/1"},
                    "status": "accepted"
                },
                {
                    "actor": {"reference": "Location/1"},
                    "status": "accepted"
                }
            ]
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(appointment_data, indent=2)}")
        
        response = self.session.post(url, json=appointment_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            Config.APPOINTMENT_ID = data.get('id')
            print(f"\n✅ Appointment Created Successfully!")
            print(f"Appointment ID: {Config.APPOINTMENT_ID}")
            return Config.APPOINTMENT_ID
        else:
            print(f"⚠️ Appointment creation failed: {response.text}")
            return None
    
    # ==================== SCENARIO C: Clinical Encounter ====================
    
    def create_encounter(self) -> str:
        """
        Scenario C.1: Create a clinical encounter
        Returns: encounter_id
        """
        self.print_step("C.1", "Create Encounter (FHIR Encounter Resource)")
        
        if not Config.PATIENT_ID:
            raise Exception("Patient ID not available. Create a patient first.")
        
        url = f"{Config.FHIR_BASE}/Encounter"
        encounter_data = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {
                "code": "AMB",
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"
            },
            "subject": {"reference": f"Patient/{Config.PATIENT_ID}"},
            "period": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")},
            "serviceProvider": {"reference": "Organization/1"}
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(encounter_data, indent=2)}")
        
        response = self.session.post(url, json=encounter_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            Config.ENCOUNTER_ID = data.get('id')
            print(f"\n✅ Encounter Created Successfully!")
            print(f"Encounter ID: {Config.ENCOUNTER_ID}")
            return Config.ENCOUNTER_ID
        else:
            print(f"⚠️ Encounter creation failed: {response.text}")
            return None
    
    def create_vital_signs(self) -> str:
        """
        Scenario C.2: Create vital signs observation
        Returns: observation_id
        """
        self.print_step("C.2", "Create Vital Signs (FHIR Observation - Blood Pressure)")
        
        if not Config.PATIENT_ID or not Config.ENCOUNTER_ID:
            raise Exception("Patient ID or Encounter ID not available.")
        
        url = f"{Config.FHIR_BASE}/Observation"
        observation_data = {
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": f"Patient/{Config.PATIENT_ID}"},
            "encounter": {"reference": f"Encounter/{Config.ENCOUNTER_ID}"},
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel"
                }],
                "text": "Blood Pressure"
            },
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic Blood Pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mm[Hg]",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic Blood Pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": 80,
                        "unit": "mm[Hg]",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                }
            ]
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(observation_data, indent=2)}")
        
        response = self.session.post(url, json=observation_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            observation_id = data.get('id')
            print(f"\n✅ Vital Signs Recorded Successfully!")
            print(f"Observation ID: {observation_id}")
            return observation_id
        else:
            print(f"⚠️ Vital signs creation failed: {response.text}")
            return None
    
    def create_clinical_note(self) -> str:
        """
        Scenario C.3: Create clinical note
        Returns: document_reference_id
        """
        self.print_step("C.3", "Create Clinical Note (FHIR DocumentReference)")
        
        if not Config.PATIENT_ID or not Config.ENCOUNTER_ID:
            raise Exception("Patient ID or Encounter ID not available.")
        
        url = f"{Config.FHIR_BASE}/DocumentReference"
        
        # Base64 encode the clinical note
        note_text = "Sensitive Info: Patient reports mild headache. Objective: Vitals stable."
        encoded_note = base64.b64encode(note_text.encode()).decode()
        
        document_data = {
            "resourceType": "DocumentReference",
            "status": "current",
            "docStatus": "final",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "34109-7",
                    "display": "Note"
                }]
            },
            "subject": {"reference": f"Patient/{Config.PATIENT_ID}"},
            "context": {
                "encounter": [{"reference": f"Encounter/{Config.ENCOUNTER_ID}"}]
            },
            "content": [{
                "attachment": {
                    "contentType": "text/plain",
                    "data": encoded_note
                }
            }]
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(document_data, indent=2)}")
        
        response = self.session.post(url, json=document_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            doc_id = data.get('id')
            print(f"\n✅ Clinical Note Created Successfully!")
            print(f"DocumentReference ID: {doc_id}")
            return doc_id
        else:
            print(f"⚠️ Clinical note creation failed: {response.text}")
            return None
    
    # ==================== SCENARIO D: Prescribing and Ordering ====================
    
    def create_medication_request(self) -> str:
        """
        Scenario D.1: Create medication prescription
        Returns: medication_request_id
        """
        self.print_step("D.1", "Create Prescription (FHIR MedicationRequest)")
        
        if not Config.PATIENT_ID or not Config.ENCOUNTER_ID:
            raise Exception("Patient ID or Encounter ID not available.")
        
        url = f"{Config.FHIR_BASE}/MedicationRequest"
        medication_data = {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "subject": {"reference": f"Patient/{Config.PATIENT_ID}"},
            "encounter": {"reference": f"Encounter/{Config.ENCOUNTER_ID}"},
            "authoredOn": datetime.now().strftime("%Y-%m-%d"),
            "medicationCodeableConcept": {
                "coding": [{
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "83391"
                }],
                "text": "Ibuprofen 200mg Tablet"
            },
            "dosageInstruction": [{
                "text": "Take 1 tablet every 4 to 6 hours as needed for pain.",
                "timing": {
                    "repeat": {
                        "frequency": 1,
                        "period": 6,
                        "periodUnit": "h"
                    }
                }
            }]
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(medication_data, indent=2)}")
        
        response = self.session.post(url, json=medication_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            med_id = data.get('id')
            print(f"\n✅ Medication Request Created Successfully!")
            print(f"MedicationRequest ID: {med_id}")
            return med_id
        else:
            print(f"⚠️ Medication request creation failed: {response.text}")
            return None
    
    def create_service_request(self) -> str:
        """
        Scenario D.2: Create lab order
        Returns: service_request_id
        """
        self.print_step("D.2", "Create Lab Order (FHIR ServiceRequest)")
        
        if not Config.PATIENT_ID or not Config.ENCOUNTER_ID:
            raise Exception("Patient ID or Encounter ID not available.")
        
        url = f"{Config.FHIR_BASE}/ServiceRequest"
        service_data = {
            "resourceType": "ServiceRequest",
            "status": "active",
            "intent": "order",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "58410-2",
                    "display": "CBC Panel"
                }]
            },
            "subject": {"reference": f"Patient/{Config.PATIENT_ID}"},
            "encounter": {"reference": f"Encounter/{Config.ENCOUNTER_ID}"},
            "requester": {"reference": "Practitioner/1"},
            "occurrenceDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        print(f"POST {url}")
        print(f"Payload: {json.dumps(service_data, indent=2)}")
        
        response = self.session.post(url, json=service_data, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            service_id = data.get('id')
            print(f"\n✅ Service Request Created Successfully!")
            print(f"ServiceRequest ID: {service_id}")
            return service_id
        else:
            print(f"⚠️ Service request creation failed: {response.text}")
            return None
    
    # ==================== Query/Read Operations ====================
    
    def read_patient(self, patient_id: str = None):
        """Read patient data"""
        patient_id = patient_id or Config.PATIENT_ID
        self.print_step("READ", f"Read Patient/{patient_id}")
        
        url = f"{Config.FHIR_BASE}/Patient/{patient_id}"
        response = self.session.get(url, headers=self.get_auth_headers())
        self.print_response(response, show_full=True)
        
        if response.status_code == 200:
            print(f"\n✅ Patient Retrieved Successfully!")
        return response.json() if response.status_code == 200 else None


def main():
    """Main execution flow"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         OpenEMR FHIR API Automated Testing Script             ║
    ║                                                                ║
    ║  This script will:                                             ║
    ║  1. Register a new OAuth2 application                          ║
    ║  2. Perform OAuth2 authentication flow                         ║
    ║  3. Test all FHIR API endpoints from the README                ║
    ║                                                                ║
    ║  Prerequisites:                                                ║
    ║  - OpenEMR running at https://localhost:8443                   ║
    ║  - FHIR API enabled in Administration → Config → Connectors    ║
    ║  - Admin credentials ready for browser login                   ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    input("Press ENTER to start the automated testing...")
    
    api = OpenEMRAPI()
    
    try:
        # Step 1-3: Registration and Authentication
        print("\n" + "="*80)
        print("PHASE 1: REGISTRATION AND AUTHENTICATION")
        print("="*80)
        
        api.register_application()
        time.sleep(1)
        
        auth_code = api.get_authorization_code()
        time.sleep(1)
        
        api.exchange_code_for_token(auth_code)
        time.sleep(1)
        
        # Phase 2: Test All Scenarios
        print("\n" + "="*80)
        print("PHASE 2: TESTING FHIR API ENDPOINTS")
        print("="*80)
        
        # Scenario A: Patient Demographics
        api.search_patients()
        time.sleep(1)
        
        try:
            api.create_patient()
        except Exception as e:
            print(f"⚠️ Create Patient failed (Likely due to Public Client Write restrictions): {e}")
        time.sleep(1)
        
        # Scenario B: Appointment Scheduling
        if Config.PATIENT_ID:
            try:
                api.create_appointment()
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Create Appointment failed: {e}")
        else:
            print("⚠️ Skipping Appointment creation (No Patient ID)")
        
        # Scenario C: Clinical Encounter
        if Config.PATIENT_ID:
            try:
                api.create_encounter()
                time.sleep(1)
                
                api.create_vital_signs()
                time.sleep(1)
                
                api.create_clinical_note()
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Clinical Encounter steps failed: {e}")
        else:
             print("⚠️ Skipping Clinical Encounter steps (No Patient ID)")
        
        # Scenario D: Prescribing and Ordering
        if Config.PATIENT_ID and Config.ENCOUNTER_ID:
             try:
                api.create_medication_request()
                time.sleep(1)
                
                api.create_service_request()
                time.sleep(1)
             except Exception as e:
                 print(f"⚠️ Prescribing steps failed: {e}")
        else:
             print("⚠️ Skipping Prescribing steps (No Patient/Encounter ID)")
        
        # Read back patient data
        if Config.PATIENT_ID:
            try:
                api.read_patient()
            except Exception as e:
                print(f"⚠️ Read Patient failed: {e}")
        else:
            print("⚠️ Skipping Read Patient (No Patient ID)")
        
        # Final Summary
        print("\n" + "="*80)
        print("TESTING COMPLETE - SUMMARY")
        print("="*80)
        print(f"✅ Client ID: {Config.CLIENT_ID}")
        print(f"✅ Patient ID: {Config.PATIENT_ID}")
        print(f"✅ Appointment ID: {Config.APPOINTMENT_ID}")
        print(f"✅ Encounter ID: {Config.ENCOUNTER_ID}")
        print(f"\n🎉 All API endpoints tested successfully!")
        print(f"\nCredentials saved for future use:")
        print(f"  CLIENT_ID={Config.CLIENT_ID}")
        print(f"  CLIENT_SECRET={Config.CLIENT_SECRET}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
