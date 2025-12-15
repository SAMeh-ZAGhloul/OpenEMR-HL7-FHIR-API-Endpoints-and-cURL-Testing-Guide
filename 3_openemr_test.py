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

    def search_patients(self):
        self.print_step("Search Patients")
        url = f"{self.fhir_url}/Patient"
        res = self.session.get(url, headers=self.get_headers())
        self.print_response(res)
        if res.status_code == 200:
            print("✅ Success")

    def create_patient(self):
        self.print_step("Create Patient")
        url = f"{self.fhir_url}/Patient"
        data = {
            "resourceType": "Patient",
            "active": True,
            "name": [{"family": "Test", "given": ["Split", "Script"]}],
            "gender": "male",
            "birthDate": "1990-01-01"
        }
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            print("✅ Created")
            self.ids['patient'] = res.json().get('id')
        
    def create_appointment(self):
        if 'patient' not in self.ids: return
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
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            self.ids['appointment'] = res.json().get('id')
            print("✅ Created")

    def create_encounter(self):
        if 'patient' not in self.ids: return
        self.print_step("Create Encounter")
        url = f"{self.fhir_url}/Encounter"
        data = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {"code": "AMB", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "period": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
        }
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            self.ids['encounter'] = res.json().get('id')
            print("✅ Created")

    def create_vitals(self):
        if 'encounter' not in self.ids: return
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
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            self.ids['vitals'] = res.json().get('id')
            print("✅ Created")

    def create_note(self):
        if 'encounter' not in self.ids: return
        self.print_step("Create Clinical Note")
        url = f"{self.fhir_url}/DocumentReference"
        note = base64.b64encode(b"Patient doing well.").decode()
        data = {
            "resourceType": "DocumentReference",
            "status": "current",
            "type": {"coding": [{"system": "http://loinc.org", "code": "34109-7"}]},
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "context": {"encounter": [{"reference": f"Encounter/{self.ids['encounter']}"}]},
            "content": [{"attachment": {"contentType": "text/plain", "data": note}}]
        }
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            self.ids['note'] = res.json().get('id')
            print("✅ Created")

    def create_medication(self):
        if 'encounter' not in self.ids: return
        self.print_step("Create Medication Request")
        url = f"{self.fhir_url}/MedicationRequest"
        data = {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "subject": {"reference": f"Patient/{self.ids['patient']}"},
            "medicationCodeableConcept": {"coding": [{"code": "83391", "system": "http://www.nlm.nih.gov/research/umls/rxnorm", "display": "Ibuprofen"}]}
        }
        res = self.session.post(url, json=data, headers=self.get_headers())
        self.print_response(res)
        if res.status_code in [200, 201]:
            self.ids['medication'] = res.json().get('id')
            print("✅ Created")

    def run(self):
        print("Starting FHIR Tests...")
        try:
            self.search_patients()
            
            try:
                self.create_patient()
                self.create_appointment()
                self.create_encounter()
                self.create_vitals()
                self.create_note()
                self.create_medication()
            except Exception as e:
                print(f"⚠️ Write Ops Error: {e}")
                
            print("\n" + "="*40)
            print("TEST REPORT")
            print("="*40)
            for k, v in self.ids.items():
                print(f"{k.title()}: {v}")
            
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    TestRunner().run()
