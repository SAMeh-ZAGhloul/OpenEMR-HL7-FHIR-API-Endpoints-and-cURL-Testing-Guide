#!/bin/bash

# OpenMRS PoC SSL Certificate Generator
echo "--- OpenMRS PoC SSL Certificate Generator ---"
echo "This script creates a self-signed certificate and key for localhost."

# 1. Ensure the 'nginx/certs' directory exists
mkdir -p nginx/certs
cd nginx/certs

# 2. Generate the self-signed certificate and key
# C=US, ST=NY, L=NewYork, O=PoC Test, CN=localhost
echo "Generating self-signed certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=NY/L=NewYork/O=PoC Test/CN=localhost"

echo "✅ Generated: nginx/certs/cert.pem"
echo "✅ Generated: nginx/certs/key.pem"
echo "---"
echo "You can now run 'docker-compose up -d' to start OpenMRS via HTTPS on port 8443."