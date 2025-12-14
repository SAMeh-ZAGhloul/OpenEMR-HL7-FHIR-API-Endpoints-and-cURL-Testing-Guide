# OpenEMR FHIR API Testing Guide & Automation Suite

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-green.svg)](https://www.hl7.org/fhir/)
[![OpenEMR](https://img.shields.io/badge/OpenEMR-7.0+-orange.svg)](https://www.open-emr.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **🚀 Complete Python automation suite** that automates OAuth2 authentication and tests all FHIR API endpoints. No more manual cURL commands!

## 📑 Table of Contents

- [Quick Start (3 Steps)](#-quick-start-3-steps)
- [What's Included](#-whats-included)
- [Automation Overview](#-automation-overview)
- [How It Works (Workflow)](#-how-it-works-workflow)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [What Gets Tested](#-what-gets-tested)
- [Troubleshooting](#-troubleshooting)
- [Configuration](#-configuration)
- [API Reference (cURL Examples)](#-api-reference-curl-examples)
- [Files in This Repository](#-files-in-this-repository)
- [Contributing](#-contributing)

---

## 🚀 Quick Start (3 Steps)

Get started testing OpenEMR FHIR APIs in under 2 minutes:

### Step 1: Check Prerequisites
```bash
python3 check_prerequisites.py
```

**Expected Output:**
```
✅ All checks passed (5/5)
🚀 You're ready to run: python3 openemr_api_test.py
```

### Step 2: Install Dependencies (if needed)
```bash
pip3 install -r requirements.txt
```

### Step 3: Run Automated Tests
```bash
python3 openemr_api_test.py
```

**What happens:**
1. Browser opens automatically for OAuth2 login
2. You log in as admin and approve consent
3. Script tests all FHIR endpoints automatically
4. Results displayed with all resource IDs

**That's it!** 🎉

---

## 📦 What's Included

This repository provides:

### **🤖 Automation Scripts**
- **`openemr_api_test.py`** (27KB) - Complete automation suite
  - OAuth2 registration and authentication
  - Tests all FHIR endpoints (Patient, Appointment, Encounter, etc.)
  - Browser-based auth with automatic callback handling
  - Detailed logging and error handling

- **`check_prerequisites.py`** (4.9KB) - Environment validator
  - Checks Python version
  - Verifies dependencies
  - Tests OpenEMR connectivity
  - Validates FHIR and OAuth2 endpoints

### **📚 Documentation**
- **README.md** (this file) - Complete guide
- **QUICKSTART.md** - 3-step quick reference
- **TESTING_GUIDE.md** - Detailed documentation
- **WORKFLOW.md** - Visual diagrams
- **AUTOMATION_SUMMARY.md** - What was created
- **INDEX.md** - Documentation navigation

### **⚙️ Configuration**
- **requirements.txt** - Python dependencies
- **docker-compose.yml** - OpenEMR Docker setup
- **nginx configs** - SSL/TLS configuration

---

## 🎯 Automation Overview

### **Before (Manual cURL):**
```bash
# 1. Register app manually
curl -X POST ... --data '{...}'
# Copy client_id and client_secret

# 2. Open browser manually, copy auth code
open "https://localhost:8443/oauth2/..."

# 3. Exchange token manually
export CLIENT_ID="..."
curl -X POST ... --data-urlencode "client_id=$CLIENT_ID" ...

# 4. Test each endpoint manually (8+ commands)
curl -X POST ... -H "Authorization: Bearer $TOKEN" ...
```

### **After (Python Automation):**
```bash
python3 openemr_api_test.py
# Everything automated! ✨
```

### **What Gets Automated:**

✅ **OAuth2 Registration** - Dynamic client registration via API  
✅ **Browser Authentication** - Opens browser, captures auth code automatically  
✅ **Token Exchange** - Gets access token and refresh token  
✅ **All FHIR Endpoints** - Tests 8+ endpoints in sequence  
✅ **Data Validation** - Reads back created resources  
✅ **Error Handling** - Detailed error messages and troubleshooting  

---

## 🔄 How It Works (Workflow)

### **Complete Automation Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    START: Run Script                            │
│              python3 openemr_api_test.py                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Register OAuth2 Application  │
         │  POST /oauth2/default/        │
         │       registration            │
         └───────────────┬───────────────┘
                         │
                         ├─► client_id
                         └─► client_secret
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Get Authorization Code       │
         │  • Opens browser automatically│
         │  • User logs in as admin      │
         │  • Approves consent           │
         │  • Callback server captures   │
         │    authorization code         │
         └───────────────┬───────────────┘
                         │
                         └─► auth_code
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Exchange for Access Token    │
         │  POST /oauth2/default/token   │
         └───────────────┬───────────────┘
                         │
                         ├─► access_token
                         └─► refresh_token
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  TEST ALL FHIR ENDPOINTS                                        │
└─────────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    [Patient]      [Appointment]   [Encounter]
         │               │               │
         └───────────────┴───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   [Vitals]         [Notes]      [Prescriptions]
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Display Results Summary      │
         │  ✅ All tests passed!         │
         │  📋 Resource IDs saved        │
         └───────────────────────────────┘
```

### **OAuth2 Authorization Flow (Detailed)**

```
Script                                    OpenEMR Server
  │                                             │
  │ 1. POST /oauth2/default/registration        │
  │ ──────────────────────────────────────────► │
  │                                             │
  │ 2. client_id, client_secret                 │
  │ ◄────────────────────────────────────────── │
  │                                             │
  │ 3. Open browser to /authorize?client_id=... │
  │ ──────────────────────────────────────────► │
  │                                             │
  │         [User logs in via browser]          │
  │                                             │
  │ 4. Redirect to callback with code           │
  │ ◄────────────────────────────────────────── │
  │    http://localhost:3000/callback?code=...  │
  │                                             │
  │ 5. POST /oauth2/default/token               │
  │    grant_type=authorization_code            │
  │ ──────────────────────────────────────────► │
  │                                             │
  │ 6. access_token, refresh_token              │
  │ ◄────────────────────────────────────────── │
  │                                             │
  │ 7. All API calls use:                       │
  │    Authorization: Bearer <access_token>     │
  │ ──────────────────────────────────────────► │
```

---

## ✅ Prerequisites

### **Required:**
1. **Python 3.7+**
   ```bash
   python3 --version
   ```

2. **OpenEMR Instance Running**
   - URL: `https://localhost:8443` (or your custom URL)
   - FHIR API enabled: **Administration → Config → Connectors**
   - SSL/TLS configured (self-signed certificates OK for testing)

3. **Admin Credentials**
   - You'll need to log in via browser during OAuth2 flow
   - Default username: `admin`

### **Optional:**
- Docker (if you need to deploy OpenEMR)
- Git (for cloning this repository)

---

## 📥 Installation

### **1. Clone Repository**
```bash
git clone https://github.com/SAMeh-ZAGhloul/OpenEMR-HL7-FHIR-API-Endpoints-and-cURL-Testing-Guide.git
cd OpenEMR-HL7-FHIR-API-Endpoints-and-cURL-Testing-Guide
```

### **2. Install Dependencies**
```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install requests urllib3
```

### **3. Make Scripts Executable** (Optional)
```bash
chmod +x *.py
```

---

## 🎮 Usage

### **Basic Usage**

```bash
# Validate environment
python3 check_prerequisites.py

# Run all tests
python3 openemr_api_test.py
```

### **What to Expect**

1. **Script starts** and registers OAuth2 application
2. **Browser opens** to OpenEMR login page
3. **You log in** as admin and approve consent
4. **Browser shows** "Authorization Successful!"
5. **Script continues** and tests all endpoints
6. **Results displayed** with resource IDs

### **Expected Output**

```
╔════════════════════════════════════════════════════════════════╗
║         OpenEMR FHIR API Automated Testing Script             ║
╚════════════════════════════════════════════════════════════════╝

================================================================================
PHASE 1: REGISTRATION AND AUTHENTICATION
================================================================================

STEP 3: Register Application via API
✅ Registration Successful!
Client ID: XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA

STEP 0.1.1: Get Authorization Code (Browser)
📌 Opening browser for authentication...
✅ Authorization Code Received

STEP 0.1.2: Exchange Code for Access Token
✅ Access Token Received!

================================================================================
PHASE 2: TESTING FHIR API ENDPOINTS
================================================================================

STEP A: Create Patient
✅ Patient Created Successfully! Patient ID: 123

STEP B: Create Appointment
✅ Appointment Created Successfully! Appointment ID: 456

STEP C.1: Create Encounter
✅ Encounter Created Successfully! Encounter ID: 789

... (continues for all scenarios)

================================================================================
TESTING COMPLETE - SUMMARY
================================================================================
✅ Client ID: XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA
✅ Patient ID: 123
✅ Appointment ID: 456
✅ Encounter ID: 789

🎉 All API endpoints tested successfully!
```

---

## 🧪 What Gets Tested

The automation script tests **all FHIR scenarios** from the API documentation:

### **Scenario A: Patient Demographics**
✅ **POST /fhir/Patient** - Create patient record
- Name, DOB, gender, contact info, address

### **Scenario B: Appointment Scheduling**
✅ **POST /fhir/Appointment** - Book appointment
- Patient reference, practitioner, location, time

### **Scenario C: Clinical Encounter**
✅ **POST /fhir/Encounter** - Start clinical encounter
- Patient reference, status, class, period

✅ **POST /fhir/Observation** - Record vital signs
- Blood pressure (systolic/diastolic)
- LOINC codes for standardization

✅ **POST /fhir/DocumentReference** - Add clinical note
- Base64-encoded note content
- Linked to encounter

### **Scenario D: Prescribing and Ordering**
✅ **POST /fhir/MedicationRequest** - Create prescription
- Medication (RxNorm codes)
- Dosage instructions

✅ **POST /fhir/ServiceRequest** - Order lab test
- Test type (LOINC codes)
- Requester, occurrence time

### **Validation**
✅ **GET /fhir/Patient/{id}** - Read patient data back
- Verify data integrity

---

## 🔧 Troubleshooting

### **Issue: "Connection refused" or SSL errors**

**Solution:** Ensure OpenEMR is running:
```bash
curl -k https://localhost:8443
```

If using Docker:
```bash
docker ps  # Check if running
docker start <container_name>  # If not running
```

---

### **Issue: Browser doesn't open for authentication**

**Solution:** Manually open the URL shown in terminal:
```
Authorization URL: https://localhost:8443/oauth2/default/authorize?...
```

Copy and paste into your browser.

---

### **Issue: "Registration failed"**

**Solution:** Check that APIs are enabled:
1. Log into OpenEMR web interface
2. Go to: **Administration → Config → Connectors**
3. Enable: ☑ **Enable OpenEMR Standard FHIR REST API**
4. Enable: ☑ **Enable OpenEMR Standard REST API**
5. Click **Save**

---

### **Issue: "Token exchange failed"**

**Solution:** Verify redirect URI matches exactly:
- In script: `http://localhost:3000/callback`
- Must match registration (no trailing slash, correct port)

Check the `Config` class in `openemr_api_test.py`:
```python
REDIRECT_URI = "http://localhost:3000/callback"
```

---

### **Issue: "Patient creation failed" or other API errors**

**Solution 1:** Check scopes include necessary permissions:
```python
SCOPES = "openid offline_access api:oemr api:fhir user/Patient.read user/Patient.write"
```

**Solution 2:** Verify access token is valid:
- Check token hasn't expired (default: 1 hour)
- Use refresh token if needed

**Solution 3:** Check OpenEMR logs:
```bash
docker logs <openemr_container>
```

---

### **Issue: "ModuleNotFoundError: No module named 'requests'"**

**Solution:** Install dependencies:
```bash
pip3 install -r requirements.txt
```

Or:
```bash
pip3 install requests urllib3
```

---

### **Issue: FHIR endpoint returns 404**

**Solution:** Verify FHIR API is enabled and accessible:
```bash
curl -k https://localhost:8443/apis/default/fhir/metadata
```

Should return FHIR CapabilityStatement (or 401 if auth required).

---

## ⚙️ Configuration

Edit the `Config` class in `openemr_api_test.py` to customize:

```python
class Config:
    """Configuration for OpenEMR API"""
    BASE_URL = "https://localhost:8443"  # Your OpenEMR URL
    OAUTH_BASE = f"{BASE_URL}/oauth2/default"
    FHIR_BASE = f"{BASE_URL}/apis/default/fhir"
    
    # OAuth2 Configuration
    REDIRECT_URI = "http://localhost:3000/callback"  # OAuth callback
    CALLBACK_PORT = 3000  # Local server port
    
    # Application Registration
    APP_NAME = "POC Testing App"
    APP_TYPE = "private"
    SCOPES = "openid offline_access api:oemr api:fhir user/Patient.read user/Observation.read"
```

### **Common Customizations:**

**Change OpenEMR URL:**
```python
BASE_URL = "https://your-openemr-server.com"
```

**Change callback port:**
```python
REDIRECT_URI = "http://localhost:5000/callback"
CALLBACK_PORT = 5000
```

**Add more scopes:**
```python
SCOPES = "openid offline_access api:oemr api:fhir user/Patient.* user/Observation.*"
```

---

## 📁 Files in This Repository

### **Python Scripts**

| File | Size | Description |
|------|------|-------------|
| **openemr_api_test.py** | 27KB | Main automation script that handles OAuth2 flow and tests all FHIR endpoints |
| **check_prerequisites.py** | 4.9KB | Validates environment (Python version, dependencies, OpenEMR connectivity) |

### **Documentation**

| File | Size | Description |
|------|------|-------------|
| **README.md** | This file | Complete guide with quick start, troubleshooting, and API reference |
| **QUICKSTART.md** | 3.5KB | 3-step quick start guide for immediate testing |
| **TESTING_GUIDE.md** | 8.7KB | Comprehensive documentation with advanced usage and troubleshooting |
| **WORKFLOW.md** | 22KB | Visual diagrams showing OAuth2 flow and API testing workflow |
| **AUTOMATION_SUMMARY.md** | 9.2KB | Overview of what was created and why |
| **INDEX.md** | 8.0KB | Navigation hub for finding the right documentation |

### **Configuration Files**

| File | Description |
|------|-------------|
| **requirements.txt** | Python dependencies (requests, urllib3) |
| **docker-compose.yml** | Docker Compose configuration for OpenEMR deployment |
| **nginx.conf** | Nginx configuration for SSL/TLS proxy |
| **generate_certs.sh** | Script to generate self-signed SSL certificates |
| **.gitignore** | Git ignore rules for Python, IDE files, and credentials |

### **Docker/Nginx Files**

| File | Description |
|------|-------------|
| **nginx/certs/cert.pem** | SSL certificate (self-signed for testing) |
| **nginx/certs/key.pem** | SSL private key |
| **nginx/conf.d/default.conf** | Nginx server configuration |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Found a bug? Open an issue on GitHub
2. **Suggest Features**: Have an idea? Create a feature request
3. **Submit PRs**: Improvements to code or documentation are appreciated
4. **Share Feedback**: Let us know how you're using this tool

### **Development Setup**

```bash
# Clone repository
git clone https://github.com/SAMeh-ZAGhloul/OpenEMR-HL7-FHIR-API-Endpoints-and-cURL-Testing-Guide.git
cd OpenEMR-HL7-FHIR-API-Endpoints-and-cURL-Testing-Guide

# Install dependencies
pip3 install -r requirements.txt

# Make changes and test
python3 openemr_api_test.py
```

---

## 📖 API Reference (cURL Examples)

> **Note:** The Python automation script handles all of this automatically. These cURL examples are provided for reference or manual testing.

### OpenEMR FHIR API Endpoints - Manual Testing Guide

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
