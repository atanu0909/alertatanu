"""
Comprehensive Database Connectivity Troubleshooting Script
=========================================================

This script helps diagnose and resolve connection issues with the SQL Server
database from both local and GitHub Actions environments.
"""

import os
import sys
import socket
import time
from datetime import datetime
import pymssql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database configuration
DB_SERVER = os.getenv('DB_SERVER', '1.22.45.168')
DB_PORT = int(os.getenv('DB_PORT', '19471'))
DB_NAME = os.getenv('DB_NAME', 'etimetrackliteWEB')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'sa@123')

# Email configuration
EMAIL_USER = os.getenv('EMAIL_USER', 'your_email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_network_connectivity():
    """Test basic network connectivity to the database server"""
    log_message("Testing network connectivity...")
    
    try:
        # Test if the server is reachable
        log_message(f"Testing connection to {DB_SERVER}:{DB_PORT}")
        
        # Create a socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)  # 30 second timeout
        
        result = sock.connect_ex((DB_SERVER, DB_PORT))
        sock.close()
        
        if result == 0:
            log_message(f"✓ Network connectivity to {DB_SERVER}:{DB_PORT} successful")
            return True
        else:
            log_message(f"✗ Network connectivity to {DB_SERVER}:{DB_PORT} failed (Error code: {result})")
            return False
            
    except Exception as e:
        log_message(f"✗ Network connectivity test failed: {str(e)}", "ERROR")
        return False

def test_database_connection():
    """Test database connection with different timeout settings"""
    log_message("Testing database connection...")
    
    connection_strings = [
        # Standard connection
        f"server={DB_SERVER};port={DB_PORT};database={DB_NAME};user={DB_USER};password={DB_PASSWORD};timeout=30",
        # Connection with longer timeout
        f"server={DB_SERVER};port={DB_PORT};database={DB_NAME};user={DB_USER};password={DB_PASSWORD};timeout=60;login_timeout=60",
        # Connection with connection pooling disabled
        f"server={DB_SERVER};port={DB_PORT};database={DB_NAME};user={DB_USER};password={DB_PASSWORD};timeout=30;pooling=false",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        try:
            log_message(f"Attempt {i}: Testing connection with different parameters...")
            
            conn = pymssql.connect(
                server=DB_SERVER,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                timeout=30,
                login_timeout=60
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            
            log_message(f"✓ Database connection successful!")
            log_message(f"  SQL Server Version: {version[0]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            log_message(f"✗ Database connection attempt {i} failed: {str(e)}", "ERROR")
            continue
    
    return False

def test_table_access():
    """Test access to required tables"""
    log_message("Testing table access...")
    
    try:
        conn = pymssql.connect(
            server=DB_SERVER,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            timeout=30,
            login_timeout=60
        )
        
        cursor = conn.cursor()
        
        # Test tables
        test_queries = [
            ("Employee table", "SELECT TOP 1 * FROM dbo.Employee"),
            ("DeviceLogs table", "SELECT TOP 1 * FROM dbo.DeviceLogs_7_2025"),
            ("Current month DeviceLogs", f"SELECT TOP 1 * FROM dbo.DeviceLogs_{datetime.now().month}_{datetime.now().year}"),
        ]
        
        for table_name, query in test_queries:
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                log_message(f"✓ {table_name} accessible")
            except Exception as e:
                log_message(f"✗ {table_name} access failed: {str(e)}", "ERROR")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log_message(f"✗ Table access test failed: {str(e)}", "ERROR")
        return False

def get_github_runner_ip():
    """Get the IP address of the GitHub Actions runner"""
    try:
        import requests
        response = requests.get('https://httpbin.org/ip', timeout=10)
        ip_info = response.json()
        runner_ip = ip_info.get('origin', 'Unknown')
        log_message(f"GitHub Actions runner IP: {runner_ip}")
        return runner_ip
    except Exception as e:
        log_message(f"Could not determine runner IP: {str(e)}", "ERROR")
        return None

def send_diagnostic_email(results):
    """Send diagnostic results via email"""
    log_message("Sending diagnostic email...")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"Database Connectivity Diagnostic Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
Database Connectivity Diagnostic Results
========================================

Environment: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database Server: {DB_SERVER}:{DB_PORT}
Database Name: {DB_NAME}

Test Results:
{results}

Recommendations:
1. Check if SQL Server port {DB_PORT} is open in firewall
2. Verify SQL Server is configured to accept remote connections
3. Check if GitHub Actions runner IPs are whitelisted
4. Consider using a VPN or database proxy if direct access is blocked
5. Verify SQL Server authentication mode allows SQL Server authentication

If the issue persists, contact your network administrator to:
- Open port {DB_PORT} for inbound connections
- Whitelist GitHub Actions runner IP ranges
- Check SQL Server configuration for remote access
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, ADMIN_EMAIL, text)
        server.quit()
        
        log_message("✓ Diagnostic email sent successfully")
        
    except Exception as e:
        log_message(f"✗ Failed to send diagnostic email: {str(e)}", "ERROR")

def main():
    """Main diagnostic function"""
    log_message("Starting comprehensive database connectivity diagnostic...")
    
    # Check environment
    is_github_actions = os.getenv('GITHUB_ACTIONS', '').lower() == 'true'
    log_message(f"Environment: {'GitHub Actions' if is_github_actions else 'Local'}")
    
    if is_github_actions:
        runner_ip = get_github_runner_ip()
    
    # Run tests
    results = []
    
    # Test 1: Network connectivity
    network_ok = test_network_connectivity()
    results.append(f"Network Connectivity: {'PASS' if network_ok else 'FAIL'}")
    
    # Test 2: Database connection
    db_ok = test_database_connection()
    results.append(f"Database Connection: {'PASS' if db_ok else 'FAIL'}")
    
    # Test 3: Table access (only if database connection works)
    if db_ok:
        table_ok = test_table_access()
        results.append(f"Table Access: {'PASS' if table_ok else 'FAIL'}")
    else:
        results.append("Table Access: SKIPPED (Database connection failed)")
    
    # Summary
    log_message("\n" + "="*50)
    log_message("DIAGNOSTIC SUMMARY")
    log_message("="*50)
    
    for result in results:
        log_message(result)
    
    # Send diagnostic email
    results_text = '\n'.join(results)
    send_diagnostic_email(results_text)
    
    # Exit with appropriate code
    if network_ok and db_ok:
        log_message("✓ All tests passed! Database connectivity is working.")
        sys.exit(0)
    else:
        log_message("✗ Some tests failed. Check the logs and recommendations above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
