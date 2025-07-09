#!/usr/bin/env python3
"""
GitHub Actions Real-Time Attendance Monitor
Monitors 8 machine operators on Device 19 and sends instant alerts for late arrivals
Runs every 5 minutes in GitHub Actions for 24/7 monitoring

Author: Atanu Ghosh
"""

import pymssql
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, time, timedelta
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubActionsAttendanceMonitor:
    def __init__(self):
        """Initialize the GitHub Actions attendance monitoring system"""
        self.late_threshold_minutes = 15
        
        # 8 Machine Operators with expected start times and email addresses
        self.employees = [
            {
                'name': 'Swarup Mahapatra', 
                'code': '3', 
                'machine': 'Ryobi 3', 
                'expected': '09:30',
                'email': 'swarup.mahapatra@company.com'
            },
            {
                'name': 'Santanu Das', 
                'code': '595', 
                'machine': 'Ryobi 3', 
                'expected': '09:00',
                'email': 'santanu.das@company.com'
            },
            {
                'name': 'Rohit Kabiraj', 
                'code': '593', 
                'machine': 'Ryobi 3', 
                'expected': '09:00',
                'email': 'rohit.kabiraj@company.com'
            },
            {
                'name': 'Soumen Ghoshal', 
                'code': '695', 
                'machine': 'Ryobi 2', 
                'expected': '09:00',
                'email': 'soumen.ghoshal@company.com'
            },
            {
                'name': 'Souvik Ghosh', 
                'code': '641', 
                'machine': 'Ryobi 2', 
                'expected': '08:30',
                'email': 'souvik.ghosh@company.com'
            },
            {
                'name': 'Manoj Maity', 
                'code': '744', 
                'machine': 'Ryobi 2', 
                'expected': '08:30',
                'email': 'manoj.maity@company.com'
            },
            {
                'name': 'Bablu Rajak', 
                'code': '20', 
                'machine': 'Flat Bed', 
                'expected': '09:30',
                'email': 'bablu.rajak@company.com'
            },
            {
                'name': 'Somen Bhattacharjee', 
                'code': '18', 
                'machine': 'Flat Bed', 
                'expected': '09:00',
                'email': 'somen.bhattacharjee@company.com'
            }
        ]
        
        # Database configuration from GitHub Secrets
        self.db_server = os.getenv('DB_SERVER', '1.22.45.168')
        self.db_port = int(os.getenv('DB_PORT', '19471'))
        self.db_name = os.getenv('DB_NAME', 'etimetrackliteWEB')
        self.db_user = os.getenv('DB_USER', 'sa')
        self.db_password = os.getenv('DB_PASSWORD', 'sa@123')
        
        # Email configuration from GitHub Secrets
        self.email_user = os.getenv('EMAIL_USER', 'atanughosh323@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your_app_password')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'atanughosh323@gmail.com')
        
        # File to track alerted employees (persistent across runs)
        self.alert_file = 'alerted_employees.json'
        
        logger.info("🚀 GitHub Actions Attendance Monitor initialized")
        logger.info(f"Monitoring {len(self.employees)} employees")

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
            logger.info("✅ Database connection successful")
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None

    def get_current_month_table(self):
        """Get current month's device logs table name"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        return f"dbo.DeviceLogs_{current_month}_{current_year}"

    def load_alerted_employees(self):
        """Load today's alerted employees from file"""
        try:
            if os.path.exists(self.alert_file):
                with open(self.alert_file, 'r') as f:
                    data = json.load(f)
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    return set(data.get(today_str, []))
            return set()
        except Exception as e:
            logger.error(f"Error loading alerted employees: {e}")
            return set()

    def save_alerted_employees(self, alerted_today):
        """Save today's alerted employees to file"""
        try:
            # Load existing data
            data = {}
            if os.path.exists(self.alert_file):
                with open(self.alert_file, 'r') as f:
                    data = json.load(f)
            
            # Update today's data
            today_str = datetime.now().strftime('%Y-%m-%d')
            data[today_str] = list(alerted_today)
            
            # Keep only last 7 days of data
            cutoff_date = datetime.now() - timedelta(days=7)
            data = {k: v for k, v in data.items() if datetime.strptime(k, '%Y-%m-%d') >= cutoff_date}
            
            # Save updated data
            with open(self.alert_file, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.error(f"Error saving alerted employees: {e}")

    def calculate_lateness_minutes(self, expected_time_str, actual_time_str):
        """Calculate lateness in minutes"""
        try:
            expected_time = datetime.strptime(expected_time_str, '%H:%M').time()
            
            # Handle different time formats
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
            logger.error(f"Error calculating lateness: {e}")
            return None

    def send_late_alert(self, employee, lateness_minutes, punch_time):
        """Send email alert for late arrival"""
        try:
            subject = f"🚨 LATE ARRIVAL ALERT - {employee['name']} ({employee['machine']})"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #dc3545; text-align: center;">⚠️ LATE ARRIVAL ALERT</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Employee Details:</h3>
                        <p><strong>Name:</strong> {employee['name']}</p>
                        <p><strong>Employee Code:</strong> {employee['code']}</p>
                        <p><strong>Machine:</strong> {employee['machine']}</p>
                        <p><strong>Expected Time:</strong> {employee['expected']}</p>
                        <p><strong>Actual Punch Time:</strong> {punch_time}</p>
                        <p><strong>Lateness:</strong> <span style="color: #dc3545; font-weight: bold; font-size: 18px;">{lateness_minutes:.1f} minutes</span></p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                        <p><strong>Alert Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                        <p><strong>Device:</strong> Device 19</p>
                    </div>
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <h4 style="color: #0c5460; margin-top: 0;">Immediate Actions Required:</h4>
                        <ul style="color: #0c5460;">
                            <li>Document the late arrival in attendance records</li>
                            <li>Follow up with the employee regarding punctuality</li>
                            <li>Review recent attendance patterns</li>
                            <li>Ensure machine operation is not affected</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p style="color: #6c757d; font-size: 14px;">
                            🤖 This is an automated alert from the Real-Time Attendance Monitor<br>
                            System runs every 5 minutes for continuous monitoring
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            
            # If you want to CC the employee (uncomment below)
            # msg['Cc'] = employee['email']
            
            # Attach HTML body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Late alert sent for {employee['name']} ({lateness_minutes:.1f} min late)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")
            return False

    def send_absent_alert(self, employee, minutes_past_expected):
        """Send alert for absent employee"""
        try:
            subject = f"🚨 ABSENT ALERT - {employee['name']} ({employee['machine']})"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #dc3545; text-align: center;">⚠️ ABSENT EMPLOYEE ALERT</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Employee Details:</h3>
                        <p><strong>Name:</strong> {employee['name']}</p>
                        <p><strong>Employee Code:</strong> {employee['code']}</p>
                        <p><strong>Machine:</strong> {employee['machine']}</p>
                        <p><strong>Expected Time:</strong> {employee['expected']}</p>
                        <p><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold; font-size: 18px;">ABSENT</span></p>
                        <p><strong>Minutes Past Expected:</strong> <span style="color: #dc3545; font-weight: bold;">{minutes_past_expected:.1f} minutes</span></p>
                    </div>
                    
                    <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">
                        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                        <p><strong>Alert Time:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                        <p><strong>Device Checked:</strong> Device 19</p>
                    </div>
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <h4 style="color: #0c5460; margin-top: 0;">🚨 URGENT Actions Required:</h4>
                        <ul style="color: #0c5460;">
                            <li><strong>Contact the employee immediately</strong></li>
                            <li>Arrange for machine coverage ({employee['machine']})</li>
                            <li>Document the absence in attendance records</li>
                            <li>Check if this is planned or unplanned absence</li>
                            <li>Review backup operator availability</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p style="color: #6c757d; font-size: 14px;">
                            🤖 This is an automated alert from the Real-Time Attendance Monitor<br>
                            System runs every 5 minutes for continuous monitoring
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = self.admin_email
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Absent alert sent for {employee['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send absent alert: {e}")
            return False

    def check_attendance(self):
        """Check attendance for all 8 employees"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            today = datetime.now().date()
            table_name = self.get_current_month_table()
            
            # Load previously alerted employees
            alerted_today = self.load_alerted_employees()
            
            employee_codes = [emp['code'] for emp in self.employees]
            employee_codes_str = "', '".join(employee_codes)
            
            # Query for today's first punch times from Device 19
            query = f"""
            SELECT 
                CAST(dl.UserId as varchar) as EmployeeCode,
                MIN(CAST(dl.LogDate as TIME)) as FirstPunchTime
            FROM {table_name} dl
            WHERE CAST(dl.LogDate as DATE) = '{today}'
                AND CAST(dl.UserId as varchar) IN ('{employee_codes_str}')
                AND dl.DeviceId = 19
            GROUP BY CAST(dl.UserId as varchar)
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert to dictionary for easy lookup
            punch_data = {}
            for row in results:
                punch_data[row[0]] = str(row[1])
            
            logger.info(f"📊 Found {len(punch_data)} employees with punches today on Device 19")
            
            # Check each employee
            alerts_sent = 0
            for emp in self.employees:
                emp_code = emp['code']
                emp_name = emp['name']
                expected_time = emp['expected']
                
                # Skip if already alerted today
                if emp_code in alerted_today:
                    logger.info(f"⏭️ Skipping {emp_name} - already alerted today")
                    continue
                
                # Check if employee punched in
                if emp_code in punch_data:
                    first_punch = punch_data[emp_code]
                    lateness = self.calculate_lateness_minutes(expected_time, first_punch)
                    
                    if lateness is not None and lateness > self.late_threshold_minutes:
                        # Employee is late - send alert
                        logger.warning(f"🚨 LATE: {emp_name} ({emp_code}) - {lateness:.1f} minutes late")
                        
                        if self.send_late_alert(emp, lateness, first_punch):
                            alerted_today.add(emp_code)
                            alerts_sent += 1
                    elif lateness is not None:
                        status = "early" if lateness < 0 else "slightly late"
                        logger.info(f"✅ ON TIME: {emp_name} ({emp_code}) - {abs(lateness):.1f} minutes {status}")
                else:
                    # Check if employee should have already arrived
                    current_time = datetime.now().time()
                    expected_dt = datetime.strptime(expected_time, '%H:%M').time()
                    
                    # Calculate minutes since expected time
                    now_dt = datetime.combine(today, current_time)
                    expected_full_dt = datetime.combine(today, expected_dt)
                    minutes_since_expected = (now_dt - expected_full_dt).total_seconds() / 60
                    
                    if minutes_since_expected > self.late_threshold_minutes:
                        # Employee is absent and late
                        logger.warning(f"🚨 ABSENT: {emp_name} ({emp_code}) - {minutes_since_expected:.1f} minutes past expected")
                        
                        if self.send_absent_alert(emp, minutes_since_expected):
                            alerted_today.add(emp_code)
                            alerts_sent += 1
                    elif minutes_since_expected > 0:
                        logger.info(f"⏳ WAITING: {emp_name} ({emp_code}) - {minutes_since_expected:.1f} minutes past expected (within threshold)")
            
            # Save updated alerted employees
            self.save_alerted_employees(alerted_today)
            
            logger.info(f"📋 Monitoring complete - {alerts_sent} alerts sent")
            
        except Exception as e:
            logger.error(f"❌ Error checking attendance: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()

def main():
    """Main function for GitHub Actions"""
    logger.info("🚀 Starting Real-Time Attendance Monitor")
    
    monitor = GitHubActionsAttendanceMonitor()
    monitor.check_attendance()
    
    logger.info("✅ Monitoring cycle completed")

if __name__ == "__main__":
    main()
