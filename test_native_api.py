#!/usr/bin/env python3
"""
Test script to access OpenEMR native API
"""
import requests
import os
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load access token from .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('ACCESS_TOKEN='):
            access_token = line.split('=')[1].strip()
            break

# Base URL
base_url = 'https://localhost:8443/apis/default/api'

# Headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Test accessing a patient
print("Testing access to patient data via native API...")
try:
    response = requests.get(f'{base_url}/patient/1', headers=headers, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# Test accessing patient encounters
print("\nTesting access to patient encounters via native API...")
try:
    response = requests.get(f'{base_url}/patient/1/encounter', headers=headers, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# Test creating an encounter via native API (this is what we want to do)
print("\nTesting encounter creation via native API...")
try:
    # First, let's get the patient ID we created earlier
    # We'll use the patient ID from the most recent test
    patient_uuid = "a0a79d7a-6cc2-45f1-938b-30a2fd0aeadf"  # From our previous test
    
    encounter_data = {
        "date": "2025-12-22 15:00:00",
        "reason": "Test encounter via API",
        "facility_id": 1,
        "provider_id": 1,
        "encounter_type": "office"
    }
    
    response = requests.post(f'{base_url}/patient/{patient_uuid}/encounter', 
                           json=encounter_data, headers=headers, verify=False)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")