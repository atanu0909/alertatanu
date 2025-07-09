#!/usr/bin/env python3
"""
Real-Time Attendance Monitor for 8 Machine Operators
Monitors Device 19 and sends instant alerts for late arrivals (>15 minutes)
Author: Atanu Ghosh
"""

import pymssql
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, time
import json

# 8 Machine Operators with expected start times
EMPLOYEES = [
    {'name': 'Swarup Mahapatra', 'code': '3', 'machine': 'Ryobi 3', 'expected': '09:30', 'email': 'swarup@company.com'},
    {'name': 'Santanu Das', 'code': '595', 'machine': 'Ryobi 3', 'expected': '09:00', 'email': 'santanu@company.com'},
    {'name': 'Rohit Kabiraj', 'code': '593', 'machine': 'Ryobi 3', 'expected': '09:00', 'email': 'rohit@company.com'},
    {'name': 'Soumen Ghoshal', 'code': '695', 'machine': 'Ryobi 2', 'expected': '09:00', 'email': 'soumen@company.com'},
    {'name': 'Souvik Ghosh', 'code': '641', 'machine': 'Ryobi 2', 'expected': '08:30', 'email': 'souvik@company.com'},
    {'name': 'Manoj Maity', 'code': '744', 'machine': 'Ryobi 2', 'expected': '08:30', 'email': 'manoj@company.com'},
    {'name': 'Bablu Rajak', 'code': '20', 'machine': 'Flat Bed', 'expected': '09:30', 'email': 'bablu@company.com'},
    {'name': 'Somen Bhattacharjee', 'code': '18', 'machine': 'Flat Bed', 'expected': '09:00', 'email': 'somen@company.com'}
]

class RealTimeAttendanceMonitor:
    def __init__(self):
        self.late_threshold_minutes = 15
        
        # Database configuration
        self.db_server = os.getenv('DB_SERVER', '1.22.45.168')
        self.db_port = int(os.getenv('DB_PORT', '19471'))
        self.db_name = os.getenv('DB_NAME', 'etimetrackliteWEB')
        self.db_user = os.getenv('DB_USER', 'sa')
        self.db_password = os.getenv('DB_PASSWORD', 'sa@123')
        
        # Email configuration
        self.email_user = os.getenv('EMAIL_USER', 'atanughosh323@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your_app_password')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'atanughosh323@gmail.com')
        
        # Track already alerted employees (GitHub Actions doesn't persist between runs)
        self.alerted_employees = set()
        
    def get_db_connection(self):
        """Get database connection using pymssql"""
        try:
            conn = pymssql.connect(
                server=self.db_server,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                timeout=30
            )
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def calculate_lateness_minutes(self, expected_time_str, actual_time_str):
        """Calculate lateness in minutes"""
        try:
            expected_time = datetime.strptime(expected_time_str, '%H:%M').time()
            
            # Handle different time formats from database
            if '.' in actual_time_str:
                actual_time_str = actual_time_str.split('.')[0]
            
            try:
                actual_time = datetime.strptime(actual_time_str, '%H:%M:%S').time()
            except ValueError:
                try:
                    actual_time = datetime.strptime(actual_time_str, '%H:%M').time()
                except ValueError:
                    return None
            
            # Convert to datetime objects for comparison
            today = datetime.now().date()
            expected_dt = datetime.combine(today, expected_time)
            actual_dt = datetime.combine(today, actual_time)
            
            # Calculate lateness in minutes
            lateness_minutes = (actual_dt - expected_dt).total_seconds() / 60
            
            return lateness_minutes
        except Exception as e:
            return None
    
    def send_late_alert(self, employee, lateness_minutes, punch_time):
        """Send email alert for late arrival"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            msg['Subject'] = f"🚨 LATE ARRIVAL ALERT - {employee['name']}"
            
            body = f"""
            <html>
            <body>
                <h2>🚨 LATE ARRIVAL ALERT</h2>
                
                <p><strong>Employee:</strong> {employee['name']} (Code: {employee['code']})</p>
                <p><strong>Machine:</strong> {employee['machine']}</p>
                <p><strong>Expected Start:</strong> {employee['expected']}</p>
                <p><strong>Actual Punch:</strong> {punch_time}</p>
                <p><strong>Lateness:</strong> {lateness_minutes:.1f} minutes</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                <p><strong>Alert Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                
                <hr>
                <p><em>This is an automated alert from the Real-Time Attendance Monitor</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Alert sent for {employee['name']} - {lateness_minutes:.1f} minutes late")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send alert for {employee['name']}: {e}")
            return False
    
    def monitor_attendance(self):
        """Monitor attendance for late arrivals"""
        print(f"🔍 Real-Time Attendance Monitor Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        conn = self.get_db_connection()
        if not conn:
            print("❌ Cannot connect to database")
            return
        
        try:
            today = datetime.now().date()
            current_time = datetime.now().time()
            
            # Get current month and year for table name
            current_month = datetime.now().month
            current_year = datetime.now().year
            table_name = f"dbo.DeviceLogs_{current_month}_{current_year}"
            
            employee_codes = [emp['code'] for emp in EMPLOYEES]
            employee_codes_str = "', '".join(employee_codes)
            
            # Query to get today's first punch times
            query = f"""
            SELECT 
                CAST(dl.UserId as varchar) as EmployeeCode,
                MIN(CAST(dl.LogDate as TIME)) as FirstPunchTime,
                MIN(dl.DeviceId) as DeviceUsed
            FROM {table_name} dl
            WHERE CAST(dl.LogDate as DATE) = '{today}'
                AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
                AND dl.DeviceId = 19
            GROUP BY CAST(dl.UserId as varchar)
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            attendance_records = cursor.fetchall()
            
            print(f"📅 Monitoring Date: {today}")
            print(f"⏰ Current Time: {current_time.strftime('%H:%M:%S')}")
            print(f"📊 Found {len(attendance_records)} punch records from Device 19")
            print()
            
            # Process each employee
            for emp in EMPLOYEES:
                emp_code = emp['code']
                emp_name = emp['name']
                expected_start = emp['expected']
                
                # Check if employee has punched in today
                emp_punch = None
                for record in attendance_records:
                    if record[0] == emp_code:
                        emp_punch = record
                        break
                
                if emp_punch:
                    first_punch = str(emp_punch[1])
                    device = emp_punch[2]
                    
                    # Calculate lateness
                    lateness = self.calculate_lateness_minutes(expected_start, first_punch)
                    
                    if lateness is not None:
                        if lateness > self.late_threshold_minutes:
                            # Employee is late by more than 15 minutes
                            alert_key = f"{emp_code}_{today}"
                            
                            if alert_key not in self.alerted_employees:
                                print(f"🔴 LATE: {emp_name} (Code: {emp_code}) - {lateness:.1f}m late")
                                
                                # Send alert
                                if self.send_late_alert(emp, lateness, first_punch):
                                    self.alerted_employees.add(alert_key)
                                
                            else:
                                print(f"🔴 ALREADY ALERTED: {emp_name} (Code: {emp_code}) - {lateness:.1f}m late")
                        
                        elif lateness > 0:
                            print(f"🟡 SLIGHT DELAY: {emp_name} (Code: {emp_code}) - {lateness:.1f}m late")
                        else:
                            print(f"🟢 ON TIME: {emp_name} (Code: {emp_code}) - {abs(lateness):.1f}m early")
                    else:
                        print(f"❓ TIME ERROR: {emp_name} (Code: {emp_code}) - Invalid time format")
                else:
                    # Check if employee should have already arrived
                    expected_time = datetime.strptime(expected_start, '%H:%M').time()
                    grace_time = datetime.combine(today, expected_time)
                    grace_time = grace_time.replace(minute=grace_time.minute + self.late_threshold_minutes)
                    
                    if current_time > grace_time.time():
                        print(f"⚪ ABSENT: {emp_name} (Code: {emp_code}) - No punch found (Expected: {expected_start})")
                    else:
                        print(f"⏳ WAITING: {emp_name} (Code: {emp_code}) - Expected: {expected_start}")
            
            print()
            print("=" * 70)
            print("✅ Monitoring cycle completed")
            
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()

def main():
    monitor = RealTimeAttendanceMonitor()
    monitor.monitor_attendance()

if __name__ == "__main__":
    main()
