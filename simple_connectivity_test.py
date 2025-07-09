#!/usr/bin/env python3
"""
Simple Database Connectivity Test
================================

Tests basic network connectivity to the SQL Server without requiring pymssql
"""

import socket
import os
from datetime import datetime

# Database configuration
DB_SERVER = os.getenv('DB_SERVER', '1.22.45.168')
DB_PORT = int(os.getenv('DB_PORT', '19471'))
DB_NAME = os.getenv('DB_NAME', 'etimetrackliteWEB')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sa@123')

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_network_connectivity():
    """Test basic network connectivity to the database server"""
    log_message("="*60)
    log_message("SIMPLE DATABASE CONNECTIVITY TEST")
    log_message("="*60)
    
    log_message(f"Database Server: {DB_SERVER}")
    log_message(f"Database Port: {DB_PORT}")
    log_message(f"Database Name: {DB_NAME}")
    log_message(f"Database User: {DB_USER}")
    log_message(f"Password: {'*' * len(DB_PASSWORD)}")
    
    log_message("Testing network connectivity...")
    
    try:
        # Test if the server is reachable
        log_message(f"Attempting to connect to {DB_SERVER}:{DB_PORT}")
        
        # Create a socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)  # 30 second timeout
        
        result = sock.connect_ex((DB_SERVER, DB_PORT))
        sock.close()
        
        if result == 0:
            log_message(f"✅ SUCCESS: Network connectivity to {DB_SERVER}:{DB_PORT} is working!")
            log_message("✅ The SQL Server port is accessible")
            log_message("✅ Your GitHub Actions should be able to connect")
            return True
        else:
            log_message(f"❌ FAILED: Network connectivity to {DB_SERVER}:{DB_PORT} failed")
            log_message(f"❌ Error code: {result}")
            log_message("❌ Possible issues:")
            log_message("   - SQL Server is not running")
            log_message("   - Port 19471 is blocked by firewall")
            log_message("   - Network connectivity issues")
            return False
            
    except Exception as e:
        log_message(f"❌ Network connectivity test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    success = test_network_connectivity()
    
    log_message("="*60)
    if success:
        log_message("✅ RESULT: DATABASE SERVER IS ACCESSIBLE!")
        log_message("✅ Your attendance monitoring system should work properly")
        log_message("✅ GitHub Actions can connect to your SQL Server")
    else:
        log_message("❌ RESULT: DATABASE SERVER IS NOT ACCESSIBLE!")
        log_message("❌ Check your SQL Server configuration and firewall settings")
        log_message("❌ GitHub Actions will not be able to connect")
    
    log_message("="*60)
    
    # GitHub Actions info
    is_github_actions = os.getenv('GITHUB_ACTIONS', '').lower() == 'true'
    log_message(f"Environment: {'GitHub Actions' if is_github_actions else 'Local Development'}")
    
    if is_github_actions:
        log_message("Running in GitHub Actions - using secrets for configuration")
    else:
        log_message("Running locally - using default configuration")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
