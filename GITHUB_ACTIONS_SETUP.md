# GitHub Actions Secrets Setup Guide

## Required Secrets for Real-Time Attendance Monitor

### Database Configuration
- **DB_SERVER**: `1.22.45.168`
- **DB_PORT**: `19471`
- **DB_NAME**: `etimetrackliteWEB`
- **DB_USER**: `sa`
- **DB_PASSWORD**: `sa@123`

### Email Configuration
- **EMAIL_USER**: `aghosh09092004@gmail.com`
- **EMAIL_PASSWORD**: `your_gmail_app_password`
- **ADMIN_EMAIL**: `aghosh09092004@gmail.com`

## How to Set Up GitHub Actions Secrets

1. **Go to your GitHub repository**: https://github.com/atanu0909/alertatanu
2. **Navigate to Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"**
4. **Add each secret** with the exact name and value as shown above

## Gmail App Password Setup

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to **Security** → **2-Step Verification** → **App passwords**
4. Generate a new app password for "Mail"
5. Use this password as `EMAIL_PASSWORD` secret

## Employee Email Addresses

The system is configured to monitor these 8 employees:
- Swarup Mahapatra (Code: 3) - swarup.mahapatra@company.com
- Santanu Das (Code: 595) - santanu.das@company.com  
- Rohit Kabiraj (Code: 593) - rohit.kabiraj@company.com
- Soumen Ghoshal (Code: 695) - soumen.ghoshal@company.com
- Souvik Ghosh (Code: 641) - souvik.ghosh@company.com
- Manoj Maity (Code: 744) - manoj.maity@company.com
- Bablu Rajak (Code: 20) - bablu.rajak@company.com
- Somen Bhattacharjee (Code: 18) - somen.bhattacharjee@company.com

## System Features

✅ **Real-time monitoring**: Runs every 5 minutes (24/7)
✅ **Device 19 monitoring**: Checks punches on Device 19 only
✅ **15-minute threshold**: Alerts for >15 minutes late
✅ **Duplicate prevention**: Won't send multiple alerts for same employee/day
✅ **Absent detection**: Alerts for missing employees
✅ **Beautiful email alerts**: HTML formatted with company branding
✅ **Persistent tracking**: Maintains alert history across runs

## Deployment Steps

1. **Set up all GitHub secrets** (as listed above)
2. **Push the code** to your repository
3. **GitHub Actions will automatically start running**
4. **Monitor the Actions tab** for execution logs
5. **Check your email** for late arrival alerts

## Monitoring

- **GitHub Actions tab**: View execution logs and status
- **Email alerts**: Receive real-time notifications
- **Alert file**: `alerted_employees.json` tracks sent alerts
- **Logs**: Check workflow runs for detailed monitoring info

## Testing

To test the system:
1. Manually trigger the workflow from GitHub Actions
2. Check the logs to see if database connection works
3. Verify email configuration by checking for test runs
4. Monitor during actual shift times for real alerts

## Support

For issues or modifications, contact: aghosh09092004@gmail.com
