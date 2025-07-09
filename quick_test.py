"""
Simple Database Connection Test
==============================

Quick test to verify database connectivity and basic functionality.
"""

import os
import sys
import socket
from datetime import datetime

def test_basic_connectivity():
    """Test basic network connectivity"""
    server = '1.22.45.168'
    port = 19471
    
    print(f"Testing network connectivity to {server}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            print("✓ Network connectivity successful")
            return True
        else:
            print(f"✗ Network connectivity failed (Error: {result})")
            return False
    except Exception as e:
        print(f"✗ Network test error: {str(e)}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        import pymssql
        
        conn = pymssql.connect(
            server='1.22.45.168',
            port=19471,
            database=os.getenv('DB_NAME', 'MainDb'),
            user=os.getenv('DB_USER', 'sa'),
            password=os.getenv('DB_PASSWORD', 'YourPassword'),
            timeout=30
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        
        print("✓ Database connection successful")
        print(f"  SQL Server Version: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("✗ pymssql not installed. Run: pip install pymssql")
        return False
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Database Connection Quick Test")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local'}")
    
    # Test network connectivity
    network_ok = test_basic_connectivity()
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Network Connectivity: {'PASS' if network_ok else 'FAIL'}")
    print(f"Database Connection: {'PASS' if db_ok else 'FAIL'}")
    
    if network_ok and db_ok:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Check connectivity and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
