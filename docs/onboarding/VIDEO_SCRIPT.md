# BARQ Fleet Management System - Video Tutorial Script

**Total Duration:** ~15 minutes
**Target Audience:** New administrators, fleet managers, and operations staff
**Video Style:** Screen recording with voiceover narration

---

## Pre-Production Notes

### Equipment Needed
- Screen recording software (OBS Studio / Loom / Camtasia)
- Microphone for clear voiceover
- Demo environment with sample data
- 1920x1080 resolution recommended

### Demo Account Setup
```
Email: demo@barq.com
Password: demo123
Organization: BARQ Logistics Demo
```

---

## SCENE 1: Introduction (0:00 - 0:45)

### Visual
- BARQ logo animation
- Dashboard overview with blur effect
- Text overlay: "BARQ Fleet Management System"

### Narration
```
"Welcome to BARQ Fleet Management - your complete solution for managing
delivery operations, fleet assets, workforce, and business analytics.

In this tutorial, we'll walk you through everything you need to know
to get started with BARQ. Whether you're managing a small delivery team
or a large logistics operation, BARQ scales with your business.

Let's begin by logging into the system."
```

### Timestamps
| Time | Action |
|------|--------|
| 0:00 | Logo animation starts |
| 0:10 | Dashboard preview (blurred) |
| 0:25 | Transition to login screen |

---

## SCENE 2: Login & Authentication (0:45 - 2:00)

### Visual
- Login page at `https://app.barq.com/login`
- Email/password fields
- Google OAuth button
- Organization selector (if multi-org)

### Narration
```
"To access BARQ, navigate to app.barq.com. You'll see the login screen
with two options: email and password login, or Google single sign-on.

[Type email] Enter your registered email address...
[Type password] And your secure password...
[Click Login] Then click Sign In.

If your account belongs to multiple organizations, you'll be prompted
to select which one you want to access. Each organization has its own
isolated data and settings.

[Select organization] Let's choose BARQ Logistics Demo.

You can switch organizations anytime from the header dropdown."
```

### Key UI Elements to Highlight
1. Email input field
2. Password field with show/hide toggle
3. "Sign in with Google" button
4. "Forgot Password" link
5. Organization selector dropdown

### Demo Actions
1. Enter email: `demo@barq.com`
2. Enter password: `demo123`
3. Click "Sign In" button
4. Select organization from dropdown
5. Show organization switcher in header

---

## SCENE 3: Dashboard Overview (2:00 - 4:00)

### Visual
- Main dashboard with KPI cards
- Charts and graphs
- Activity feed
- Quick action buttons

### Narration
```
"Welcome to your command center - the BARQ Dashboard. Here you get
a real-time overview of your entire operation at a glance.

[Point to KPI cards] At the top, you'll see key performance indicators:
- Active Couriers currently on duty
- Today's Deliveries with completion rate
- Fleet Utilization showing how many vehicles are in use
- Pending Tasks requiring your attention

[Point to charts] Below, we have visual analytics:
- The delivery trend chart shows your daily performance over time
- The pie chart breaks down delivery statuses
- The fleet health gauge shows your overall operational score

[Point to alerts] On the right side, you'll see System Alerts -
these highlight items needing immediate attention, like vehicles
due for maintenance or couriers with expiring documents.

[Point to activity feed] The Recent Activity feed shows live updates
across your organization - new orders, status changes, and team actions."
```

### Key UI Elements to Highlight
1. KPI Cards: Couriers, Deliveries, Fleet, Pending Tasks
2. Delivery Trend Chart (Area Chart)
3. Status Distribution (Pie Chart)
4. Fleet Health Score (Radial Gauge)
5. System Alerts Panel
6. Recent Activity Feed
7. Quick Actions: New Delivery, Add Courier, Schedule Maintenance

### Demo Actions
1. Hover over KPI cards to show tooltips
2. Click chart legend items to filter data
3. Click an alert to navigate to detail
4. Scroll activity feed
5. Click "New Delivery" quick action

---

## SCENE 4: Fleet Management - Couriers (4:00 - 6:30)

### Visual
- Fleet > Couriers list page
- Courier detail/profile page
- Performance metrics

### Narration
```
"Let's explore Fleet Management, starting with Couriers.
Navigate to Fleet in the sidebar, then click Couriers.

[Show list] Here you see all your delivery personnel with their
current status, assigned vehicle, and today's statistics.

[Point to filters] Use filters to find specific couriers -
by status, zone, or search by name or ID.

[Click courier] Click any courier to see their detailed profile.

[Show profile tabs] The profile has several sections:
- Overview: Basic info, contact details, emergency contacts
- Performance: Delivery stats, ratings, on-time percentage
- Documents: License, ID, certifications with expiry tracking
- Vehicle History: Past and current vehicle assignments
- Attendance: Clock-in/out records and shift patterns
- Financials: Earnings, bonuses, deductions

[Show performance metrics] The performance tab is particularly
useful - you can see delivery completion rate, customer ratings,
and compare against team averages."
```

### Key UI Elements to Highlight
1. Courier list with status badges
2. Search and filter controls
3. Status indicator (Online/Offline/On Delivery)
4. Profile tabs navigation
5. Performance charts
6. Document expiry warnings
7. Quick actions: Call, Message, Assign Vehicle

### Demo Actions
1. Navigate: Sidebar > Fleet > Couriers
2. Use search to find "Ahmed"
3. Apply filter: Status = Online
4. Click courier row to open profile
5. Navigate through profile tabs
6. Show performance comparison chart
7. Click "Assign Vehicle" button

---

## SCENE 5: Fleet Management - Vehicles (6:30 - 8:30)

### Visual
- Fleet > Vehicles list page
- Vehicle detail page
- Maintenance schedule

### Narration
```
"Next, let's look at Vehicle Management. Go to Fleet > Vehicles.

[Show list] Each vehicle card shows the plate number, model,
current assignment, and maintenance status. Green means healthy,
yellow indicates upcoming maintenance, red requires attention.

[Point to stats] The top row summarizes your fleet:
- Total vehicles
- Currently assigned
- In maintenance
- Available

[Click vehicle] Let's open a vehicle profile.

[Show details] Here you see:
- Vehicle specifications and registration
- Insurance and permit information
- Current courier assignment
- Fuel consumption history
- Maintenance log with scheduled services
- Inspection records

[Show maintenance] The Maintenance tab shows upcoming and past
service records. BARQ automatically tracks mileage and alerts
you when service is due.

[Show fuel tracking] Fuel Tracking integrates with Syarah for
real-time fuel consumption data and cost analysis."
```

### Key UI Elements to Highlight
1. Vehicle cards with status indicators
2. Fleet summary stats
3. Vehicle details panel
4. Maintenance schedule calendar
5. Fuel consumption chart
6. Document management
7. Assignment history

### Demo Actions
1. Navigate: Sidebar > Fleet > Vehicles
2. Show fleet summary statistics
3. Filter by status: "Needs Maintenance"
4. Click vehicle to view details
5. Navigate to Maintenance tab
6. Show upcoming service alert
7. Navigate to Fuel Tracking
8. Demonstrate Syarah integration

---

## SCENE 6: Operations - Deliveries (8:30 - 10:30)

### Visual
- Operations > Deliveries list
- Delivery detail view
- Order tracking timeline

### Narration
```
"Operations is where the action happens. Let's start with Deliveries.

[Show list] The deliveries page shows all orders with their
current status, assigned courier, and timeline.

[Point to statuses] Orders flow through these stages:
- Pending: Waiting for assignment
- Assigned: Courier accepted
- Picked Up: Package collected
- In Transit: En route to customer
- Delivered: Successfully completed
- Failed: Delivery attempt unsuccessful

[Use filters] Filter by date, status, zone, or courier to
find specific orders quickly.

[Click delivery] Opening a delivery shows the complete journey:
- Customer details and address
- Package information
- Assigned courier and vehicle
- Real-time tracking map
- Timeline of all status updates
- Proof of delivery photos

[Show map] The map shows the courier's current location and
route to the destination.

[Show dispatch] For new orders, the Auto-Dispatch feature
automatically assigns the nearest available courier based
on location, workload, and skills."
```

### Key UI Elements to Highlight
1. Delivery list with status badges
2. Filter panel (date, status, zone, courier)
3. Bulk actions (assign, reassign, cancel)
4. Delivery detail modal
5. Real-time tracking map
6. Status timeline
7. Proof of delivery section
8. Auto-dispatch settings

### Demo Actions
1. Navigate: Sidebar > Operations > Deliveries
2. Apply filter: Today's deliveries
3. Sort by status
4. Click delivery to view details
5. Show tracking map with live location
6. Scroll timeline
7. Show proof of delivery photos
8. Demonstrate dispatch feature

---

## SCENE 7: HR & Finance (10:30 - 12:00)

### Visual
- HR module overview
- Leave management
- Payroll/salary

### Narration
```
"BARQ includes comprehensive HR and Finance management.

[Show HR menu] Under HR, you can manage:
- Leave Requests: Employees submit leave, managers approve
- Attendance: Automatic tracking with clock-in/out
- Loans: Employee advance requests and repayment tracking
- Assets: Company equipment assigned to staff

[Show leave] Let's look at Leave Management. Employees request
time off through the app, and it comes here for approval.
You can see remaining balances, approve or reject with notes.

[Show finance menu] Under Finance:
- Salary Calculation: Automatic payroll based on attendance
- Bonuses: Performance incentives
- Deductions: Penalties, loan repayments
- COD Reconciliation: Cash collected by couriers

[Show salary] The Salary module calculates pay based on:
- Base salary
- Delivery bonuses
- Attendance records
- Deductions and advances

Reports can be exported to Excel for accounting systems."
```

### Key UI Elements to Highlight
1. Leave request list with status
2. Leave balance display
3. Approval workflow buttons
4. Salary calculation breakdown
5. Export to Excel button
6. COD reconciliation dashboard

### Demo Actions
1. Navigate: Sidebar > HR > Leave
2. Show pending requests
3. Approve a leave request
4. Navigate: Sidebar > Finance > Salary
5. View salary breakdown for courier
6. Export salary report

---

## SCENE 8: Analytics & Reports (12:00 - 13:30)

### Visual
- Analytics dashboard
- Custom report builder
- Export options

### Narration
```
"Data drives decisions, and BARQ's Analytics module gives you
deep insights into every aspect of your operation.

[Show analytics menu] Analytics includes:
- Overview Dashboard: High-level KPIs and trends
- Fleet Analytics: Vehicle utilization, costs, efficiency
- HR Analytics: Workforce metrics, attendance patterns
- Financial Analytics: Revenue, costs, profitability
- Operations Analytics: Delivery performance, SLA compliance

[Show fleet analytics] Fleet Analytics shows:
- Utilization rates per vehicle
- Fuel efficiency comparisons
- Maintenance cost trends
- Idle time analysis

[Show custom reports] The Report Builder lets you create
custom reports with any metrics you need. Choose dimensions,
filters, and visualization types.

[Show scheduling] Reports can be scheduled for automatic
email delivery - daily, weekly, or monthly."
```

### Key UI Elements to Highlight
1. Analytics navigation menu
2. Interactive charts with drill-down
3. Date range selector
4. Export buttons (PDF, Excel, CSV)
5. Report builder interface
6. Scheduling options

### Demo Actions
1. Navigate: Sidebar > Analytics > Overview
2. Change date range to "Last 30 days"
3. Drill into Fleet Analytics
4. Show vehicle comparison chart
5. Open Report Builder
6. Create simple custom report
7. Show export and schedule options

---

## SCENE 9: Settings & Administration (13:30 - 14:30)

### Visual
- Settings page
- User management
- Organization settings

### Narration
```
"Finally, let's cover Settings and Administration.

[Show settings] Under Settings, you can configure:
- Profile: Your personal information
- Notifications: Email and in-app alerts
- Language: English or Arabic with RTL support
- Theme: Light or dark mode

[Show admin] Organization administrators have access to:
- User Management: Add, edit, remove team members
- Roles & Permissions: Control who can access what
- API Keys: For integrations with other systems
- Audit Logs: Complete activity history

[Show user management] Adding a new user is simple:
Enter their email, assign a role, and send the invitation.
They'll receive an email to set their password.

[Show roles] BARQ has four built-in roles:
- Owner: Full access to everything
- Admin: All features except billing
- Manager: Operations and fleet management
- Viewer: Read-only access to reports"
```

### Key UI Elements to Highlight
1. Settings navigation
2. Profile editor
3. Notification preferences
4. Language selector
5. User list with roles
6. Add user form
7. Role permissions matrix
8. Audit log viewer

### Demo Actions
1. Navigate: Sidebar > Settings
2. Show profile settings
3. Toggle dark mode
4. Change language to Arabic (show RTL)
5. Navigate: Admin > Users
6. Click "Add User"
7. Show role selection
8. View audit logs

---

## SCENE 10: Conclusion (14:30 - 15:00)

### Visual
- Quick tips overlay
- Support resources
- BARQ logo

### Narration
```
"Congratulations! You now have a solid understanding of BARQ
Fleet Management System.

Here are some quick tips to remember:
- Use keyboard shortcuts for faster navigation
- Set up notification preferences to stay informed
- Check the Dashboard daily for alerts and KPIs
- Use the Help button for in-app documentation

If you need assistance:
- Click the Support icon for help articles
- Email support@barq.com for technical issues
- Check our knowledge base at docs.barq.com

Thank you for choosing BARQ. We're here to help your
delivery operations run smoothly.

Happy delivering!"
```

### End Screen
- BARQ logo centered
- "Get Started at app.barq.com"
- Support contact information
- Social media links

---

## Post-Production Notes

### Editing Guidelines
1. Add zoom effects on UI elements being discussed
2. Use highlight boxes around clickable areas
3. Add chapter markers for easy navigation
4. Include captions/subtitles (English and Arabic)
5. Add background music at 10% volume

### Thumbnail Design
- Dashboard screenshot with BARQ logo
- Text: "Getting Started Tutorial"
- Duration badge: "15 min"

### Distribution
- YouTube (public or unlisted)
- Embed in app Help section
- Share link in onboarding emails
- Add to knowledge base

---

## Appendix: Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Quick search |
| `Ctrl/Cmd + N` | New delivery |
| `Ctrl/Cmd + /` | Keyboard shortcuts help |
| `G + D` | Go to Dashboard |
| `G + C` | Go to Couriers |
| `G + V` | Go to Vehicles |
| `G + O` | Go to Deliveries |
| `Esc` | Close modal/drawer |

---

**Document Version:** 1.0
**Last Updated:** December 9, 2025
**Author:** BARQ Development Team
