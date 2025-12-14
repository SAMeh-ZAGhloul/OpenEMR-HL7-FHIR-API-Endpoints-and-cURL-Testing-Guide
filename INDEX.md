# 📚 OpenEMR FHIR API Testing - Documentation Index

Welcome! This directory contains a complete automation suite for testing OpenEMR FHIR APIs.

## 🚀 Quick Start (Choose Your Path)

### Path 1: I want to run tests NOW! ⚡
1. Read: **[QUICKSTART.md](QUICKSTART.md)** (2 min read)
2. Run: `python3 check_prerequisites.py`
3. Run: `python3 openemr_api_test.py`

### Path 2: I want to understand first 📖
1. Read: **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** (5 min read)
2. Read: **[WORKFLOW.md](WORKFLOW.md)** (visual diagrams)
3. Then follow Path 1

### Path 3: I need detailed documentation 📚
1. Read: **[TESTING_GUIDE.md](TESTING_GUIDE.md)** (comprehensive guide)
2. Reference: **[README.md](README.md)** (API documentation)

---

## 📁 File Directory

### 🎯 Getting Started Files

| File | Size | Purpose | When to Use |
|------|------|---------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | 3.5K | 3-step quick start guide | Want to run tests immediately |
| **[check_prerequisites.py](check_prerequisites.py)** | 4.9K | Validates your environment | Before running tests |
| **[requirements.txt](requirements.txt)** | 32B | Python dependencies | For pip install |

### 🔧 Main Testing Files

| File | Size | Purpose | When to Use |
|------|------|---------|-------------|
| **[openemr_api_test.py](openemr_api_test.py)** | 27K | Main automation script | To run all API tests |

### 📖 Documentation Files

| File | Size | Purpose | When to Use |
|------|------|---------|-------------|
| **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)** | 9.2K | Overview of what was created | Want high-level understanding |
| **[WORKFLOW.md](WORKFLOW.md)** | 22K | Visual workflow diagrams | Want to see the flow visually |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | 8.7K | Comprehensive documentation | Need detailed info/troubleshooting |
| **[README.md](README.md)** | 15K | Original API documentation | Reference for API endpoints |
| **[INDEX.md](INDEX.md)** | - | This file | Finding the right document |

---

## 🎯 Use Case → File Mapping

### "I want to..."

#### ...run the tests right now
→ **[QUICKSTART.md](QUICKSTART.md)** → `python3 openemr_api_test.py`

#### ...check if my environment is ready
→ `python3 check_prerequisites.py`

#### ...understand what was created
→ **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)**

#### ...see how the OAuth2 flow works
→ **[WORKFLOW.md](WORKFLOW.md)** (OAuth2 section)

#### ...see all API endpoints visually
→ **[WORKFLOW.md](WORKFLOW.md)** (Complete flow section)

#### ...troubleshoot an error
→ **[TESTING_GUIDE.md](TESTING_GUIDE.md)** (Troubleshooting section)

#### ...customize the script
→ **[TESTING_GUIDE.md](TESTING_GUIDE.md)** (Configuration section)

#### ...understand FHIR API endpoints
→ **[README.md](README.md)** (Scenarios A-D)

#### ...see what dependencies are needed
→ **[requirements.txt](requirements.txt)**

#### ...modify the test scenarios
→ Edit **[openemr_api_test.py](openemr_api_test.py)** (see TESTING_GUIDE.md first)

---

## 📊 File Relationships

```
INDEX.md (you are here)
    │
    ├─► QUICKSTART.md ────────► Quick 3-step guide
    │       │
    │       └─► check_prerequisites.py ─► Validates setup
    │       └─► openemr_api_test.py ────► Runs tests
    │
    ├─► AUTOMATION_SUMMARY.md ─► What was created & why
    │
    ├─► WORKFLOW.md ───────────► Visual diagrams & flows
    │
    ├─► TESTING_GUIDE.md ──────► Detailed documentation
    │       │
    │       └─► Troubleshooting
    │       └─► Configuration
    │       └─► Advanced usage
    │
    ├─► README.md ─────────────► Original API docs (corrected)
    │       │
    │       └─► cURL examples
    │       └─► API endpoints
    │       └─► FHIR resources
    │
    └─► requirements.txt ──────► Dependencies list
```

---

## 🎓 Recommended Reading Order

### For Beginners:
1. **INDEX.md** (this file) - 2 min
2. **QUICKSTART.md** - 2 min
3. **AUTOMATION_SUMMARY.md** - 5 min
4. Run: `python3 openemr_api_test.py`
5. **WORKFLOW.md** - 10 min (to understand what happened)

### For Developers:
1. **AUTOMATION_SUMMARY.md** - 5 min
2. **WORKFLOW.md** - 10 min
3. **TESTING_GUIDE.md** - 15 min
4. **openemr_api_test.py** - Review code
5. **README.md** - Reference as needed

### For Troubleshooting:
1. Run: `python3 check_prerequisites.py`
2. **TESTING_GUIDE.md** → Troubleshooting section
3. **WORKFLOW.md** → Understand the flow
4. **README.md** → Verify API endpoints

---

## 🔍 Quick Reference

### Commands
```bash
# Check environment
python3 check_prerequisites.py

# Install dependencies
pip3 install -r requirements.txt

# Run all tests
python3 openemr_api_test.py

# Make scripts executable
chmod +x *.py
```

### Configuration
Edit `Config` class in `openemr_api_test.py`:
```python
BASE_URL = "https://localhost:8443"
REDIRECT_URI = "http://localhost:3000/callback"
SCOPES = "openid offline_access api:oemr api:fhir ..."
```

### Prerequisites
- ✅ Python 3.7+
- ✅ OpenEMR running at https://localhost:8443
- ✅ FHIR API enabled (Administration → Config → Connectors)
- ✅ Admin credentials for browser login

---

## 📈 What Gets Tested

The automation script tests **all scenarios** from README.md:

✅ **Scenario A**: Patient Demographics (FHIR Patient)  
✅ **Scenario B**: Appointment Scheduling (FHIR Appointment)  
✅ **Scenario C**: Clinical Encounter (Encounter, Observation, DocumentReference)  
✅ **Scenario D**: Prescribing & Ordering (MedicationRequest, ServiceRequest)  

Plus:
✅ OAuth2 registration  
✅ Authorization code flow  
✅ Token exchange  
✅ Token refresh  
✅ Patient data retrieval  

---

## 🎯 Success Criteria

After running `python3 openemr_api_test.py`, you should see:

```
✅ All checks passed (5/5)
✅ Registration Successful!
✅ Authorization Code Received
✅ Access Token Received!
✅ Patient Created Successfully!
✅ Appointment Created Successfully!
✅ Encounter Created Successfully!
✅ Vital Signs Recorded Successfully!
✅ Clinical Note Created Successfully!
✅ Medication Request Created Successfully!
✅ Service Request Created Successfully!
✅ Patient Retrieved Successfully!

🎉 All API endpoints tested successfully!
```

---

## 🆘 Getting Help

### Issue: Script fails
1. Run: `python3 check_prerequisites.py`
2. Check: **TESTING_GUIDE.md** → Troubleshooting
3. Verify: OpenEMR is running (`curl -k https://localhost:8443`)

### Issue: Can't find the right documentation
1. Check this **INDEX.md** file
2. Use the "I want to..." section above

### Issue: Don't understand OAuth2 flow
1. Read: **WORKFLOW.md** → OAuth2 section
2. Read: **README.md** → Authentication section

### Issue: Need to customize the script
1. Read: **TESTING_GUIDE.md** → Configuration
2. Edit: `openemr_api_test.py` → `Config` class

---

## 📝 What Was Fixed

The original **README.md** had issues in the "API Configuration and Authentication" section:

❌ **Issue 1**: Redirect URI mismatch (`localhost:8443` vs `localhost:3000`)  
❌ **Issue 2**: Shell variables not expanding (single quotes in curl)  
❌ **Issue 3**: Same issue in refresh token command  

✅ **All fixed!** See README.md for corrected version.

---

## 🎉 Summary

You have:
- ✅ Complete automation suite (700+ lines of Python)
- ✅ Prerequisite validation script
- ✅ Comprehensive documentation (5 markdown files)
- ✅ Visual workflow diagrams
- ✅ Quick start guide
- ✅ Troubleshooting guide
- ✅ Corrected API documentation

**Total**: 8 files, ~90KB of code and documentation

---

## 🚀 Ready to Start?

```bash
# Step 1: Check prerequisites
python3 check_prerequisites.py

# Step 2: Run tests
python3 openemr_api_test.py
```

**Or read more first:**
- Quick overview: **[AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md)**
- Visual diagrams: **[WORKFLOW.md](WORKFLOW.md)**
- Detailed guide: **[TESTING_GUIDE.md](TESTING_GUIDE.md)**

---

**Happy Testing!** 🎊

*Last updated: 2025-12-14*
