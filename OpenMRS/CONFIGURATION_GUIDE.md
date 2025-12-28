# OpenMRS Configuration Guide

## Default Credentials

### Initial Setup
- **Username**: `admin`
- **Password**: `test`
- **Database User**: `openmrs` (with password `openmrs`)

### After Initial Setup
After the first-time setup wizard, the default admin credentials are:
- **Username**: `admin`
- **Password**: `Admin123` (in some distributions)

## Step-by-Step Configuration

### 1. Initial Access
1. Navigate to `https://localhost:8443` (or `http://localhost:8080` without HTTPS proxy)
2. You'll be redirected to the OpenMRS setup wizard
3. Complete the initial setup:
   - Choose "Create a new database"
   - Set database connection parameters:
     - Database name: `openmrs`
     - Database user: `openmrs`
     - Database password: `openmrs`
   - Set admin password (default is `Admin123`)

### 2. Install FHIR2 Module
1. Log in as admin
2. Go to **Administration** → **Manage Modules**
3. Click **"Install Module"** button
4. Upload the FHIR2 module file (`.omod` file) or use the module repository:
   - Look for **"FHIR2 Module"** in the available modules
   - Click **"Install"** or **"Upgrade"** if already installed
5. Wait for installation to complete
6. Restart OpenMRS if prompted

### 3. Install OAuth2 Module
1. Go to **Administration** → **Manage Modules**
2. Click **"Install Module"** button
3. Upload the OAuth2 module file (`.omod` file) or use the module repository:
   - Look for **"OAuth2 Module"** in the available modules
   - Click **"Install"** or **"Upgrade"** if already installed
4. Wait for installation to complete
5. Restart OpenMRS if prompted

### 4. Configure FHIR2 Module
1. Go to **Administration** → **System Administration** → **FHIR2**
2. Configure the following settings:
   - **FHIR Base URL**: `https://localhost:8443/ws/fhir2`
   - **R4 Endpoint Enabled**: Check this box
   - **DSTU3 Endpoint Enabled**: Check this box (optional)
   - **Security Settings**: Configure as needed for your environment
3. Save the configuration

### 5. Configure OAuth2 Module
1. Go to **Administration** → **System Administration** → **OAuth2 Settings**
2. Configure OAuth2 settings:
   - **Client ID**: `fhir-client-app` (or your preferred client ID)
   - **Client Secret**: Generate or set a secure secret
   - **Redirect URIs**: Add `http://127.0.0.1:3000/callback`
   - **Scopes**: Include `openid`, `fhirUser`, `patient/*.*`, `user/*.*`
3. Save the configuration

### 6. Register OAuth2 Application (Alternative Method)
If using the automatic registration approach in the Python scripts:
1. Go to **Administration** → **System** → **API Clients** (or similar path depending on OAuth2 module version)
2. Look for the client registered by the script (named "OpenMRS POC Testing App")
3. Ensure the client is **enabled**
4. Note the Client ID and Client Secret for manual configuration if needed

## API Endpoints

### FHIR Endpoints
- **Metadata**: `https://localhost:8443/ws/fhir2/R4/metadata`
- **Patient**: `https://localhost:8443/ws/fhir2/R4/Patient`
- **Encounter**: `https://localhost:8443/ws/fhir2/R4/Encounter`
- **Observation**: `https://localhost:8443/ws/fhir2/R4/Observation`
- **Appointment**: `https://localhost:8443/ws/fhir2/R4/Appointment`

### OAuth2 Endpoints
- **Authorization**: `https://localhost:8443/oauth2/authorize`
- **Token**: `https://localhost:8443/oauth2/token`
- **Registration**: `https://localhost:8443/oauth2/register` (if supported)

## Troubleshooting

### Common Issues
1. **Module Installation Fails**: Ensure you're using compatible module versions for your OpenMRS platform version
2. **FHIR Endpoints Return 404**: Verify FHIR2 module is installed and enabled
3. **OAuth2 Authentication Fails**: Check that OAuth2 module is installed and configured properly
4. **Database Connection Issues**: Verify database credentials in docker-compose.yml match the ones in OpenMRS setup

### Verification Steps
1. Check if modules are installed: **Administration** → **Manage Modules**
2. Test FHIR metadata endpoint: `https://localhost:8443/ws/fhir2/R4/metadata`
3. Verify OAuth2 endpoints are accessible
4. Test basic FHIR queries through the web interface

## Security Considerations

### For Production
- Change default passwords immediately
- Use proper SSL certificates (not self-signed)
- Configure proper authentication methods
- Set up user roles and permissions appropriately
- Regularly update modules and platform

### For Development/Testing
- The default credentials are acceptable for local testing
- Self-signed certificates are fine for development
- Ensure firewall rules allow necessary ports