#!/usr/bin/env python3
"""
OpenEMR FHIR Test Script
1. Loads credentials from .env
2. Runs FHIR API Tests
3. Generates Test Report
"""

import requests
import json
import base64
from datetime import datetime, timedelta
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.env = self.load_env()
        self.base_url = self.env.get('OPENEMR_BASE_URL', 'https://localhost:8443')
        self.fhir_url = f"{self.base_url}/apis/default/fhir"
        self.token = self.env.get('ACCESS_TOKEN')
        self.ids = {}

        # Validate that we have required credentials
        if not self.token:
            raise Exception("Access token not found in .env file. Run 2_openemr_auth.py first.")

    def load_env(self):
        env = {}
        if not os.path.exists('.env'):
            raise Exception(".env file not found. Run 2_openemr_auth.py first.")
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    env[key] = val
        return env

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def print_step(self, name):
        print(f"\nTEST: {name}")
        print("-" * 40)

    def print_response(self, res):
        print(f"Status: {res.status_code}")
        if res.status_code >= 400:
            print(f"Error: {res.text[:200]}")
        else:
            print(f"Response: {res.text[:200]}...")

    def search_patients(self):
        self.print_step("Search Patients")
        url = f"{self.fhir_url}/Patient"
        try:
            res = self.session.get(url, headers=self.get_headers())
            self.print_response(res)
            if res.status_code == 200:
                print("✅ Success")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_patient(self):
        self.print_step("Create Patient")
        url = f"{self.fhir_url}/Patient"
        data = {
            "resourceType": "Patient",
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": "Test",
                    "given": ["Split", "Script"]
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-01"
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                print("✅ Created")
                # Debug: Print full response info
                print(f"DEBUG: Response Headers: {dict(res.headers)}")

                # Parse response body
                response_data = {}
                if res.text.strip():
                    try:
                        response_data = res.json()
                        print(f"DEBUG: Response Body: {json.dumps(response_data, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"DEBUG: Response Body (non-JSON): {res.text}")
                        return True  # Still consider successful if status indicates success

                # Extract patient ID from response
                self.ids['patient'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )

                print(f"Captured Patient ID: {self.ids.get('patient', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def extract_id_from_location_header(self, headers):
        """Extract resource ID from Location header if present"""
        location = headers.get('Location', '')
        if location:
            # Extract ID from URL path
            parts = location.rstrip('/').split('/')
            if parts and parts[-1]:
                return parts[-1]
        return None

    def create_appointment(self):
        if not self.ids.get('patient'):
            print("⚠️ Skipping Appointment: No Patient ID captured")
            return
        self.print_step("Create Appointment")
        url = f"{self.fhir_url}/Appointment"
        next_hour = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(hours=1, minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

        data = {
            "resourceType": "Appointment",
            "status": "booked",
            "start": next_hour,
            "end": end_time,
            "participant": [
                {"actor": {"reference": f"Patient/{self.ids['patient']}"}, "status": "accepted"},
                {"actor": {"reference": "Practitioner/1"}, "status": "accepted"}
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['appointment'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created Appointment ID: {self.ids.get('appointment', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_encounter(self):
        if not self.ids.get('patient'):
            print("⚠️ Skipping Encounter: No Patient ID captured")
            return
        self.print_step("Create Encounter")
        url = f"{self.fhir_url}/Encounter"
        data = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {"code": "AMB", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "period": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['encounter'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created Encounter ID: {self.ids.get('encounter', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_vitals(self):
        if 'encounter' not in self.ids:
            print("⚠️ Skipping Vitals: No Encounter ID captured")
            return
        self.print_step("Create Vital Signs (BP)")
        url = f"{self.fhir_url}/Observation"
        data = {
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "encounter": {"reference": f"Encounter/{self.ids['encounter']}"},
            "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "BP Panel"}]},
            "component": [
                {"code": {"coding": [{"code": "8480-6"}]}, "valueQuantity": {"value": 120, "unit": "mmHg"}},
                {"code": {"coding": [{"code": "8462-4"}]}, "valueQuantity": {"value": 80, "unit": "mmHg"}}
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['vitals'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created Observation ID: {self.ids.get('vitals', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_note(self):
        if 'encounter' not in self.ids:
            print("⚠️ Skipping Note: No Encounter ID captured")
            return
        self.print_step("Create Clinical Note")
        url = f"{self.fhir_url}/DocumentReference"
        note = base64.b64encode(b"Patient doing well.").decode()
        data = {
            "resourceType": "DocumentReference",
            "status": "current",
            "docStatus": "final",
            "type": {"coding": [{"system": "http://loinc.org", "code": "11488-4", "display": "Consult Note"}]},
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "context": {"encounter": [{"reference": f"Encounter/{self.ids['encounter']}"}]},
            "content": [{"attachment": {"contentType": "text/plain", "data": note}}]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['note'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created DocumentReference ID: {self.ids.get('note', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_medication(self):
        if 'encounter' not in self.ids:
            print("⚠️ Skipping Medication: No Encounter ID captured")
            return
        self.print_step("Create Medication Request")
        url = f"{self.fhir_url}/MedicationRequest"
        data = {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "medicationCodeableConcept": {"coding": [{"code": "83391", "system": "http://www.nlm.nih.gov/research/umls/rxnorm", "display": "Ibuprofen"}]}
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['medication'] = (
                    response_data.get('id') or
                    response_data.get('uuid') or
                    response_data.get('pid') or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created MedicationRequest ID: {self.ids.get('medication', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def run(self):
        print("Starting FHIR Tests...")
        try:
            # Validate token first
            print(f"Using token: {'Present' if self.token else 'Missing'}")
            print(f"FHIR URL: {self.fhir_url}")

            # Run search test first to validate authentication
            search_success = self.search_patients()

            if not search_success:
                print("\n❌ Authentication or connectivity issue detected. Stopping tests.")
                return

            # Run write operations sequentially
            operations = [
                ('create_patient', 'Patient'),
                ('create_encounter', 'Encounter'),
                ('create_vitals', 'Vital Signs'),
                ('create_note', 'Note'),
                ('create_medication', 'Medication')
            ]

            for method_name, resource_name in operations:
                print(f"\n--- Processing {resource_name} ---")
                method = getattr(self, method_name)
                try:
                    success = method()
                    if not success:
                        print(f"⚠️ {resource_name} creation failed, continuing with other tests...")
                except Exception as e:
                    print(f"❌ Error creating {resource_name}: {e}")

            print("\n" + "="*40)
            print("TEST REPORT")
            print("="*40)
            if self.ids:
                for k, v in self.ids.items():
                    print(f"{k.title()}: {v}")
            else:
                print("No resources were created successfully.")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    TestRunner().run()
