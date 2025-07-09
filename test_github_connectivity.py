#!/usr/bin/env python3
"""
Test GitHub Actions connectivity to database
Check if IP 1.22.45.168:19471 is accessible from GitHub Actions
"""

import socket
import pymssql
import os
from datetime import datetime

def test_network_connectivity():
    """Test basic network connectivity to the database server"""
    print("🔍 Testing network connectivity...")
    
    host = '1.22.45.168'
    port = 19471
    timeout = 10
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Network connectivity SUCCESS: {host}:{port} is reachable")
            return True
        else:
            print(f"❌ Network connectivity FAILED: {host}:{port} is not reachable")
            return False
    except Exception as e:
        print(f"❌ Network test error: {e}")
        return False

def test_database_connection():
    """Test actual database connection"""
    print("\n🔍 Testing database connection...")
    
    # Use environment variables if available, otherwise defaults
    db_server = os.getenv('DB_SERVER', '1.22.45.168')
    db_port = int(os.getenv('DB_PORT', '19471'))
    db_name = os.getenv('DB_NAME', 'etimetrackliteWEB')
    db_user = os.getenv('DB_USER', 'sa')
    db_password = os.getenv('DB_PASSWORD', 'sa@123')
    
    print(f"📊 Connection details:")
    print(f"   Server: {db_server}")
    print(f"   Port: {db_port}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    
    try:
        conn = pymssql.connect(
            server=db_server,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            timeout=30
        )
        
        print("✅ Database connection SUCCESS")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT GETDATE() as CurrentTime")
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Database query SUCCESS: Server time is {result[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection FAILED: {e}")
        return False

def test_table_access():
    """Test access to specific tables used by the monitor"""
    print("\n🔍 Testing table access...")
    
    db_server = os.getenv('DB_SERVER', '1.22.45.168')
    db_port = int(os.getenv('DB_PORT', '19471'))
    db_name = os.getenv('DB_NAME', 'etimetrackliteWEB')
    db_user = os.getenv('DB_USER', 'sa')
    db_password = os.getenv('DB_PASSWORD', 'sa@123')
    
    try:
        conn = pymssql.connect(
            server=db_server,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            timeout=30
        )
        
        cursor = conn.cursor()
        
        # Test Employee table
        try:
            cursor.execute("SELECT COUNT(*) FROM dbo.Employee")
            emp_count = cursor.fetchone()[0]
            print(f"✅ Employee table access SUCCESS: {emp_count} records found")
        except Exception as e:
            print(f"❌ Employee table access FAILED: {e}")
        
        # Test DeviceLogs table for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        table_name = f"dbo.DeviceLogs_{current_month}_{current_year}"
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            log_count = cursor.fetchone()[0]
            print(f"✅ {table_name} access SUCCESS: {log_count} records found")
        except Exception as e:
            print(f"❌ {table_name} access FAILED: {e}")
        
        # Test Device 19 records
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table_name} 
                WHERE CAST(LogDate as DATE) = '{today}' AND DeviceId = 19
            """)
            device19_count = cursor.fetchone()[0]
            print(f"✅ Device 19 today's records: {device19_count} punches found")
        except Exception as e:
            print(f"❌ Device 19 query FAILED: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Table access test FAILED: {e}")
        return False

def main():
    print("🚀 GitHub Actions Database Connectivity Test")
    print("=" * 50)
    print(f"Test time: {datetime.now()}")
    print(f"Running from: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local Environment'}")
    print("=" * 50)
    
    # Test 1: Network connectivity
    network_ok = test_network_connectivity()
    
    # Test 2: Database connection
    db_ok = test_database_connection()
    
    # Test 3: Table access
    table_ok = test_table_access()
    
    print("\n" + "=" * 50)
    print("📊 CONNECTIVITY TEST SUMMARY")
    print("=" * 50)
    print(f"Network Connectivity: {'✅ PASS' if network_ok else '❌ FAIL'}")
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Table Access: {'✅ PASS' if table_ok else '❌ FAIL'}")
    
    if network_ok and db_ok and table_ok:
        print("\n🎉 ALL TESTS PASSED - GitHub Actions can access the database!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Check the errors above")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
