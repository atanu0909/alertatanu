# Database Connectivity Issues - Troubleshooting Guide

## Current Status
The attendance monitoring system is experiencing **login timeout errors** when connecting to the SQL Server database from GitHub Actions runners. This is a common issue when the database server is not accessible from the public internet.

## Problem Analysis
- **Error**: `Login timeout expired` when connecting to `1.22.45.168:19471`
- **Cause**: The SQL Server port may be blocked by firewall or not configured for remote access
- **Environment**: GitHub Actions runners are trying to connect from various public IP addresses

## Immediate Solutions

### 1. Test Connectivity Locally
First, run the diagnostic script to confirm the issue:

```bash
# Install required packages
pip install pymssql pandas requests

# Run the diagnostic script
python troubleshoot_connectivity.py
```

### 2. Network Administrator Actions Required
Contact your network administrator to:

1. **Open SQL Server Port**
   - Ensure port `19471` is open for inbound connections
   - Check both Windows Firewall and router/gateway firewall

2. **SQL Server Configuration**
   - Enable TCP/IP protocol in SQL Server Configuration Manager
   - Verify SQL Server is listening on port 19471
   - Enable SQL Server Authentication mode

3. **GitHub Actions IP Ranges**
   - Whitelist GitHub Actions runner IP ranges (see below)
   - Or consider using a VPN/proxy solution

### 3. GitHub Actions IP Ranges
GitHub Actions runners use dynamic IP addresses. You may need to whitelist these IP ranges:

```
# GitHub Actions IP ranges (updated regularly)
# Check: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses

# Example ranges (these change frequently):
140.82.112.0/20
185.199.108.0/22
192.30.252.0/22
```

## Alternative Solutions

### Option 1: Database Proxy/VPN
Set up a database proxy or VPN that GitHub Actions can connect to:

1. **Azure SQL Database**: Migrate to Azure SQL with firewall rules
2. **AWS RDS**: Use AWS RDS with security groups
3. **VPN Gateway**: Set up a VPN endpoint for GitHub Actions

### Option 2: Webhook-Based System
Instead of polling from GitHub Actions, use webhooks:

1. Set up a local service that monitors the database
2. Use GitHub webhooks to trigger monitoring
3. Local service sends alerts via email

### Option 3: Scheduled Local Script
Run the monitoring script locally on a server with database access:

1. Set up a local server/VM with database access
2. Use Windows Task Scheduler or cron to run every 5 minutes
3. Use the existing monitoring script

## Testing Commands

### Test Network Connectivity
```bash
# Test if port is open (replace IP/port)
telnet 1.22.45.168 19471

# Or use PowerShell (Windows)
Test-NetConnection -ComputerName 1.22.45.168 -Port 19471
```

### Test SQL Server Connection
```bash
# Using sqlcmd (if available)
sqlcmd -S 1.22.45.168,19471 -U sa -P YourPassword -d MainDb -Q "SELECT @@VERSION"
```

### Test from GitHub Actions
The diagnostic script can be run in GitHub Actions to get the runner's IP:

```yaml
- name: Test Database Connectivity
  run: python troubleshoot_connectivity.py
```

## Recommended Immediate Actions

1. **Run Local Diagnostic**
   ```bash
   python troubleshoot_connectivity.py
   ```

2. **Check SQL Server Status**
   - Verify SQL Server service is running
   - Check SQL Server Configuration Manager
   - Review SQL Server error logs

3. **Firewall Configuration**
   - Windows Firewall: Allow port 19471
   - Router/Gateway: Port forwarding for 19471
   - Network firewall: Allow inbound connections

4. **Contact Network Admin**
   - Share this guide with your network administrator
   - Request firewall configuration changes
   - Discuss alternative solutions

## Files Created for Troubleshooting

1. **`troubleshoot_connectivity.py`**: Comprehensive diagnostic script
2. **`monitor_fallback.py`**: Enhanced monitor with retry logic and fallback strategies
3. **This guide**: Step-by-step troubleshooting instructions

## Next Steps

1. Run the diagnostic script locally to confirm the issue
2. Work with your network administrator to resolve firewall/connectivity issues
3. Consider alternative deployment strategies if direct database access cannot be enabled
4. Test the fallback monitor script once connectivity is resolved

## Support

If you need additional help:
1. Share the diagnostic script output
2. Provide SQL Server configuration details
3. Confirm network topology and firewall settings
4. Consider scheduling a technical review with your IT team

The monitoring system is ready to work once the connectivity issue is resolved!
