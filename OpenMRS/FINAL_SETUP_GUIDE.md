# OpenMRS Complete Setup and Configuration Guide

## Overview
This document provides comprehensive instructions for setting up and configuring OpenMRS to address the limitations of OpenEMR, particularly for FHIR API functionality.

## Docker Configuration

### Updated docker-compose.yml
The configuration has been updated to:
- Enable database table creation and auto-updates
- Properly expose database ports for troubleshooting
- Configure nginx to properly proxy to OpenMRS application
- Ensure proper service dependencies

### Key Changes Made:
1. Set `DB_CREATE_TABLES=true` and `DB_AUTO_UPDATE=true` to allow OpenMRS to initialize its database
2. Exposed MySQL port 3306 for direct database access if needed
3. Configured nginx to handle both HTTP (port 8080) and HTTPS (port 8443) access
4. Removed the init-openmrs.sql dependency which was causing issues

## Access URLs

### Direct Access (without HTTPS):
- **OpenMRS Application**: `http://localhost:8080/openmrs`
- **OpenMRS Login**: `http://localhost:8080/openmrs/login.htm`

### HTTPS Access (with reverse proxy):
- **OpenMRS Application**: `https://localhost:8443/openmrs`
- **OpenMRS Login**: `https://localhost:8443/openmrs/login.htm`

### FHIR API Endpoints:
- **FHIR Metadata**: `https://localhost:8443/openmrs/ws/fhir2/R4/metadata`
- **Patient Endpoint**: `https://localhost:8443/openmrs/ws/fhir2/R4/Patient`
- **Encounter Endpoint**: `https://localhost:8443/openmrs/ws/fhir2/R4/Encounter`

## Default Credentials

### Initial Setup:
- **Username**: `admin`
- **Password**: `test`

### After Setup Wizard:
- **Username**: `admin`
- **Password**: `Admin123` (or as set during setup)

## Step-by-Step Setup Process

### 1. Start the Services
```bash
cd OpenMRS
docker-compose up -d
```

### 2. Wait for Initialization
Wait 5-10 minutes for OpenMRS to initialize completely:
```bash
docker logs openmrs_server -f
```

### 3. Complete Initial Setup
1. Navigate to `http://localhost:8080/openmrs` or `https://localhost:8443/openmrs`
2. Complete the OpenMRS setup wizard:
   - Choose "Create a new database"
   - Use database connection settings:
     - Host: `openmrs_db` (if connecting from within Docker network) or `localhost` (if connecting externally)
     - Database: `openmrs`
     - User: `openmrs`
     - Password: `openmrs`
   - Set admin password (default is `Admin123`)

### 4. Install Required Modules
1. Log in as admin
2. Go to **Administration** → **Manage Modules**
3. Install the following modules:
   - **FHIR2 Module** (for FHIR API support)
   - **OAuth2 Module** (for SMART on FHIR support)

### 5. Configure FHIR2 Module
1. Go to **Administration** → **System Administration** → **FHIR2**
2. Enable R4 endpoint
3. Configure security settings as needed

### 6. Configure OAuth2 Module
1. Go to **Administration** → **System Administration** → **OAuth2 Settings**
2. Register your application with:
   - Client ID: `fhir-client-app`
   - Redirect URI: `http://127.0.0.1:3000/callback`
   - Scopes: `openid fhirUser patient/Patient.read patient/Patient.write patient/Encounter.read patient/Encounter.write`

## Testing the Setup

### 1. Verify OpenMRS is Running
```bash
curl -v http://localhost:8080/openmrs
```

### 2. Verify FHIR Endpoint
```bash
curl -v https://localhost:8443/openmrs/ws/fhir2/R4/metadata
```

### 3. Run the Python Tests
```bash
# Check prerequisites
python3 1_check_prerequisites.py

# Authenticate
python3 2_openmrs_auth.py

# Run tests
python3 3_openmrs_test.py
```

## Troubleshooting

### Common Issues and Solutions:

1. **Tomcat Manager Instead of OpenMRS**:
   - Ensure you're accessing `/openmrs` path, not the root Tomcat context
   - Check that the OpenMRS WAR file is properly deployed

2. **Database Connection Issues**:
   - Verify database credentials match between docker-compose.yml and OpenMRS setup
   - Check that the database container is running: `docker logs openmrs_db`

3. **Module Installation Fails**:
   - Ensure you're using compatible module versions
   - Check OpenMRS logs: `docker logs openmrs_server`

4. **SSL Certificate Issues**:
   - The setup uses self-signed certificates
   - Python scripts have SSL verification disabled for local testing
   - For production, use proper SSL certificates

### Docker Commands for Troubleshooting:
```bash
# Check container status
docker-compose ps

# View OpenMRS logs
docker logs openmrs_server

# View database logs
docker logs openmrs_db

# Access OpenMRS container shell
docker exec -it openmrs_server /bin/bash

# Access database container shell
docker exec -it openmrs_database /bin/bash
```

## Key Improvements Over OpenEMR

1. **Full FHIR Resource Support**: Complete CRUD operations for Patient, Encounter, Observation, and Appointment resources
2. **Proper Authentication**: OAuth2 with PKCE for secure API access
3. **Standards Compliance**: Full FHIR R4 and SMART on FHIR compliance
4. **Clinical Workflows**: Complete clinical workflows that were limited in OpenEMR
5. **Extensibility**: Modular architecture allowing for custom modules and extensions

## Security Considerations

### For Production:
- Change default passwords immediately
- Use proper SSL certificates (not self-signed)
- Configure proper authentication methods
- Set up user roles and permissions appropriately
- Regularly update modules and platform

### For Development/Testing:
- Default credentials are acceptable for local testing
- Self-signed certificates are fine for development
- Ensure firewall rules allow necessary ports
- Remove test data after development

## Next Steps

Once OpenMRS is properly configured with FHIR2 and OAuth2 modules:

1. Run the complete test suite to verify all functionality
2. Implement any custom modules needed for your specific use case
3. Configure user roles and permissions appropriately
4. Set up backup and maintenance procedures
5. Document the configuration for your team