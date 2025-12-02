# BARQ Fleet Management - Administrator Guide

## Overview

Complete administrator guide for BARQ Fleet Management System. This guide covers system configuration, user management, security settings, monitoring, and maintenance.

---

## Table of Contents

1. [Admin Dashboard](#admin-dashboard)
2. [User Management](#user-management)
3. [Role & Permission Management](#role--permission-management)
4. [System Configuration](#system-configuration)
5. [Security Settings](#security-settings)
6. [Integrations](#integrations)
7. [Monitoring & Health](#monitoring--health)
8. [Backup & Recovery](#backup--recovery)
9. [Audit Logs](#audit-logs)
10. [Maintenance](#maintenance)

---

## Admin Dashboard

### Accessing Admin Panel

1. Log in with admin credentials
2. Navigate to **Admin** in the main menu
3. View admin dashboard

### Admin Dashboard Overview

The admin dashboard provides:
- **System Health:** Server status, database connection, cache status
- **User Statistics:** Total users, active sessions, recent signups
- **System Metrics:** API requests, error rates, response times
- **Quick Actions:** Create user, backup database, view logs
- **Alerts:** System warnings, failed jobs, security alerts

---

## User Management

### Creating a User

1. Go to **Admin → Users**
2. Click **"+ Create User"**
3. Fill in user details:
   - Email
   - Full Name
   - Role
   - Phone Number
   - Department (optional)
4. Set password or send invitation email
5. Assign permissions (or use role defaults)
6. Click **"Create User"**

### Managing Users

**View User Details:**
1. Go to **Admin → Users**
2. Click on user name
3. View:
   - Profile information
   - Role and permissions
   - Login history
   - Activity log
   - Assigned resources

**Edit User:**
1. Open user profile
2. Click **"Edit"**
3. Modify information
4. Click **"Save Changes"**

**Deactivate User:**
1. Open user profile
2. Click **"Actions" → "Deactivate"**
3. Provide reason
4. Confirm deactivation
5. User is logged out immediately

**Reset User Password:**
1. Open user profile
2. Click **"Reset Password"**
3. Choose option:
   - Send reset email
   - Generate temporary password
4. Confirm

**Unlock Locked Account:**
1. Go to **Admin → Users → Locked Accounts**
2. Find locked user
3. Click **"Unlock"**
4. Add note explaining unlock reason
5. Confirm

### Bulk Operations

**Import Users:**
1. Go to **Admin → Users → Import**
2. Download CSV template
3. Fill template with user data
4. Upload CSV file
5. Review import preview
6. Click **"Import Users"**

**Export Users:**
1. Go to **Admin → Users**
2. Apply filters if needed
3. Click **"Export"**
4. Select format (CSV, Excel)
5. Download file

---

## Role & Permission Management

### Understanding Roles

BARQ uses Role-Based Access Control (RBAC):

| Role | Description | Default Permissions |
|------|-------------|-------------------|
| **Super Admin** | Full system access | All permissions |
| **Admin** | System administrator | Most permissions |
| **Manager** | Department manager | Department-specific |
| **Supervisor** | Team supervisor | Team-specific |
| **User** | Standard employee | Limited access |
| **Courier** | Delivery personnel | Mobile app only |

### Creating a Role

1. Navigate to **Admin → Roles**
2. Click **"+ Create Role"**
3. Enter role details:
   - Role Name
   - Description
   - Department (optional)
4. Assign permissions:
   - Fleet Management
   - HR Management
   - Operations
   - Analytics
   - Admin Functions
5. Set permission levels:
   - Read
   - Write
   - Delete
   - Admin
6. Click **"Create Role"**

### Permission Structure

Permissions follow a resource:action format:

```
fleet:couriers:read
fleet:couriers:write
fleet:couriers:delete
fleet:vehicles:read
hr:leave:approve
operations:deliveries:create
admin:users:manage
```

### Assigning Roles

**To Individual User:**
1. Go to **Admin → Users**
2. Open user profile
3. Click **"Edit Roles"**
4. Select role(s)
5. Click **"Save"**

**Bulk Role Assignment:**
1. Go to **Admin → Users**
2. Select multiple users (checkbox)
3. Click **"Bulk Actions" → "Assign Role"**
4. Select role
5. Confirm

### Custom Permissions

**Override Role Permissions:**
1. Open user profile
2. Go to **"Permissions"** tab
3. Click **"Customize Permissions"**
4. Add/remove specific permissions
5. Click **"Save"**

---

## System Configuration

### General Settings

**Access General Settings:**
1. Navigate to **Admin → Settings → General**
2. Configure:
   - Company Name
   - System Email
   - Timezone
   - Date Format
   - Currency
   - Default Language

### Email Configuration

1. Go to **Admin → Settings → Email**
2. Configure SMTP:
   - SMTP Host
   - SMTP Port
   - Username
   - Password
   - Encryption (TLS/SSL)
3. Set email templates:
   - Welcome Email
   - Password Reset
   - Notifications
4. Test email configuration
5. Click **"Save Settings"**

### Notification Settings

1. Navigate to **Admin → Settings → Notifications**
2. Configure notification channels:
   - Email
   - SMS
   - Push Notifications
   - In-App
3. Set notification rules:
   - Delivery Status Changes
   - Approval Requests
   - System Alerts
4. Configure notification templates
5. Click **"Save"**

### Business Rules

**Configure Business Hours:**
1. Go to **Admin → Settings → Business Rules**
2. Set operating hours:
   - Working Days
   - Start Time
   - End Time
   - Break Times
3. Configure holidays
4. Set overtime rules
5. Click **"Save"**

**Leave Policies:**
1. Go to **Admin → Settings → HR → Leave Policies**
2. Configure leave types:
   - Annual Leave (days per year)
   - Sick Leave (days per year)
   - Emergency Leave
3. Set approval workflow
4. Configure accrual rules
5. Click **"Save"**

**Salary Structure:**
1. Go to **Admin → Settings → HR → Salary**
2. Configure components:
   - Basic Salary
   - Allowances
   - Deductions
3. Set calculation formulas
4. Configure payment schedule
5. Click **"Save"**

---

## Security Settings

### Authentication Settings

**Password Policy:**
1. Navigate to **Admin → Security → Password Policy**
2. Configure requirements:
   - Minimum length (default: 8)
   - Require uppercase
   - Require lowercase
   - Require numbers
   - Require special characters
   - Password expiry (days)
   - Password history (prevent reuse)
3. Click **"Save Policy"**

**Two-Factor Authentication (2FA):**
1. Go to **Admin → Security → 2FA**
2. Enable 2FA:
   - Optional for all users
   - Mandatory for admin roles
   - Mandatory for all users
3. Choose 2FA method:
   - SMS
   - Authenticator App (TOTP)
   - Email
4. Click **"Save Settings"**

**Session Management:**
1. Go to **Admin → Security → Sessions**
2. Configure:
   - Session timeout (minutes)
   - Maximum concurrent sessions
   - Remember me duration (days)
   - Force logout on password change
3. Click **"Save"**

### IP Whitelisting

1. Navigate to **Admin → Security → IP Whitelist**
2. Click **"+ Add IP Range"**
3. Enter:
   - IP Address or CIDR range
   - Description
   - Active/Inactive
4. Click **"Add"**

**Note:** Be careful with IP whitelisting. Ensure you don't lock yourself out!

### API Keys

**Create API Key:**
1. Go to **Admin → Security → API Keys**
2. Click **"+ Generate API Key"**
3. Configure:
   - Key Name
   - Description
   - Scopes/Permissions
   - Expiration Date
   - Rate Limit
4. Click **"Generate"**
5. **IMPORTANT:** Copy the key immediately (shown only once)

**Manage API Keys:**
1. Go to **Admin → Security → API Keys**
2. View all API keys
3. Actions:
   - View usage statistics
   - Rotate key
   - Revoke key
   - Adjust rate limits

### Audit & Compliance

**Enable Audit Logging:**
1. Go to **Admin → Security → Audit**
2. Configure audit settings:
   - Log all user actions
   - Log API requests
   - Log admin actions
   - Log failed login attempts
   - Retention period (days)
3. Click **"Save Settings"**

**GDPR Compliance:**
1. Go to **Admin → Security → GDPR**
2. Enable features:
   - Data export requests
   - Data deletion requests
   - Cookie consent
   - Privacy policy acceptance
3. Configure retention policies
4. Click **"Save"**

---

## Integrations

### Third-Party Integrations

**Google OAuth:**
1. Navigate to **Admin → Integrations → Google**
2. Enter credentials:
   - Client ID
   - Client Secret
3. Configure:
   - Allowed domains
   - Auto-create users
   - Default role for new users
4. Test connection
5. Click **"Save Integration"**

**Email Service (SendGrid/SES):**
1. Go to **Admin → Integrations → Email**
2. Select provider
3. Enter API credentials
4. Configure sender email
5. Test integration
6. Click **"Save"**

**SMS Provider:**
1. Go to **Admin → Integrations → SMS**
2. Select provider (Twilio, etc.)
3. Enter API credentials
4. Configure sender number
5. Test SMS
6. Click **"Save"**

**Payment Gateway:**
1. Navigate to **Admin → Integrations → Payments**
2. Select provider
3. Enter merchant credentials
4. Configure:
   - Currency
   - Webhook URL
   - Test/Live mode
5. Test integration
6. Click **"Save"**

### Webhooks

**Configure Webhooks:**
1. Go to **Admin → Integrations → Webhooks**
2. Click **"+ Add Webhook"**
3. Enter details:
   - Name
   - URL
   - Secret Key
   - Events to subscribe:
     - delivery.created
     - delivery.completed
     - user.created
     - etc.
4. Configure retry policy
5. Test webhook
6. Click **"Save"**

**Monitor Webhooks:**
1. Go to **Admin → Integrations → Webhooks**
2. View webhook logs:
   - Request/Response
   - Success/Failure
   - Retry attempts
3. Replay failed webhooks

---

## Monitoring & Health

### System Health Dashboard

1. Navigate to **Admin → Monitoring → Health**
2. View system status:
   - API Server: ✅ Healthy
   - Database: ✅ Connected
   - Redis Cache: ✅ Running
   - Background Jobs: ✅ Processing
3. View metrics:
   - CPU Usage
   - Memory Usage
   - Disk Space
   - Network I/O

### Performance Monitoring

**View Performance Metrics:**
1. Go to **Admin → Monitoring → Performance**
2. View charts:
   - API Response Times
   - Request Rate
   - Error Rate
   - Database Query Times
3. Filter by:
   - Time range
   - Endpoint
   - Status code

**Set Performance Alerts:**
1. Go to **Admin → Monitoring → Alerts**
2. Click **"+ Create Alert"**
3. Configure:
   - Metric to monitor
   - Threshold value
   - Alert recipients
   - Alert channels (Email, SMS, Slack)
4. Click **"Create Alert"**

### Error Monitoring

**View Error Logs:**
1. Navigate to **Admin → Monitoring → Errors**
2. View recent errors:
   - Error message
   - Timestamp
   - User/API
   - Stack trace
3. Filter/search errors
4. Mark as resolved

**Error Notifications:**
Admins receive notifications for:
- 500 errors
- Database connection failures
- API timeouts
- Background job failures

---

## Backup & Recovery

### Automated Backups

**Configure Automated Backups:**
1. Go to **Admin → Backup → Settings**
2. Configure backup schedule:
   - Frequency (Daily, Weekly)
   - Time (e.g., 3:00 AM)
   - Retention (30 days)
3. Select backup location:
   - Cloud Storage (GCS, S3)
   - Local Storage
4. Enable encryption
5. Click **"Save Settings"**

### Manual Backup

**Create Manual Backup:**
1. Navigate to **Admin → Backup**
2. Click **"Create Backup Now"**
3. Select:
   - Full backup
   - Database only
   - Files only
4. Add description/label
5. Click **"Create Backup"**
6. Monitor progress

**Download Backup:**
1. Go to **Admin → Backup → History**
2. Find backup
3. Click **"Download"**
4. Enter admin password for verification
5. Download file

### Restore from Backup

**IMPORTANT:** Only perform restoration in maintenance mode or after hours.

1. Navigate to **Admin → Backup → Restore**
2. Select backup to restore
3. Choose restore options:
   - Full restore
   - Database only
   - Specific tables
4. Confirm (requires admin password)
5. Monitor restoration progress
6. Verify data after restoration

---

## Audit Logs

### Viewing Audit Logs

1. Go to **Admin → Audit Logs**
2. View logged activities:
   - User logins
   - Data changes
   - Admin actions
   - API requests
   - Permission changes
3. Filter by:
   - User
   - Action type
   - Resource
   - Date range

### Audit Log Details

Each audit entry contains:
- **Timestamp:** When action occurred
- **User:** Who performed the action
- **Action:** What was done
- **Resource:** What was affected
- **IP Address:** Where from
- **Changes:** Before/After values (for updates)

### Exporting Audit Logs

1. Go to **Admin → Audit Logs**
2. Apply filters
3. Click **"Export"**
4. Select format (CSV, JSON)
5. Download file

**Use Cases:**
- Compliance reporting
- Security investigations
- User activity tracking
- Troubleshooting

---

## Maintenance

### System Maintenance Mode

**Enable Maintenance Mode:**
1. Navigate to **Admin → Maintenance**
2. Click **"Enable Maintenance Mode"**
3. Configure:
   - Maintenance message
   - Estimated duration
   - Allow admin access
   - Allowed IP addresses
4. Click **"Enable"**

**Disable Maintenance Mode:**
1. Go to **Admin → Maintenance**
2. Click **"Disable Maintenance Mode"**
3. Confirm
4. Users can access system immediately

### Database Maintenance

**Run Database Optimization:**
1. Go to **Admin → Maintenance → Database**
2. View database statistics:
   - Table sizes
   - Index usage
   - Query performance
3. Click **"Optimize Tables"**
4. Monitor progress

**Clear Old Data:**
1. Navigate to **Admin → Maintenance → Cleanup**
2. Select data to clean:
   - Old audit logs (> 90 days)
   - Deleted records (soft deletes)
   - Old sessions
   - Expired tokens
3. Preview items to delete
4. Click **"Clean Up"**

### Cache Management

**Clear Cache:**
1. Go to **Admin → Maintenance → Cache**
2. Select cache to clear:
   - All cache
   - API cache
   - Session cache
   - Specific cache keys
3. Click **"Clear Cache"**

**View Cache Statistics:**
1. Navigate to **Admin → Maintenance → Cache**
2. View:
   - Hit rate
   - Memory usage
   - Top keys
   - Eviction rate

### Background Jobs

**View Job Queue:**
1. Go to **Admin → Maintenance → Jobs**
2. View jobs:
   - Pending
   - Processing
   - Completed
   - Failed
3. Actions:
   - Retry failed jobs
   - Cancel pending jobs
   - View job details

---

## Best Practices

### Security

1. **Enable 2FA** for all admin accounts
2. **Rotate API keys** every 90 days
3. **Review audit logs** weekly
4. **Update passwords** regularly
5. **Limit admin access** to necessary personnel
6. **Use IP whitelisting** for admin access
7. **Enable security alerts**

### Performance

1. **Monitor system health** daily
2. **Review performance metrics** weekly
3. **Optimize database** monthly
4. **Clear old data** regularly
5. **Update dependencies** as needed

### Backups

1. **Verify backups** weekly
2. **Test restoration** monthly
3. **Store backups** in multiple locations
4. **Encrypt sensitive backups**
5. **Document recovery procedures**

### User Management

1. **Deactivate** unused accounts
2. **Review permissions** quarterly
3. **Audit admin actions** monthly
4. **Train users** on security best practices

---

## Troubleshooting

### Common Issues

**Users Cannot Log In:**
1. Check if account is active
2. Verify password hasn't expired
3. Check if account is locked
4. Review failed login attempts
5. Verify email/username is correct

**System Performance Issues:**
1. Check system health dashboard
2. Review error logs
3. Check database performance
4. Verify cache is working
5. Check background job queue

**Integration Failures:**
1. Verify API credentials
2. Check integration logs
3. Test connection
4. Review error messages
5. Contact integration support

**Backup Failures:**
1. Check storage space
2. Verify permissions
3. Review backup logs
4. Test backup manually
5. Check backup schedule

---

## Support

For admin-level support:
- **Email:** admin-support@barq.com
- **Phone:** +966 XX XXX XXXX
- **Emergency:** +966 XX XXX XXXX (24/7)
- **Slack:** #barq-admin

---

**Version:** 1.0.0
**Last Updated:** December 2, 2025
**Maintained By:** BARQ Admin Team
