# OpenMRS FHIR API Testing Suite - Setup Instructions

## Docker Access Issue

We encountered an issue with Docker access in the current environment. The Docker commands are returning "Not Found" errors, which may be due to:

1. Docker not being properly installed or configured
2. Network restrictions preventing access to Docker Hub
3. Docker daemon not running

## How to Run This Project

Once Docker access is available, you can run this project using the following steps:

### 1. Generate SSL Certificates
```bash
cd OpenMRS
chmod +x generate_certs.sh
./generate_certs.sh
```

### 2. Start OpenMRS Services
```bash
docker-compose up -d
```

### 3. Wait for Initialization
Wait 5-10 minutes for OpenMRS to fully initialize. You can check the logs with:
```bash
docker logs openmrs_server -f
```

### 4. Access OpenMRS
Navigate to `https://localhost:8443` in your browser and use default credentials: admin/test

### 5. Install Required Modules
- Go to Administration → Manage Modules
- Install the FHIR2 module if not already present
- Install the OAuth2 module for SMART on FHIR support

### 6. Run the Tests
```bash
# Check prerequisites
python3 1_check_prerequisites.py

# Install dependencies
pip3 install -r requirements.txt

# Authenticate
python3 2_openmrs_auth.py

# Run tests
python3 3_openmrs_test.py
```

## Key Improvements Over OpenEMR

1. **Full FHIR Resource Support**: Unlike OpenEMR 7.0.3, OpenMRS supports full CRUD operations for Patient, Encounter, Observation, and Appointment resources
2. **Complete Clinical Workflows**: Full clinical workflows that were limited in OpenEMR
3. **Better Standards Compliance**: Enhanced FHIR R4 and SMART on FHIR compliance
4. **Extensibility**: Modular architecture allowing for custom modules and extensions

## Troubleshooting

If you continue to have Docker issues:

1. Verify Docker is installed and running:
   ```bash
   docker --version
   docker ps
   ```

2. Check Docker Hub connectivity:
   ```bash
   docker pull hello-world
   ```

3. If using Docker Desktop, ensure it's running

4. Check for proxy or firewall restrictions that might block Docker Hub access

## Alternative: Manual OpenMRS Installation

If Docker continues to be problematic, you can install OpenMRS manually:
1. Download OpenMRS from https://openmrs.org/download/
2. Follow the standard installation guide
3. Install the FHIR2 and OAuth2 modules
4. Configure the FHIR endpoints
5. Run the Python test scripts against your manual installation