#!/usr/bin/env python3
"""
Deployment Verification Script
=============================

Verifies that all components are properly configured for GitHub Actions deployment
"""

import os
import json
from datetime import datetime

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def verify_deployment():
    """Verify all deployment components"""
    print("="*60)
    print("DEPLOYMENT VERIFICATION")
    print("="*60)
    print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_good = True
    
    # Check core files
    print("📁 Core Files:")
    all_good &= check_file_exists("monitor.py", "Main monitoring script")
    all_good &= check_file_exists("troubleshoot_connectivity.py", "Connectivity test script")
    print()
    
    # Check GitHub workflow
    print("⚙️ GitHub Actions Configuration:")
    all_good &= check_file_exists(".github/workflows/attendance-monitor.yml", "GitHub workflow file")
    print()
    
    # Check requirements
    print("📦 Dependencies:")
    if check_file_exists("requirements.txt", "Requirements file"):
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            if "pymssql" in requirements:
                print("✅ pymssql dependency found")
            else:
                print("❌ pymssql dependency missing")
                all_good = False
    else:
        all_good = False
    print()
    
    # Verify configuration
    print("🔧 Configuration:")
    
    # Check monitor.py configuration
    if os.path.exists("monitor.py"):
        with open("monitor.py", "r") as f:
            content = f.read()
            if "etimetrackliteWEB" in content:
                print("✅ Correct database name in monitor.py")
            else:
                print("❌ Incorrect database name in monitor.py")
                all_good = False
                
            if "1.22.45.168" in content:
                print("✅ Correct server IP in monitor.py")
            else:
                print("❌ Incorrect server IP in monitor.py")
                all_good = False
                
            if "19471" in content:
                print("✅ Correct port in monitor.py")
            else:
                print("❌ Incorrect port in monitor.py")
                all_good = False
    print()
    
    # Check GitHub secrets requirements
    print("🔐 Required GitHub Secrets:")
    secrets_needed = [
        "DB_SERVER (1.22.45.168)",
        "DB_PORT (19471)", 
        "DB_NAME (etimetrackliteWEB)",
        "DB_USER (sa)",
        "DB_PASSWORD (sa@123)",
        "EMAIL_USER (your Gmail)",
        "EMAIL_PASSWORD (your app password)",
        "ADMIN_EMAIL (your admin email)"
    ]
    
    for secret in secrets_needed:
        print(f"📝 {secret}")
    print()
    
    # Final status
    print("="*60)
    if all_good:
        print("✅ DEPLOYMENT READY!")
        print("✅ All components are properly configured")
        print("✅ You can deploy to GitHub Actions")
        print()
        print("📋 Next Steps:")
        print("1. Run deploy_to_github.bat to deploy")
        print("2. Check GitHub Actions: https://github.com/atanu0909/alertatanu/actions")
        print("3. Monitor workflow status and logs")
    else:
        print("❌ DEPLOYMENT ISSUES FOUND!")
        print("❌ Please fix the issues above before deploying")
    print("="*60)
    
    return all_good

if __name__ == "__main__":
    verify_deployment()
