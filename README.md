# OpenEMR FHIR API Testing Guide & Automation Suite

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-green.svg)](https://www.hl7.org/fhir/)
[![OpenEMR](https://img.shields.io/badge/OpenEMR-7.0+-orange.svg)](https://www.open-emr.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **🚀 NEW!** This repository now includes a **complete Python automation suite** that automates OAuth2 authentication and tests all FHIR API endpoints. No more manual cURL commands!

## 📚 Quick Navigation

| Document | Purpose | For |
|----------|---------|-----|
| **[INDEX.md](INDEX.md)** | Documentation hub | Finding the right guide |
| **[QUICKSTART.md](QUICKSTART.md)** | 3-step setup | Running tests immediately |
| **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** | What was created | Understanding the automation |
| **[WORKFLOW.md](WORKFLOW.md)** | Visual diagrams | Seeing the flow |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Comprehensive docs | Detailed information |
| **README.md** (this file) | API documentation | cURL examples & reference |

## 🎯 Choose Your Path

### Path 1: Automated Testing (Recommended) ⚡
```bash
# Check prerequisites
python3 check_prerequisites.py

# Run all tests automatically
python3 openemr_api_test.py
```
**→ See [QUICKSTART.md](QUICKSTART.md) for details**

### Path 2: Manual cURL Testing 📝
Follow the detailed cURL examples in this README below.

---

# OpenEMR Real API Endpoints and cURL Testing Guide (FHIR ONLY)

This guide provides the necessary steps and actual OpenEMR RESTful API endpoints for testing the Proof of Concept (PoC) scenarios, exclusively using the HL7 FHIR standard.

**NOTE:** These commands assume your deployed OpenEMR instance (e.g., via Docker) has its FHIR API enabled and properly configured.

## Prerequisites: API Configuration and Authentication

You must obtain an OAuth 2.0 access token to make secure API calls.

### Step 1: Enable the APIs

Navigate to: **Administration → Config → Connectors**

Enable the following checkboxes:
- ☑ **Enable OpenEMR Standard REST API** (for `/api/` endpoints)
- ☑ **Enable OpenEMR Standard FHIR REST API** (for `/fhir/` endpoints)

### Step 2: Configure SSL/TLS (Required for OAuth2)

Navigate to: **Administration → Config → Connectors → Site Address**

Set your base URL (required for OAuth2 and FHIR):
- Example: `https://your-openemr.example.com` or `https://localhost:8443`

### Step 3: Register Your Application via API

**⚠️ NOTE:** OpenEMR uses **dynamic client registration** via API call, NOT a web interface form.

Use the following cURL command to register your application:

```bash
curl -X POST -k -H 'Content-Type: application/json' \
  https://localhost:8443/oauth2/default/registration \
  --data '{
    "application_type": "private",
    "redirect_uris": ["https://client.example.org/callback"],
    "post_logout_redirect_uris": ["https://client.example.org/logout/callback"],
    "client_name": "POC Testing App",
    "token_endpoint_auth_method": "client_secret_post",
    "contacts": ["admin@example.com"],
    "scope": "openid offline_access api:oemr api:fhir user/Patient.read user/Observation.read"
  }'
```

**Important Parameters:**
- `application_type`: `"private"` (confidential client with shared secret)
- `client_name`: Human-readable app name
- `token_endpoint_auth_method`: `"client_secret_post"` (uses client_secret)
- `scope`: Space-separated list of requested scopes

### Step 4: Save Your Credentials

The registration response will include:

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "registration_access_token": "...",
  "client_id_issued_at": 1604767861,
  "client_secret_expires_at": 0
}
```

"client_id":"OsBbkF36Da-XraOFwbchuEkDVyrkPFyNV2OinjDeFxg"
"client_secret":"iyPLK7aB3PR30mwnN8xJVcgF1F4v8ReMefJ0gy_Z1XcQmRJWox9JX1a_Z3FrjAT_YOAFBmcWvPGKSzECyxKNiQ"
"registration_access_token":"tMHVlC2JyF8tEZiX-EZw_m76iAkaiBVsgaTBFX2rq9M"
"registration_client_uri":"https:\/\/localhost:8443\/oauth2\/default\/client\/Qtrg19RbVccMMidAvZp2hQ"
"client_id_issued_at":1765724421
"client_secret_expires_at":0
"client_role":"user"
"contacts":["admin@example.com"]
"application_type":"private"
"client_name":"POC Testing App"
"redirect_uris":["https:\/\/client.example.org\/callback"]
"post_logout_redirect_uris":["https:\/\/client.example.org\/logout\/callback"]
"token_endpoint_auth_method":"client_secret_post"
"scope":"openid offline_access api:oemr api:fhir user\/Patient.read user\/Observation.read"
"dsi_type":"none"

**ACTION:** Copy and save `client_id` and `client_secret` immediately. The secret cannot be retrieved later.

### Step 0.1: Obtain Access Token (Authorization Code Grant)

This instance supports the **Authorization Code Grant** flow. Follow these steps:

| Variable       | Description               | Example Value                          |
|----------------|---------------------------|----------------------------------------|
| $CLIENT_ID     | From registration response | XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA |
| $CLIENT_SECRET | From registration response | Gzd9cooABqpT5ObaBf0RvkNILGTEqDafKs6aVfHdnfkjqtowKIpZ5j3yf6sDokNN9AAVsCSO |
| $REDIRECT_URI  | Registered callback URL    | http://localhost:3000/callback |

#### Step 1: Get Authorization Code (Browser)

Open this URL in your browser and log in as **admin**:

```
https://localhost:8443/oauth2/default/authorize?response_type=code&client_id=XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&scope=openid%20offline_access%20user/Patient.read&state=random_state_12345
```

After approving the consent screen, you will be redirected to:
```
http://localhost:3000/callback?code=AUTHORIZATION_CODE&state=random_state_12345
```

**Copy the authorization code from the URL.**

#### Step 2: Exchange Code for Access Token

```bash
export CLIENT_ID="XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA"
export CLIENT_SECRET="Gzd9cooABqpT5ObaBf0RvkNILGTEqDafKs6aVfHdnfkjqtowKIpZ5j3yf6sDokNN9AAVsCSO"
export AUTH_CODE="PASTE_YOUR_AUTH_CODE_HERE"
export REDIRECT_URI="http://localhost:3000/callback"

curl -X POST -k -H 'Content-Type: application/x-www-form-urlencoded' \
  https://localhost:8443/oauth2/default/token \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode "client_secret=$CLIENT_SECRET" \
  --data-urlencode "redirect_uri=$REDIRECT_URI" \
  --data-urlencode "code=$AUTH_CODE"
```

#### Token Response

Expected response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def5020017b484b0add020bf3491a8a537fa04eda12...",
  "scope": "openid offline_access user/Patient.read"
}
```

**ACTION:** Save the `access_token` value as `$API_TOKEN`

#### Refresh Token (Optional)

To refresh an expired access token:

```bash
export REFRESH_TOKEN="def5020017b484b0add020bf3491a8a537fa04eda12..."
export CLIENT_ID="XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA"
export CLIENT_SECRET="Gzd9cooABqpT5ObaBf0RvkNILGTEqDafKs6aVfHdnfkjqtowKIpZ5j3yf6sDokNN9AAVsCSO"

curl -X POST -k -H 'Content-Type: application/x-www-form-urlencoded' \
  https://localhost:8443/oauth2/default/token \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode "client_secret=$CLIENT_SECRET" \
  --data-urlencode "refresh_token=$REFRESH_TOKEN"
```

## 1. Scenario A: Patient Demographics and Registration (FHIR Patient)

**Goal:** Create a new patient record using the FHIR Patient resource.

### API Endpoint: Patient Creation

| Method | Endpoint                                    | Description                |
|--------|---------------------------------------------|----------------------------|
| POST   | $OPENEMR_HOST/apis/default/fhir/Patient    | Creates a new FHIR Patient resource. |

### cURL Script (Patient Registration)

```bash
# 1. Register Patient (POST /apis/default/fhir/Patient)
# A successful response will return a 201 Created status and the new Patient ID.

curl -X POST "https://localhost:8443/apis/default/fhir/Patient" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "Patient",
    "active": true,
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
}'
```

**ACTION:** Save the resulting Patient ID from the response (e.g., "id": "123") as `$PATIENT_ID`

## 2. Scenario B: Scheduling and Appointment Workflow (FHIR Appointment)

**Goal:** Book a new appointment for the registered patient using the FHIR Appointment resource.

### API Endpoint: Appointment Creation

| Method | Endpoint                                      | Description                           |
|--------|-----------------------------------------------|---------------------------------------|
| POST   | $OPENEMR_HOST/apis/default/fhir/Appointment  | Schedules a new FHIR Appointment resource. |

### cURL Script (Appointment Booking)

The appointment requires references to the patient (`$PATIENT_ID`) and the intended provider (Practitioner/1).

```bash
# 2. Book Appointment (POST /apis/default/fhir/Appointment)
# Books a 30-minute appointment for tomorrow at 11:00 AM.

curl -X POST "https://localhost:8443/apis/default/fhir/Appointment" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "Appointment",
    "status": "booked",
    "description": "Annual Wellness Visit PoC",
    "start": "2025-12-14T11:00:00Z",
    "end": "2025-12-14T11:30:00Z",
    "participant": [
        {
            "actor": {"reference": "Patient/$PATIENT_ID"},
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
}'
```

## 3. Scenario C: Clinical Encounter and Notes (FHIR Encounter & Observation)

**Goal:** Start a new encounter, log Vitals, and add a clinical note using FHIR.

### API Endpoints: Encounter & Vitals

| Method | Endpoint                                      | Description                          |
|--------|-----------------------------------------------|--------------------------------------|
| POST   | $OPENEMR_HOST/apis/default/fhir/Encounter    | Starts a new FHIR Encounter.        |
| POST   | $OPENEMR_HOST/apis/default/fhir/Observation  | Records individual Vital Signs (Observations). |

### cURL Script (FHIR Encounter Workflow)

#### Step 3.1: Start a New Encounter

```bash
# 3.1 Start New Encounter (POST /apis/default/fhir/Encounter)
# The response will return the unique Encounter ID.

curl -X POST "https://localhost:8443/apis/default/fhir/Encounter" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "Encounter",
    "status": "in-progress",
    "class": {"code": "AMB", "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode"},
    "subject": {"reference": "Patient/$PATIENT_ID"},
    "period": {"start": "2025-12-13T10:00:00Z"},
    "serviceProvider": {"reference": "Organization/1"}
}'
```

**ACTION:** Save the resulting "id" value from the response as `$ENCOUNTER_ID`

#### Step 3.2: Log Vital Signs (FHIR Observation)

FHIR requires separate Observation resources for each vital sign. We will demonstrate Blood Pressure (a complex, multi-component Observation).

```bash
# 3.2 Log Vitals - Blood Pressure (POST /apis/default/fhir/Observation)
# Uses LOINC codes for standardized vital sign definition (85354-9 is BP).

curl -X POST "https://localhost:8443/apis/default/fhir/Observation" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "Observation",
    "status": "final",
    "subject": {"reference": "Patient/$PATIENT_ID"},
    "encounter": {"reference": "Encounter/$ENCOUNTER_ID"},
    "code": {
        "coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}],
        "text": "Blood Pressure"
    },
    "component": [
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic Blood Pressure"}]},
            "valueQuantity": {"value": 120, "unit": "mm[Hg]", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}
        },
        {
            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic Blood Pressure"}]},
            "valueQuantity": {"value": 80, "unit": "mm[Hg]", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}
        }
    ]
}'
```

**NOTE:** Separate Observation POSTs are required for temperature (8310-5), heart rate (8867-4), etc.

#### Step 3.3: Add Clinical Note (FHIR DocumentReference)

Clinical notes (SOAP) are stored as a FHIR DocumentReference linking to the text content. This is more robust than storing narrative within the Encounter.

| Method | Endpoint                                              | Description                          |
|--------|-------------------------------------------------------|--------------------------------------|
| POST   | $OPENEMR_HOST/apis/default/fhir/DocumentReference    | Saves a clinical note or document pointer. |

```bash
# 3.3 Add Clinical Note (POST /apis/default/fhir/DocumentReference)

curl -X POST "https://localhost:8443/apis/default/fhir/DocumentReference" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "DocumentReference",
    "status": "current",
    "docStatus": "final",
    "type": {
        "coding": [{"system": "http://loinc.org", "code": "34109-7", "display": "Note"}]
    },
    "subject": {"reference": "Patient/$PATIENT_ID"},
    "context": {"encounter": [{"reference": "Encounter/$ENCOUNTER_ID"}]},
    "content": [{
        "attachment": {
            "contentType": "text/plain",
            "data": "U2Vuc2l0aXZlIEluZm86IFBhdGllbnQgcmVwb3J0cyBtaWxkIGhlYWRhY2hlLiBPYmplY3RpdmU6IFZpdGFscyBzdGFibGUu"
            # Base64 encoded: "Sensitive Info: Patient reports mild headache. Objective: Vitals stable."
        }
    }]
}'
```

## 4. Scenario D: Electronic Prescribing and Ordering (FHIR MedicationRequest and ServiceRequest)

**Goal:** Create a medication prescription and a lab order using FHIR.

### API Endpoints (FHIR)

| Method | Endpoint                                          | Description                           |
|--------|---------------------------------------------------|---------------------------------------|
| POST   | $OPENEMR_HOST/apis/default/fhir/MedicationRequest | Creates a request for a prescription. |
| POST   | $OPENEMR_HOST/apis/default/fhir/ServiceRequest    | Creates an order for a lab test.      |

### cURL Script (FHIR Ordering Workflow)

#### Step 4.1: Create a Prescription Order (FHIR MedicationRequest)

```bash
# 4.1 Create Prescription (POST /apis/default/fhir/MedicationRequest)
curl -X POST "https://localhost:8443/apis/default/fhir/MedicationRequest" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "MedicationRequest",
    "status": "active",
    "intent": "order",
    "subject": {"reference": "Patient/$PATIENT_ID"},
    "encounter": {"reference": "Encounter/$ENCOUNTER_ID"},
    "authoredOn": "2025-12-13",
    "medicationCodeableConcept": {
        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "83391"}],
        "text": "Ibuprofen 200mg Tablet"
    },
    "dosageInstruction": [{
        "text": "Take 1 tablet every 4 to 6 hours as needed for pain.",
        "timing": {"repeat": {"frequency": 1, "period": 6, "periodUnit": "h"}}
    }]
}'
```

#### Step 4.2: Create a Lab Order (FHIR ServiceRequest)

```bash
# 4.2 Create Lab Order (POST /apis/default/fhir/ServiceRequest)
curl -X POST "https://localhost:8443/apis/default/fhir/ServiceRequest" \
-H "Authorization: Bearer $API_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "resourceType": "ServiceRequest",
    "status": "active",
    "intent": "order",
    "code": {
        "coding": [{"system": "http://loinc.org", "code": "58410-2", "display": "CBC Panel"}]
    },
    "subject": {"reference": "Patient/$PATIENT_ID"},
    "encounter": {"reference": "Encounter/$ENCOUNTER_ID"},
    "requester": {"reference": "Practitioner/1"},
    "occurrenceDateTime": "2025-12-13T10:00:00Z"
}'
```
```
