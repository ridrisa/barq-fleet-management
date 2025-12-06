# BARQ Fleet Management - User Journey Maps

**Created:** December 6, 2025
**Phase:** 2 - User Research & Benchmarking

---

## Journey Overview

| Journey | Primary Actor | Duration | Pain Points | Opportunity Score |
|---------|---------------|----------|-------------|-------------------|
| Courier Onboarding | HR Admin | 5-7 days | 14 | High |
| Daily Dispatch Flow | Dispatch Supervisor | 14 hours | 27 | Critical |
| Delivery Lifecycle | Courier/Dispatch | 30-90 min | 31 | Critical |
| Incident Resolution | Support Agent | 2-7 days | 26 | High |
| Leave Request | Courier/HR | 3-14 days | 24 | Medium |

---

## Journey 1: Courier Onboarding

**Duration:** 5-7 days
**Key Actors:** HR Admin, Fleet Manager, New Courier
**Goal:** Transform a new hire into a productive, compliant courier

### Journey Stages

```
[HIRING] → [DOCUMENTATION] → [SYSTEM SETUP] → [TRAINING] → [ASSIGNMENT] → [FIRST DELIVERY]
   1 day       2-3 days          1 day          1 day        0.5 day         1 day
```

### Stage Details

| Stage | Actions | Touchpoints | Emotions | Pain Points |
|-------|---------|-------------|----------|-------------|
| **1. Hiring** | Interview, offer, accept | External HR system | Excited | No system integration |
| **2. Documentation** | Collect ID, license, visa, GOSI | Courier Profile page | Anxious | Manual document upload, chase required |
| **3. System Setup** | Create account, assign role | Admin > Users | Neutral | Multiple screens to configure |
| **4. Training** | Safety, app, procedures | External/Manual | Engaged | No in-app training module |
| **5. Assignment** | Assign vehicle, zone | Fleet > Assignments | Relieved | Manual matching process |
| **6. First Delivery** | Shadow shift, first solo | Operations > Dispatch | Nervous→Proud | No guided first-day workflow |

### Opportunity Map

```
                    HIGH IMPACT
                         │
    ┌────────────────────┼────────────────────┐
    │   Auto-Document    │   Digital          │
    │   Verification     │   Training         │
    │                    │   Module           │
LOW ├────────────────────┼────────────────────┤ HIGH
EFFORT                   │                    EFFORT
    │   Template         │   Guided           │
    │   Profiles         │   First Day        │
    │                    │   Workflow         │
    └────────────────────┼────────────────────┘
                    LOW IMPACT
```

### Recommendations
1. **Quick Win:** Pre-filled profile templates (2 hours saved)
2. **Medium:** Digital document upload with OCR
3. **Strategic:** In-app training module with certification

---

## Journey 2: Daily Dispatch Flow

**Duration:** 14 hours (6 AM - 8 PM)
**Key Actors:** Dispatch Supervisor, Couriers
**Goal:** Efficiently allocate and monitor all deliveries

### Journey Stages

```
[SHIFT START] → [ALLOCATION] → [DISPATCH] → [MONITORING] → [ESCALATIONS] → [CLOSEOUT]
   30 min         90 min        60 min      Continuous       Variable       60 min
```

### Detailed Flow

```
06:00 ┌─────────────────────────────────────────────────────────────────┐
      │ SHIFT START                                                      │
      │ • Review overnight incidents                                     │
      │ • Check courier availability (WhatsApp!)                         │
      │ • Prepare delivery manifests                                     │
      └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
06:30 ┌─────────────────────────────────────────────────────────────────┐
      │ ALLOCATION (90 MINUTES - CRITICAL BOTTLENECK)                   │
      │ • Match deliveries to couriers manually                         │
      │ • Consider zones, vehicle capacity, skills                      │
      │ • Handle last-minute absences                                   │
      │ • No route optimization                                         │
      └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
08:00 ┌─────────────────────────────────────────────────────────────────┐
      │ DISPATCH                                                         │
      │ • Brief couriers on their routes                                │
      │ • Distribute paper manifests (no mobile app)                    │
      │ • Confirm vehicle assignments                                   │
      └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
08:30 ┌─────────────────────────────────────────────────────────────────┐
      │ MONITORING (ALL DAY)                                            │
      │ • Track via WhatsApp/calls (no real-time tracking)             │
      │ • Handle customer inquiries                                     │
      │ • Coordinate re-attempts                                        │
      │ • Monitor COD collections                                       │
      └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
18:00 ┌─────────────────────────────────────────────────────────────────┐
      │ CLOSEOUT                                                         │
      │ • Collect COD cash                                              │
      │ • Process returns                                               │
      │ • Update delivery statuses                                      │
      │ • Handover to night shift                                       │
      └─────────────────────────────────────────────────────────────────┘
```

### Pain Points by Stage

| Stage | Pain Point | Impact | Solution |
|-------|------------|--------|----------|
| Allocation | 90 min manual process | High | Auto-dispatch algorithm |
| Allocation | No route optimization | High | ML-based routing |
| Monitoring | WhatsApp for status | Critical | Courier mobile app |
| Monitoring | No real-time tracking | Critical | FMS integration |
| Closeout | Manual COD reconciliation | Medium | Digital COD tracking |

### Critical Opportunity: Auto-Dispatch

**Current State:**
- 90 minutes manual allocation
- 200+ deliveries matched by hand
- Error-prone, suboptimal routes

**Target State:**
- 15 minutes with auto-dispatch
- ML-optimized route suggestions
- Human review and override

**Impact:** 83% time reduction, better route efficiency

---

## Journey 3: Delivery Lifecycle

**Duration:** 30-90 minutes per delivery
**Key Actors:** Courier, Customer, Dispatch
**Goal:** Successfully complete delivery and collect payment

### Journey Stages

```
[ASSIGNED] → [EN ROUTE] → [ARRIVED] → [HANDOVER] → [COMPLETED] → [COD COLLECTED]
   5 min       15-45 min    5 min      5-15 min      2 min          2 min
```

### Swimlane Diagram

```
COURIER    ─┬─[Accept]─────[Navigate]───[Arrive]────[Deliver]───[Confirm]──[Collect COD]
            │      │            │           │           │            │           │
CUSTOMER   ─┼──────┼────────────┼───────────┼────[Receive]───[Sign]───┼───────────┤
            │      │            │           │           │            │           │
DISPATCH   ─┼──[Assign]────────┼─[Monitor]─┼──────[Track]────────────┼─[Verify]──┤
            │      │            │           │           │            │           │
SYSTEM     ─┴──[Queue]────[Status]────[Notify]────[POD]────[Complete]─┴─[Reconcile]
```

### Critical Gap: No Courier Mobile App

**Current Pain Points:**
- Status updates via WhatsApp/call
- Paper manifests
- No navigation integration
- No proof of delivery
- Manual COD tracking

**With Mobile App:**
- One-tap status updates
- Digital manifest with offline support
- Turn-by-turn navigation
- Photo/signature POD
- Integrated COD collection

---

## Journey 4: Incident Resolution

**Duration:** 2-7 days average
**Key Actors:** Customer, Support Agent, Courier, Manager
**Goal:** Resolve delivery issues and restore satisfaction

### Journey Stages

```
[REPORT] → [TRIAGE] → [INVESTIGATE] → [RESOLVE] → [VERIFY] → [CLOSE]
  5 min     15 min      1-4 hours     Variable    30 min     5 min
```

### Escalation Flow

```
                    ┌─────────────────┐
                    │  Customer       │
                    │  Reports Issue  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  L1: Support    │
                    │  Agent          │──── 70% resolved
                    └────────┬────────┘
                             │ 30%
                    ┌────────▼────────┐
                    │  L2: Dispatch   │
                    │  Supervisor     │──── 20% resolved
                    └────────┬────────┘
                             │ 10%
                    ┌────────▼────────┐
                    │  L3: Operations │
                    │  Manager        │──── 9% resolved
                    └────────┬────────┘
                             │ 1%
                    ┌────────▼────────┐
                    │  L4: Executive  │
                    │  Escalation     │──── 1% resolved
                    └─────────────────┘
```

### Pain Points
- Evidence scattered (photos, WhatsApp, email)
- No structured escalation workflow
- SLA tracking is manual
- Resolution authority unclear
- Customer not updated automatically

### Recommendations
1. Centralized evidence collection
2. Automated escalation rules
3. SLA countdown timers
4. Customer notification automation
5. Root cause categorization

---

## Journey 5: Leave Request Process

**Duration:** 3-14 days
**Key Actors:** Courier, HR Admin, Manager
**Goal:** Request and approve leave while maintaining operations

### Current Flow (Problematic)

```
[COURIER] ──WhatsApp──► [MANAGER] ──WhatsApp──► [HR] ──Excel──► [APPROVED]
                              │                      │
                              ▼                      ▼
                        No Audit Trail        Manual Balance Update
```

### Target Flow (Digital)

```
[COURIER] ──App──► [AUTO-CHECK] ──► [MANAGER] ──► [HR] ──► [APPROVED]
                        │               │          │           │
                        ▼               ▼          ▼           ▼
                   Balance OK      Notification   Auto-Update   Calendar
                                                              Sync
```

### Pain Points
- WhatsApp-based approval (no audit trail)
- Manual balance calculations
- Approval delays (3-5 days)
- Coverage planning is reactive
- Accrual errors common

### Quick Win: Digital Leave Request
- Mobile-first leave application
- Auto balance check
- Push notification approvals
- Calendar integration
- Audit trail

---

## Cross-Journey Pain Point Summary

| Pain Point | Affected Journeys | Priority | Solution |
|------------|-------------------|----------|----------|
| No courier mobile app | 2, 3, 4, 5 | Critical | Build BARQ Courier App |
| Manual dispatch allocation | 2 | Critical | Auto-dispatch algorithm |
| WhatsApp-based communication | 1, 2, 3, 4, 5 | High | In-app messaging |
| No real-time tracking | 2, 3, 4 | High | FMS integration |
| Scattered documentation | 1, 4 | Medium | Document management |

---

## Implementation Priority

### Phase 1 (Quick Wins - Weeks 1-4)
- Digital leave request form
- Document upload improvements
- SLA tracking automation

### Phase 2 (Core - Months 2-3)
- Courier mobile app MVP
- Auto-dispatch algorithm
- Real-time tracking integration

### Phase 3 (Enhancement - Months 4-6)
- ML route optimization
- Predictive maintenance alerts
- Customer self-service portal

---

## ROI Projections

| Improvement | Time Saved | Annual Value |
|-------------|------------|--------------|
| Auto-dispatch (83% reduction) | 75 min/day | $50K+ |
| Courier app (status updates) | 2 hours/day | $30K+ |
| Digital leave (approval time) | 4 days→1 day | $20K+ |
| Incident automation | 2 hours/incident | $40K+ |

**Total Estimated Annual Value:** $140K+

---

*Document created as part of Phase 2 - User Research & Benchmarking*
