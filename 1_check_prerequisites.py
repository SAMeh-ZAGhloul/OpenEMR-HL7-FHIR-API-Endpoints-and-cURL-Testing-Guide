#!/usr/bin/env python3
"""
Quick validation script to check if OpenEMR is ready for API testing
"""

import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False

def check_dependencies():
    """Check required Python packages"""
    print("\n🔍 Checking dependencies...")
    try:
        import requests
        print(f"   ✅ requests {requests.__version__}")
        return True
    except ImportError:
        print("   ❌ requests not installed")
        print("      Run: pip3 install -r requirements.txt")
        return False

def check_openemr_connection():
    """Check if OpenEMR is accessible"""
    print("\n🔍 Checking OpenEMR connection...")
    url = "https://localhost:8443"
    
    try:
        response = requests.get(url, verify=False, timeout=5)
        if response.status_code in [200, 302, 401]:
            print(f"   ✅ OpenEMR is accessible at {url}")
            return True
        else:
            print(f"   ⚠️  OpenEMR responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to {url}")
        print("      Make sure OpenEMR is running")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Connection timeout to {url}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def check_fhir_endpoint():
    """Check if FHIR endpoint is accessible"""
    print("\n🔍 Checking FHIR endpoint...")
    url = "https://localhost:8443/apis/default/fhir/metadata"
    
    try:
        response = requests.get(url, verify=False, timeout=5)
        # 401 is expected without auth, but means endpoint exists
        if response.status_code in [200, 401]:
            print(f"   ✅ FHIR endpoint is accessible")
            return True
        elif response.status_code == 404:
            print(f"   ❌ FHIR endpoint not found (404)")
            print("      Enable FHIR API in: Administration → Config → Connectors")
            return False
        else:
            print(f"   ⚠️  FHIR endpoint responded with status {response.status_code}")
            return True  # Might still work
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to FHIR endpoint")
        return False
    except Exception as e:
        print(f"   ⚠️  Error checking FHIR: {str(e)}")
        return False

def check_oauth_endpoint():
    """Check if OAuth2 endpoint is accessible"""
    print("\n🔍 Checking OAuth2 endpoint...")
    url = "https://localhost:8443/oauth2/default/registration"
    
    try:
        # POST with empty body should return 400 (bad request) not 404
        response = requests.post(url, json={}, verify=False, timeout=5)
        if response.status_code in [400, 401, 422]:
            print(f"   ✅ OAuth2 registration endpoint is accessible")
            return True
        elif response.status_code == 404:
            print(f"   ❌ OAuth2 endpoint not found (404)")
            print("      Check OpenEMR configuration")
            return False
        else:
            print(f"   ⚠️  OAuth2 endpoint responded with status {response.status_code}")
            return True
    except Exception as e:
        print(f"   ⚠️  Error checking OAuth2: {str(e)}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║           OpenEMR API Testing - Prerequisites Check            ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_openemr_connection(),
        check_fhir_endpoint(),
        check_oauth_endpoint()
    ]
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🚀 You're ready to run: python3 2_openemr_auth.py")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n📝 Please fix the issues above before running the test script")
        return 1

if __name__ == "__main__":
    sys.exit(main())
