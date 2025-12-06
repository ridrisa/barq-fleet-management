# BARQ Fleet Management System - User Journey Maps

## Overview

This document maps the critical user journeys through the BARQ Fleet Management system, identifying touchpoints, emotions, pain points, and opportunities for improvement across five key workflows.

**Version:** 1.0
**Last Updated:** December 6, 2025
**Purpose:** UX optimization and process improvement

---

## Journey Map Legend

```
Stages:      Major phases of the journey
Actions:     What the user does
Touchpoints: Pages/features/systems interacted with
Emotions:    😊 Happy  😐 Neutral  😟 Frustrated  😡 Angry  🎉 Delighted
Pain Points: ⚠️  Friction points that slow users down
Opportunities: 💡 Areas for improvement
```

---

# Journey 1: Courier Onboarding

## User Persona
**Name:** Ahmed - HR Manager
**Goal:** Efficiently onboard a new courier and get them ready for first delivery
**Context:** 15-20 new courier hires per month across multiple cities

---

## Journey Stages

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   HIRING    │  DOCUMENT   │   SYSTEM    │   VEHICLE   │  TRAINING & │    FIRST    │
│  COMPLETE   │ COLLECTION  │    SETUP    │ ASSIGNMENT  │ VALIDATION  │  DELIVERY   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
     Day 1         Day 1-2       Day 2-3       Day 3-4       Day 4-5       Day 5+
```

---

### Stage 1: Hiring Complete (Day 1)

**Actions:**
- HR receives hiring approval
- Collects courier personal information
- Prepares to create system record

**Touchpoints:**
- External hiring system
- Paper documents / Email
- Excel tracking sheet

**Emotions:** 😊 Excited to bring new team member

**Pain Points:**
- ⚠️ Information scattered across multiple sources
- ⚠️ No single source of truth for courier data
- ⚠️ Manual data entry prone to errors

**Opportunities:**
- 💡 API integration with HR/recruiting system
- 💡 Digital onboarding form sent to courier's phone
- 💡 Auto-populate from government ID scanning (OCR)

---

### Stage 2: Document Collection (Day 1-2)

**Actions:**
- Request copies of: Iqama, Passport, Driver's License, Bank details
- Verify document expiry dates
- Scan/photograph documents
- Upload to system

**Touchpoints:**
- `/fleet/couriers` - Create New Courier
- Document upload interface
- File management system

**Emotions:** 😐 Neutral - Administrative work

**Pain Points:**
- ⚠️ Couriers forget documents, causing delays
- ⚠️ No validation for document expiry dates at upload
- ⚠️ Image quality issues require re-upload
- ⚠️ No automatic expiry reminders set up

**Opportunities:**
- 💡 Mobile app for courier self-service document upload
- 💡 Real-time expiry validation (reject if < 90 days)
- 💡 Image quality checker with instant feedback
- 💡 Auto-calendar reminders 30/60/90 days before expiry
- 💡 Document checklist with completion tracking

---

### Stage 3: System Setup (Day 2-3)

**Actions:**
- Navigate to Couriers page
- Click "Add Courier" button
- Fill 20+ form fields:
  - Basic info (name, email, mobile, BARQ ID)
  - Employment (employee ID, status, joining date)
  - Documents (Iqama #, expiry, passport, license)
  - Banking (account, IBAN, bank name)
  - Platform IDs (Jahez, Hunger, Mrsool)
- Set status to "ONBOARDING"
- Save courier record

**Touchpoints:**
- `/fleet/couriers` page
- Courier creation form (CourierForm component)
- Database validation

**Emotions:** 😟 Frustrated - Long, tedious form

**Pain Points:**
- ⚠️ Single long form is overwhelming (20+ fields)
- ⚠️ No auto-save; data loss if connection fails
- ⚠️ BARQ ID must be manually generated
- ⚠️ Can't skip optional fields (form UX issue)
- ⚠️ No field help text for complex fields (e.g., IBAN format)
- ⚠️ Duplicate detection happens after full submission

**Opportunities:**
- 💡 Multi-step wizard (4 steps: Basic → Employment → Documents → Banking)
- 💡 Auto-save draft every 30 seconds
- 💡 Auto-generate BARQ ID from pattern (city-date-sequence)
- 💡 Collapsible sections with progress indicators
- 💡 Inline validation with helpful error messages
- 💡 Duplicate check on BARQ ID/email/mobile as user types
- 💡 Pre-fill templates for common courier types

---

### Stage 4: Vehicle Assignment (Day 3-4)

**Actions:**
- Navigate to Vehicle Assignments
- Search for available vehicles in courier's city
- Check vehicle condition and maintenance status
- Create assignment record:
  - Select courier
  - Select vehicle
  - Set assignment type (permanent/temporary)
  - Record start date and mileage
  - Add assignment notes
- Update courier status to "ACTIVE"

**Touchpoints:**
- `/fleet/vehicle-assignments` page
- Assignment creation form
- Vehicle inventory view
- Dashboard stats update

**Emotions:** 😐 Neutral - Routine administrative task

**Pain Points:**
- ⚠️ No visibility into which vehicles are truly available
- ⚠️ Can assign vehicle with pending maintenance
- ⚠️ Manual cross-checking between vehicles and assignments
- ⚠️ Doesn't validate if courier has valid license
- ⚠️ No automatic notification to courier about vehicle

**Opportunities:**
- 💡 "Available Vehicles" smart filter (exclude maintenance/assigned)
- 💡 Vehicle recommendation based on courier city/project type
- 💡 Pre-assignment validation checklist:
  - ✓ Courier has valid license
  - ✓ Vehicle passed inspection
  - ✓ No pending maintenance
  - ✓ Insurance valid
- 💡 Auto-SMS/email to courier with vehicle details
- 💡 Digital vehicle handover checklist with photos
- 💡 QR code on vehicle for easy lookup

---

### Stage 5: Training & Validation (Day 4-5)

**Actions:**
- Schedule safety orientation
- Conduct delivery platform training (Jahez/Hunger/Mrsool)
- Add platform IDs to courier record
- Verify FMS GPS tracking setup
- Test dispatch system integration
- Complete compliance checklist

**Touchpoints:**
- Training management system (external)
- `/fleet/couriers` - Edit courier
- Platform IDs field entry
- FMS integration validation
- Manual checklist (paper/Excel)

**Emotions:** 😟 Frustrated - Disconnected systems

**Pain Points:**
- ⚠️ Training completion not tracked in BARQ system
- ⚠️ Platform IDs entered manually (typo risk)
- ⚠️ FMS sync is manual and often fails silently
- ⚠️ No unified "Onboarding Checklist" view
- ⚠️ Can't see progress across multiple new couriers
- ⚠️ Compliance requirements vary by city but not enforced

**Opportunities:**
- 💡 Integrated onboarding workflow with checklist:
  - [ ] Documents verified
  - [ ] System record created
  - [ ] Vehicle assigned
  - [ ] Safety training complete
  - [ ] Platform accounts active
  - [ ] FMS tracking verified
  - [ ] First test delivery
- 💡 API integration with training platform
- 💡 Auto-sync platform IDs from partner APIs
- 💡 FMS health check with visual status indicator
- 💡 Onboarding dashboard showing all new couriers
- 💡 City-specific compliance rules engine

---

### Stage 6: First Delivery (Day 5+)

**Actions:**
- Assign simple test delivery to new courier
- Monitor delivery via GPS tracking
- Evaluate performance and provide feedback
- Mark onboarding complete
- Change courier status from "ONBOARDING" to "ACTIVE"

**Touchpoints:**
- `/operations/deliveries` page
- Dispatch assignment interface
- Real-time GPS tracking map
- Performance evaluation form
- Courier record status update

**Emotions:** 🎉 Delighted - New courier successfully onboarded!

**Pain Points:**
- ⚠️ Test delivery looks identical to regular delivery
- ⚠️ No structured feedback collection for first delivery
- ⚠️ Onboarding completion is manual status change
- ⚠️ No celebration/welcome notification to courier
- ⚠️ Performance baseline not established

**Opportunities:**
- 💡 "Trial Delivery" flag with special handling
- 💡 First-delivery evaluation form with key metrics:
  - Timeliness
  - Customer service
  - App usage proficiency
  - Safety compliance
- 💡 Automatic status change to ACTIVE after successful first delivery
- 💡 Welcome message + gamification (badges for milestones)
- 💡 30-day onboarding follow-up checklist
- 💡 Performance baseline dashboard for new couriers

---

## Journey Summary: Courier Onboarding

**Total Duration:** 5-7 days
**Key Touchpoints:** 8 major touchpoints
**Critical Pain Points:** 14 identified
**High-Impact Opportunities:** 28 improvement areas

### Top 3 Quick Wins
1. **Multi-step form wizard** - Reduce cognitive load during courier creation
2. **Onboarding checklist dashboard** - Single view of all new courier progress
3. **Auto-save drafts** - Prevent data loss and user frustration

### Top 3 Long-term Improvements
1. **Integrated onboarding workflow engine** - End-to-end automation
2. **Mobile self-service app** - Courier uploads docs, completes forms
3. **API integrations** - HR system, training platform, delivery partners

---

# Journey 2: Daily Dispatch Flow

## User Persona
**Name:** Fatima - Dispatch Manager
**Goal:** Efficiently assign deliveries to couriers from morning shift start to end of day
**Context:** Manages 40-60 active couriers, processes 200-400 deliveries daily

---

## Journey Stages

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   SHIFT     │   DELIVERY  │   COURIER   │  DISPATCH & │  REAL-TIME  │  END OF DAY │
│   START     │   INTAKE    │  ALLOCATION │   MONITOR   │ ADJUSTMENTS │   CLOSEOUT  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   6:00-7:00     7:00-9:00     9:00-11:00    11:00-18:00   Throughout    18:00-20:00
```

---

### Stage 1: Shift Start (6:00-7:00 AM)

**Actions:**
- Log into BARQ system
- Review dashboard for today's overview
- Check courier attendance status
- Review vehicle availability
- Identify any issues (absences, vehicle problems)
- Plan day's capacity and zones

**Touchpoints:**
- Login page (`/login`)
- Dashboard (`/dashboard`)
- Attendance tracking (manual check)
- Vehicle status view
- Shift planning spreadsheet (external)

**Emotions:** 😐 Neutral - Starting the day

**Pain Points:**
- ⚠️ No unified "Morning Briefing" dashboard
- ⚠️ Courier attendance tracked externally (not in BARQ)
- ⚠️ Vehicle issues discovered reactively, not proactively
- ⚠️ Capacity planning done manually in Excel
- ⚠️ Weather/traffic not considered in planning

**Opportunities:**
- 💡 "Dispatch Command Center" dashboard:
  - Today's stats (couriers on duty, deliveries pending, capacity)
  - Attendance roll call with quick check-in
  - Vehicle health alerts
  - Zone-wise demand forecast
  - Weather and traffic overlay
- 💡 Mobile attendance app for couriers to self-check-in
- 💡 Predictive capacity recommendations
- 💡 Automated shift readiness report
- 💡 Integration with zone-based demand forecasting

---

### Stage 2: Delivery Intake (7:00-9:00 AM)

**Actions:**
- Receive delivery orders from multiple platforms:
  - Jahez
  - Hunger Station
  - Mrsool
  - Direct clients
  - E-commerce partners
- Manually enter delivery details:
  - Tracking number
  - Pickup address
  - Delivery address
  - Customer name and phone
  - COD amount
  - Special instructions
- Prioritize based on SLA/urgency
- Group by zone for efficient routing

**Touchpoints:**
- Platform notification emails/portals (external)
- `/operations/deliveries` - Create Delivery
- Delivery form entry
- Priority queue management
- Zone mapping (mental model)

**Emotions:** 😟 Frustrated - High-volume data entry

**Pain Points:**
- ⚠️ Manual copy-paste from 5+ different sources
- ⚠️ High risk of data entry errors (addresses, phone numbers)
- ⚠️ No API integration with delivery platforms
- ⚠️ Duplicate deliveries not detected automatically
- ⚠️ Priority rules are in dispatcher's head, not system
- ⚠️ Zone assignment is manual guesswork
- ⚠️ Peak hours create massive backlog (200+ deliveries to enter)

**Opportunities:**
- 💡 **Critical:** API integrations with all major platforms
- 💡 Bulk import via CSV/Excel with validation
- 💡 Auto-geocoding of addresses with zone detection
- 💡 Duplicate detection on tracking number
- 💡 Priority scoring engine:
  - SLA deadline
  - COD amount
  - Customer VIP status
  - Delivery urgency flags
- 💡 Auto-batching by zone and time window
- 💡 Email-to-delivery parser (AI extracts order details)
- 💡 Mobile app for quick delivery creation

---

### Stage 3: Courier Allocation (9:00-11:00 AM)

**Actions:**
- Review pending deliveries in priority queue
- Check courier availability and current load
- Manually match deliveries to couriers based on:
  - Geographic proximity
  - Current workload
  - Courier skill/rating
  - Vehicle type
  - Platform assignment
- Create dispatch assignments
- Notify couriers via phone/WhatsApp (external)
- Wait for courier acceptance
- Handle rejections and reassignments

**Touchpoints:**
- `/operations/priority-queue` page
- `/operations/dispatch` - Create Assignment
- Courier availability view
- Manual mental mapping
- Phone/WhatsApp (external communication)
- Delivery status tracking

**Emotions:** 😡 Angry - Extremely manual and time-consuming

**Pain Points:**
- ⚠️ **Critical bottleneck:** Fully manual assignment process
- ⚠️ Can't see courier real-time location
- ⚠️ Don't know courier's current load accurately
- ⚠️ No distance calculation tools
- ⚠️ Route optimization requires external tools (Google Maps)
- ⚠️ Courier acceptance/rejection happens outside system
- ⚠️ No visibility into why couriers reject assignments
- ⚠️ Reassignment starts from scratch (no learning)

**Opportunities:**
- 💡 **Game-changer:** Auto-dispatch algorithm with options:
  - Nearest available courier
  - Load-balanced across fleet
  - Zone-based specialists
  - AI-optimized for cost/time
- 💡 Live courier map showing:
  - Current location
  - Active deliveries
  - Capacity remaining
  - ETA to pickup points
- 💡 One-click assignment with auto-notification
- 💡 In-app courier acceptance (mobile app)
- 💡 Smart reassignment suggestions when rejected
- 💡 Assignment explanation for couriers (why this delivery?)
- 💡 Batch assignment (assign 5-10 deliveries at once)
- 💡 A/B test different dispatch strategies

---

### Stage 4: Dispatch & Monitor (11:00-18:00 PM)

**Actions:**
- Monitor active deliveries in real-time
- Track GPS location via FMS integration
- Handle courier issues (breakdowns, accidents, delays)
- Respond to customer inquiries
- Manage delivery status updates:
  - Picked up
  - In transit
  - Delivered
  - Failed/Returned
- Resolve exceptions and escalations
- Coordinate with supervisors for problem resolution

**Touchpoints:**
- Dashboard delivery tracking
- FMS GPS tracking map (external)
- Delivery status updates (manual)
- Phone calls (couriers and customers)
- `/operations/incidents` (if issues arise)
- Status change interface

**Emotions:** 😟 Frustrated - Reactive firefighting

**Pain Points:**
- ⚠️ No unified real-time tracking view in BARQ
- ⚠️ Switch between BARQ and FMS for GPS
- ⚠️ Status updates rely on courier calling in
- ⚠️ Can't proactively identify at-risk deliveries
- ⚠️ Customer inquiries go to external call center
- ⚠️ No automated alerts for delays/exceptions
- ⚠️ Incident reporting is separate workflow
- ⚠️ No predictive ETA for customers

**Opportunities:**
- 💡 Unified dispatch monitoring dashboard:
  - Live map with all active deliveries
  - Status timeline for each delivery
  - Alerts for delays/issues
  - Customer inquiry integration
- 💡 Embedded FMS GPS tracking in BARQ
- 💡 Auto-status updates from courier mobile app
- 💡 Predictive delay detection (ML):
  - Traffic conditions
  - Courier velocity
  - Historical patterns
- 💡 Automated customer notifications:
  - Out for delivery
  - 15 minutes away
  - Delivered
- 💡 Quick incident creation from delivery view
- 💡 Heat map showing delivery density and bottlenecks

---

### Stage 5: Real-time Adjustments (Throughout Day)

**Actions:**
- Handle courier absence/sickness mid-shift
- Reassign deliveries from courier with vehicle breakdown
- Rush assignments for urgent/VIP deliveries
- Balance load across couriers (some overloaded, some idle)
- Approve overtime or shift extensions
- Coordinate with other zones for support
- Escalate major issues to management

**Touchpoints:**
- Live delivery dashboard
- Courier status management
- Reassignment interface
- Manual coordination (calls/WhatsApp)
- Priority queue adjustments
- Supervisor escalation (external)

**Emotions:** 😟 Frustrated - Constant firefighting

**Pain Points:**
- ⚠️ Reassignment is manual recreation of assignments
- ⚠️ Can't easily see workload imbalance
- ⚠️ No system support for shift extensions
- ⚠️ Cross-zone coordination is ad-hoc
- ⚠️ Lost visibility when courier goes offline
- ⚠️ Emergency assignments disrupt planned routes

**Opportunities:**
- 💡 One-click bulk reassignment (move all deliveries to new courier)
- 💡 Workload balance visualization with rebalance suggestions
- 💡 Shift extension workflow with approval chain
- 💡 Multi-zone dispatcher collaboration tools
- 💡 Courier offline alerts with auto-escalation
- 💡 Emergency assignment queue with SLA tracking
- 💡 AI re-optimization throughout day (dynamic routing)

---

### Stage 6: End of Day Closeout (18:00-20:00 PM)

**Actions:**
- Reconcile all deliveries:
  - Delivered successfully
  - Failed (attempt count)
  - Returned to sender
  - Pending for next day
- Collect COD amounts from couriers
- Record fuel logs and mileage
- Process courier performance data
- Generate daily reports:
  - Delivery success rate
  - Courier productivity
  - Zone performance
  - Revenue collected
- Identify and escalate unresolved issues
- Plan for next day

**Touchpoints:**
- Delivery summary reports
- `/operations/cod-management` page
- Manual COD reconciliation (cash counting)
- Performance tracking spreadsheet
- Various report exports
- Email reports to management

**Emotions:** 😐 Neutral - Tired but routine

**Pain Points:**
- ⚠️ COD reconciliation is manual and error-prone
- ⚠️ Reports require data from multiple pages
- ⚠️ No single "End of Day" workflow
- ⚠️ Can't track COD collection status real-time
- ⚠️ Performance metrics calculated manually
- ⚠️ Failed deliveries require manual follow-up planning
- ⚠️ Reports sent via email (not in-system dashboards)

**Opportunities:**
- 💡 "End of Day Wizard":
  - Step 1: Verify all deliveries closed
  - Step 2: COD reconciliation with variance alerts
  - Step 3: Performance review
  - Step 4: Issue summary
  - Step 5: Generate reports
  - Step 6: Set next-day priorities
- 💡 Real-time COD tracking throughout day
- 💡 Auto-calculated KPIs and performance scores
- 💡 Failed delivery auto-rescheduling
- 💡 In-system report dashboards (no email)
- 💡 Next-day preparation suggestions
- 💡 Anomaly detection (unusual patterns flagged)

---

## Journey Summary: Daily Dispatch Flow

**Total Duration:** 14 hours (6 AM - 8 PM)
**Key Touchpoints:** 15+ major touchpoints
**Critical Pain Points:** 27 identified
**High-Impact Opportunities:** 35 improvement areas

### Top 3 Quick Wins
1. **Unified dispatch dashboard** - Single pane of glass for all operations
2. **Auto-status updates** - Reduce manual status tracking burden
3. **COD real-time tracking** - Know collection status throughout day

### Top 3 Long-term Improvements
1. **Auto-dispatch algorithm** - AI-powered optimal courier assignment
2. **Platform API integrations** - Eliminate manual delivery entry
3. **End-to-end delivery workflow** - From intake to closeout automation

---

# Journey 3: Delivery Lifecycle

## User Persona
**Name:** Khalid - Courier/Driver
**Goal:** Complete deliveries efficiently, safely, and meet customer expectations
**Context:** Handles 15-25 deliveries per shift, uses mobile phone for navigation

---

## Journey Stages

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  ASSIGNMENT │   PICKUP    │    ROUTE    │   DELIVERY  │ CONFIRMATION│  COLLECTION │
│  RECEIVED   │   GOODS     │  TO CUSTOMER│  HANDOVER   │   & PROOF   │     COD     │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
    5 min         15-30 min     5-45 min      5-10 min       2-5 min      2-5 min
```

---

### Stage 1: Assignment Received (5 minutes)

**Actions:**
- Receive delivery assignment notification
- Review delivery details:
  - Pickup location
  - Delivery address
  - Customer name and phone
  - Special instructions
  - COD amount
- Decide whether to accept or reject
- If reject, provide reason
- Plan route mentally
- Check vehicle fuel level

**Touchpoints:**
- Phone call from dispatcher (primary)
- WhatsApp message (secondary)
- Platform app notification (Jahez/Hunger/etc.)
- No BARQ mobile app currently

**Emotions:** 😐 Neutral - Routine assignment

**Pain Points:**
- ⚠️ No dedicated BARQ app for couriers
- ⚠️ Delivery details scattered (call + WhatsApp + platform)
- ⚠️ Can't see delivery on map before accepting
- ⚠️ Unclear pickup address leads to wasted time
- ⚠️ No estimate of delivery time/distance
- ⚠️ Multiple assignments cause confusion
- ⚠️ Can't negotiate or swap with other couriers

**Opportunities:**
- 💡 **Critical:** BARQ mobile courier app
- 💡 Push notification with full delivery card:
  - Map preview
  - Estimated distance/time
  - Current load + this delivery
  - Priority level
- 💡 One-tap accept/reject with quick reasons
- 💡 Voice-activated acceptance (hands-free)
- 💡 Batch assignment view (see all deliveries at once)
- 💡 Route optimization preview
- 💡 Peer-to-peer delivery exchange (with approval)

---

### Stage 2: Pickup Goods (15-30 minutes)

**Actions:**
- Navigate to pickup location using Google Maps
- Find parking (often difficult in city centers)
- Locate merchant/warehouse
- Verify delivery order against pickup slip:
  - Customer name
  - Order number
  - Items/package count
  - COD amount
- Take photo of package (informal backup)
- Load items onto vehicle
- Update status to "Picked Up" (via dispatcher call)
- Get merchant signature (sometimes)

**Touchpoints:**
- Google Maps (external)
- Merchant location (physical)
- Package inspection (manual)
- Phone/camera for photo
- Phone call to dispatcher for status
- Paper pickup slip

**Emotions:** 😟 Frustrated - Navigation and verification issues

**Pain Points:**
- ⚠️ Pickup addresses incomplete or incorrect
- ⚠️ No in-app navigation (must use Google Maps separately)
- ⚠️ Parking challenges waste time
- ⚠️ No barcode/QR scanning for verification
- ⚠️ Package photos not stored in system
- ⚠️ Status update requires calling dispatcher (unsafe while riding)
- ⚠️ No digital proof of pickup
- ⚠️ COD amount mismatch discovered at delivery (too late)

**Opportunities:**
- 💡 Integrated turn-by-turn navigation in courier app
- 💡 Pickup location tips (e.g., "Use back entrance")
- 💡 QR code scanning for package verification
- 💡 In-app photo upload for package condition
- 💡 One-tap status updates (no call needed)
- 💡 Digital pickup signature capture
- 💡 COD amount confirmation at pickup (avoid issues later)
- 💡 Parking spot recommendations (crowdsourced data)
- 💡 Multi-pickup optimization (grab 3 orders from same area)

---

### Stage 3: Route to Customer (5-45 minutes)

**Actions:**
- Open Google Maps with delivery address
- Navigate through traffic
- Monitor GPS signal (sometimes lost)
- Check time to ensure meeting SLA
- Call customer if address unclear (common)
- Deal with road closures/diversions
- Monitor vehicle fuel/health
- Sometimes handle multiple deliveries in sequence

**Touchpoints:**
- Google Maps navigation
- Phone for customer calls
- Vehicle dashboard
- Traffic conditions (real-time experience)
- FMS GPS tracker (passive background)

**Emotions:** 😟 Frustrated - Traffic, unclear addresses, time pressure

**Pain Points:**
- ⚠️ Customer addresses incomplete ("Near X landmark")
- ⚠️ Building/apartment numbers missing
- ⚠️ Gated communities with complex access
- ⚠️ Customer phone turned off or unreachable
- ⚠️ Traffic not accounted for in time estimates
- ⚠️ No optimized multi-stop routing
- ⚠️ Fuel running low but no time for refill
- ⚠️ Can't share live location with customer

**Opportunities:**
- 💡 Address quality score and validation at intake
- 💡 Customer pre-delivery SMS with:
  - Courier name and photo
  - Live tracking link
  - Estimated arrival time
  - "Call me" button
- 💡 Smart routing considering:
  - Real-time traffic
  - Multiple delivery optimization
  - Fuel stops
  - Prayer time breaks
- 💡 Offline navigation support (pre-cached maps)
- 💡 Community-sourced delivery notes (e.g., "Building entrance is on north side")
- 💡 Live ETA updates to customer
- 💡 Fuel station finder with quickest route

---

### Stage 4: Delivery Handover (5-10 minutes)

**Actions:**
- Find customer location (building/apartment)
- Contact customer if needed
- Wait for customer to come down (apartments)
- Verify customer identity
- Hand over package
- If COD: Collect cash payment
  - Count cash
  - Provide verbal confirmation
  - No receipt given (courier keeps cash)
- Explain any special instructions
- Handle customer questions/complaints

**Touchpoints:**
- Physical customer interaction
- Package handover
- Cash transaction (if COD)
- Verbal confirmation
- Customer phone (for contact)

**Emotions:** 😐 Neutral - Routine interaction, 😟 Frustrated if issues

**Pain Points:**
- ⚠️ Customer not home (wasted trip)
- ⚠️ Wrong person receives (security concern)
- ⚠️ Customer disputes COD amount
- ⚠️ No change for large bills
- ⚠️ Customer refuses delivery (now what?)
- ⚠️ Unsafe cash handling (robbery risk)
- ⚠️ No customer signature/OTP verification
- ⚠️ Contactless delivery unclear during COVID-like situations

**Opportunities:**
- 💡 Customer identity verification:
  - OTP (sent to customer's registered phone)
  - Photo ID check
  - QR code on delivery receipt
- 💡 Digital payment options (reduce cash handling):
  - Link sent to customer
  - Card reader on courier's phone
  - Digital wallet integration
- 💡 Contactless delivery protocol:
  - Photo proof of delivery location
  - OTP-only verification
- 💡 Cash management:
  - Real-time COD collection tracking
  - Digital receipt generation
  - Change calculation assistant
- 💡 Failed delivery workflow:
  - Reason selection
  - Reschedule options
  - Return to warehouse routing

---

### Stage 5: Confirmation & Proof (2-5 minutes)

**Actions:**
- Take photo of delivered package (some couriers)
- Get customer signature (if required)
- Mark delivery as complete:
  - Call dispatcher
  - Update platform app
  - No BARQ status update
- Move to next delivery
- Store COD cash securely

**Touchpoints:**
- Phone call to dispatcher
- Platform app status update
- Phone camera for photos
- Paper delivery log (some couriers)

**Emotions:** 😊 Happy - Delivery complete!

**Pain Points:**
- ⚠️ Duplicate status updates (dispatcher + platform app)
- ⚠️ Delivery proof photos not centralized
- ⚠️ No timestamp/GPS stamp on proof
- ⚠️ Customer signature only on paper (if at all)
- ⚠️ Can forget to update status until end of day
- ⚠️ No integration between BARQ and platform apps

**Opportunities:**
- 💡 One-tap delivery completion in courier app:
  - Auto-status update to BARQ and platform
  - Photo proof upload with GPS and timestamp
  - Digital signature capture
  - Delivery rating (customer service quality)
- 💡 Auto-completion after customer OTP verification
- 💡 Delivery summary card:
  - Time taken
  - Distance covered
  - Earnings for this delivery
  - Performance score
- 💡 Batch completion (mark multiple deliveries done at once)

---

### Stage 6: COD Collection (2-5 minutes, End of Shift)

**Actions:**
- Count total COD collected during shift
- Reconcile against assigned deliveries
- Report amount to dispatcher (phone call)
- Travel to office/collection point
- Hand over cash to accountant
- Get receipt for cash submitted
- Resolve any discrepancies

**Touchpoints:**
- Manual cash counting
- Phone call to dispatcher
- Physical office visit
- Paper receipt
- Accountant verification

**Emotions:** 😐 Neutral - End of day routine, 😟 Frustrated if discrepancies

**Pain Points:**
- ⚠️ Cash carried all day (theft/loss risk)
- ⚠️ Manual counting error-prone
- ⚠️ Discrepancies hard to trace (which delivery?)
- ⚠️ Office visit adds 30-60 minutes to day
- ⚠️ No digital receipt/confirmation
- ⚠️ Accountant not available = courier waits
- ⚠️ Lost cash = courier liable

**Opportunities:**
- 💡 Real-time COD tracking in app:
  - Each delivery logs COD collected
  - Running total visible
  - Auto-reconciliation with assignments
- 💡 Digital payment priority (reduce cash handling)
- 💡 Multiple COD collection points (zones)
- 💡 Photo documentation of cash handover
- 💡 Digital receipt with QR code
- 💡 Instant notification to courier and dispatcher
- 💡 Discrepancy resolution workflow with evidence

---

## Journey Summary: Delivery Lifecycle

**Total Duration:** 30-90 minutes per delivery
**Key Touchpoints:** 11 major touchpoints
**Critical Pain Points:** 31 identified
**High-Impact Opportunities:** 34 improvement areas

### Top 3 Quick Wins
1. **BARQ courier mobile app** - Critical for digital transformation
2. **One-tap status updates** - Reduce dispatcher calls by 80%
3. **Customer pre-delivery SMS** - Reduce "not home" failures

### Top 3 Long-term Improvements
1. **End-to-end digital workflow** - From assignment to proof of delivery
2. **Digital payment integration** - Eliminate cash handling risks
3. **AI-powered routing** - Real-time optimization for multi-delivery routes

---

# Journey 4: Incident Resolution

## User Persona
**Name:** Sarah - Operations Supervisor
**Goal:** Quickly resolve incidents to minimize impact on operations and customer satisfaction
**Context:** Handles 5-15 incidents per week ranging from minor to severe

---

## Journey Stages

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│  INCIDENT   │   INITIAL   │  ASSIGN &   │ INVESTIGATION│  RESOLUTION │   CLOSURE & │
│   REPORTED  │  TRIAGE     │  ESCALATE   │   & ACTION   │  EXECUTION  │   LEARNING  │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
    0-30 min     30-60 min     1-2 hours     2-24 hours    1-7 days     Final step
```

---

### Stage 7: Incident Reported (0-30 minutes)

**Actions:**
- Receive incident notification:
  - Courier calls/WhatsApp
  - Customer complaint via call center
  - Dispatcher flags issue
  - Automated alert (rare)
- Gather initial information:
  - What happened?
  - Who is involved? (courier, vehicle, customer)
  - Where did it occur?
  - When did it happen?
  - Any injuries or damage?
  - Deliveries affected?
- Create initial incident record

**Touchpoints:**
- Phone calls (primary)
- WhatsApp messages
- Call center ticket system (external)
- `/operations/incidents` - Create Incident
- Incident form entry

**Emotions:** 😟 Concerned - Need to assess severity quickly

**Pain Points:**
- ⚠️ Incident reporting is ad-hoc (phone/WhatsApp)
- ⚠️ No standardized incident categories
- ⚠️ Critical information often missing
- ⚠️ Can't capture photos/evidence immediately
- ⚠️ Multiple people report same incident (duplicates)
- ⚠️ No severity auto-classification
- ⚠️ Delayed reporting (hours after incident)

**Opportunities:**
- 💡 **Critical:** In-app incident reporting:
  - Quick report button in courier app
  - Pre-defined incident types:
    - Vehicle accident
    - Theft (package/vehicle/cash)
    - Customer dispute
    - Vehicle breakdown
    - Traffic violation
    - Personal injury
    - Package damage
  - Required fields with smart defaults
  - Photo/video evidence upload
  - GPS and timestamp auto-capture
- 💡 Customer incident portal (self-service reporting)
- 💡 Auto-severity classification based on incident type
- 💡 Duplicate detection and merging
- 💡 Automated notifications to stakeholders
- 💡 Voice-to-text incident description

---

### Stage 2: Initial Triage (30-60 minutes)

**Actions:**
- Assess incident severity:
  - Critical (injury, major accident, theft)
  - High (vehicle disabled, multiple deliveries impacted)
  - Medium (minor accident, customer complaint)
  - Low (documentation issue, minor delay)
- Determine immediate actions needed:
  - Emergency services required?
  - Courier safety ensured?
  - Deliveries need reassignment?
  - Customer notification needed?
  - Insurance claim required?
- Assign incident status: "REPORTED" → "INVESTIGATING"
- Log in incident tracking system

**Touchpoints:**
- Incident details review
- Internal assessment (mental model)
- Incident status update
- Communication with courier/dispatcher
- Initial stakeholder notifications

**Emotions:** 😟 Stressed - Balancing urgency with accuracy

**Pain Points:**
- ⚠️ Severity assessment is subjective
- ⚠️ No clear escalation criteria
- ⚠️ Immediate action checklist not standardized
- ⚠️ Hard to track which incidents need urgent response
- ⚠️ SLA for incident response not enforced
- ⚠️ Critical incidents can slip through cracks

**Opportunities:**
- 💡 Severity auto-scoring algorithm:
  - Injury = Critical
  - Vehicle total loss = Critical
  - Theft > $X = High
  - Customer VIP involved = +1 severity
- 💡 Incident response playbooks by type:
  - Checklist of immediate actions
  - Who to notify
  - What to document
  - Expected response time
- 💡 SLA timer starts automatically
- 💡 Escalation alerts if SLA at risk
- 💡 Color-coded incident dashboard (red/yellow/green)
- 💡 Automated stakeholder notifications (email/SMS)

---

### Stage 3: Assign & Escalate (1-2 hours)

**Actions:**
- Assign incident owner:
  - Sarah (supervisor) for most
  - HR for employee issues
  - Fleet manager for vehicle damage
  - Legal for serious accidents
  - Finance for theft/fraud
- Notify assigned owner
- Escalate to management if:
  - Critical severity
  - Potential legal liability
  - Media attention risk
  - Policy violation
- Create investigation task list
- Set resolution deadline

**Touchpoints:**
- Incident assignment interface
- Email/phone to notify assignee
- Management escalation (call/email)
- Internal ticketing system
- Manual task tracking (Excel/notepad)

**Emotions:** 😐 Neutral - Following procedure

**Pain Points:**
- ⚠️ Assignment rules are tribal knowledge
- ⚠️ No workflow automation for routing
- ⚠️ Assignees not notified in real-time
- ⚠️ Management escalation is manual email
- ⚠️ Task lists recreated each time (no templates)
- ⚠️ Resolution deadlines not tracked systematically

**Opportunities:**
- 💡 Auto-assignment rules engine:
  - Route by incident type and severity
  - Check assignee availability
  - Load balancing across team
- 💡 Workflow state machine:
  - REPORTED → TRIAGED → ASSIGNED → INVESTIGATING → RESOLVED → CLOSED
- 💡 In-app notifications to assignees
- 💡 Auto-escalation workflows:
  - Critical incidents → notify manager immediately
  - SLA breach imminent → escalate
  - Awaiting response > X hours → remind assignee
- 💡 Incident type templates with task checklists
- 💡 Resolution deadline calculator based on SLA
- 💡 Collaborative incident workspace (comments, attachments)

---

### Stage 4: Investigation & Action (2-24 hours)

**Actions:**
- **For Accidents:**
  - Review GPS tracking data
  - Get courier statement
  - Obtain police report if applicable
  - Inspect vehicle damage (photos)
  - Interview witnesses
  - Contact insurance

- **For Theft:**
  - Verify COD discrepancy
  - Check delivery proof
  - Review courier history
  - File police report
  - Activate recovery process

- **For Customer Disputes:**
  - Listen to customer complaint
  - Review delivery records
  - Check proof of delivery
  - Assess legitimacy
  - Determine compensation

- **For Vehicle Breakdowns:**
  - Send tow truck
  - Arrange replacement vehicle
  - Reassign affected deliveries
  - Schedule repair
  - Log maintenance need

**Touchpoints:**
- FMS GPS tracking data (external)
- Courier interview (phone/in-person)
- Police reports (external)
- Insurance portal (external)
- Delivery history review
- Photo evidence examination
- Customer call records
- Vehicle inspection reports
- Multiple systems for data gathering

**Emotions:** 😟 Frustrated - Data scattered across systems

**Pain Points:**
- ⚠️ Evidence collection is manual and scattered
- ⚠️ GPS data requires logging into separate FMS system
- ⚠️ No centralized incident evidence repository
- ⚠️ Courier statements not documented formally
- ⚠️ Police reports stored as PDFs in folders
- ⚠️ Investigation progress not visible to stakeholders
- ⚠️ Same incident type = redo investigation from scratch
- ⚠️ Root cause analysis not standardized

**Opportunities:**
- 💡 Integrated evidence collection:
  - GPS data auto-pulled into incident
  - Photos/videos uploaded to incident file
  - Courier statement form with structured fields
  - Customer communication log
  - Document attachment hub
- 💡 Investigation timeline view
- 💡 Incident type-specific investigation guides:
  - Required evidence checklist
  - Interview question templates
  - Analysis frameworks
- 💡 Root cause analysis tool (5 Whys, Fishbone)
- 💡 Similar incident finder (learn from past cases)
- 💡 Real-time investigation status updates
- 💡 Integration with insurance/police systems

---

### Stage 5: Resolution Execution (1-7 days)

**Actions:**
- Execute resolution plan:
  - **Accidents:** Insurance claim, vehicle repair, courier discipline/training
  - **Theft:** Recovery attempts, police follow-up, policy review
  - **Disputes:** Customer refund/compensation, courier coaching
  - **Breakdowns:** Vehicle repair, preventive maintenance review

- Coordinate with stakeholders:
  - Finance (refunds, insurance)
  - HR (discipline, training)
  - Fleet (repairs, replacements)
  - Legal (if needed)

- Monitor resolution progress
- Update incident status to "RESOLVED"
- Document final outcome

**Touchpoints:**
- Task management for resolution steps
- Finance system (external)
- HR records (external)
- Fleet maintenance tracker
- Email coordination
- Incident status updates
- Outcome documentation

**Emotions:** 😐 Neutral - Executing plan, 🎉 Relieved when resolved

**Pain Points:**
- ⚠️ Resolution tasks tracked outside incident system
- ⚠️ Coordination across departments is manual (email threads)
- ⚠️ Can't see resolution progress at a glance
- ⚠️ Stakeholders not updated proactively
- ⚠️ Final outcome documentation inconsistent
- ⚠️ Lessons learned not captured

**Opportunities:**
- 💡 Integrated resolution task management:
  - Tasks assigned to other departments within incident
  - Status tracking and due dates
  - Automated reminders
- 💡 Cross-department collaboration workspace
- 💡 Resolution progress dashboard
- 💡 Auto-notifications on key milestones
- 💡 Structured outcome documentation:
  - Actions taken
  - Results achieved
  - Costs incurred
  - Time to resolution
- 💡 Lessons learned template
- 💡 Automatic closure criteria checklist

---

### Stage 6: Closure & Learning (Final Step)

**Actions:**
- Final incident review:
  - All actions completed?
  - Stakeholders satisfied?
  - Documentation complete?
- Capture lessons learned:
  - What went well?
  - What could be improved?
  - Root cause identified?
  - Preventive measures needed?
- Update policies/procedures if needed
- Close incident status: "RESOLVED" → "CLOSED"
- Archive incident for future reference
- Generate incident report for management
- Track incident metrics:
  - Time to resolution
  - Cost impact
  - Recurrence rate

**Touchpoints:**
- Final incident review checklist
- Lessons learned documentation
- Policy update process (external)
- Incident closure action
- Reporting dashboard
- Metrics tracking spreadsheet

**Emotions:** 😊 Satisfied - Learning for future prevention

**Pain Points:**
- ⚠️ Lessons learned often skipped due to time pressure
- ⚠️ No systematic review process
- ⚠️ Policy updates happen separately (not linked to incident)
- ⚠️ Incident knowledge not shared with team
- ⚠️ Metrics calculated manually
- ⚠️ Hard to identify trends across incidents

**Opportunities:**
- 💡 Mandatory lessons learned step before closure
- 💡 Incident retrospective template
- 💡 Policy update workflow triggered from incident
- 💡 Team knowledge sharing:
  - Incident digest email
  - Monthly incident review meeting
  - Searchable incident knowledge base
- 💡 Auto-calculated incident metrics:
  - Average time to resolution by type
  - Cost per incident category
  - Recurrence patterns
  - Top root causes
- 💡 Trend analysis dashboard:
  - Incident frequency over time
  - High-risk couriers/vehicles/zones
  - Seasonal patterns
- 💡 Preventive action tracker (from lessons learned)

---

## Journey Summary: Incident Resolution

**Total Duration:** Hours to weeks (varies by severity)
**Key Touchpoints:** 12 major touchpoints
**Critical Pain Points:** 26 identified
**High-Impact Opportunities:** 31 improvement areas

### Top 3 Quick Wins
1. **In-app incident reporting** - Standardize and speed up reporting
2. **Auto-severity classification** - Ensure critical incidents get immediate attention
3. **Evidence collection hub** - Centralize all incident-related data

### Top 3 Long-term Improvements
1. **Incident workflow automation** - Routing, assignments, escalations
2. **Integrated investigation workspace** - All stakeholders collaborate in one place
3. **Predictive incident prevention** - ML identifies high-risk patterns before incidents occur

---

# Journey 5: Leave Request Process

## User Persona
**Name:** Mohammed - Courier
**Goal:** Request time off for personal/family reasons and get quick approval
**Context:** Requests annual leave, sick days, emergency leave 2-4 times per year

---

## Journey Stages

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   NEED      │  REQUEST    │  SUPERVISOR │    HR       │   FINAL     │   LEAVE     │
│  ARISES     │ SUBMISSION  │   REVIEW    │  APPROVAL   │ CONFIRMATION│  MANAGEMENT │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
   Day -14      Day -14       Day -13      Day -12       Day -11       Day 0
```

---

### Stage 1: Need Arises (Day -14, Planning)

**Actions:**
- Identify need for time off:
  - Annual leave (vacation)
  - Sick leave (illness)
  - Emergency leave (family)
  - Religious holiday
- Check leave balance (if known)
- Determine dates needed
- Consider impact on work schedule
- Informally discuss with colleagues

**Touchpoints:**
- Personal calendar
- Informal memory of leave days used
- Colleague conversations (informal)
- No system access for couriers currently

**Emotions:** 😐 Neutral - Planning ahead

**Pain Points:**
- ⚠️ Couriers don't have access to BARQ system
- ⚠️ Don't know current leave balance
- ⚠️ Don't know company leave policy details
- ⚠️ Unclear how far in advance to request
- ⚠️ No visibility into team's leave calendar (avoid conflicts)
- ⚠️ Uncertainty if request will be approved

**Opportunities:**
- 💡 **Critical:** Self-service portal for couriers:
  - View leave balance by type
  - See leave policy (annual days, rules)
  - Team leave calendar (who else is off?)
  - Submit leave request
- 💡 Mobile app for easy access
- 💡 Leave balance notifications (e.g., "You have 12 days remaining")
- 💡 Blackout dates visible (busy periods = no leave)
- 💡 Suggested dates based on low-demand forecasts
- 💡 Approval likelihood indicator

---

### Stage 2: Request Submission (Day -14)

**Actions:**
- Contact supervisor (currently via WhatsApp/call)
- Provide leave details:
  - Leave type (annual, sick, emergency)
  - Start date
  - End date
  - Number of days
  - Reason (sometimes)
- Wait for supervisor acknowledgment
- Hope it doesn't get lost in messages

**Touchpoints:**
- WhatsApp message to supervisor
- Phone call (sometimes)
- No formal system

**Emotions:** 😟 Anxious - Will it be approved? Did supervisor see it?

**Pain Points:**
- ⚠️ **Critical:** No formal leave request system
- ⚠️ Requests via WhatsApp can get lost
- ⚠️ No proof of submission
- ⚠️ No standard request format
- ⚠️ Supervisor might be off/busy and miss it
- ⚠️ No tracking of request status
- ⚠️ Courier must follow up repeatedly

**Opportunities:**
- 💡 **Game-changer:** Digital leave request form:
  - Pre-filled fields (courier name, ID, current balance)
  - Date picker with conflict warnings
  - Leave type dropdown
  - Reason text field (optional)
  - Supporting documents upload (e.g., medical certificate)
  - Submit button with confirmation
- 💡 Auto-notification to supervisor
- 💡 Request tracking number
- 💡 Submission confirmation (email/SMS)
- 💡 Status tracking: "Submitted → Under Review → Approved/Rejected"
- 💡 Estimated approval timeline shown

---

### Stage 3: Supervisor Review (Day -13)

**Actions:**
- Receive leave request (WhatsApp/call)
- Check team schedule:
  - Who else is on leave?
  - Can we cover the workload?
  - Is it a busy delivery period?
- Review courier's performance/attendance
- Check leave balance (if tracked)
- Make decision: Approve or Deny
- Communicate decision to courier (WhatsApp/call)
- If approved, forward to HR (email/WhatsApp)

**Touchpoints:**
- WhatsApp/phone for request receipt
- Mental/paper schedule check
- Excel sheet for leave tracking (some supervisors)
- Performance review (informal)
- Communication back to courier
- HR notification (informal)

**Emotions:** 😐 Neutral - Routine decision, 😟 Concerned if staffing tight

**Pain Points:**
- ⚠️ No centralized view of team leave calendar
- ⚠️ Courier leave balances not readily accessible
- ⚠️ Can't see workload forecast for requested dates
- ⚠️ Performance data not integrated
- ⚠️ Approval decision is manual and subjective
- ⚠️ Easy to approve conflicting leave requests
- ⚠️ No audit trail of approval

**Opportunities:**
- 💡 Supervisor dashboard showing:
  - All pending leave requests
  - Team leave calendar
  - Workload forecast for dates
  - Courier leave balances
  - Courier performance scores
  - Leave policy rules (auto-check)
- 💡 Approval workflow:
  - One-click approve/reject
  - Reason required for rejection
  - Conditional approval (e.g., pending coverage)
- 💡 Conflict detection and warnings
- 💡 Alternative date suggestions
- 💡 Auto-routing to HR after approval
- 💡 Approval SLA (respond within 2 days)

---

### Stage 4: HR Approval (Day -12)

**Actions:**
- Receive supervisor's approval (email/WhatsApp)
- Verify leave request details
- Check courier leave balance in HR system
- Validate against policy:
  - Sufficient balance?
  - Meets notice period?
  - Emergency leave justified?
  - Supporting docs provided (sick leave)?
- Process leave in HR system:
  - Deduct from balance
  - Update leave records
  - Generate leave approval letter (sometimes)
- Notify courier and supervisor of final approval

**Touchpoints:**
- Email/WhatsApp from supervisor
- HR management system (external, e.g., Excel or HR software)
- Leave balance ledger
- Policy documentation
- Communication to courier and supervisor

**Emotions:** 😐 Neutral - Administrative processing

**Pain Points:**
- ⚠️ HR system not integrated with BARQ
- ⚠️ Duplicate data entry (BARQ + HR system)
- ⚠️ Leave balance discrepancies common
- ⚠️ Policy rules enforced manually (error-prone)
- ⚠️ No workflow automation between supervisor and HR
- ⚠️ Approval delays if HR is busy
- ⚠️ Courier and supervisor not updated proactively

**Opportunities:**
- 💡 Integrated leave management module in BARQ:
  - Single source of truth for leave balances
  - Auto-deduction upon approval
  - Policy rules engine (auto-validate)
- 💡 Workflow automation:
  - Supervisor approval → auto-route to HR
  - HR one-click final approval
  - Auto-notifications to all parties
- 💡 Digital approval letter generation
- 💡 Supporting document verification checklist
- 💡 SLA tracking (HR approval within 1 day)
- 💡 Sync with external HR system (if needed)

---

### Stage 5: Final Confirmation (Day -11)

**Actions:**
- Courier receives approval notification (WhatsApp/call)
- Verifies leave dates
- Prepares for absence:
  - Informs regular customers (informal)
  - Coordinates with colleague for handover (if needed)
  - Plans return date
- Updates personal calendar
- No formal confirmation in system

**Touchpoints:**
- WhatsApp/phone notification
- Personal calendar
- Informal customer notifications
- Colleague coordination (ad-hoc)

**Emotions:** 😊 Happy - Leave approved! 🎉 Relieved

**Pain Points:**
- ⚠️ No formal digital confirmation
- ⚠️ Courier doesn't receive approval document
- ⚠️ Leave not visible in BARQ dispatch system
- ⚠️ Risk of being assigned deliveries on leave day
- ⚠️ No handover process
- ⚠️ Updated leave balance not communicated

**Opportunities:**
- 💡 Automated approval notification:
  - SMS + email with leave details
  - PDF approval letter attached
  - Updated leave balance shown
  - Calendar invite for leave days
- 💡 Self-service confirmation portal
- 💡 Leave added to courier's profile (visible to dispatch)
- 💡 Auto-block from dispatch assignments during leave
- 💡 Handover workflow:
  - Assign temporary replacement
  - Transfer critical deliveries
  - Customer notification automation
- 💡 Pre-leave checklist (e.g., return vehicle, submit COD)

---

### Stage 6: Leave Management (Day 0, During Leave)

**Actions:**
- **On leave day:**
  - Courier is off
  - Dispatcher knows not to assign (ideally)
  - Attendance marked as "ON_LEAVE"

- **Potential issues:**
  - Emergency recall (rare)
  - Leave extension needed (illness)
  - Early return

- **After leave:**
  - Courier returns to work
  - Resume normal assignments
  - Leave balance updated

**Touchpoints:**
- Attendance tracking system
- Dispatcher awareness (informal)
- Leave extension request (phone/WhatsApp)
- Return confirmation (informal check-in)

**Emotions:** 😊 Happy - Enjoying time off, 😟 Worried if emergencies arise

**Pain Points:**
- ⚠️ Attendance system doesn't auto-mark leave days
- ⚠️ Dispatch might accidentally assign delivery (no system block)
- ⚠️ Leave extension requires re-starting approval process
- ⚠️ No easy way to cancel/modify approved leave
- ⚠️ Return to work not formalized (just shows up)
- ⚠️ Leave balance updates not real-time

**Opportunities:**
- 💡 Auto-attendance marking for approved leave days
- 💡 System-level dispatch block (can't assign courier on leave)
- 💡 Leave modification workflow:
  - Extend leave (quick approval)
  - Cancel leave (restore balance)
  - Early return (partial restoration)
- 💡 Return-to-work checklist:
  - Confirm availability
  - Update system status to ACTIVE
  - Re-assign vehicle if needed
- 💡 Real-time leave balance dashboard
- 💡 Leave history and audit trail
- 💡 Analytics: Leave patterns, no-shows, balance utilization

---

## Journey Summary: Leave Request Process

**Total Duration:** 14 days (request to leave date)
**Key Touchpoints:** 8 major touchpoints
**Critical Pain Points:** 24 identified
**High-Impact Opportunities:** 28 improvement areas

### Top 3 Quick Wins
1. **Digital leave request form** - Replace WhatsApp with formal system
2. **Leave balance visibility** - Couriers can check their balance anytime
3. **Auto-dispatch blocking** - Prevent assignment during approved leave

### Top 3 Long-term Improvements
1. **Integrated leave management module** - End-to-end workflow in BARQ
2. **Self-service courier portal** - Empowerment and efficiency
3. **Workflow automation** - From request to approval to attendance marking

---

# Cross-Journey Insights

## Recurring Themes Across All Journeys

### Pain Point Patterns

1. **System Fragmentation** (Appears in 5/5 journeys)
   - Multiple disconnected tools
   - Manual data transfer
   - No single source of truth

2. **Manual Processes** (Appears in 5/5 journeys)
   - Heavy reliance on phone/WhatsApp
   - Paper-based documentation
   - No automation

3. **Lack of Mobile Access** (Appears in 4/5 journeys)
   - Couriers have no mobile app
   - Managers work on desktop only
   - No field-accessible tools

4. **Poor Visibility** (Appears in 5/5 journeys)
   - Can't track real-time status
   - No progress dashboards
   - Stakeholders uninformed

5. **No Proactive Features** (Appears in 5/5 journeys)
   - Reactive problem-solving
   - No predictive alerts
   - No automation suggestions

### Opportunity Themes

1. **Workflow Automation** (35+ opportunities)
   - Reduce manual steps
   - Auto-routing and assignments
   - Smart notifications

2. **Mobile-First Solutions** (28+ opportunities)
   - Courier mobile app (critical)
   - Manager mobile dashboards
   - Self-service portals

3. **Integration & API Connectivity** (22+ opportunities)
   - Delivery platform APIs
   - HR/Payroll systems
   - FMS GPS tracking
   - External service providers

4. **Real-Time Intelligence** (30+ opportunities)
   - Live tracking and monitoring
   - Predictive analytics
   - AI-powered recommendations

5. **Self-Service & Empowerment** (20+ opportunities)
   - Courier self-service portal
   - Customer tracking
   - Automated approvals

---

## User Emotion Heatmap

```
Journey Stage               Onboarding  Dispatch  Delivery  Incident  Leave
────────────────────────────────────────────────────────────────────────────
Stage 1 (Start)                😊         😐        😐        😟       😐
Stage 2 (Data Entry)           😟         😟        😟        😟       😟
Stage 3 (Assignment/Action)    😐         😡        😟        😐       😟
Stage 4 (Execution)            😐         😟        😐        😟       😐
Stage 5 (Validation)           😟         😟        😊        😐       🎉
Stage 6 (Completion)           🎉         😐        😐        😊       😊
────────────────────────────────────────────────────────────────────────────
Overall Sentiment:           Mixed     Negative   Mixed     Mixed   Positive
```

### Insight:
- **Dispatch Flow** has most frustration (manual allocation bottleneck)
- **Leave Request** ends positively (approval = relief)
- **Data entry stages** consistently frustrating across all journeys
- **Completion stages** generally positive (accomplishment)

---

## Priority Action Matrix

Based on **Impact × Frequency × Effort**, here are the top 10 improvements:

| Rank | Opportunity | Affected Journeys | Impact | Effort | Priority Score |
|------|-------------|-------------------|--------|--------|----------------|
| 1 | **BARQ Courier Mobile App** | 3/5 (Dispatch, Delivery, Leave) | Very High | High | **Critical** |
| 2 | **Auto-Dispatch Algorithm** | Dispatch, Delivery | Very High | High | **Critical** |
| 3 | **Platform API Integrations** | Dispatch, Delivery | Very High | Medium | **Critical** |
| 4 | **Digital Leave Management** | Leave Request | High | Low | **High** |
| 5 | **Onboarding Workflow Engine** | Onboarding | High | Medium | **High** |
| 6 | **Incident Reporting App** | Incident Resolution | High | Low | **High** |
| 7 | **Real-Time Dispatch Dashboard** | Dispatch, Delivery | High | Medium | **High** |
| 8 | **Multi-Step Courier Creation Form** | Onboarding | Medium | Low | **Medium** |
| 9 | **COD Digital Tracking** | Dispatch, Delivery | Medium | Low | **Medium** |
| 10 | **Customer SMS Notifications** | Delivery | Medium | Low | **Medium** |

---

## Recommended Implementation Roadmap

### Phase 1: Foundation (Months 1-3)
**Quick Wins & Critical Blockers**

1. Multi-step courier creation form
2. Digital leave request system
3. Incident reporting improvements
4. Real-time dispatch dashboard
5. Customer SMS notifications

**Expected Impact:** 30% reduction in manual work, improved user satisfaction

---

### Phase 2: Mobile & Automation (Months 4-6)
**High-Impact Transformations**

1. **BARQ Courier Mobile App** (MVP):
   - Delivery assignments
   - Status updates
   - COD tracking
   - Leave requests

2. **Auto-dispatch algorithm** (basic):
   - Nearest courier assignment
   - Load balancing
   - Zone optimization

3. **Onboarding workflow engine**

**Expected Impact:** 50% efficiency gains, courier satisfaction +40%

---

### Phase 3: Integration & Intelligence (Months 7-12)
**Long-Term Excellence**

1. Platform API integrations (Jahez, Hunger, Mrsool)
2. Advanced auto-dispatch with AI
3. Predictive analytics and forecasting
4. End-to-end workflow automation
5. Advanced incident management
6. Comprehensive mobile feature set

**Expected Impact:** 70% automation rate, near-elimination of manual processes

---

## Success Metrics

### Courier Onboarding
- **Before:** 7 days average, 14 pain points
- **Target:** 3 days average, <5 pain points
- **KPI:** Time to first delivery, data accuracy rate

### Daily Dispatch
- **Before:** 90 min manual allocation time, 200+ manual entries
- **Target:** 15 min with auto-dispatch, <20 manual entries
- **KPI:** Deliveries per dispatcher, assignment accuracy

### Delivery Lifecycle
- **Before:** 8 status update calls per delivery, 30% "not home" failures
- **Target:** 0 calls (app-based), 10% failure rate
- **KPI:** On-time delivery rate, customer satisfaction

### Incident Resolution
- **Before:** 4 days average resolution, scattered documentation
- **Target:** 2 days average, 100% documented with evidence
- **KPI:** Resolution time, recurrence rate

### Leave Request
- **Before:** 3-5 days approval time, WhatsApp-based
- **Target:** 24 hours approval time, fully digital
- **KPI:** Approval cycle time, courier satisfaction

---

## Conclusion

These user journey maps reveal a system with **strong operational foundations** but significant opportunities for **digital transformation**. The recurring themes of manual processes, system fragmentation, and lack of mobile access point to clear areas for improvement.

**Key Takeaway:** Implementing the recommended improvements in a phased approach will transform BARQ from a functional management system into a **world-class, automated fleet operations platform**.

---

**Document Metadata**
- **Created:** December 6, 2025
- **Version:** 1.0
- **Next Review:** March 6, 2026
- **Owner:** UX Design Team
- **Stakeholders:** Product, Engineering, Operations, HR

**Changelog:**
- v1.0 (2025-12-06): Initial journey maps created for 5 critical workflows
