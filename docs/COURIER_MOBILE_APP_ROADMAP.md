# BARQ Courier Mobile App - Product Roadmap

## Executive Summary

The BARQ Courier Mobile App is a dedicated mobile application for delivery couriers that enables them to manage their daily operations, track deliveries, submit requests, and communicate with the fleet management system in real-time.

---

## Product Vision

> **"Empower couriers with a seamless, intuitive mobile experience that simplifies their daily work, provides real-time information, and enables instant communication with the BARQ Fleet Management system."**

---

## Target Users

| User Type | Description |
|-----------|-------------|
| **Active Couriers** | Full-time delivery personnel assigned to BARQ |
| **Freelance Couriers** | Part-time/contract-based delivery personnel |
| **Trial Couriers** | New couriers in onboarding/probation period |

---

## App Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    COURIER MOBILE APP                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   Home   │ │Deliveries│ │ Requests │ │ Profile  │           │
│  │Dashboard │ │ & Routes │ │ & Forms  │ │& Settings│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
├─────────────────────────────────────────────────────────────────┤
│              GraphQL API Gateway (Real-time Sync)               │
├─────────────────────────────────────────────────────────────────┤
│                 BARQ Fleet Management Backend                   │
└─────────────────────────────────────────────────────────────────┘
```

---

# PHASE 1: Core Features (MVP)

## 1.1 Authentication & Onboarding

### Login Screen
- **BARQ ID Login**: Enter BARQ ID + Password
- **Mobile Number Login**: OTP-based authentication
- **Biometric Login**: Face ID / Fingerprint (after initial setup)
- **Remember Device**: Stay logged in on trusted devices

### First-Time Setup
- Welcome walkthrough (3-4 screens)
- Permission requests (Location, Camera, Notifications)
- Profile verification
- Emergency contact setup

---

## 1.2 Home Dashboard

### Daily Overview Card
```
┌─────────────────────────────────────────┐
│  Good Morning, Ahmed! ☀️                 │
│  Tuesday, December 3, 2024              │
├─────────────────────────────────────────┤
│  📦 Today's Deliveries                   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │  12 │ │  8  │ │  3  │ │  1  │       │
│  │Total│ │Done │ │Left │ │Failed│       │
│  └─────┘ └─────┘ └─────┘ └─────┘       │
├─────────────────────────────────────────┤
│  💰 COD to Collect: SAR 1,250           │
│  🛵 Vehicle: Honda PCX (BRQ-1234)       │
└─────────────────────────────────────────┘
```

### Quick Actions
| Action | Description |
|--------|-------------|
| Start Shift | Clock in for the day |
| End Shift | Clock out and submit daily report |
| View Route | See today's optimized route |
| Report Issue | Quick incident reporting |

### Alerts & Notifications
- Pending approval notifications
- Document expiry warnings (Iqama, License)
- New delivery assignments
- Shift reminders

---

## 1.3 Attendance Module

### Clock In/Out Screen
```
┌─────────────────────────────────────────┐
│        ATTENDANCE                        │
├─────────────────────────────────────────┤
│                                          │
│           ┌──────────────┐               │
│           │   09:32 AM   │               │
│           │   CLOCK IN   │               │
│           └──────────────┘               │
│                                          │
│  📍 Location: Riyadh - Al Olaya         │
│  🛵 Vehicle: Honda PCX - BRQ-1234       │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │     [START SHIFT]                  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Today's Schedule: 09:00 AM - 06:00 PM  │
│  Break: 1:00 PM - 2:00 PM               │
└─────────────────────────────────────────┘
```

### Features
- **GPS-verified clock in/out**
- **Photo capture** at clock-in (optional)
- **Late arrival notification** to supervisor
- **Overtime tracking**
- **Break time management**

### Attendance History
- View past 30 days attendance
- See hours worked per day/week/month
- Export attendance report

---

## 1.4 Delivery Management

### Delivery List View
```
┌─────────────────────────────────────────┐
│  TODAY'S DELIVERIES                      │
│  ┌─────────────────────────────────────┐│
│  │ 🟢 #DEL-001 - Al Olaya              ││
│  │    Customer: Mohammed Ali           ││
│  │    COD: SAR 150                     ││
│  │    [Navigate] [Call] [Details]      ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ 🟡 #DEL-002 - King Fahd Road        ││
│  │    Customer: Sara Ahmed             ││
│  │    COD: SAR 0 (Prepaid)             ││
│  │    [Navigate] [Call] [Details]      ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ ⚪ #DEL-003 - Al Malaz              ││
│  │    Customer: Khalid Hassan          ││
│  │    COD: SAR 320                     ││
│  │    [Navigate] [Call] [Details]      ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Delivery Detail Screen
- Customer name & contact
- Pickup address with map
- Delivery address with map
- Package details (size, weight, special handling)
- COD amount
- Special instructions
- Order history with customer

### Delivery Actions
| Status | Actions Available |
|--------|-------------------|
| Pending | Accept, Reject (with reason) |
| Accepted | Start Pickup, Contact Customer |
| Picked Up | Start Delivery, Report Issue |
| In Transit | Complete Delivery, Mark Failed |
| Delivered | Confirm COD, Get Signature |
| Failed | Select Reason, Reschedule, Return |

### Delivery Completion Form
```
┌─────────────────────────────────────────┐
│  COMPLETE DELIVERY                       │
├─────────────────────────────────────────┤
│  Order: #DEL-001                         │
│  Customer: Mohammed Ali                  │
├─────────────────────────────────────────┤
│  COD Collection                          │
│  Amount Due: SAR 150                     │
│  ┌────────────────────────────────────┐ │
│  │ Amount Received: [SAR 150      ]   │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Proof of Delivery                       │
│  ┌────────────────────────────────────┐ │
│  │ [📷 Take Photo]  [✍️ Get Signature]│ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Received By:                            │
│  ┌────────────────────────────────────┐ │
│  │ ○ Customer                         │ │
│  │ ○ Family Member                    │ │
│  │ ○ Security/Reception               │ │
│  │ ○ Left at Door                     │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Notes (Optional):                       │
│  ┌────────────────────────────────────┐ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [        CONFIRM DELIVERY        ]     │
└─────────────────────────────────────────┘
```

### Failed Delivery Form
```
┌─────────────────────────────────────────┐
│  MARK AS FAILED                          │
├─────────────────────────────────────────┤
│  Order: #DEL-001                         │
├─────────────────────────────────────────┤
│  Reason for Failure:                     │
│  ┌────────────────────────────────────┐ │
│  │ ○ Customer Not Available           │ │
│  │ ○ Wrong Address                    │ │
│  │ ○ Customer Refused                 │ │
│  │ ○ Cannot Access Location           │ │
│  │ ○ Customer Requested Reschedule    │ │
│  │ ○ Package Damaged                  │ │
│  │ ○ Other (specify below)            │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  📷 Photo Evidence (Required):           │
│  ┌────────────────────────────────────┐ │
│  │      [Take Photo of Location]      │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Additional Notes:                       │
│  ┌────────────────────────────────────┐ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [      SUBMIT FAILED DELIVERY      ]   │
└─────────────────────────────────────────┘
```

---

## 1.5 Route & Navigation

### Route Overview
```
┌─────────────────────────────────────────┐
│  TODAY'S ROUTE                           │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │        [MAP VIEW]                   ││
│  │    Shows all stops on map           ││
│  │    with optimized path              ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  📍 8 Stops | 📏 45 km | ⏱️ ~3.5 hrs    │
├─────────────────────────────────────────┤
│  1. 🟢 Al Olaya Mall (Pickup)           │
│  2. ⚪ King Fahd Road (Delivery)        │
│  3. ⚪ Al Malaz (Delivery)              │
│  4. ⚪ Al Sulimaniyah (Delivery)        │
│  5. ⚪ Al Muruj (Delivery)              │
│  ...                                     │
├─────────────────────────────────────────┤
│  [START NAVIGATION] [OPTIMIZE ROUTE]    │
└─────────────────────────────────────────┘
```

### Navigation Features
- Integration with Google Maps / Apple Maps
- Turn-by-turn directions
- Real-time traffic updates
- ETA calculations
- Re-routing on traffic delays

---

## 1.6 COD Management

### COD Summary
```
┌─────────────────────────────────────────┐
│  COD COLLECTION                          │
├─────────────────────────────────────────┤
│  Today's Summary                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │SAR 2,500│ │SAR 1,250│ │SAR 1,250│   │
│  │  Total  │ │Collected│ │ Pending │   │
│  └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────┤
│  Collection History                      │
│  ┌─────────────────────────────────────┐│
│  │ #DEL-001 | SAR 150 | ✅ Collected   ││
│  │ #DEL-002 | SAR 0   | - Prepaid      ││
│  │ #DEL-003 | SAR 320 | ⏳ Pending     ││
│  │ #DEL-004 | SAR 180 | ✅ Collected   ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  [DEPOSIT COD] [VIEW HISTORY]           │
└─────────────────────────────────────────┘
```

### COD Deposit Form
```
┌─────────────────────────────────────────┐
│  DEPOSIT COD                             │
├─────────────────────────────────────────┤
│  Amount to Deposit: SAR 1,250           │
├─────────────────────────────────────────┤
│  Deposit Method:                         │
│  ○ Bank Transfer                         │
│  ○ Cash to Supervisor                    │
│  ○ Office Drop-off                       │
├─────────────────────────────────────────┤
│  Reference Number:                       │
│  ┌────────────────────────────────────┐ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  📷 Receipt Photo:                       │
│  ┌────────────────────────────────────┐ │
│  │      [Upload Receipt Image]        │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [        CONFIRM DEPOSIT        ]      │
└─────────────────────────────────────────┘
```

---

# PHASE 2: HR & Self-Service

## 2.1 Leave Request Module

### Leave Request Form
```
┌─────────────────────────────────────────┐
│  REQUEST LEAVE                           │
├─────────────────────────────────────────┤
│  Leave Type:                             │
│  ┌────────────────────────────────────┐ │
│  │ ○ Annual Leave                     │ │
│  │ ○ Sick Leave                       │ │
│  │ ○ Emergency Leave                  │ │
│  │ ○ Unpaid Leave                     │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Duration:                               │
│  From: [📅 Select Date]                  │
│  To:   [📅 Select Date]                  │
│  Days: 3 working days                    │
├─────────────────────────────────────────┤
│  Reason:                                 │
│  ┌────────────────────────────────────┐ │
│  │ Family emergency - need to travel  │ │
│  │ to hometown                        │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  📎 Attachment (for sick leave):         │
│  [Upload Medical Certificate]            │
├─────────────────────────────────────────┤
│  [        SUBMIT REQUEST        ]       │
└─────────────────────────────────────────┘
```

### Leave Balance View
```
┌─────────────────────────────────────────┐
│  MY LEAVE BALANCE                        │
├─────────────────────────────────────────┤
│  Annual Leave                            │
│  ████████░░░░░░░░  12/21 days remaining │
│                                          │
│  Sick Leave                              │
│  ██████████████░░  8/10 days remaining  │
│                                          │
│  Emergency Leave                         │
│  ██████████████░░  3/5 days remaining   │
├─────────────────────────────────────────┤
│  Recent Requests                         │
│  ┌─────────────────────────────────────┐│
│  │ Dec 15-17 | Annual | ✅ Approved    ││
│  │ Nov 5     | Sick   | ✅ Approved    ││
│  │ Oct 20-22 | Annual | ✅ Approved    ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  [REQUEST NEW LEAVE]                     │
└─────────────────────────────────────────┘
```

### Leave Request Status
- **Pending** → Awaiting supervisor approval
- **Approved** → Leave granted
- **Rejected** → Leave denied (with reason)
- **Cancelled** → Cancelled by courier

---

## 2.2 Loan Request Module

### Loan Request Form
```
┌─────────────────────────────────────────┐
│  REQUEST LOAN                            │
├─────────────────────────────────────────┤
│  Loan Amount:                            │
│  ┌────────────────────────────────────┐ │
│  │ SAR [5000                       ]  │ │
│  └────────────────────────────────────┘ │
│  Min: SAR 500 | Max: SAR 10,000         │
├─────────────────────────────────────────┤
│  Loan Type:                              │
│  ┌────────────────────────────────────┐ │
│  │ ○ Salary Advance                   │ │
│  │ ○ Emergency Loan                   │ │
│  │ ○ Personal Loan                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Repayment Period:                       │
│  ┌────────────────────────────────────┐ │
│  │ [3 months ▼]                       │ │
│  └────────────────────────────────────┘ │
│  Monthly Deduction: SAR 1,666.67        │
├─────────────────────────────────────────┤
│  Purpose/Reason:                         │
│  ┌────────────────────────────────────┐ │
│  │ Medical expenses for family        │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  📎 Supporting Documents:                │
│  [Upload Documents]                      │
├─────────────────────────────────────────┤
│  [        SUBMIT REQUEST        ]       │
└─────────────────────────────────────────┘
```

### Active Loans View
```
┌─────────────────────────────────────────┐
│  MY LOANS                                │
├─────────────────────────────────────────┤
│  Active Loan                             │
│  ┌─────────────────────────────────────┐│
│  │ Loan #LN-2024-001                   ││
│  │ Amount: SAR 5,000                   ││
│  │ Outstanding: SAR 3,333.34           ││
│  │ Monthly Deduction: SAR 833.33       ││
│  │ Remaining: 4 payments               ││
│  │ ████████████░░░░░░ 67% paid        ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Payment Schedule                        │
│  ┌─────────────────────────────────────┐│
│  │ Jan 2024 | SAR 833.33 | ✅ Paid     ││
│  │ Feb 2024 | SAR 833.33 | ✅ Paid     ││
│  │ Mar 2024 | SAR 833.33 | ⏳ Due      ││
│  │ Apr 2024 | SAR 833.33 | ⏳ Upcoming ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  [REQUEST NEW LOAN]                      │
└─────────────────────────────────────────┘
```

---

## 2.3 Salary & Earnings

### Salary View
```
┌─────────────────────────────────────────┐
│  MY EARNINGS                             │
│  November 2024                           │
├─────────────────────────────────────────┤
│  Base Salary         SAR 3,500.00       │
│  Delivery Bonus      SAR   850.00       │
│  Overtime            SAR   420.00       │
│  Allowances          SAR   300.00       │
│  ─────────────────────────────────────  │
│  Gross               SAR 5,070.00       │
│  ─────────────────────────────────────  │
│  GOSI Deduction      SAR  (175.00)      │
│  Loan Deduction      SAR  (833.33)      │
│  Penalties           SAR   (50.00)      │
│  ─────────────────────────────────────  │
│  Net Salary          SAR 4,011.67       │
├─────────────────────────────────────────┤
│  Payment Status: ✅ Paid on Nov 28      │
├─────────────────────────────────────────┤
│  [VIEW PAYSLIP PDF] [HISTORY]           │
└─────────────────────────────────────────┘
```

### Earnings History
- Monthly salary breakdown
- Year-to-date earnings
- Bonus history
- Deduction details
- Download payslips (PDF)

---

## 2.4 Bonuses & Penalties

### Bonuses View
```
┌─────────────────────────────────────────┐
│  MY BONUSES                              │
├─────────────────────────────────────────┤
│  This Month                              │
│  ┌─────────────────────────────────────┐│
│  │ Performance Bonus   SAR 500  ✅ Paid ││
│  │ Attendance Bonus    SAR 200  ✅ Paid ││
│  │ Customer Rating     SAR 150  ⏳ Pend ││
│  └─────────────────────────────────────┘│
│  Total: SAR 850                          │
├─────────────────────────────────────────┤
│  Bonus Criteria                          │
│  ┌─────────────────────────────────────┐│
│  │ 📦 100+ deliveries = SAR 500        ││
│  │ ⏰ Perfect attendance = SAR 200     ││
│  │ ⭐ Rating > 4.8 = SAR 150           ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Penalties View
```
┌─────────────────────────────────────────┐
│  MY PENALTIES                            │
├─────────────────────────────────────────┤
│  This Month                              │
│  ┌─────────────────────────────────────┐│
│  │ Late Arrival (Nov 5) SAR 25        ││
│  │ Failed Delivery      SAR 25        ││
│  └─────────────────────────────────────┘│
│  Total: SAR 50                           │
├─────────────────────────────────────────┤
│  [DISPUTE PENALTY]                       │
└─────────────────────────────────────────┘
```

---

# PHASE 3: Documents & Compliance

## 3.1 Document Management

### My Documents
```
┌─────────────────────────────────────────┐
│  MY DOCUMENTS                            │
├─────────────────────────────────────────┤
│  ⚠️ 2 documents expiring soon            │
├─────────────────────────────────────────┤
│  Identification                          │
│  ┌─────────────────────────────────────┐│
│  │ 🔴 Iqama                             ││
│  │    Expires: Dec 15, 2024 (12 days)  ││
│  │    [View] [Upload New]              ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ 🟢 Passport                          ││
│  │    Expires: Mar 2026                ││
│  │    [View]                           ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Driver's License                        │
│  ┌─────────────────────────────────────┐│
│  │ 🟡 License                           ││
│  │    Expires: Jan 30, 2025 (58 days)  ││
│  │    [View] [Upload New]              ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Employment                              │
│  ┌─────────────────────────────────────┐│
│  │ 🟢 Employment Contract               ││
│  │    Valid until: Dec 2025            ││
│  │    [View]                           ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Document Upload Form
```
┌─────────────────────────────────────────┐
│  UPLOAD DOCUMENT                         │
├─────────────────────────────────────────┤
│  Document Type:                          │
│  ┌────────────────────────────────────┐ │
│  │ [Iqama ▼]                          │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Document Number:                        │
│  ┌────────────────────────────────────┐ │
│  │ [2456789012                     ]  │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Issue Date: [📅 Select]                 │
│  Expiry Date: [📅 Select]                │
├─────────────────────────────────────────┤
│  Upload File:                            │
│  ┌────────────────────────────────────┐ │
│  │  📷 Take Photo                      │ │
│  │  📁 Choose from Gallery             │ │
│  │  📄 Upload PDF                      │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [        UPLOAD DOCUMENT        ]      │
└─────────────────────────────────────────┘
```

---

## 3.2 Asset Management

### Assigned Assets
```
┌─────────────────────────────────────────┐
│  MY ASSETS                               │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │ 📱 Mobile Device                     ││
│  │    Samsung A54                       ││
│  │    Assigned: Oct 1, 2024            ││
│  │    Condition: Good                  ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ 👕 Uniform Set                       ││
│  │    2x Polo, 2x Pants                ││
│  │    Assigned: Oct 1, 2024            ││
│  │    Condition: Good                  ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ 🎒 Delivery Bag                      ││
│  │    Thermal Bag (Large)              ││
│  │    Assigned: Oct 1, 2024            ││
│  │    Condition: Good                  ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  [REPORT DAMAGED ASSET]                  │
└─────────────────────────────────────────┘
```

---

# PHASE 4: Vehicle & Safety

## 4.1 Vehicle Information

### My Vehicle
```
┌─────────────────────────────────────────┐
│  MY VEHICLE                              │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │  🛵 Honda PCX 150                    ││
│  │     Plate: BRQ-1234                 ││
│  │     Color: White                    ││
│  │     Year: 2023                      ││
│  │     Assignment: Permanent           ││
│  │     Since: Jan 15, 2024             ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Status                                  │
│  ┌─────────────────────────────────────┐│
│  │ Mileage: 12,450 km                  ││
│  │ Fuel: 75% ████████░░                ││
│  │ Last Service: Nov 15, 2024          ││
│  │ Next Service: Dec 15, 2024 (due)    ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Documents                               │
│  ┌─────────────────────────────────────┐│
│  │ 🟢 Registration (Mulkiya)           ││
│  │ 🟢 Insurance                        ││
│  │ 🟡 Service Book                     ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  [DAILY CHECKLIST] [REPORT ISSUE]       │
└─────────────────────────────────────────┘
```

### Daily Vehicle Checklist
```
┌─────────────────────────────────────────┐
│  DAILY VEHICLE CHECK                     │
├─────────────────────────────────────────┤
│  Before starting your shift, verify:     │
│                                          │
│  ☑️ Tires in good condition              │
│  ☑️ Brakes working properly              │
│  ☑️ Lights functional (front/rear)       │
│  ☑️ Mirrors properly adjusted            │
│  ☑️ Fuel level adequate                  │
│  ☑️ Horn working                         │
│  ☐ No visible damage                     │
│  ☐ Delivery box secure                   │
├─────────────────────────────────────────┤
│  Current Mileage:                        │
│  ┌────────────────────────────────────┐ │
│  │ [12,450 km                      ]  │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  [SUBMIT CHECKLIST]                      │
└─────────────────────────────────────────┘
```

---

## 4.2 Incident Reporting

### Report Incident Form
```
┌─────────────────────────────────────────┐
│  REPORT INCIDENT                         │
├─────────────────────────────────────────┤
│  Incident Type:                          │
│  ┌────────────────────────────────────┐ │
│  │ ○ Traffic Accident                 │ │
│  │ ○ Vehicle Breakdown                │ │
│  │ ○ Theft/Robbery                    │ │
│  │ ○ Package Damage                   │ │
│  │ ○ Customer Complaint               │ │
│  │ ○ Other                            │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Date & Time:                            │
│  [📅 Dec 3, 2024] [🕐 14:30]             │
├─────────────────────────────────────────┤
│  Location:                               │
│  ┌────────────────────────────────────┐ │
│  │ 📍 Use Current Location            │ │
│  │ ✏️ Enter Manually                   │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Description:                            │
│  ┌────────────────────────────────────┐ │
│  │ Minor collision at intersection... │ │
│  │                                    │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  📷 Photos (Required):                   │
│  ┌────────────────────────────────────┐ │
│  │ [+] Add Photos (min 2)             │ │
│  └────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│  Injuries?  ○ Yes  ● No                  │
│  Police Report?  ○ Yes  ● No             │
├─────────────────────────────────────────┤
│  [        SUBMIT REPORT        ]        │
└─────────────────────────────────────────┘
```

---

# PHASE 5: Profile & Settings

## 5.1 Courier Profile

### Profile Screen
```
┌─────────────────────────────────────────┐
│  ┌─────────┐                             │
│  │  PHOTO  │  Ahmed Mohammed             │
│  │         │  Courier ID: BRQ-0042       │
│  └─────────┘  ⭐ 4.8 Rating               │
├─────────────────────────────────────────┤
│  Contact Information                     │
│  📱 +966 55 123 4567                     │
│  ✉️ ahmed.m@barq.sa                      │
│  📍 Riyadh, Al Olaya                     │
├─────────────────────────────────────────┤
│  Employment                              │
│  🏢 Status: Active                       │
│  📅 Joined: January 15, 2024             │
│  🚀 Project: E-Commerce                  │
│  👤 Supervisor: Khalid Hassan            │
├─────────────────────────────────────────┤
│  Performance This Month                  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │ 245 │ │ 98% │ │4.8⭐│ │ 12  │       │
│  │Deliv│ │OnTim│ │Ratng│ │Days │       │
│  └─────┘ └─────┘ └─────┘ └─────┘       │
├─────────────────────────────────────────┤
│  [EDIT PROFILE] [SETTINGS]              │
└─────────────────────────────────────────┘
```

### Edit Profile Form
```
┌─────────────────────────────────────────┐
│  EDIT PROFILE                            │
├─────────────────────────────────────────┤
│  Profile Photo                           │
│  ┌─────────────────────────────────────┐│
│  │      [📷 Change Photo]              ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Personal Information                    │
│  Full Name: [Ahmed Mohammed        ]     │
│  Email: [ahmed.m@barq.sa           ]     │
│  Mobile: [+966 55 123 4567         ]     │
├─────────────────────────────────────────┤
│  Emergency Contact                       │
│  Name: [Mohammed Ahmed             ]     │
│  Phone: [+966 55 987 6543          ]     │
│  Relationship: [Father ▼           ]     │
├─────────────────────────────────────────┤
│  Bank Details                            │
│  Bank: [Al Rajhi Bank ▼            ]     │
│  IBAN: [SA02 8000 0000 1234 5678 9]     │
├─────────────────────────────────────────┤
│  [        SAVE CHANGES        ]         │
└─────────────────────────────────────────┘
```

---

## 5.2 App Settings

### Settings Screen
```
┌─────────────────────────────────────────┐
│  SETTINGS                                │
├─────────────────────────────────────────┤
│  Notifications                           │
│  ┌─────────────────────────────────────┐│
│  │ Push Notifications      [████ ON]   ││
│  │ Delivery Alerts         [████ ON]   ││
│  │ Shift Reminders         [████ ON]   ││
│  │ Promotional             [░░░░ OFF]  ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Preferences                             │
│  ┌─────────────────────────────────────┐│
│  │ Language         [English ▼]        ││
│  │ Navigation App   [Google Maps ▼]    ││
│  │ Dark Mode        [░░░░ OFF]         ││
│  │ Sound Effects    [████ ON]          ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Security                                │
│  ┌─────────────────────────────────────┐│
│  │ Change Password         [>]         ││
│  │ Biometric Login         [████ ON]   ││
│  │ Two-Factor Auth         [████ ON]   ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Support                                 │
│  ┌─────────────────────────────────────┐│
│  │ Help Center              [>]        ││
│  │ Contact Support          [>]        ││
│  │ Report a Bug             [>]        ││
│  │ Terms & Conditions       [>]        ││
│  │ Privacy Policy           [>]        ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  App Version: 1.0.0                      │
│  [LOG OUT]                               │
└─────────────────────────────────────────┘
```

---

# PHASE 6: Communication & Support

## 6.1 Notifications Center

### Notifications List
```
┌─────────────────────────────────────────┐
│  NOTIFICATIONS                           │
├─────────────────────────────────────────┤
│  Today                                   │
│  ┌─────────────────────────────────────┐│
│  │ 🔔 New Delivery Assigned            ││
│  │    Order #DEL-005 to Al Malaz       ││
│  │    2 minutes ago                    ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ ✅ Leave Request Approved           ││
│  │    Dec 15-17 annual leave approved  ││
│  │    1 hour ago                       ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Yesterday                               │
│  ┌─────────────────────────────────────┐│
│  │ 💰 Salary Processed                 ││
│  │    November salary credited         ││
│  │    Yesterday at 4:30 PM             ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │ ⚠️ Document Expiring Soon           ││
│  │    Iqama expires in 12 days         ││
│  │    Yesterday at 9:00 AM             ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

---

## 6.2 Support Chat

### Help & Support
```
┌─────────────────────────────────────────┐
│  HELP & SUPPORT                          │
├─────────────────────────────────────────┤
│  How can we help?                        │
│  ┌─────────────────────────────────────┐│
│  │ 🔍 Search FAQs...                   ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Quick Help                              │
│  ┌─────────────────────────────────────┐│
│  │ 📱 App Issues                        ││
│  │ 🛵 Vehicle Problems                  ││
│  │ 📦 Delivery Help                     ││
│  │ 💰 Payment Questions                 ││
│  │ 📄 Document Help                     ││
│  │ 👤 Account Issues                    ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Contact Support                         │
│  ┌─────────────────────────────────────┐│
│  │ 💬 Live Chat (9AM-9PM)              ││
│  │ 📞 Call: 800-BARQ (2279)            ││
│  │ ✉️ Email: support@barq.sa           ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

---

# Feature Summary by Phase

## MVP (Phase 1)
| Feature | Priority | Status |
|---------|----------|--------|
| Login/Authentication | P0 | Required |
| Home Dashboard | P0 | Required |
| Attendance (Clock In/Out) | P0 | Required |
| Delivery List & Management | P0 | Required |
| Delivery Completion Forms | P0 | Required |
| Route Navigation | P0 | Required |
| COD Collection | P0 | Required |
| Push Notifications | P0 | Required |

## Phase 2 - HR Self-Service
| Feature | Priority | Status |
|---------|----------|--------|
| Leave Requests | P1 | Planned |
| Leave Balance | P1 | Planned |
| Loan Requests | P1 | Planned |
| Salary View | P1 | Planned |
| Bonuses View | P2 | Planned |
| Penalties View | P2 | Planned |

## Phase 3 - Documents
| Feature | Priority | Status |
|---------|----------|--------|
| Document Viewer | P1 | Planned |
| Document Upload | P1 | Planned |
| Expiry Alerts | P1 | Planned |
| Asset Management | P2 | Planned |

## Phase 4 - Vehicle
| Feature | Priority | Status |
|---------|----------|--------|
| Vehicle Info | P1 | Planned |
| Daily Checklist | P1 | Planned |
| Incident Reporting | P1 | Planned |
| Maintenance Alerts | P2 | Planned |

## Phase 5 - Profile
| Feature | Priority | Status |
|---------|----------|--------|
| Profile View | P1 | Planned |
| Edit Profile | P1 | Planned |
| App Settings | P1 | Planned |
| Security Settings | P2 | Planned |

## Phase 6 - Support
| Feature | Priority | Status |
|---------|----------|--------|
| Notification Center | P1 | Planned |
| Help Center | P2 | Planned |
| Live Chat | P2 | Planned |
| FAQ | P2 | Planned |

---

# Technical Requirements

## Platform Support
- **iOS**: 14.0+
- **Android**: 8.0+ (API 26)

## Core Technologies
- **Framework**: React Native / Flutter
- **API**: GraphQL with real-time subscriptions
- **State Management**: Redux/Zustand (React Native) or Riverpod (Flutter)
- **Offline Support**: SQLite local database
- **Maps**: Google Maps SDK
- **Push**: Firebase Cloud Messaging

## Key Integrations
- BARQ Fleet Management Backend (GraphQL API)
- Google Maps / Apple Maps
- Firebase (Auth, Push, Analytics)
- Camera & Gallery
- GPS Location Services
- Biometric Authentication

## Offline Capabilities
- Cache delivery list
- Queue completed deliveries for sync
- Store offline attendance records
- Cache profile data
- Download routes for offline navigation

---

# Success Metrics

## Operational KPIs
- Delivery completion rate
- On-time delivery percentage
- COD collection accuracy
- Average deliveries per day

## App Engagement KPIs
- Daily Active Users (DAU)
- Session duration
- Feature adoption rates
- App crash rate

## Courier Satisfaction KPIs
- App Store ratings
- In-app feedback scores
- Support ticket volume
- Feature request frequency

---

# Appendix: Form Field Reference

## All Forms Summary

### 1. Clock In/Out
- GPS location (auto)
- Timestamp (auto)
- Optional photo
- Vehicle mileage

### 2. Delivery Completion
- COD amount received
- Delivery photo
- Signature (optional)
- Receiver type (dropdown)
- Notes

### 3. Failed Delivery
- Failure reason (dropdown)
- Location photo (required)
- Notes
- Reschedule option

### 4. Leave Request
- Leave type (dropdown)
- Start date
- End date
- Reason (text)
- Attachment (optional)

### 5. Loan Request
- Amount
- Loan type (dropdown)
- Repayment period (dropdown)
- Purpose (text)
- Documents (optional)

### 6. Document Upload
- Document type (dropdown)
- Document number
- Issue date
- Expiry date
- File (photo/PDF)

### 7. Incident Report
- Incident type (dropdown)
- Date/time
- Location
- Description
- Photos (required)
- Injuries (yes/no)
- Police report (yes/no)

### 8. Vehicle Checklist
- Checklist items (checkboxes)
- Current mileage
- Issues found (text)
- Photos (if issues)

### 9. COD Deposit
- Deposit amount
- Deposit method (dropdown)
- Reference number
- Receipt photo

### 10. Profile Edit
- Photo
- Mobile number
- Email
- Emergency contact
- Bank details

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Author: BARQ Product Team*
