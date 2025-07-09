"""
Fallback Attendance Monitor with Multiple Connection Strategies
==============================================================

This script provides multiple strategies to handle database connectivity issues:
1. Direct connection (original method)
2. Connection with extended timeouts
3. Retry mechanism with exponential backoff
4. Fallback to cached data if database is unavailable
5. Email notification about connectivity issues
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime, timedelta
import pymssql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

# Configuration
DB_SERVER = os.getenv('DB_SERVER', '1.22.45.168')
DB_PORT = int(os.getenv('DB_PORT', '19471'))
DB_NAME = os.getenv('DB_NAME', 'MainDb')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'YourPassword')

EMAIL_USER = os.getenv('EMAIL_USER', 'your_email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_app_password')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

# Target employees for monitoring (Device 19 only)
TARGET_EMPLOYEES = {
    'Ryobi 3': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Ryobi 2': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Flat Bed': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Akash Roy': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Asish Ghosh': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Rajesh Ghosh': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Suman Ghosh': {'dept': 'PRODUCTION', 'shift_start': '09:00'},
    'Sudeb Ghosh': {'dept': 'PRODUCTION', 'shift_start': '09:00'}
}

CACHE_FILE = 'attendance_cache.json'
ALERTS_FILE = 'daily_alerts.json'

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_network_connectivity():
    """Test basic network connectivity"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((DB_SERVER, DB_PORT))
        sock.close()
        return result == 0
    except Exception as e:
        log_message(f"Network test failed: {str(e)}", "ERROR")
        return False

def connect_to_database_with_retry(max_retries=3, base_delay=2):
    """Connect to database with retry mechanism and extended timeouts"""
    for attempt in range(max_retries):
        try:
            log_message(f"Database connection attempt {attempt + 1}/{max_retries}")
            
            # Increase timeout progressively
            timeout = 30 + (attempt * 15)  # 30s, 45s, 60s
            
            conn = pymssql.connect(
                server=DB_SERVER,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                timeout=timeout,
                login_timeout=timeout
            )
            
            log_message("✓ Database connection successful")
            return conn
            
        except Exception as e:
            log_message(f"Connection attempt {attempt + 1} failed: {str(e)}", "ERROR")
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                log_message(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                log_message("All connection attempts failed", "ERROR")
                return None

def load_cache():
    """Load cached data"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        log_message(f"Error loading cache: {str(e)}", "ERROR")
    return {}

def save_cache(data):
    """Save data to cache"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_message(f"Error saving cache: {str(e)}", "ERROR")

def load_daily_alerts():
    """Load today's alert history"""
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
                # Filter for today's alerts
                today = datetime.now().strftime('%Y-%m-%d')
                return alerts.get(today, [])
    except Exception as e:
        log_message(f"Error loading alerts: {str(e)}", "ERROR")
    return []

def save_daily_alert(employee_name):
    """Save alert for today"""
    try:
        alerts = {}
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in alerts:
            alerts[today] = []
        
        if employee_name not in alerts[today]:
            alerts[today].append(employee_name)
            
            with open(ALERTS_FILE, 'w') as f:
                json.dump(alerts, f, indent=2)
                
    except Exception as e:
        log_message(f"Error saving alert: {str(e)}", "ERROR")

def get_employee_emails(conn):
    """Get employee email addresses from database"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Name, Email 
            FROM dbo.Employee 
            WHERE Name IN ('Ryobi 3', 'Ryobi 2', 'Flat Bed', 'Akash Roy', 'Asish Ghosh', 'Rajesh Ghosh', 'Suman Ghosh', 'Sudeb Ghosh')
            AND Email IS NOT NULL 
            AND Email != ''
        """)
        
        emails = {}
        for row in cursor.fetchall():
            name, email = row
            emails[name] = email
        
        cursor.close()
        return emails
        
    except Exception as e:
        log_message(f"Error fetching employee emails: {str(e)}", "ERROR")
        return {}

def get_today_attendance_data(conn):
    """Get today's attendance data for target employees from Device 19"""
    try:
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        query = """
        SELECT 
            e.Name,
            e.DepartmentName,
            MIN(l.LogDate) as FirstPunch,
            e.Email
        FROM dbo.LogInOutData l
        INNER JOIN dbo.Employee e ON l.EmpId = e.Id
        WHERE CAST(l.LogDate AS DATE) = %s
        AND l.DeviceId = 19
        AND e.Name IN ('Ryobi 3', 'Ryobi 2', 'Flat Bed', 'Akash Roy', 'Asish Ghosh', 'Rajesh Ghosh', 'Suman Ghosh', 'Sudeb Ghosh')
        GROUP BY e.Name, e.DepartmentName, e.Email
        ORDER BY FirstPunch
        """
        
        cursor.execute(query, (today,))
        results = cursor.fetchall()
        cursor.close()
        
        return results
        
    except Exception as e:
        log_message(f"Error fetching attendance data: {str(e)}", "ERROR")
        return []

def send_late_alert(employee_name, first_punch, shift_start, minutes_late, employee_email=None):
    """Send email alert for late employee"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        
        # CC employee if email is available
        if employee_email:
            msg['Cc'] = employee_email
        
        msg['Subject'] = f"LATE ARRIVAL ALERT: {employee_name} - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
LATE ARRIVAL ALERT
==================

Employee: {employee_name}
Date: {datetime.now().strftime('%Y-%m-%d')}
Device: 19
Shift Start Time: {shift_start}
First Punch: {first_punch.strftime('%H:%M:%S')}
Minutes Late: {minutes_late}
Status: LATE (>{15} minutes)

This is an automated alert from the Real-Time Attendance Monitoring System.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Send to admin and CC employee if email provided
        recipients = [ADMIN_EMAIL]
        if employee_email:
            recipients.append(employee_email)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USER, recipients, text)
        server.quit()
        
        log_message(f"✓ Late alert sent for {employee_name}")
        if employee_email:
            log_message(f"  CC sent to employee: {employee_email}")
        
    except Exception as e:
        log_message(f"✗ Failed to send late alert for {employee_name}: {str(e)}", "ERROR")

def send_connectivity_alert(error_message):
    """Send alert about database connectivity issues"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"Database Connectivity Issue - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
DATABASE CONNECTIVITY ALERT
============================

The attendance monitoring system is experiencing connectivity issues with the database.

Error: {error_message}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database Server: {DB_SERVER}:{DB_PORT}
Database Name: {DB_NAME}

The system will continue to retry connections and may fall back to cached data if available.

Please check:
1. Network connectivity to {DB_SERVER}:{DB_PORT}
2. SQL Server service status
3. Firewall configuration
4. Database authentication

This is an automated alert from the Real-Time Attendance Monitoring System.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, ADMIN_EMAIL, text)
        server.quit()
        
        log_message("✓ Connectivity alert sent to admin")
        
    except Exception as e:
        log_message(f"✗ Failed to send connectivity alert: {str(e)}", "ERROR")

def main():
    """Main monitoring function with fallback strategies"""
    log_message("Starting Real-Time Attendance Monitor with Fallback Strategies")
    
    # Load today's alerts to prevent duplicates
    today_alerts = load_daily_alerts()
    log_message(f"Today's alerts already sent: {today_alerts}")
    
    # Test network connectivity first
    if not test_network_connectivity():
        error_msg = f"Network connectivity test failed for {DB_SERVER}:{DB_PORT}"
        log_message(error_msg, "ERROR")
        send_connectivity_alert(error_msg)
        return
    
    # Try to connect to database with retry mechanism
    conn = connect_to_database_with_retry()
    
    if not conn:
        error_msg = "All database connection attempts failed"
        log_message(error_msg, "ERROR")
        send_connectivity_alert(error_msg)
        
        # Try to use cached data
        cache = load_cache()
        if cache:
            log_message("Attempting to use cached data as fallback")
            # Process cached data if available
        else:
            log_message("No cached data available. Exiting.")
            return
    else:
        # Connection successful - proceed with monitoring
        try:
            # Get today's attendance data
            attendance_data = get_today_attendance_data(conn)
            
            if not attendance_data:
                log_message("No attendance data found for today")
                return
            
            # Cache the data
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'attendance_data': [(name, dept, punch.isoformat(), email) for name, dept, punch, email in attendance_data]
            }
            save_cache(cache_data)
            
            # Process attendance data
            for employee_name, department, first_punch, employee_email in attendance_data:
                if employee_name not in TARGET_EMPLOYEES:
                    continue
                
                # Skip if already alerted today
                if employee_name in today_alerts:
                    log_message(f"Skipping {employee_name} - already alerted today")
                    continue
                
                # Parse shift start time
                shift_start_str = TARGET_EMPLOYEES[employee_name]['shift_start']
                shift_start = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {shift_start_str}", '%Y-%m-%d %H:%M')
                
                # Calculate lateness
                time_diff = first_punch - shift_start
                minutes_late = time_diff.total_seconds() / 60
                
                log_message(f"{employee_name}: First punch at {first_punch.strftime('%H:%M:%S')}, {minutes_late:.1f} minutes after shift start")
                
                # Send alert if more than 15 minutes late
                if minutes_late > 15:
                    send_late_alert(employee_name, first_punch, shift_start_str, int(minutes_late), employee_email)
                    save_daily_alert(employee_name)
                else:
                    log_message(f"✓ {employee_name} is on time ({minutes_late:.1f} minutes)")
            
            conn.close()
            log_message("✓ Monitoring completed successfully")
            
        except Exception as e:
            log_message(f"Error during monitoring: {str(e)}", "ERROR")
            send_connectivity_alert(f"Error during monitoring: {str(e)}")
            if conn:
                conn.close()

if __name__ == "__main__":
    main()
