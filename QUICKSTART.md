# Quick Start Guide - OpenEMR API Testing

This guide will get you testing the OpenEMR FHIR API in 3 simple steps.

## 📋 Step 1: Check Prerequisites

Run the validation script to ensure everything is ready:

```bash
python3 check_prerequisites.py
```

**Expected Output:**
```
✅ All checks passed (5/5)
🚀 You're ready to run: python3 openemr_api_test.py
```

**If checks fail**, follow the instructions shown to fix issues.

## 📦 Step 2: Install Dependencies (if needed)

```bash
pip3 install -r requirements.txt
```

## 🚀 Step 3: Run the Automated Tests

```bash
python3 openemr_api_test.py
```

### What to Expect:

1. **Browser Opens Automatically**
   - Log in with your OpenEMR admin credentials
   - Approve the OAuth consent screen
   - Browser will show "Authorization Successful!"

2. **Script Runs All Tests**
   - Creates a test patient
   - Books an appointment
   - Records clinical encounter
   - Adds vital signs and notes
   - Creates prescription and lab orders

3. **Results Displayed**
   ```
   🎉 All API endpoints tested successfully!
   
   Credentials saved for future use:
     CLIENT_ID=XjhIuBGu_UdwK18o2LqH0XR07ouvf645iBeXq6plGfA
     CLIENT_SECRET=Gzd9cooABqpT5ObaBf0RvkNILGTEqDafKs6aVfHdnfkjqtowKIpZ5j3yf6sDokNN9AAVsCSO
   ```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `openemr_api_test.py` | Main automated testing script |
| `check_prerequisites.py` | Validates your setup before testing |
| `requirements.txt` | Python dependencies |
| `TESTING_GUIDE.md` | Comprehensive documentation |
| `README.md` | Original API documentation with cURL examples |

## 🔧 Troubleshooting

### Issue: "Cannot connect to https://localhost:8443"

**Solution:** Start your OpenEMR Docker container:
```bash
docker ps  # Check if running
docker start <container_name>  # If not running
```

### Issue: "FHIR endpoint not found (404)"

**Solution:** Enable FHIR API in OpenEMR:
1. Log into OpenEMR web interface
2. Go to: **Administration → Config → Connectors**
3. Check: ☑ **Enable OpenEMR Standard FHIR REST API**
4. Click **Save**

### Issue: "Browser doesn't open"

**Solution:** Copy the URL from terminal and open manually in your browser.

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution:** Install dependencies:
```bash
pip3 install requests urllib3
```

## 📚 Next Steps

- **Read TESTING_GUIDE.md** for advanced usage and customization
- **Read README.md** for detailed API documentation
- **Modify the script** to test your specific use cases

## 🎯 Quick Commands Reference

```bash
# Check if everything is ready
python3 check_prerequisites.py

# Run full automated test suite
python3 openemr_api_test.py

# Install/update dependencies
pip3 install -r requirements.txt

# Make scripts executable (Unix/Mac)
chmod +x *.py
```

## ⚡ One-Liner Setup

```bash
pip3 install -r requirements.txt && python3 check_prerequisites.py && python3 openemr_api_test.py
```

This will:
1. Install dependencies
2. Check prerequisites
3. Run all tests (if checks pass)

## 💡 Tips

- **First Run**: Takes ~2 minutes (includes browser login)
- **Subsequent Runs**: Can reuse credentials (see TESTING_GUIDE.md)
- **Debugging**: Each API call shows full request/response
- **Customization**: Edit `Config` class in `openemr_api_test.py`

## 🆘 Getting Help

1. Check error messages in terminal output
2. Review TESTING_GUIDE.md for detailed troubleshooting
3. Verify OpenEMR is running: `curl -k https://localhost:8443`
4. Check OpenEMR logs for server-side errors

---

**Ready to test?** Run: `python3 openemr_api_test.py` 🚀
