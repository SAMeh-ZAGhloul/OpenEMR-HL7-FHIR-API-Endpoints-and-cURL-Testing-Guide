# OpenEMR FHIR API Testing Guide & Automation Suite

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-green.svg)](https://www.hl7.org/fhir/)
[![OpenEMR](https://img.shields.io/badge/OpenEMR-7.0+-orange.svg)](https://www.open-emr.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **🚀 Complete Python automation suite** that automates OAuth2 authentication and tests FHIR API endpoints. Replaces manual cURL workflows with a browser-based login and programmatic validation.

---

## ⚠️ Current Status

**Dec 2025**

- **Authentication**: Registers a confidential (`private`) client and completes OAuth2 Authorization Code flow using `client_secret_post`.
- **Scopes**: Requests `user/Patient.read` and `user/Patient.write` in addition to `openid`, `offline_access`, `api:oemr`, and `api:fhir`.
- **Read Access**: Verified via `Search Patients` test.
- **Write Operations**: Attempted in sequence (Patient, Appointment, Encounter, Vitals, Note, Medication). Success depends on server configuration and granted scopes. If the server denies write scopes, these calls may return `401/403`.

---

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [Automation Overview](#-automation-overview)
- [How It Works](#-how-it-works)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Repository Structure](#-repository-structure)
- [License](#-license)

---

## 🚀 Quick Start

Get started testing OpenEMR FHIR APIs locally.

### Step 1: Check Prerequisites
Validates Python environment, dependencies, and connectivity to OpenEMR endpoints.
```bash
python3 1_check_prerequisites.py
```
Expected: `✅ All checks passed`

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 3: Run Automated Tests

The suite runs in two steps:

1) Authenticate
```bash
python3 2_openemr_auth.py
```
Registers the app, opens the browser for login, and saves credentials to `.env`.

2) Run Tests
```bash
python3 3_openemr_test.py
```
Reads credentials and performs FHIR API tests.

---

## 🐳 Deployment

Run the OpenEMR environment locally using Docker and an Nginx reverse proxy terminating HTTPS on `8443`.

### 1) Generate SSL Certificates
Generate self-signed certificates for local HTTPS:
```bash
chmod +x generate_certs.sh
./generate_certs.sh
```
Creates `nginx/certs/cert.pem` and `nginx/certs/key.pem`.

### 2) Start Services
Pull images and start containers:
```bash
docker-compose up -d
```
Wait a few minutes for OpenEMR to initialize (database population).

### 3) Verify Deployment
- URL: `https://localhost:8443`
- Login: Use your OpenEMR credentials. Fresh installs may prompt initial setup.

### 4) Stop Services
```bash
docker-compose down
```

---

## 🎯 Automation Overview

Replaces manual cURL workflows with modular Python scripts and a browser-based OAuth2 flow.

| Feature | Manual cURL | Python Automation |
| :--- | :--- | :--- |
| Registration | JSON payload construction | ✅ Automatic (API-based) |
| Auth | Copy-paste URLs & codes | ✅ Automatic (Browser + local callback) |
| Token Mgmt | Export env vars | ✅ Automatic (exchange) |
| Testing | One-off cURL calls | ✅ Endpoints tested in sequence |
| Validation | Manual JSON reading | ✅ Programmatic validation |

---

## 🔄 How It Works

### Flow

```mermaid
sequenceDiagram
    participant User
    participant Script
    participant Browser
    participant OpenEMR

    User->>Script: Run 2_openemr_auth.py / 3_openemr_test.py
    Script->>OpenEMR: Register confidential client
    OpenEMR-->>Script: Client ID & Secret
    Script->>Browser: Open Authorization URL
    Browser->>User: Show login & consent
    User->>Browser: Login & approve
    Browser->>Script: Callback with auth code
    Script->>OpenEMR: Exchange code for token (client_secret_post)
    OpenEMR-->>Script: Access token
    Script->>OpenEMR: Test FHIR endpoints
    Script->>User: Display results
```

### Execution Timeline
- 0:00 Register client
- 0:02 Browser opens
- 0:05 Token acquired
- 0:06 Read access verified
- 0:07+ Write scenarios attempted

---

## ⚙️ Configuration

### What Gets Tested
Scenarios attempted:
- Patient demographics (create/search)
- Appointment scheduling (book)
- Clinical encounter (encounter, vitals, notes)
- Prescribing (MedicationRequest)

### Auth Script Settings
Edit the `Config` class in `2_openemr_auth.py`:

```python
class Config:
    BASE_URL = "https://localhost:8443"
    REDIRECT_URI = "http://127.0.0.1:3000/callback"
    CALLBACK_PORT = 3000
    SCOPES = "openid offline_access api:oemr api:fhir user/Patient.read user/Patient.write"
    APP_TYPE = "private"
    AUTH_METHOD = "client_secret_post"
```

### Script Architecture
- `2_openemr_auth.py` (`OpenEMRAuth`)
  - `register_application()`: Register OAuth2 client
  - `get_authorization_code()`: Browser login & local callback
  - `exchange_code_for_token()`: Token exchange (confidential client)
  - `save_to_env()`: Persist credentials to `.env`
- `3_openemr_test.py` (`TestRunner`)
  - `load_env()`: Load `.env`
  - `run()`: Execute FHIR endpoint tests

### Enable the Client in OpenEMR
- After registration, newly created clients may be disabled by default. Enable the client under `Admin → System → API Clients`.

### Discovery & Endpoints
- OIDC Discovery: `<BASE_URL>/oauth2/default/.well-known/openid-configuration`
- Registration: `<BASE_URL>/oauth2/default/registration`
- Authorization: `<BASE_URL>/oauth2/default/authorize`
- Token: `<BASE_URL>/oauth2/default/token`

### Scope Conventions
- SMART scopes often use capitalized FHIR resource names, e.g., `system/Patient.read`, `user/Encounter.write`.
- Some environments accept lowercase resource names; prefer capitalized names for compatibility.

---

## 🔧 Troubleshooting

### 401/403 on Write Operations
- Cause: Missing or denied `system/*` or `user/*` write scopes
- Fix: Adjust server configuration to grant appropriate scopes; confirm client type is allowed to request them

### Connection Refused
- Ensure OpenEMR is running (`docker ps`)
- Verify `BASE_URL` in `Config`

### Browser Doesn't Open
- Manually copy the URL printed in the terminal

---

## 📁 Repository Structure

Top-level layout for quick orientation:

- `1_check_prerequisites.py`: Environment checks (Python, endpoints)
- `2_openemr_auth.py`: OAuth2 client registration, browser auth, token exchange, `.env` save
- `3_openemr_test.py`: FHIR tests (read/write scenarios)
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: OpenEMR app, DB, and HTTPS reverse proxy
- `nginx/conf.d/default.conf`: Nginx site config (SSL termination, proxy to app)
- `nginx/certs/`: Self-signed TLS certs generated locally
- `generate_certs.sh`: Helper to generate `cert.pem`/`key.pem`

## 🪪 License

MIT License. See `LICENSE`.
