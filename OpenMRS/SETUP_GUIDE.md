# OpenMRS Setup Guide

This guide provides instructions for setting up OpenMRS with FHIR capabilities to replace the limited functionality of OpenEMR.

## Prerequisites

- Docker and Docker Compose
- Python 3.7+
- OpenSSL (for certificate generation)

## Initial Setup

1. **Generate SSL certificates**:
   ```bash
   chmod +x generate_certs.sh
   ./generate_certs.sh
   ```

2. **Start OpenMRS services**:
   ```bash
   docker-compose up -d
   ```

3. **Wait for initialization**:
   Wait 5-10 minutes for OpenMRS to fully initialize. You can check the logs with:
   ```bash
   docker logs openmrs_server -f
   ```

4. **Access OpenMRS web interface**:
   - Navigate to `https://localhost:8443`
   - Use default credentials: admin/test
   - Complete the initial setup wizard if prompted

5. **Install FHIR2 module**:
   - Go to Administration → Manage Modules
   - Install the FHIR2 module if not already present
   - Restart OpenMRS if required after installation

6. **Install OAuth2 module** (for SMART on FHIR):
   - Go to Administration → Manage Modules
   - Install the OAuth2 module
   - Configure OAuth2 settings under Administration → OAuth2 Settings

## Configuration

### Enable FHIR API
1. Go to Administration → System Administration → FHIR2
2. Configure the FHIR API settings
3. Ensure the API endpoints are enabled

### Configure OAuth2
1. Go to Administration → System Administration → OAuth2 Settings
2. Register a new client application with:
   - Client ID: `fhir-client-app`
   - Redirect URI: `http://127.0.0.1:3000/callback`
   - Scopes: `openid fhirUser patient/Patient.read patient/Patient.write patient/Encounter.read patient/Encounter.write`

## Running the Tests

1. **Check prerequisites**:
   ```bash
   python3 1_check_prerequisites.py
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Authenticate**:
   ```bash
   python3 2_openmrs_auth.py
   ```

4. **Run tests**:
   ```bash
   python3 3_openmrs_test.py
   ```

## Key Improvements Over OpenEMR

1. **Full FHIR Resource Support**: Unlike OpenEMR 7.0.3, OpenMRS supports full CRUD operations for Patient, Encounter, Observation, and Appointment resources.

2. **Clinical Workflows**: Complete clinical workflows that were limited in OpenEMR.

3. **Standards Compliance**: Better FHIR R4 and SMART on FHIR compliance.

4. **Extensibility**: Modular architecture allowing for custom modules and extensions.

## Troubleshooting

### Common Issues

1. **Service not starting**: Check logs with `docker logs openmrs_server`
2. **SSL certificate errors**: Ensure certificates are properly generated and referenced
3. **Authentication failures**: Verify OAuth2 module is installed and configured
4. **Database connection issues**: Check database credentials and connectivity

### Verification Steps

1. Confirm OpenMRS is accessible at `https://localhost:8443`
2. Verify FHIR metadata endpoint: `https://localhost:8443/ws/fhir2/R4/metadata`
3. Check OAuth2 endpoints are available
4. Test basic FHIR queries through the web interface