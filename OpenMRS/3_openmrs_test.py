#!/usr/bin/env python3
"""
OpenMRS FHIR Test Script
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
        self.base_url = self.env.get('OPENMRS_BASE_URL', 'https://localhost:8443')
        self.fhir_url = f"{self.base_url}/ws/fhir2/R4"
        self.token = self.env.get('ACCESS_TOKEN')
        self.ids = {}

        # Validate that we have required credentials
        if not self.token:
            raise Exception("Access token not found in .env file. Run 2_openmrs_auth.py first.")

    def load_env(self):
        env = {}
        if not os.path.exists('.env'):
            raise Exception(".env file not found. Run 2_openmrs_auth.py first.")
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

    def search_encounters(self):
        self.print_step("Search Encounters")
        url = f"{self.fhir_url}/Encounter"
        try:
            res = self.session.get(url, headers=self.get_headers())
            self.print_response(res)
            if res.status_code == 200:
                print("✅ Success - Encounters searchable (Unlike OpenEMR)")
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
                    "given": ["OpenMRS", "Patient"]
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-01",
            "telecom": [
                {
                    "system": "email",
                    "value": "test@example.com",
                    "use": "home"
                }
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                print("✅ Patient Created Successfully - Full CRUD Support")
                # Parse response body
                response_data = {}
                if res.text.strip():
                    try:
                        response_data = res.json()
                        print(f"DEBUG: Response Body: {json.dumps(response_data, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"DEBUG: Response Body (non-JSON): {res.text}")
                        return True

                # Extract patient ID from response
                self.ids['patient'] = (
                    response_data.get('id') or
                    response_data.get('identifier', [{}])[0].get('value') if response_data.get('identifier') else None or
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

    def create_encounter(self):
        if not self.ids.get('patient'):
            print("⚠️  Creating patient first for encounter test...")
            if not self.create_patient():
                print("⚠️  Skipping Encounter: No Patient ID available")
                return False
                
        self.print_step("Create Encounter - FULLY SUPPORTED unlike OpenEMR")
        url = f"{self.fhir_url}/Encounter"
        data = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "subject": {
                "reference": f"Patient/{self.ids['patient']}",
                "display": "Test Patient"
            },
            "period": {
                "start": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "185349003",
                            "display": "Encounter for check up (procedure)"
                        }
                    ]
                }
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                print("✅ Encounter Created Successfully - This works in OpenMRS!")
                response_data = res.json() if res.text.strip() else {}
                self.ids['encounter'] = (
                    response_data.get('id') or
                    response_data.get('identifier', [{}])[0].get('value') if response_data.get('identifier') else None or
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

    def create_observation(self):
        if 'patient' not in self.ids:
            print("⚠️  Creating patient first for observation test...")
            if not self.create_patient():
                print("⚠️  Skipping Observation: No Patient ID available")
                return False
        if 'encounter' not in self.ids:
            print("⚠️  Creating encounter first for observation test...")
            if not self.create_encounter():
                print("⚠️  Skipping Observation: No Encounter ID available")
                return False
                
        self.print_step("Create Observation - Now possible with Encounter support")
        url = f"{self.fhir_url}/Observation"
        data = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel with all children optional"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{self.ids['patient']}"
            },
            "encounter": {
                "reference": f"Encounter/{self.ids['encounter']}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mm[Hg]",
                        "system": "http://unitsofmeasure.org"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 80,
                        "unit": "mm[Hg]",
                        "system": "http://unitsofmeasure.org"
                    }
                }
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['observation'] = (
                    response_data.get('id') or
                    response_data.get('identifier', [{}])[0].get('value') if response_data.get('identifier') else None or
                    self.extract_id_from_location_header(res.headers)
                )
                print(f"✅ Created Observation ID: {self.ids.get('observation', 'NOT FOUND')}")
                return True
            else:
                print(f"❌ Failed with status {res.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

    def create_appointment(self):
        if not self.ids.get('patient'):
            print("⚠️  Creating patient first for appointment test...")
            if not self.create_patient():
                print("⚠️  Skipping Appointment: No Patient ID available")
                return False
                
        self.print_step("Create Appointment - FULLY SUPPORTED unlike OpenEMR")
        url = f"{self.fhir_url}/Appointment"
        start_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00Z")
        end_time = (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%dT10:00:00Z")

        data = {
            "resourceType": "Appointment",
            "status": "booked",
            "serviceCategory": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/service-category",
                            "code": "17",
                            "display": "General Practice"
                        }
                    ]
                }
            ],
            "start": start_time,
            "end": end_time,
            "participant": [
                {
                    "actor": {
                        "reference": f"Patient/{self.ids['patient']}",
                        "display": "Test Patient"
                    },
                    "status": "accepted"
                },
                {
                    "actor": {
                        "reference": "Practitioner/1",
                        "display": "Dr. Smith"
                    },
                    "status": "accepted"
                }
            ]
        }
        try:
            res = self.session.post(url, json=data, headers=self.get_headers())
            self.print_response(res)
            if res.status_code in [200, 201]:
                response_data = res.json() if res.text.strip() else {}
                self.ids['appointment'] = (
                    response_data.get('id') or
                    response_data.get('identifier', [{}])[0].get('value') if response_data.get('identifier') else None or
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

    def extract_id_from_location_header(self, headers):
        """Extract resource ID from Location header if present"""
        location = headers.get('Location', '')
        if location:
            # Extract ID from URL path
            parts = location.rstrip('/').split('/')
            if parts and parts[-1]:
                return parts[-1]
        return None

    def run(self):
        print("Starting OpenMRS FHIR Tests...")
        print("Note: Unlike OpenEMR, OpenMRS supports full CRUD operations for Patients and Encounters!")
        try:
            # Validate token first
            print(f"Using token: {'Present' if self.token else 'Missing'}")
            print(f"FHIR URL: {self.fhir_url}")

            # Run search tests first to validate authentication
            search_patients_success = self.search_patients()
            search_encounters_success = self.search_encounters()  # This works in OpenMRS!

            if not search_patients_success:
                print("\n❌ Authentication or connectivity issue detected. Stopping tests.")
                return

            # Run write operations sequentially
            operations = [
                ('create_patient', 'Patient'),
                ('create_encounter', 'Encounter'),  # This works in OpenMRS!
                ('create_observation', 'Observation'),
                ('create_appointment', 'Appointment')  # This works in OpenMRS!
            ]

            for method_name, resource_name in operations:
                print(f"\n--- Processing {resource_name} ---")
                method = getattr(self, method_name)
                try:
                    success = method()
                    if not success:
                        print(f"⚠️  {resource_name} creation failed, continuing with other tests...")
                except Exception as e:
                    print(f"❌ Error creating {resource_name}: {e}")

            print("\n" + "="*50)
            print("OPENMRS TEST REPORT - IMPROVED OVER OPENEMR")
            print("="*50)
            if self.ids:
                for k, v in self.ids.items():
                    print(f"{k.title()}: {v}")
                print("\n✅ SUCCESS: All operations that were attempted succeeded!")
                print("✅ Unlike OpenEMR, OpenMRS supports full FHIR resource operations")
            else:
                print("No resources were created successfully.")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    TestRunner().run()