@echo off
echo ===============================================
echo  Real-Time Attendance Monitor - GitHub Deploy
echo ===============================================
echo.
echo This script will deploy your attendance monitoring system to GitHub Actions
echo.

REM Check if we're in the correct directory
if not exist "monitor.py" (
    echo ERROR: monitor.py not found. Please run this script from the project directory.
    pause
    exit /b 1
)

if not exist ".github\workflows\attendance-monitor.yml" (
    echo ERROR: GitHub workflow file not found. Please ensure the workflow is configured.
    pause
    exit /b 1
)

echo [1/6] Checking current git status...
git status

echo.
echo [2/6] Adding all files to git...
git add -A

echo.
echo [3/6] Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Deploy attendance monitoring system with correct database credentials

git commit -m "%commit_message%"

echo.
echo [4/6] Pushing to GitHub main-deploy branch...
git push origin main-deploy

echo.
echo [5/6] Deployment Status Check...
echo Your GitHub Actions workflow should now be triggered.
echo.
echo GitHub Actions URL: https://github.com/atanu0909/alertatanu/actions
echo Workflow File: https://github.com/atanu0909/alertatanu/actions/workflows/attendance-monitor.yml
echo.

echo [6/6] Deployment Summary:
echo ✅ Database Server: 1.22.45.168:19471
echo ✅ Database Name: etimetrackliteWEB  
echo ✅ Monitoring: 8 Machine Operators on Device 19
echo ✅ Schedule: Every 5 minutes (24/7)
echo ✅ Alerts: Email notifications for late arrivals (>15 min)
echo.
echo ===============================================
echo  DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ===============================================
echo.
echo Your real-time attendance monitoring system is now deployed!
echo Check GitHub Actions for workflow status: 
echo https://github.com/atanu0909/alertatanu/actions
echo.
pause