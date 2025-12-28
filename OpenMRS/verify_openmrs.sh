#!/bin/bash

# OpenMRS Verification Script
# This script verifies the OpenMRS setup and configuration

echo "OpenMRS Verification Script"
echo "==========================="

# Check if Docker is available
if command -v docker &> /dev/null && docker info &> /dev/null; then
    DOCKER_AVAILABLE=true
    echo "✅ Docker is available"
else
    DOCKER_AVAILABLE=false
    echo "⚠️  Docker is not available"
fi

# Check if required files exist
echo ""
echo "Checking required files..."

REQUIRED_FILES=(
    "docker-compose.yml"
    "nginx/conf.d/default.conf"
    "generate_certs.sh"
    "1_check_prerequisites.py"
    "2_openmrs_auth.py"
    "3_openmrs_test.py"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Check Python dependencies
echo ""
echo "Checking Python dependencies..."
if python3 -c "import requests, urllib3, cryptography"; then
    echo "✅ Python dependencies are available"
else
    echo "⚠️  Python dependencies may be missing - run: pip3 install -r requirements.txt"
fi

# Check if certificates exist
echo ""
echo "Checking SSL certificates..."
if [ -f "nginx/certs/cert.pem" ] && [ -f "nginx/certs/key.pem" ]; then
    echo "✅ SSL certificates exist"
else
    echo "⚠️  SSL certificates missing - run: ./generate_certs.sh"
fi

# Docker status check if available
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    echo "Checking Docker containers..."
    if docker-compose ps &> /dev/null; then
        docker-compose ps
    else
        echo "No containers running (expected if not started yet)"
    fi
else
    echo ""
    echo "⚠️  Cannot check Docker containers - Docker not available"
fi

# Check if .env file exists
echo ""
echo "Checking .env file..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    # Show what's configured (without showing sensitive values)
    if grep -q "OPENMRS_BASE_URL" .env; then
        echo "✅ Base URL configured"
    fi
    if grep -q "CLIENT_ID" .env; then
        echo "✅ Client ID configured"
    fi
    if grep -q "ACCESS_TOKEN" .env; then
        echo "✅ Access token present"
    fi
else
    echo "ℹ️  .env file does not exist (expected before authentication)"
fi

echo ""
echo "Verification complete!"
echo ""
echo "To run the full OpenMRS setup:"
echo "1. Ensure Docker is running"
echo "2. Generate certificates: ./generate_certs.sh"
echo "3. Start services: docker-compose up -d"
echo "4. Complete OpenMRS setup wizard at http://localhost:8080/openmrs"
echo "5. Install FHIR2 and OAuth2 modules"
echo "6. Run authentication: python3 2_openmrs_auth.py"
echo "7. Run tests: python3 3_openmrs_test.py"