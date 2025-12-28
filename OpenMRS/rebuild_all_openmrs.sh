#!/bin/bash

# Complete OpenMRS Rebuild and Setup Script
# This script will rebuild all OpenMRS Docker containers and set up the complete environment

set -e  # Exit on any error

echo "=================================================="
echo "OpenMRS Complete Rebuild and Setup Script"
echo "=================================================="
echo ""

# Function to print status messages
print_status() {
    echo "✅ $1"
}

print_warning() {
    echo "⚠️  $1"
}

print_error() {
    echo "❌ $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    echo "Please install Docker Desktop or Docker Engine before running this script"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "Please start Docker Desktop or the Docker service before running this script"
    exit 1
fi

print_status "Docker is available and daemon is running"

# Navigate to the OpenMRS directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "Current directory: $(pwd)"

# Generate SSL certificates if they don't exist
if [ ! -f "nginx/certs/cert.pem" ] || [ ! -f "nginx/certs/key.pem" ]; then
    echo ""
    echo "Generating SSL certificates..."
    if [ -f "generate_certs.sh" ]; then
        chmod +x generate_certs.sh
        ./generate_certs.sh
        print_status "SSL certificates generated"
    else
        print_error "generate_certs.sh not found"
        exit 1
    fi
else
    print_status "SSL certificates already exist"
fi

# Stop existing containers if running
echo ""
echo "Stopping existing containers..."
docker-compose down --remove-orphans || print_warning "No containers were running"

# Remove existing images to ensure clean rebuild
echo ""
echo "Removing existing OpenMRS images..."
docker rmi openmrs/openmrs-reference-application-distro:latest --force 2>/dev/null || print_warning "OpenMRS image was not present"
docker rmi mysql:8.0 --force 2>/dev/null || print_warning "MySQL image was not present"
docker rmi nginx:stable-alpine --force 2>/dev/null || print_warning "Nginx image was not present"

# Pull the latest images
echo ""
echo "Pulling latest images..."
if docker-compose pull; then
    print_status "Successfully pulled all images"
else
    print_error "Failed to pull images. Attempting to build directly..."
    docker pull openmrs/openmrs-reference-application-distro:latest
    docker pull mysql:8.0
    docker pull nginx:stable-alpine
fi

# Build and start the containers
echo ""
echo "Starting OpenMRS containers..."
if docker-compose up -d --force-recreate; then
    print_status "Containers started successfully"
else
    print_error "Failed to start containers"
    exit 1
fi

# Wait for containers to start
echo ""
echo "Waiting for containers to start (10 seconds)..."
sleep 10

# Show container status
echo ""
echo "Container status:"
docker-compose ps

# Wait for OpenMRS to initialize
echo ""
echo "Waiting for OpenMRS to initialize (this may take 5-10 minutes)..."
echo "You can monitor the logs with: docker-compose logs -f openmrs_server"
echo ""
echo "Monitor initialization with this command in another terminal:"
echo "docker-compose logs -f openmrs_server"
echo ""

# Wait for initialization
sleep 30

# Check if OpenMRS is responding
echo ""
echo "Checking if OpenMRS is responding..."
if curl -f -k -s --max-time 10 http://localhost:8080/openmrs > /dev/null 2>&1; then
    print_status "OpenMRS is responding at http://localhost:8080/openmrs"
else
    print_warning "OpenMRS may still be initializing. This is normal for first-time setup."
    echo "Please wait 5-10 minutes and check the logs with: docker-compose logs openmrs_server"
fi

# Provide complete next steps
echo ""
echo "=================================================="
echo "OpenMRS Rebuild Complete!"
echo "=================================================="
echo ""
echo "Next steps to complete the setup:"
echo ""
echo "1. Wait 5-10 minutes for OpenMRS to fully initialize"
echo "2. Check logs: docker-compose logs openmrs_server"
echo "3. Access OpenMRS setup wizard at: http://localhost:8080/openmrs"
echo "   OR with HTTPS: https://localhost:8443/openmrs"
echo ""
echo "4. Complete the OpenMRS setup wizard:"
echo "   - Choose 'Create a new database'"
echo "   - Database connection settings:"
echo "     * Host: openmrs_db (if prompted for internal Docker name)"
echo "     * Host: localhost (if prompted for external access)"
echo "     * Database: openmrs"
echo "     * User: openmrs"
echo "     * Password: openmrs"
echo "   - Set admin password (default is 'Admin123')"
echo ""
echo "5. After setup, install required modules:"
echo "   - Go to Administration → Manage Modules"
echo "   - Install FHIR2 Module"
echo "   - Install OAuth2 Module"
echo ""
echo "6. Configure FHIR2 and OAuth2 modules as needed"
echo ""
echo "7. Once OpenMRS is fully configured, run the tests:"
echo "   - python3 1_check_prerequisites.py"
echo "   - python3 2_openmrs_auth.py"
echo "   - python3 3_openmrs_test.py"
echo ""
echo "8. Access FHIR API endpoints:"
echo "   - Metadata: https://localhost:8443/openmrs/ws/fhir2/R4/metadata"
echo "   - Patient: https://localhost:8443/openmrs/ws/fhir2/R4/Patient"
echo "   - Encounter: https://localhost:8443/openmrs/ws/fhir2/R4/Encounter"
echo ""
echo "Troubleshooting:"
echo "- If containers fail to start: docker-compose logs openmrs_server"
echo "- If database issues occur: docker-compose logs openmrs_db"
echo "- To restart: docker-compose restart"
echo "- To stop: docker-compose down"
echo ""
echo "The OpenMRS implementation addresses all OpenEMR limitations:"
echo "- Full FHIR R4 compliance"
echo "- Complete Patient, Encounter, Observation, Appointment CRUD operations"
echo "- SMART on FHIR support"
echo "- Proper OAuth2 authentication"
echo "=================================================="