# BARQ Fleet Management System - User Personas

## Overview

This document defines the key user personas for the BARQ Fleet Management platform. These personas represent the primary users who interact with the system across fleet management, HR, operations, and administrative functions. Understanding these personas is critical for product development, feature prioritization, and UX design decisions.

---

## Persona 1: Fleet Operations Manager

### Profile

| Attribute | Details |
|-----------|---------|
| **Name** | Ahmed Al-Rashid |
| **Role** | Fleet Operations Manager |
| **Age** | 38 years old |
| **Experience** | 12 years in logistics, 5 years in fleet management |
| **Tech Savviness** | Moderate to High |
| **Work Environment** | Office-based with frequent floor visits; uses desktop primarily, tablet for inspections |
| **Reports To** | Director of Operations |
| **Team Size** | Manages 8 supervisors, oversees 200+ couriers |

### Goals and Motivations

1. **Maximize Fleet Utilization** - Ensure vehicles and couriers are optimally assigned to minimize idle time
2. **Reduce Operational Costs** - Lower maintenance costs through proactive scheduling and fuel efficiency tracking
3. **Maintain Compliance** - Keep all vehicle registrations, insurance, and courier documents current
4. **Improve Delivery Performance** - Achieve and exceed SLA targets for delivery operations
5. **Data-Driven Decisions** - Access real-time analytics to make informed fleet allocation decisions

### Pain Points

1. **Document Tracking Complexity** - Managing expiry dates for licenses, iqamas, insurance across 200+ couriers is overwhelming with spreadsheets
2. **Reactive Maintenance** - Vehicles break down unexpectedly due to missed service schedules
3. **Assignment Visibility Gap** - Difficulty seeing which couriers have vehicles and which are unassigned at any moment
4. **Report Generation** - Spending hours compiling weekly fleet status reports manually
5. **Cross-System Data** - FMS/GPS data lives in a separate system, requiring manual correlation

### Key Daily Tasks

| Task | Frequency | Time Spent |
|------|-----------|------------|
| Review fleet dashboard for alerts | Daily | 30 min |
| Process vehicle assignments | Daily | 1 hour |
| Review maintenance requests | Daily | 45 min |
| Check document expiry alerts | Daily | 20 min |
| Approve new vehicle registrations | Weekly | 2 hours |
| Generate fleet performance reports | Weekly | 3 hours |
| Strategic fleet capacity planning | Monthly | 4 hours |

### Success Metrics

- **Vehicle Utilization Rate** > 85%
- **Maintenance SLA Compliance** > 95%
- **Document Compliance Rate** = 100%
- **Unscheduled Breakdown Rate** < 3%
- **Average Vehicle Downtime** < 48 hours
- **Cost per Delivery** trending downward quarter-over-quarter

### Feature Priorities

| Priority | Module | Features |
|----------|--------|----------|
| Critical | Fleet Management | Vehicle tracking, assignment management, maintenance scheduling |
| Critical | Analytics | Fleet utilization dashboard, cost analysis, trend reports |
| High | Fleet Management | Document expiry alerts, inspection tracking, accident logs |
| High | FMS Integration | GPS tracking sync, geofence monitoring, real-time location |
| Medium | Operations | Delivery performance by vehicle type, route optimization |
| Low | Support | Vehicle-related ticket management |

### Typical User Journey

1. Log in each morning and review the Dashboard for critical alerts (expired documents, maintenance due)
2. Navigate to Fleet > Vehicles to check status of vehicles in maintenance
3. Process any pending vehicle assignment requests from supervisors
4. Review courier-vehicle allocation across cities
5. Check FMS sync status for GPS data accuracy
6. Export weekly fleet report for management meeting

---

## Persona 2: HR & Payroll Administrator

### Profile

| Attribute | Details |
|-----------|---------|
| **Name** | Fatima Hassan |
| **Role** | HR & Payroll Administrator |
| **Age** | 32 years old |
| **Experience** | 8 years in HR, 4 years in delivery/logistics sector |
| **Tech Savviness** | Moderate |
| **Work Environment** | Office-based; desktop primary, occasional mobile for approvals |
| **Reports To** | HR Manager |
| **Responsibilities** | 250+ courier records, payroll processing, compliance |

### Goals and Motivations

1. **Accurate Payroll Processing** - Zero errors in monthly salary calculations including deductions and allowances
2. **Compliance Management** - Ensure all couriers have valid work permits (iqama), licenses, and GOSI registration
3. **Efficient Onboarding** - Streamline new courier documentation and system setup
4. **Leave Management** - Fairly manage leave requests while maintaining operational capacity
5. **Loan Tracking** - Accurately track employee loans and monthly deductions

### Pain Points

1. **Manual Salary Calculations** - Complex calculations with base salary, allowances, deductions, GOSI, and loan repayments
2. **Document Chase** - Constantly following up with couriers for expired or missing documents
3. **Multiple Data Sources** - Attendance, leaves, loans spread across different files and systems
4. **Audit Preparation** - Scrambling to compile records for labor audits
5. **Sponsorship Complexity** - Different rules for AJEER vs in-house vs freelancer couriers

### Key Daily Tasks

| Task | Frequency | Time Spent |
|------|-----------|------------|
| Process new courier registrations | Daily | 1.5 hours |
| Review and approve leave requests | Daily | 1 hour |
| Update courier personal information | Daily | 45 min |
| Monitor document expiry status | Daily | 30 min |
| Process loan applications | Weekly | 2 hours |
| Generate payroll calculations | Monthly | 2 full days |
| GOSI reporting and compliance | Monthly | 4 hours |
| Handle HR-related support tickets | Daily | 1 hour |

### Success Metrics

- **Payroll Accuracy Rate** = 100%
- **Document Compliance Rate** > 98%
- **Average Onboarding Time** < 3 days
- **Leave Request Processing Time** < 24 hours
- **GOSI Compliance** = 100%
- **Employee Query Resolution Time** < 4 hours

### Feature Priorities

| Priority | Module | Features |
|----------|--------|----------|
| Critical | HR | Salary management, payroll processing, GOSI calculations |
| Critical | Fleet - Courier | Courier profiles, document management, sponsorship tracking |
| High | HR | Leave management, attendance tracking, loan management |
| High | HR | Bonus/penalty management, asset tracking |
| Medium | Analytics | HR reports, payroll summaries, compliance dashboards |
| Medium | Support | HR ticket handling for employee inquiries |
| Low | Accommodation | Room/bed allocation for company housing |

### Typical User Journey

1. Start day checking new courier onboarding queue
2. Review courier list filtered by "Expiring Documents" within 30 days
3. Process pending leave requests from overnight submissions
4. Navigate to HR > Salary to verify previous month's calculations
5. Handle HR-category support tickets from couriers
6. End of month: Run full payroll calculation workflow, verify GOSI deductions

---

## Persona 3: Dispatch Supervisor

### Profile

| Attribute | Details |
|-----------|---------|
| **Name** | Khalid Mansour |
| **Role** | Dispatch Supervisor / Shift Lead |
| **Age** | 29 years old |
| **Experience** | 6 years in delivery operations |
| **Tech Savviness** | Moderate |
| **Work Environment** | Operations floor; uses tablet 70% of time, mobile 30% |
| **Reports To** | Fleet Operations Manager |
| **Team Size** | Directly supervises 25-30 couriers per shift |

### Goals and Motivations

1. **Meet Delivery SLAs** - Ensure all deliveries within the shift meet time commitments
2. **Maximize Courier Productivity** - Optimize route assignments to minimize idle time
3. **Quick Issue Resolution** - Address delivery failures, incidents, and customer complaints rapidly
4. **Team Management** - Track attendance, manage handovers, and ensure shift coverage
5. **Real-Time Visibility** - Know exactly where every courier is and their delivery status

### Pain Points

1. **Last-Minute Changes** - Couriers calling in sick with no visibility into backup options
2. **Route Inefficiency** - Manually deciding which courier gets which zone
3. **Communication Gaps** - Difficulty reaching couriers in the field for urgent re-routing
4. **Incident Handling** - No structured way to log and track delivery incidents
5. **Shift Handover** - Information gets lost between shifts

### Key Daily Tasks

| Task | Frequency | Time Spent |
|------|-----------|------------|
| Review courier attendance for shift | Start of shift | 20 min |
| Assign deliveries to available couriers | Throughout shift | Continuous |
| Monitor live delivery progress | Throughout shift | Continuous |
| Handle escalated delivery issues | As needed | 1-2 hours |
| Process shift handover | End of shift | 30 min |
| Log incidents and quality issues | As needed | 30 min |
| COD collection reconciliation | End of shift | 45 min |

### Success Metrics

- **On-Time Delivery Rate** > 95%
- **Delivery Completion Rate** > 98%
- **Average Delivery Time** within target by zone
- **Incident Rate** < 2% of deliveries
- **COD Collection Accuracy** = 100%
- **Shift Coverage** > 95%

### Feature Priorities

| Priority | Module | Features |
|----------|--------|----------|
| Critical | Operations | Dispatch board, delivery tracking, route management |
| Critical | Operations | Zone management, priority queue, real-time status |
| High | Fleet - Courier | Courier availability, status, current assignment |
| High | Operations | Incident logging, quality tracking, SLA monitoring |
| High | Operations | COD management, handover processing |
| Medium | Support | Creating/escalating operational tickets |
| Low | Analytics | Shift performance reports |

### Typical User Journey

1. Log in at shift start, review operations dashboard
2. Check courier attendance and confirm who is available vs on leave
3. Open dispatch board to see pending deliveries by zone
4. Assign deliveries based on courier location and zone expertise
5. Monitor SLA tracker for any at-risk deliveries
6. Handle incoming escalations (failed delivery attempts, customer complaints)
7. Process end-of-shift handover, log any incidents, verify COD collection

---

## Persona 4: System Administrator

### Profile

| Attribute | Details |
|-----------|---------|
| **Name** | Omar Qasim |
| **Role** | System Administrator / IT Manager |
| **Age** | 35 years old |
| **Experience** | 10 years in IT, 3 years with fleet management systems |
| **Tech Savviness** | Very High |
| **Work Environment** | IT office; desktop primary, server room access |
| **Reports To** | IT Director |
| **Responsibilities** | System configuration, user management, integrations, security |

### Goals and Motivations

1. **System Uptime** - Maintain 99.9% availability for all business-critical functions
2. **Security Compliance** - Ensure proper access controls, audit trails, and data protection
3. **Efficient User Management** - Streamline onboarding/offboarding of system users
4. **Integration Health** - Keep all external system integrations (FMS, delivery platforms) running smoothly
5. **Scalability** - Ensure the system can handle growth in users, data, and transactions

### Pain Points

1. **Permission Complexity** - Managing granular permissions across many roles is time-consuming
2. **Audit Preparation** - Extracting audit logs and access reports for compliance reviews
3. **Integration Failures** - FMS sync issues that require manual intervention
4. **Onboarding Delays** - New users waiting for access while approvals are pending
5. **Multi-Tenant Management** - Ensuring proper data isolation across organizations

### Key Daily Tasks

| Task | Frequency | Time Spent |
|------|-----------|------------|
| Monitor system health/health endpoint | Daily | 15 min |
| Review security alerts and audit logs | Daily | 30 min |
| Process user access requests | Daily | 1 hour |
| Check integration sync status (FMS, APIs) | Daily | 20 min |
| Configure new roles/permissions | Weekly | 2 hours |
| Generate compliance/audit reports | Monthly | 4 hours |
| System backup verification | Weekly | 30 min |
| API key rotation and management | Monthly | 1 hour |

### Success Metrics

- **System Uptime** > 99.9%
- **Mean Time to Resolution (MTTR)** < 1 hour for critical issues
- **User Access Request SLA** < 4 hours
- **Security Incident Count** = 0
- **Integration Sync Success Rate** > 99.5%
- **Audit Finding Count** = 0 critical findings

### Feature Priorities

| Priority | Module | Features |
|----------|--------|----------|
| Critical | Admin | User management, role/permission configuration |
| Critical | Admin | Audit logs, system monitoring, API key management |
| High | Admin | Backup management, system settings, integrations |
| High | Tenant | Organization management, multi-tenancy configuration |
| Medium | Analytics | System usage reports, performance metrics |
| Medium | Support | IT-category ticket handling |
| Low | All Modules | General system configuration options |

### Typical User Journey

1. Check system health dashboard and verify all services are operational
2. Review overnight audit logs for any suspicious activity
3. Process pending user access requests and role assignments
4. Check FMS integration sync status and resolve any failures
5. Configure new API keys for third-party integration
6. Generate monthly security compliance report

---

## Persona 5: Customer Support Agent

### Profile

| Attribute | Details |
|-----------|---------|
| **Name** | Noura Al-Ameri |
| **Role** | Customer Support Agent |
| **Age** | 26 years old |
| **Experience** | 4 years in customer service, 2 years in logistics support |
| **Tech Savviness** | Moderate |
| **Work Environment** | Call center; desktop with dual monitors, headset |
| **Reports To** | Support Team Lead |
| **Responsibilities** | Ticket resolution, customer communication, escalation |

### Goals and Motivations

1. **Fast Resolution** - Resolve support tickets within SLA targets
2. **Customer Satisfaction** - Achieve high CSAT scores through quality interactions
3. **First-Contact Resolution** - Solve issues without needing escalation when possible
4. **Accurate Information** - Provide correct information using knowledge base and system data
5. **Efficient Workflow** - Handle high ticket volumes without sacrificing quality

### Pain Points

1. **Information Scattered** - Need to check multiple screens to understand a courier's full situation
2. **Escalation Complexity** - Unclear escalation paths for different issue types
3. **Knowledge Gaps** - FAQ and knowledge base not always up to date
4. **SLA Pressure** - Racing against SLA clocks while handling complex issues
5. **Repetitive Queries** - Answering same questions repeatedly without automation

### Key Daily Tasks

| Task | Frequency | Time Spent |
|------|-----------|------------|
| Review assigned ticket queue | Continuous | All day |
| Respond to new tickets | Continuous | 4-5 hours |
| Research courier/vehicle information | Per ticket | Varies |
| Escalate complex issues | As needed | 1 hour |
| Update knowledge base articles | Weekly | 1 hour |
| Participate in team huddles | Daily | 15 min |
| Review SLA compliance | End of day | 15 min |

### Success Metrics

- **First Response Time** < 1 hour
- **Average Resolution Time** < 4 hours (by category)
- **First Contact Resolution Rate** > 70%
- **Customer Satisfaction (CSAT)** > 4.5/5
- **Tickets Handled per Day** > 30
- **SLA Compliance Rate** > 95%

### Feature Priorities

| Priority | Module | Features |
|----------|--------|----------|
| Critical | Support | Ticket management, reply system, SLA tracking |
| Critical | Support | Knowledge base, FAQ access, canned responses |
| High | Support | Ticket templates, category routing, escalation workflow |
| High | Fleet - Courier | Quick lookup of courier information for context |
| Medium | Support | Chat support, ticket merging, feedback collection |
| Medium | Analytics | Personal performance dashboard, queue analytics |
| Low | Operations | Read-only access to delivery status for inquiries |

### Typical User Journey

1. Log in and review ticket queue sorted by SLA urgency
2. Open highest-priority ticket and review full context
3. Look up courier information if ticket is courier-related
4. Search knowledge base for relevant solution articles
5. Compose response using canned response as starting point
6. If cannot resolve, escalate with detailed notes
7. Monitor queue and handle incoming urgent tickets
8. End of day: Review SLA metrics and pending tickets

---

## Persona Comparison Matrix

| Dimension | Fleet Manager | HR Admin | Dispatch Supervisor | System Admin | Support Agent |
|-----------|---------------|----------|---------------------|--------------|---------------|
| **Primary Focus** | Vehicles & Assets | People & Payroll | Deliveries & Couriers | Systems & Security | Tickets & Resolution |
| **Decision Type** | Strategic | Compliance | Operational | Technical | Service |
| **Time Horizon** | Weekly/Monthly | Monthly | Real-time/Daily | Ongoing | Per-ticket |
| **Data Needs** | Analytics & Trends | Records & History | Live Status | Logs & Metrics | Context & History |
| **Top Module** | Fleet Management | HR | Operations | Admin | Support |
| **Device Preference** | Desktop/Tablet | Desktop | Tablet/Mobile | Desktop | Desktop |
| **Peak Activity** | Morning | End of Month | Shift Hours | Ongoing | Business Hours |

---

## Usage Patterns by Persona

### Login Frequency

| Persona | Daily Logins | Session Duration | Peak Time |
|---------|--------------|------------------|-----------|
| Fleet Manager | 3-4 | 2-3 hours | 8-10 AM |
| HR Admin | 2-3 | 3-4 hours | 9 AM - 2 PM |
| Dispatch Supervisor | 1 (shift-long) | 8+ hours | Shift-based |
| System Admin | 5-10 | 15-30 min each | Morning + as-needed |
| Support Agent | 1 (shift-long) | 8+ hours | Business hours |

### Feature Usage Heat Map

| Feature | Fleet Mgr | HR Admin | Dispatch | Sys Admin | Support |
|---------|-----------|----------|----------|-----------|---------|
| Dashboard | HIGH | MEDIUM | HIGH | MEDIUM | LOW |
| Courier List | MEDIUM | HIGH | HIGH | LOW | MEDIUM |
| Vehicle List | HIGH | LOW | MEDIUM | LOW | LOW |
| Assignments | HIGH | LOW | HIGH | LOW | LOW |
| HR - Salary | LOW | HIGH | LOW | LOW | LOW |
| HR - Leave | LOW | HIGH | MEDIUM | LOW | MEDIUM |
| Operations | MEDIUM | LOW | HIGH | LOW | LOW |
| Tickets | LOW | MEDIUM | MEDIUM | MEDIUM | HIGH |
| Admin - Users | LOW | LOW | LOW | HIGH | LOW |
| Analytics | HIGH | MEDIUM | LOW | MEDIUM | LOW |

---

## Design Implications

### Navigation Priorities

Based on persona analysis, the main navigation should be organized by frequency of use:

1. **Dashboard** - Universal entry point with role-specific widgets
2. **Fleet** - Couriers, Vehicles, Assignments (top priority for Fleet Manager, Dispatch)
3. **Operations** - Deliveries, Dispatch, Routes (top priority for Dispatch)
4. **HR** - Salary, Leave, Attendance (top priority for HR Admin)
5. **Support** - Tickets, KB, Chat (top priority for Support Agent)
6. **Admin** - Users, Roles, Settings (top priority for System Admin)
7. **Analytics** - Reports, KPIs, Export (varying priority)

### Role-Based Dashboard Customization

Each persona should see a tailored dashboard view:

- **Fleet Manager**: Fleet health score, vehicle status chart, document alerts, maintenance queue
- **HR Admin**: Payroll status, document compliance, leave calendar, onboarding queue
- **Dispatch Supervisor**: Live delivery map, SLA tracker, courier availability, incident feed
- **System Admin**: System health, integration status, user activity, security alerts
- **Support Agent**: Ticket queue, SLA countdown, personal metrics, quick search

### Mobile Considerations

- **High Mobile Need**: Dispatch Supervisor (tablet for floor work)
- **Moderate Mobile Need**: Fleet Manager (inspections), HR Admin (approvals)
- **Low Mobile Need**: System Admin, Support Agent (desktop-focused)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | Product Team | Initial persona definitions |

---

## Next Steps

1. Validate personas through user interviews
2. Create journey maps for critical workflows per persona
3. Develop feature prioritization matrix based on persona impact
4. Design role-specific dashboard mockups
5. Establish persona-based testing scenarios for QA
