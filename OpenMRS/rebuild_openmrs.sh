#!/bin/bash

# OpenMRS Docker Rebuild Script
# This script will rebuild the OpenMRS Docker containers when Docker access is available

set -e  # Exit on any error

echo "OpenMRS Docker Rebuild Script"
echo "==============================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop or the Docker service."
    exit 1
fi

echo "✅ Docker is available and daemon is running"

# Navigate to the OpenMRS directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"

# Stop existing containers if running
echo "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Remove existing images to ensure rebuild
echo "Removing existing OpenMRS images..."
docker rmi openmrs/openmrs-reference-application-distro:latest --force || true

# Pull the latest images
echo "Pulling latest OpenMRS images..."
docker-compose pull

# Build and start the containers
echo "Starting OpenMRS containers..."
docker-compose up -d --force-recreate

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 10

# Show container status
echo "Container status:"
docker-compose ps

# Wait for OpenMRS to initialize
echo "Waiting for OpenMRS to initialize (this may take 5-10 minutes)..."
echo "You can monitor the logs with: docker-compose logs -f openmrs_server"

# Provide next steps
echo ""
echo "Next steps:"
echo "1. Wait 5-10 minutes for OpenMRS to fully initialize"
echo "2. Check logs: docker-compose logs openmrs_server"
echo "3. Access OpenMRS at: http://localhost:8080/openmrs"
echo "4. Complete the initial setup wizard"
echo "5. Install FHIR2 and OAuth2 modules"
echo "6. Run: python3 1_check_prerequisites.py"
echo "7. Run: python3 2_openmrs_auth.py"
echo "8. Run: python3 3_openmrs_test.py"

echo ""
echo "To check if OpenMRS is ready, you can run:"
echo "curl -v http://localhost:8080/openmrs"