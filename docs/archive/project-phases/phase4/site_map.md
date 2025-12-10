# BARQ Fleet Management - Information Architecture

**Created:** December 6, 2025
**Phase:** 4 - Information Architecture & Wireframing

---

## Site Map

```
BARQ Fleet Management
│
├── 🏠 Dashboard
│   ├── Overview (KPIs, Charts, Alerts)
│   ├── Quick Actions
│   └── Recent Activity
│
├── 🚗 Fleet Management
│   ├── Vehicles
│   │   ├── Vehicle List
│   │   ├── Vehicle Details
│   │   ├── Add/Edit Vehicle
│   │   └── Vehicle Documents
│   ├── Couriers
│   │   ├── Courier List
│   │   ├── Courier Profile
│   │   ├── Add/Edit Courier
│   │   ├── Documents
│   │   └── Performance
│   ├── Assignments
│   │   ├── Active Assignments
│   │   ├── Create Assignment
│   │   └── Assignment History
│   ├── Maintenance
│   │   ├── Schedule
│   │   ├── Work Orders
│   │   └── Service History
│   ├── Inspections
│   │   ├── Inspection List
│   │   ├── Create Inspection
│   │   └── Inspection Reports
│   └── Fuel Logs
│       ├── Fuel Entries
│       └── Fuel Analytics
│
├── 📦 Operations
│   ├── Deliveries
│   │   ├── All Deliveries
│   │   ├── Create Delivery
│   │   ├── Delivery Details
│   │   └── Delivery History
│   ├── Dispatch
│   │   ├── Dispatch Board
│   │   ├── Auto-Assign
│   │   └── Manual Assign
│   ├── Routes
│   │   ├── Route List
│   │   ├── Route Planner
│   │   └── Route Optimization
│   ├── Zones
│   │   ├── Zone Management
│   │   └── Zone Analytics
│   ├── COD Management
│   │   ├── Collections
│   │   ├── Reconciliation
│   │   └── Reports
│   ├── Incidents
│   │   ├── Incident List
│   │   ├── Report Incident
│   │   └── Incident Details
│   └── Handovers
│       ├── Shift Handovers
│       └── Package Transfers
│
├── 👥 HR & Finance
│   ├── Employees
│   │   ├── Employee List
│   │   └── Employee Profile
│   ├── Attendance
│   │   ├── Daily Attendance
│   │   ├── Shift Management
│   │   └── Overtime
│   ├── Leave Management
│   │   ├── Leave Requests
│   │   ├── Leave Balances
│   │   ├── Leave Calendar
│   │   └── Leave Policies
│   ├── Payroll
│   │   ├── Salary Processing
│   │   ├── Payslips
│   │   ├── Deductions
│   │   └── GOSI Reports
│   ├── Loans
│   │   ├── Loan Requests
│   │   ├── Active Loans
│   │   └── Repayment Schedule
│   ├── Assets
│   │   ├── Asset Inventory
│   │   └── Asset Assignment
│   └── End of Service
│       ├── EOS Calculator
│       └── EOS Processing
│
├── 🏢 Accommodation
│   ├── Buildings
│   │   ├── Building List
│   │   └── Building Details
│   ├── Rooms
│   │   ├── Room List
│   │   └── Room Details
│   ├── Beds
│   │   └── Bed Management
│   └── Allocations
│       ├── Current Allocations
│       └── Allocation History
│
├── 📊 Analytics
│   ├── Fleet Analytics
│   │   ├── Utilization
│   │   ├── Maintenance Costs
│   │   └── Fuel Efficiency
│   ├── Operations Analytics
│   │   ├── Delivery Performance
│   │   ├── SLA Compliance
│   │   └── Zone Performance
│   ├── HR Analytics
│   │   ├── Workforce Metrics
│   │   ├── Attendance Trends
│   │   └── Turnover Analysis
│   ├── Financial Analytics
│   │   ├── Revenue
│   │   ├── Costs
│   │   └── Profitability
│   └── Reports
│       ├── Report Builder
│       ├── Scheduled Reports
│       └── Export Center
│
├── 🔄 Workflows
│   ├── Templates
│   │   ├── Template List
│   │   └── Template Designer
│   ├── Instances
│   │   ├── Active Workflows
│   │   └── Completed Workflows
│   └── Approval Chains
│       ├── Pending Approvals
│       └── Approval History
│
├── 🎧 Support
│   ├── Tickets
│   │   ├── All Tickets
│   │   ├── My Tickets
│   │   ├── Create Ticket
│   │   └── Ticket Details
│   ├── Knowledge Base
│   │   ├── Articles
│   │   ├── Categories
│   │   └── Search
│   ├── FAQ
│   │   └── FAQ Management
│   └── Analytics
│       ├── Support Metrics
│       └── Agent Performance
│
├── ⚙️ Admin
│   ├── Users
│   │   ├── User List
│   │   ├── User Details
│   │   └── Invite User
│   ├── Roles & Permissions
│   │   ├── Role Management
│   │   └── Permission Matrix
│   ├── Organizations
│   │   ├── Organization Settings
│   │   └── Subscription
│   ├── Integrations
│   │   ├── API Keys
│   │   ├── Webhooks
│   │   └── Third-party Apps
│   ├── Audit Logs
│   │   └── Activity History
│   ├── System Settings
│   │   ├── General
│   │   ├── Notifications
│   │   └── Security
│   └── Backups
│       ├── Backup Schedule
│       └── Restore Points
│
└── 👤 User Account
    ├── Profile
    ├── Preferences
    ├── Notifications
    └── Security
```

---

## Navigation Structure

### Primary Navigation (Sidebar)

| Icon | Label | Access Level | Badge |
|------|-------|--------------|-------|
| 🏠 | Dashboard | All | - |
| 🚗 | Fleet | Fleet roles | Alerts count |
| 📦 | Operations | Operations roles | Active deliveries |
| 👥 | HR & Finance | HR roles | Pending approvals |
| 🏢 | Accommodation | Admin, HR | - |
| 📊 | Analytics | Manager+ | - |
| 🔄 | Workflows | All | Pending items |
| 🎧 | Support | All | Open tickets |
| ⚙️ | Admin | Admin only | - |

### Secondary Navigation (Top Bar)

| Element | Purpose |
|---------|---------|
| Search | Global search across all modules |
| Notifications | Bell icon with unread count |
| Organization Switcher | Multi-tenant selection |
| User Menu | Profile, settings, logout |

---

## User Flow Priorities

### Primary Flows (Daily Use)
1. Dashboard → Quick Stats → Drill-down
2. Dispatch → Assign → Monitor → Complete
3. Leave → Request → Approve → Update Balance

### Secondary Flows (Weekly)
1. Analytics → Generate Report → Export
2. Maintenance → Schedule → Complete → Log
3. Payroll → Process → Review → Finalize

### Tertiary Flows (Monthly/As Needed)
1. User Management → Add/Remove → Permissions
2. Workflow Design → Create → Deploy
3. Integration Setup → Configure → Test

---

*Document created as part of Phase 4 - Information Architecture & Wireframing*
