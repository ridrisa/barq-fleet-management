# BARQ Fleet Management - User Guide

**Version:** 1.0.0
**Last Updated:** November 23, 2025
**Audience:** End Users (Administrators, Managers, HR)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Roles](#user-roles)
3. [Dashboard](#dashboard)
4. [Fleet Management](#fleet-management)
5. [HR & Payroll](#hr--payroll)
6. [Operations](#operations)
7. [Accommodation](#accommodation)
8. [Workflows & Approvals](#workflows--approvals)
9. [Reports & Analytics](#reports--analytics)
10. [Support](#support)
11. [FAQ](#faq)

---

## Getting Started

### System Requirements

- **Browser:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Internet:** Stable internet connection
- **Screen Resolution:** Minimum 1280x720

### First Time Login

1. **Open BARQ Application**
   - Navigate to: https://app.barq.com
   - You'll see the login screen

2. **Login Options**

   **Option A: Email & Password**
   ```
   Email: your-email@company.com
   Password: your-password
   ```
   Click "Sign In"

   **Option B: Google Sign-In**
   - Click "Sign in with Google"
   - Select your Google account
   - Grant permissions
   - You'll be logged in automatically

3. **First Login Setup**
   - Update your profile
   - Change temporary password
   - Set up 2FA (recommended)

### Navigation

**Main Menu (Left Sidebar):**
- Dashboard
- Fleet Management
  - Couriers
  - Vehicles
  - Assignments
- HR & Finance
  - Attendance
  - Payroll
  - Loans
  - Leave Requests
- Operations
  - Deliveries
  - Incidents
  - Vehicle Logs
- Accommodation
  - Buildings
  - Rooms
- Workflows
- Support Tickets
- Settings

**Top Bar:**
- Search (global search across all modules)
- Notifications
- User Profile
- Logout

---

## User Roles

### Administrator
**Full system access**
- Manage all modules
- Create/edit/delete all records
- Manage users and permissions
- Access all reports
- System configuration

### Manager
**Fleet and operations management**
- View/edit couriers and vehicles
- Assign vehicles to couriers
- View deliveries and incidents
- Approve workflows (leaves, loans)
- Generate reports

### HR Manager
**HR and finance functions**
- Manage attendance
- Process payroll
- Review loan requests
- Manage leave requests
- Access HR reports

### Operations
**Day-to-day operations**
- Manage deliveries
- Log incidents
- Update vehicle logs
- View courier assignments

### Support
**Customer support**
- View tickets
- Respond to tickets
- Limited read access

---

## Dashboard

### Overview Dashboard

**Metrics Displayed:**
- Total Couriers (Active/Inactive)
- Total Vehicles (Available/Assigned/Maintenance)
- Today's Deliveries (Completed/Pending)
- Active Workflows (Pending Approvals)
- Recent Activity

**Quick Actions:**
- Add New Courier
- Add New Vehicle
- Create Delivery
- View Pending Approvals

**Recent Activity Feed:**
- Latest couriers added
- Recent vehicle assignments
- Completed deliveries
- Approved workflows

### Customizing Dashboard

1. Click "Customize Dashboard" (top right)
2. Drag and drop widgets
3. Show/hide metrics
4. Save layout

---

## Fleet Management

### Managing Couriers

#### View Couriers List

1. Navigate to **Fleet > Couriers**
2. You'll see a table of all couriers

**Columns:**
- Name
- Phone
- Email
- Status (Active/Inactive/Suspended)
- Assigned Vehicle
- Hire Date

**Actions:**
- **Search:** Type name, phone, or email in search box
- **Filter:** Click "Filters" to filter by status
- **Sort:** Click column headers to sort

#### Add New Courier

1. Click **"+ Add Courier"** button
2. Fill in the form:

   **Personal Information:**
   - Full Name (required)
   - Email (required, unique)
   - Phone (required, format: +966XXXXXXXXX)
   - National ID (required, 10 digits)
   - Date of Birth
   - Nationality

   **Employment Details:**
   - Hire Date (required)
   - Basic Salary (SAR)
   - Allowances (SAR)
   - Status (Active/Inactive)

   **Documents:**
   - License Number
   - License Expiry Date
   - Upload license copy (PDF/Image)

   **Banking Information:**
   - Bank Name
   - IBAN
   - Account Number

   **Emergency Contact:**
   - Name
   - Phone
   - Relationship

3. Click **"Create Courier"**
4. Confirmation message appears
5. Courier is now in the system

#### Edit Courier Information

1. Click on courier name (or click **Edit** icon)
2. Update fields as needed
3. Click **"Save Changes"**
4. Confirmation message appears

#### Deactivate Courier

1. Go to courier details
2. Click **"Change Status"**
3. Select "Inactive"
4. Enter termination date
5. Add notes (reason for termination)
6. Click **"Confirm"**

**Note:** Deactivated couriers are soft-deleted (data retained for reports)

---

### Managing Vehicles

#### View Vehicles List

1. Navigate to **Fleet > Vehicles**
2. View table of all vehicles

**Columns:**
- Plate Number
- Model
- Type (Car/Motorcycle/Van)
- Status (Available/Assigned/Maintenance/Retired)
- Assigned To
- Mileage

#### Add New Vehicle

1. Click **"+ Add Vehicle"**
2. Fill in the form:

   **Vehicle Information:**
   - Plate Number (required, unique)
   - Model (e.g., "Honda CRV 2023")
   - Type (Car/Motorcycle/Van)
   - Year
   - Color
   - VIN (Vehicle Identification Number)

   **Purchase Details:**
   - Purchase Date
   - Purchase Price (SAR)

   **Insurance & Registration:**
   - Insurance Company
   - Insurance Policy Number
   - Insurance Expiry Date
   - Registration Expiry Date

   **Maintenance:**
   - Current Mileage
   - Last Maintenance Date
   - Next Maintenance Due

3. Click **"Create Vehicle"**
4. Vehicle added to fleet

#### Assign Vehicle to Courier

**Method 1: From Vehicles Page**
1. Go to vehicle details
2. Click **"Assign to Courier"**
3. Select courier from dropdown
4. Set assignment start date
5. Add notes (optional)
6. Click **"Assign"**

**Method 2: From Couriers Page**
1. Go to courier details
2. Click **"Assign Vehicle"**
3. Select vehicle from dropdown
4. Set assignment start date
5. Click **"Assign"**

**Result:**
- Vehicle status changes to "Assigned"
- Courier profile shows assigned vehicle
- Assignment logged in system

#### End Vehicle Assignment

1. Go to courier or vehicle details
2. Click **"End Assignment"**
3. Set end date
4. Add notes (optional)
5. Click **"Confirm"**

**Result:**
- Vehicle status changes to "Available"
- Courier shows no assigned vehicle

---

### Vehicle Maintenance Logs

#### Log Maintenance

1. Navigate to **Fleet > Vehicles**
2. Click on vehicle
3. Go to **"Maintenance Logs"** tab
4. Click **"+ Log Maintenance"**
5. Fill in:
   - Log Type (Maintenance/Repair/Inspection/Accident)
   - Date
   - Description
   - Cost (SAR)
   - Mileage at service
   - Performed by (service provider)
6. Click **"Save"**

#### View Maintenance History

1. Go to vehicle details
2. Click **"Maintenance Logs"** tab
3. View chronological list of all maintenance
4. Export to Excel/PDF if needed

---

## HR & Payroll

### Attendance Management

#### Mark Daily Attendance

**Method 1: Individual Entry**
1. Navigate to **HR > Attendance**
2. Click **"+ Mark Attendance"**
3. Select courier
4. Select date
5. Enter:
   - Check-in time
   - Check-out time
   - Status (Present/Absent/Late/Leave)
   - Notes (optional)
6. Click **"Save"**

**Method 2: Bulk Import**
1. Navigate to **HR > Attendance**
2. Click **"Import Attendance"**
3. Download Excel template
4. Fill in attendance data
5. Upload file
6. Review and confirm
7. Click **"Import"**

#### View Attendance Reports

1. Navigate to **HR > Attendance**
2. Select date range
3. Filter by courier (optional)
4. Click **"Generate Report"**
5. Export to Excel/PDF

**Report Includes:**
- Courier name
- Present days
- Absent days
- Late days
- Leave days
- Total hours worked

---

### Payroll Management

#### Generate Monthly Payroll

1. Navigate to **HR > Payroll**
2. Click **"Generate Payroll"**
3. Select month and year
4. System automatically calculates:
   - Basic salary
   - Allowances
   - Bonuses
   - Deductions (loans, fines)
   - Net salary
5. Review payroll summary
6. Click **"Generate"**
7. Payroll records created for all active couriers

#### Review Payroll

1. Navigate to **HR > Payroll**
2. Filter by month/year
3. View list of payroll records
4. Click on record to see details:
   - Basic salary
   - Allowances breakdown
   - Bonuses
   - Deductions breakdown
   - Gross salary
   - Net salary

#### Approve Payroll

1. Go to payroll record
2. Click **"Approve"**
3. Enter approval notes
4. Click **"Confirm"**
5. Status changes to "Approved"

#### Mark as Paid

1. Go to approved payroll record
2. Click **"Mark as Paid"**
3. Enter:
   - Payment date
   - Payment method (Bank Transfer/Cash)
   - Transaction reference (optional)
4. Click **"Confirm"**
5. Status changes to "Paid"

#### Export Payroll

1. Navigate to **HR > Payroll**
2. Filter by month/year
3. Click **"Export"**
4. Choose format (Excel/PDF/CSV)
5. File downloads

---

### Loan Management

#### Submit Loan Request (Courier)

1. Navigate to **HR > Loans**
2. Click **"+ Request Loan"**
3. Fill in:
   - Loan amount (SAR)
   - Number of installments
   - Reason
4. Click **"Submit Request"**
5. Request sent to HR Manager

#### Review Loan Requests (HR Manager)

1. Navigate to **HR > Loans**
2. Filter by status: "Pending"
3. Click on loan request
4. Review details:
   - Courier information
   - Loan amount
   - Installments
   - Reason
   - Courier's salary
   - Current loans

#### Approve/Reject Loan

**To Approve:**
1. Click **"Approve"**
2. Confirm approval
3. Status changes to "Approved"
4. Loan becomes active
5. Monthly deduction starts next payroll

**To Reject:**
1. Click **"Reject"**
2. Enter rejection reason
3. Confirm
4. Courier is notified

#### Track Loan Repayment

1. Go to loan details
2. View:
   - Original amount
   - Installment amount
   - Paid installments
   - Remaining amount
   - Remaining installments
3. System automatically deducts from monthly payroll

---

### Leave Management

#### Submit Leave Request (Courier)

1. Navigate to **HR > Leaves**
2. Click **"+ Request Leave"**
3. Fill in:
   - Leave type (Annual/Sick/Emergency/Unpaid)
   - Start date
   - End date
   - Reason
4. Click **"Submit"**
5. Request sent for approval

#### Approve/Reject Leave (Manager)

1. Navigate to **HR > Leaves**
2. Filter: "Pending Approval"
3. Click on leave request
4. Review:
   - Courier details
   - Leave type and dates
   - Days count
   - Reason
   - Remaining leave balance

**To Approve:**
1. Click **"Approve"**
2. Confirm
3. Courier notified

**To Reject:**
1. Click **"Reject"**
2. Enter reason
3. Confirm
4. Courier notified

#### View Leave Balance

1. Go to courier details
2. Click **"Leave Balance"** tab
3. View:
   - Annual leave: X days remaining
   - Sick leave: X days remaining
   - Emergency leave: X days remaining

---

## Operations

### Delivery Management

#### Create Delivery Task

1. Navigate to **Operations > Deliveries**
2. Click **"+ Create Delivery"**
3. Fill in:
   - Order number
   - Customer name
   - Customer phone
   - Pickup address
   - Delivery address
   - Assign to courier
   - Scheduled time
   - COD amount (if applicable)
   - Delivery fee
4. Click **"Create"**

#### Track Deliveries

1. Navigate to **Operations > Deliveries**
2. View deliveries by status:
   - Pending
   - In Progress
   - Completed
   - Failed
3. Click on delivery to see details
4. View real-time status updates

#### Complete Delivery

1. Go to delivery details
2. Click **"Mark as Completed"**
3. Enter:
   - Actual delivery time
   - Customer signature (optional)
   - Photo proof (optional)
4. Click **"Complete"**

---

### Incident Management

#### Report Incident

1. Navigate to **Operations > Incidents**
2. Click **"+ Report Incident"**
3. Fill in:
   - Incident type (Accident/Theft/Damage/Other)
   - Involved courier
   - Involved vehicle
   - Date and time
   - Location
   - Description
   - Severity (Low/Medium/High/Critical)
   - Police report number (if applicable)
   - Photos (upload)
4. Click **"Submit"**

#### Track Incident Resolution

1. Go to incident details
2. View status:
   - Reported
   - Investigating
   - Resolved
   - Closed
3. Add updates/notes as needed
4. Upload documents (insurance claims, etc.)

---

## Accommodation

### Building Management

#### Add Building

1. Navigate to **Accommodation > Buildings**
2. Click **"+ Add Building"**
3. Fill in:
   - Building name
   - Full address
   - City
   - Total rooms
   - Monthly rent
   - Contract start/end dates
   - Landlord information
4. Click **"Create"**

### Room Management

#### Add Room

1. Go to building details
2. Click **"+ Add Room"**
3. Fill in:
   - Room number
   - Capacity (max occupants)
4. Click **"Create"**

#### Assign Courier to Room

1. Go to room details
2. Click **"Assign Courier"**
3. Select courier
4. Set start date
5. Click **"Assign"**

**Note:** System prevents over-capacity assignments

#### View Occupancy

1. Navigate to **Accommodation > Rooms**
2. View occupancy status:
   - Available (green)
   - Occupied (yellow)
   - Full (red)
   - Maintenance (gray)

---

## Workflows & Approvals

### Pending Approvals

1. Navigate to **Workflows**
2. View pending approvals:
   - Leave requests
   - Loan requests
   - Vehicle assignments
   - Other workflows
3. Click **"View"** to see details
4. Approve or reject

### Workflow History

1. Navigate to **Workflows > History**
2. Filter by:
   - Type
   - Status
   - Date range
3. View complete workflow history

---

## Reports & Analytics

### Available Reports

1. **Fleet Reports**
   - Courier roster
   - Vehicle inventory
   - Assignment history
   - Maintenance costs

2. **HR Reports**
   - Attendance summary
   - Payroll summary
   - Loan status
   - Leave balance

3. **Operations Reports**
   - Delivery performance
   - Incident summary
   - Vehicle utilization

### Generate Report

1. Navigate to **Reports**
2. Select report type
3. Set parameters:
   - Date range
   - Filters
   - Group by
4. Click **"Generate"**
5. View report
6. Export (Excel/PDF/CSV)

---

## Support

### Create Support Ticket

1. Navigate to **Support > Tickets**
2. Click **"+ New Ticket"**
3. Fill in:
   - Category (Vehicle/Delivery/HR/Technical)
   - Priority (Low/Medium/High/Critical)
   - Subject
   - Description
   - Attachments (optional)
4. Click **"Submit"**

### Track Ticket Status

1. Navigate to **Support > Tickets**
2. View your tickets
3. Click on ticket to see:
   - Status (Open/In Progress/Resolved/Closed)
   - Responses
   - Updates
4. Add comments as needed

---

## FAQ

**Q: I forgot my password. How do I reset it?**
A: Click "Forgot Password" on login page. Enter your email. Check email for reset link.

**Q: How do I change my profile information?**
A: Click your name (top right) > Profile > Edit > Save Changes

**Q: Can I export data to Excel?**
A: Yes, most pages have an "Export" button. Choose Excel format.

**Q: How do I assign multiple vehicles?**
A: You can only assign one vehicle per courier at a time. End current assignment first.

**Q: When is payroll processed?**
A: Payroll is generated on the last day of each month and paid on the 1st of the following month.

**Q: How many days of annual leave do couriers get?**
A: 21 days per year (configurable per company policy).

**Q: Can I delete a courier?**
A: No, couriers are soft-deleted to maintain data integrity. Mark as "Inactive" instead.

**Q: How do I get help?**
A: Create a support ticket or email support@barq.com

---

**Need More Help?**
- **Email:** support@barq.com
- **Phone:** +966 XX XXX XXXX
- **Support Hours:** Sunday-Thursday, 9 AM - 5 PM (UTC+3)

---

**Document Version:** 1.0.0
**Last Updated:** November 23, 2025
**Next Update:** As needed based on feature releases
