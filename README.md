# Real-Time Attendance Monitoring System

## Overview
A cloud-based real-time attendance monitoring system that tracks the first IN punch of 8 machine operators daily and sends automated email alerts for late arrivals (>15 minutes).

## Features
- ✅ **Real-time monitoring** of 8 machine operators
- ✅ **Automated email alerts** for late arrivals (>15 minutes)
- ✅ **24/7 cloud operation** on GitHub Actions
- ✅ **Smart duplicate prevention** (one alert per employee per day)
- ✅ **Comprehensive logging** for monitoring and debugging
- ✅ **Database integration** with existing attendance system
- ✅ **Professional email formatting** with company branding

## Monitored Employees

### Ryobi 3 Operators
- **Swarup Mahapatra** (Code: 3) - Shift starts: 09:30
- **Santanu Das** (Code: 595) - Shift starts: 09:30
- **Rohit Kabiraj** (Code: 593) - Shift starts: 09:30
- **Soumen Ghoshal** (Code: 695) - Shift starts: 09:30
- **Souvik Ghosh** (Code: 641) - Shift starts: 09:30

### Ryobi 2 Operators
- **Manoj Maity** (Code: 744) - Shift starts: 09:30

### Flat Bed Operators
- **Bablu Rajak** (Code: 20) - Shift starts: 09:30
- **Somen Bhattacharjee** (Code: 18) - Shift starts: 09:30

### Ryobi 2 Operators
- **Soumen Ghoshal** (Code: 695) - Shift starts: 09:00
- **Souvik Ghosh** (Code: 641) - Shift starts: 08:30
- **Manoj Maity** (Code: 744) - Shift starts: 08:30

### Flat Bed Operators
- **Bablu Rajak** (Code: 20) - Shift starts: 09:30
- **Somen Bhattacharjee** (Code: 18) - Shift starts: 09:00

## Technical Architecture

### Database Integration
- **Source**: SQL Server database `etimetrackliteWEB`
- **Devices**: Monitors punch data from Device 19 and 20
- **Tables**: `DeviceLogs_MM_YYYY`, `Employees`, `ShiftGroups`, `Shifts`
- **Connection**: Uses `pymssql` for cloud compatibility

### Email System
- **Provider**: Gmail SMTP
- **Format**: Professional HTML emails with company branding
- **Authentication**: App-specific password for security
- **Duplicate Prevention**: Tracks alerted employees in database

### Cloud Platform
- **Platform**: Railway (https://railway.app)
- **Type**: Worker service (background process)
- **Monitoring**: Real-time logs and health checks
- **Cost**: ~$5-10/month for 24/7 operation

## Files Structure

```
connect/
├── cloud_monitor.py           # Main monitoring script
├── requirements.txt           # Python dependencies
├── Procfile                  # Railway process definition
├── railway.json              # Railway configuration
├── .env.example              # Environment variables template
├── deploy_to_railway.sh      # Linux/Mac deployment script
├── deploy_to_railway.ps1     # Windows PowerShell deployment script
├── RAILWAY_DEPLOYMENT_GUIDE.md # Detailed deployment guide
└── README.md                 # This file
```

## Quick Start

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Clone and Deploy
```bash
git clone <your-repo>
cd connect
./deploy_to_railway.sh  # Linux/Mac
# or
.\deploy_to_railway.ps1  # Windows PowerShell
```

### 3. Monitor
- Visit Railway dashboard to view logs
- Check email delivery
- Monitor system performance

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_SERVER` | Database server IP | `192.168.1.73` |
| `DB_PORT` | Database port | `1433` |
| `DB_NAME` | Database name | `etimetrackliteWEB` |
| `DB_USER` | Database username | `sa` |
| `DB_PASSWORD` | Database password | `sa@123` |
| `EMAIL_ENABLED` | Enable email alerts | `True` |
| `COMPANY_NAME` | Company name for emails | `Stylo Media Pvt Ltd` |
| `GMAIL_USER` | Gmail username | `your-email@gmail.com` |
| `GMAIL_PASSWORD` | Gmail app password | `your-app-password` |
| `TZ` | Timezone | `Asia/Kolkata` |

## How It Works

### 1. Continuous Monitoring
- Runs 24/7 on Railway cloud platform
- Checks attendance every 2 minutes
- Monitors specific devices (19 and 20) used by operators

### 2. Lateness Detection
- Compares first IN punch with expected shift start time
- Triggers alert only if late by more than 15 minutes
- Uses actual shift data from database

### 3. Email Alerts
- Sends professional HTML emails to late employees
- Includes detailed lateness information
- Prevents duplicate alerts (one per employee per day)

### 4. Logging and Monitoring
- Comprehensive logging for debugging
- Real-time monitoring through Railway dashboard
- Automatic restart on failure

## Sample Email Alert

```html
Subject: ATTENDANCE ALERT - Late Arrival on 2025-01-04

Dear [Employee Name],

Our records indicate that you arrived late today.

┌─────────────┬──────────────────┬─────────────────┬──────────┐
│ Date        │ Expected In Time │ Actual In Time  │ Late By  │
├─────────────┼──────────────────┼─────────────────┼──────────┤
│ 2025-01-04  │ 09:00:00        │ 09:23:45       │ 00:23    │
└─────────────┴──────────────────┴─────────────────┴──────────┘

Please ensure timely attendance in the future.

Regards,
HR Department
Stylo Media Pvt Ltd
```

## Prerequisites

1. **Install Python** (3.8 or higher)
2. **Install SQL Server ODBC Driver**:
   - Download and install "ODBC Driver 17 for SQL Server" from Microsoft
   - Or install "ODBC Driver 18 for SQL Server" for newer versions
3. **Install Dependencies**:
   ```powershell
   pip install pyodbc pandas openpyxl requests
   ```

## Real-Time Monitoring System

The system now includes a real-time monitoring component that:
- Continuously monitors the database for new punch records
- Detects when any of the 8 machine operators makes their first IN punch for the day
- Compares the punch time with their expected shift start time
- Immediately sends an email alert if they are late
- Runs as a Windows service that starts automatically on system boot

### Deployment

To deploy the real-time monitoring system:
1. Run `setup_monitor_service.bat` with administrator privileges
2. Verify installation with `check_service_status.bat`
3. Use `control_monitor_service.bat` to manage the service

See `DEPLOYMENT_GUIDE.md` and `IT_TECHNICAL_GUIDE.md` for detailed instructions.

## Attendance Alert System Scripts

### Main Scripts
- **`get_device21_employees.py`**: Main script for analyzing attendance data
- **`late_comer_notifier.py`**: Script for identifying late comers and sending alerts
- **`send_alerts.py`**: Simplified interface for sending alerts for a specific date
- **`attendance_alert.py`**: Alert logic for late/absent employees
- **`attendance_report.py`**: Generate attendance reports for any date
- **`check_attendance.py`**: Command-line tool for reporting and alerting
- **`realtime_lateness_monitor.py`**: Real-time monitoring of first IN punches

### Configuration
- **`alert_config.py`**: Configuration for email and SMS settings
- **`employee_shift_overrides.py`**: Custom shift time overrides for specific employees

### Deployment Scripts
- **`setup_monitor_service.bat`**: Installs the real-time monitor as a Windows service
- **`control_monitor_service.bat`**: Manages the monitoring service
- **`check_service_status.bat`**: Checks if the monitoring service is running

### Data Files
- **`Comprehensive_Shift_Schedule.xlsx`**: Shift schedule for employees

### Output Folders
- **`Attendance_Alert_Reports/`**: CSV reports of late and absent employees
- **`Daily_Attendance_Reports/`**: Excel reports of daily attendance

## Usage Examples

### Send Alerts for Late Comers and Absentees

```powershell
# Send alerts for a specific date
python send_alerts.py 2025-06-26

# Send alerts for the default date (June 26, 2025)
python send_alerts.py
```

### Check Attendance for a Specific Date

```powershell
# Check attendance for a specific date
python check_attendance.py 2025-06-26

# Check attendance for the default date (June 26, 2025)
python check_attendance.py
```

### Generate Attendance Report

```powershell
# Generate attendance report for a specific date
python attendance_report.py 2025-06-26
```

## Configuring Email and SMS Alerts

Before sending actual alerts, update the `alert_config.py` file with your email and SMS credentials:

1. **For email alerts**:
   - Set `EMAIL_SENDER` to your email address
   - Set `EMAIL_PASSWORD` to your email password or app password
   - Set `EMAIL_SMTP_SERVER` and `EMAIL_SMTP_PORT` according to your email provider
   - Set `ENABLE_EMAIL_ALERTS = True` to enable actual email sending

2. **For SMS alerts (using Twilio)**:
   - Set `SMS_ACCOUNT_SID`, `SMS_AUTH_TOKEN`, and `SMS_FROM_NUMBER` to your Twilio credentials
   - Set `ENABLE_SMS_ALERTS = True` to enable actual SMS sending

3. **Update company information**:
   - Set `COMPANY_NAME`, `HR_CONTACT_EMAIL`, and `HR_CONTACT_PHONE` to your company's details

## Monitored Machine Operators

The system checks attendance for the following machine operators:

### Ryobi 3
- Swarup Mahapatra (Code: 3)
- Santanu Das (Code: 595)
- Rohit Kabiraj (Code: 593)

### Ryobi 2
- Soumen Ghoshal (Code: 695)
- Souvik Ghosh (Code: 641)
- Manoj Maity (Code: 744)

### Flat Bed
- Bablu Rajak (Code: 20)
- Somen Bhattacharjee (Code: 18)

## Troubleshooting

### Common Issues

1. **"ODBC Driver not found"**:
   - Install ODBC Driver 17 or 18 for SQL Server
   - Update the driver name in connection string if needed

2. **Connection timeout**:
   - Check if SQL Server is running
   - Verify firewall settings allow port 1433
   - Ensure SQL Server Authentication is enabled

3. **Login failed**:
   - Verify username and password

4. **Missing shift information**:
   - Ensure `Comprehensive_Shift_Schedule.xlsx` is properly formatted and contains data for all employees

5. **Email/SMS sending failures**:
   - Check your email credentials and SMTP settings
   - For Gmail, use an App Password if 2FA is enabled
   - Verify Twilio credentials for SMS
   - Check if SQL Server Authentication is enabled
   - Ensure the 'sa' account is not disabled

4. **SSL/Certificate errors**:
   - The connection uses `TrustServerCertificate=yes` to bypass SSL issues
   - For production, consider proper SSL certificate setup

## Security Notes

⚠️ **Important**: This configuration contains hardcoded credentials for development purposes. For production:
- Use environment variables for sensitive data
- Implement proper connection pooling
- Use Windows Authentication when possible
- Enable SSL/TLS encryption

## Next Steps

Once connected successfully, you can:
- Explore your database schema
- Create data analysis scripts
- Build web applications
- Set up automated reporting
- Implement ETL processes

## Attendance Search Tool

The project now includes a flexible attendance search tool for finding employee attendance records based on various criteria.

### Features

- Search by employee code or name
- Search by date range
- Search by device ID
- Filter by minimum/maximum number of punches
- Generate summary statistics
- Export results to Excel

### Command Line Usage

```powershell
python search_attendance.py [options]
```

### Available Options

- `--start-date`: Start date for search (format: YYYY-MM-DD)
- `--end-date`: End date for search (format: YYYY-MM-DD)
- `--employee-codes`: List of employee codes to search for
- `--employee-names`: List of employee names to search for (partial match)
- `--devices`: List of device IDs to search for
- `--min-punches`: Minimum number of punches
- `--max-punches`: Maximum number of punches
- `--output`: Output Excel file path
- `--summary`: Show summary statistics only

### Examples

1. Search for specific employees on a specific date:
   ```powershell
   python search_attendance.py --employee-codes 18 20 --start-date 2025-06-25 --end-date 2025-06-25
   ```

2. Search for all employees using Device 21 in June 2025:
   ```powershell
   python search_attendance.py --devices 21 --start-date 2025-06-01 --end-date 2025-06-30
   ```

3. Show only summary statistics:
   ```powershell
   python search_attendance.py --employee-codes 18 20 --start-date 2025-06-01 --end-date 2025-06-30 --summary
   ```
