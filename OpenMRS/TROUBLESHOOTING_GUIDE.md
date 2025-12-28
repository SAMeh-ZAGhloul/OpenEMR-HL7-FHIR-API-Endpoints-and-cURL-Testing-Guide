# OpenMRS Access and Troubleshooting Guide

## Current Issue: Tomcat Manager Instead of OpenMRS

The error you're seeing indicates that you're accessing the Tomcat manager application instead of the OpenMRS application. This suggests that:

1. The OpenMRS WAR file may not be properly deployed
2. The OpenMRS application may not be running
3. The Docker configuration might need adjustment

## Correct OpenMRS Access URLs

### Direct Tomcat Access (without reverse proxy):
- **OpenMRS Application**: `https://localhost:8443/openmrs` or `http://localhost:8080/openmrs`
- **OpenMRS Login**: `https://localhost:8443/openmrs/login.htm` or `http://localhost:8080/openmrs/login.htm`

### FHIR API Endpoints:
- **FHIR Metadata**: `https://localhost:8443/openmrs/ws/fhir2/R4/metadata`
- **Patient Endpoint**: `https://localhost:8443/openmrs/ws/fhir2/R4/Patient`

## Docker Configuration Issues

The current docker-compose.yml might need adjustment. The OpenMRS reference application should be deployed as a web application within Tomcat, not replace the entire Tomcat server.

### Recommended Docker Configuration:

```yaml
version: '3.8'

services:
  # MySQL Database for OpenMRS
  openmrs_db:
    image: mysql:8.0
    container_name: openmrs_database
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=openmrs
      - MYSQL_USER=openmrs
      - MYSQL_PASSWORD=openmrs
    command: --default-authentication-plugin=mysql_native_password
    volumes:
      - openmrs_db_data:/var/lib/mysql
    ports:
      - "3306:3306"

  # OpenMRS Application Server
  openmrs:
    image: openmrs/openmrs-reference-application-distro:latest
    container_name: openmrs_server
    restart: always
    environment:
      - DATABASE_HOST=openmrs_db
      - DATABASE_NAME=openmrs
      - DATABASE_USER=openmrs
      - DATABASE_PASSWORD=openmrs
    depends_on:
      - openmrs_db
    ports:
      - "8080:8080"
    volumes:
      - openmrs_data:/openmrs/data

  # Nginx Reverse Proxy for HTTPS
  nginx_proxy:
    image: nginx:stable-alpine
    container_name: openmrs_nginx_proxy
    restart: always
    ports:
      - "8443:443"
      - "8080:80"
    depends_on:
      - openmrs
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certs:/etc/nginx/certs:ro

volumes:
  openmrs_data:
  openmrs_db_data:
```

## Steps to Fix the Issue

### 1. Check Docker Container Status
```bash
docker-compose ps
docker logs openmrs_server
docker logs openmrs_db
```

### 2. Verify OpenMRS Installation
If the OpenMRS application is not properly installed:
1. Access the initial setup at `http://localhost:8080` (or `https://localhost:8443/openmrs` if using reverse proxy)
2. Complete the OpenMRS installation wizard
3. Point to the MySQL database with the credentials specified in docker-compose.yml

### 3. Alternative: Manual OpenMRS Installation
If Docker continues to have issues, you can install OpenMRS manually:

1. Download OpenMRS WAR file from https://openmrs.org/download/
2. Deploy to a Tomcat server
3. Access the setup wizard at `http://your-server:8080/openmrs`
4. Follow the installation wizard to connect to your database

### 4. Verify Module Installation
After OpenMRS is running:
1. Log in as admin (default: admin/test or admin/Admin123)
2. Go to **Administration** → **Manage Modules**
3. Install FHIR2 and OAuth2 modules if not already present

## Correct Default Credentials

### OpenMRS Application:
- **URL**: `http://localhost:8080/openmrs` or `https://localhost:8443/openmrs`
- **Username**: `admin`
- **Password**: `test` (initial) or `Admin123` (after setup)

### Tomcat Manager (different from OpenMRS):
- **URL**: `http://localhost:8080/manager/html` - This is NOT the OpenMRS application
- **Credentials**: Configured in `conf/tomcat-users.xml`

## Troubleshooting Steps

### 1. Check if OpenMRS is Running
```bash
curl -v http://localhost:8080/openmrs
```

### 2. Check Docker Logs
```bash
docker logs openmrs_server
```

### 3. Verify Database Connection
```bash
docker logs openmrs_db
```

### 4. Check if the OpenMRS Application is Deployed
The OpenMRS application should be deployed as `/openmrs` context in Tomcat, not replace the entire Tomcat manager.

## Important Notes

- The Tomcat manager interface is separate from the OpenMRS application
- OpenMRS runs as a web application within Tomcat, typically under the `/openmrs` context
- The 401 Unauthorized error on the Tomcat manager is normal if you haven't configured manager users
- You should access OpenMRS at `/openmrs` path, not at the root Tomcat context