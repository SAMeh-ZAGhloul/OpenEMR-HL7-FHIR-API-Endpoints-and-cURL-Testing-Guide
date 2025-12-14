# OpenEMR FHIR API Automated Testing Script

## Overview

This Python script automates the complete OAuth2 authentication flow and tests all FHIR API endpoints documented in the main README.md. It eliminates manual cURL commands and provides a comprehensive validation of your OpenEMR FHIR API setup.

## Features

✅ **Automated OAuth2 Flow**
- Dynamic client registration
- Browser-based authorization code grant
- Automatic token exchange
- Token refresh capability

✅ **Complete FHIR API Testing**
- **Scenario A**: Patient Demographics (FHIR Patient)
- **Scenario B**: Appointment Scheduling (FHIR Appointment)
- **Scenario C**: Clinical Encounter (FHIR Encounter, Observation, DocumentReference)
- **Scenario D**: Prescribing and Ordering (FHIR MedicationRequest, ServiceRequest)

✅ **Developer-Friendly**
- Detailed logging of all API calls
- Pretty-printed JSON responses
- Error handling and validation
- Step-by-step progress tracking

## Prerequisites

1. **OpenEMR Instance Running**
   - URL: `https://localhost:8443` (or update `Config.BASE_URL` in script)
   - FHIR API enabled: Administration → Config → Connectors
   - SSL/TLS configured (can be self-signed)

2. **Python 3.7+**
   ```bash
   python3 --version
   ```

3. **Admin Credentials**
   - You'll need to log in via browser during OAuth2 flow
   - Default: username `admin`

## Installation

1. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

   Or manually:
   ```bash
   pip3 install requests urllib3
   ```

2. **Make Script Executable** (optional)
   ```bash
   chmod +x openemr_api_test.py
   ```

## Usage

### Basic Usage

```bash
python3 openemr_api_test.py
```

### What Happens During Execution

1. **Application Registration** (Step 3)
   - Registers a new OAuth2 client via API
   - Saves `client_id` and `client_secret`

2. **Browser Authentication** (Step 0.1.1)
   - Opens your browser to OpenEMR login
   - You log in as admin and approve consent
   - Script captures authorization code automatically

3. **Token Exchange** (Step 0.1.2)
   - Exchanges authorization code for access token
   - Saves access token for API calls

4. **API Testing** (Scenarios A-D)
   - Creates a test patient
   - Books an appointment
   - Creates a clinical encounter
   - Records vital signs
   - Adds clinical notes
   - Creates prescription
   - Orders lab test
   - Reads patient data back

### Expected Output

```
╔════════════════════════════════════════════════════════════════╗
║         OpenEMR FHIR API Automated Testing Script             ║
║                                                                ║
║  This script will:                                             ║
║  1. Register a new OAuth2 application                          ║
║  2. Perform OAuth2 authentication flow                         ║
║  3. Test all FHIR API endpoints from the README                ║
╚════════════════════════════════════════════════════════════════╝

================================================================================
STEP 3: Register Application via API
================================================================================
POST https://localhost:8443/oauth2/default/registration
...
✅ Registration Successful!
Client ID: XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA
...

================================================================================
STEP A: Create Patient (FHIR Patient Resource)
================================================================================
✅ Patient Created Successfully!
Patient ID: 123
...

🎉 All API endpoints tested successfully!
```

## Configuration

Edit the `Config` class in `openemr_api_test.py` to customize:

```python
class Config:
    BASE_URL = "https://localhost:8443"  # Your OpenEMR URL
    REDIRECT_URI = "http://localhost:3000/callback"  # OAuth callback
    CALLBACK_PORT = 3000  # Local server port for callback
    
    # Scopes requested
    SCOPES = "openid offline_access api:oemr api:fhir user/Patient.read user/Observation.read"
```

## Troubleshooting

### Issue: "Connection refused" or SSL errors

**Solution**: Ensure OpenEMR is running and accessible:
```bash
curl -k https://localhost:8443
```

### Issue: Browser doesn't open for authentication

**Solution**: Manually open the URL shown in the terminal:
```
Authorization URL: https://localhost:8443/oauth2/default/authorize?...
```

### Issue: "Registration failed"

**Solution**: Check that APIs are enabled:
1. Log into OpenEMR
2. Go to: Administration → Config → Connectors
3. Enable: ☑ Enable OpenEMR Standard FHIR REST API

### Issue: "Token exchange failed"

**Solution**: Verify redirect URI matches:
- In script: `http://localhost:3000/callback`
- Must match exactly (no trailing slash, correct port)

### Issue: "Patient creation failed"

**Solution**: Check scopes include necessary permissions:
```python
SCOPES = "openid offline_access api:oemr api:fhir user/Patient.read user/Patient.write"
```

## Advanced Usage

### Running Individual Scenarios

You can modify the `main()` function to run specific scenarios:

```python
# Only test patient creation
api.create_patient()

# Only test appointments
api.create_patient()
api.create_appointment()
```

### Using Existing Credentials

If you already have `client_id` and `client_secret`, set them before running:

```python
Config.CLIENT_ID = "your_existing_client_id"
Config.CLIENT_SECRET = "your_existing_client_secret"

# Then skip registration and go straight to auth
auth_code = api.get_authorization_code()
api.exchange_code_for_token(auth_code)
```

### Saving Credentials for Reuse

After first run, save the credentials:

```bash
export OPENEMR_CLIENT_ID="XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA"
export OPENEMR_CLIENT_SECRET="Gzd9cooABqpT5ObaBf0RvkNILGTEqDafKs6aVfHdnfkjqtowKIpZ5j3yf6sDokNN9AAVsCSO"
```

## Script Architecture

```
OpenEMRAPI Class
├── Authentication Methods
│   ├── register_application()      # Dynamic client registration
│   ├── get_authorization_code()    # Browser-based auth
│   ├── exchange_code_for_token()   # Token exchange
│   └── refresh_access_token()      # Token refresh
│
├── Scenario A: Patient Demographics
│   └── create_patient()
│
├── Scenario B: Appointment Scheduling
│   └── create_appointment()
│
├── Scenario C: Clinical Encounter
│   ├── create_encounter()
│   ├── create_vital_signs()
│   └── create_clinical_note()
│
├── Scenario D: Prescribing and Ordering
│   ├── create_medication_request()
│   └── create_service_request()
│
└── Utility Methods
    ├── read_patient()
    ├── print_step()
    └── print_response()
```

## Security Notes

⚠️ **Important Security Considerations**:

1. **Self-Signed Certificates**: The script disables SSL verification (`verify=False`) for development. In production, use proper SSL certificates.

2. **Credentials Storage**: Client secrets are displayed in terminal output. In production:
   - Store in environment variables
   - Use secure credential management
   - Never commit to version control

3. **Scopes**: Request only necessary scopes for your use case.

## Output Files

The script doesn't create any files, but you can modify it to save:
- Credentials to `.env` file
- API responses to JSON files
- Test results to log files

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: OpenEMR API Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run API tests
        run: python3 openemr_api_test.py
        env:
          OPENEMR_URL: ${{ secrets.OPENEMR_URL }}
```

## Contributing

To extend the script with additional FHIR resources:

1. Add method to `OpenEMRAPI` class
2. Follow naming convention: `create_<resource_name>()`
3. Use `self.print_step()` for logging
4. Handle errors gracefully
5. Return resource ID on success

## License

This script is provided as-is for testing OpenEMR FHIR APIs.

## Support

For issues related to:
- **Script functionality**: Check this README
- **OpenEMR setup**: See main README.md
- **FHIR specification**: Visit https://www.hl7.org/fhir/

## Version History

- **v1.0** (2025-12-14): Initial release
  - OAuth2 automation
  - All FHIR scenarios from README
  - Browser-based authentication
