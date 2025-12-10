# BARQ Fleet Management - Usability Test Plan

**Created:** December 6, 2025
**Phase:** 6 - Validation & Testing Plan
**Version:** 1.0

---

## Executive Summary

This document outlines a comprehensive usability testing strategy for the BARQ Fleet Management system. The plan covers remote and in-person testing methodologies, participant recruitment, task scenarios, and success metrics.

---

## Testing Objectives

### Primary Objectives
1. Validate that core workflows can be completed efficiently
2. Identify friction points in the user experience
3. Measure task completion rates and time-on-task
4. Gather qualitative feedback on interface clarity
5. Validate accessibility compliance in real-world usage

### Secondary Objectives
1. Compare performance against baseline metrics
2. Validate design system effectiveness
3. Test mobile responsiveness with actual users
4. Identify training needs for different user roles

---

## Participant Recruitment

### Target Participants

| Role | Count | Criteria |
|------|-------|----------|
| Fleet Manager | 4 | 2+ years fleet experience, daily system use |
| HR Administrator | 3 | Familiar with Saudi labor law, payroll |
| Dispatch Supervisor | 4 | Active dispatch responsibilities |
| System Administrator | 2 | Technical background, admin experience |
| Support Agent | 3 | Customer-facing role experience |

**Total Participants: 16**

### Recruitment Channels
1. Current BARQ beta users
2. Industry contacts via logistics associations
3. LinkedIn targeted outreach
4. Partner company referrals

### Screening Criteria
- Must use fleet/logistics software regularly
- Mix of technical proficiency levels
- Diverse age range (25-55)
- Both Arabic and English speakers
- No prior deep familiarity with BARQ

### Incentives
- SAR 200 gift card per 60-minute session
- Priority access to new features
- Extended trial period for their organization

---

## Testing Methodology

### Session Format

```
┌─────────────────────────────────────────────────────────────┐
│                    60-MINUTE SESSION                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  0:00 - 0:05   Introduction & Consent                        │
│                - Explain purpose                             │
│                - Sign consent form                           │
│                - Enable recording                            │
│                                                              │
│  0:05 - 0:10   Background Questions                          │
│                - Role and experience                         │
│                - Current tools used                          │
│                - Pain points today                           │
│                                                              │
│  0:10 - 0:45   Task Scenarios                                │
│                - 4-6 core tasks                              │
│                - Think-aloud protocol                        │
│                - Observe & note issues                       │
│                                                              │
│  0:45 - 0:55   Post-Task Questionnaire                       │
│                - SUS (System Usability Scale)                │
│                - Custom satisfaction questions               │
│                                                              │
│  0:55 - 1:00   Debrief                                       │
│                - Open feedback                               │
│                - Feature requests                            │
│                - Thank you & next steps                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Testing Modalities

| Method | Participants | When | Tools |
|--------|--------------|------|-------|
| Remote Moderated | 10 | Week 1-2 | Zoom, Lookback |
| In-Person Lab | 4 | Week 2 | Screen recording |
| Unmoderated Remote | 20 | Week 3 | Maze, Hotjar |

---

## Task Scenarios

### Scenario 1: Fleet Manager - Vehicle Assignment

**Persona:** Ahmed (Fleet Manager)
**Goal:** Assign a vehicle to a new courier

**Steps to evaluate:**
1. Navigate to vehicle management
2. Find an available vehicle
3. Assign to specific courier
4. Verify assignment confirmation

**Success Criteria:**
- Complete in < 3 minutes
- No more than 2 errors
- Can locate feature without help

**Observation Points:**
- [ ] Can find vehicle section easily
- [ ] Filter/search works intuitively
- [ ] Assignment flow is clear
- [ ] Confirmation message noticed

---

### Scenario 2: HR Admin - Leave Approval

**Persona:** Fatima (HR Administrator)
**Goal:** Review and approve a leave request

**Steps to evaluate:**
1. Access pending leave requests
2. Review request details
3. Check leave balance
4. Approve with comment

**Success Criteria:**
- Complete in < 2 minutes
- Balance information visible
- Comment saved correctly

**Observation Points:**
- [ ] Notification badge noticed
- [ ] Leave details sufficient
- [ ] Approval flow clear
- [ ] Confirmation received

---

### Scenario 3: Dispatch - Daily Assignment

**Persona:** Omar (Dispatch Supervisor)
**Goal:** Assign 10 deliveries to 3 couriers

**Steps to evaluate:**
1. Access dispatch board
2. View unassigned deliveries
3. Check courier availability
4. Assign deliveries (bulk or individual)
5. Confirm dispatch

**Success Criteria:**
- Complete in < 5 minutes
- All deliveries assigned correctly
- Couriers notified

**Observation Points:**
- [ ] Dispatch board understandable
- [ ] Drag-drop works (if applicable)
- [ ] Courier capacity visible
- [ ] Bulk actions discovered

---

### Scenario 4: Support - Ticket Resolution

**Persona:** Noura (Support Agent)
**Goal:** Resolve a customer complaint ticket

**Steps to evaluate:**
1. Find the specific ticket
2. Review customer history
3. Add internal note
4. Respond to customer
5. Close or escalate

**Success Criteria:**
- Complete in < 4 minutes
- Customer history accessible
- Response sent correctly

**Observation Points:**
- [ ] Search/filter effective
- [ ] Related info available
- [ ] Response templates found
- [ ] Status update clear

---

### Scenario 5: Admin - User Creation

**Persona:** Khalid (System Administrator)
**Goal:** Create a new user with specific permissions

**Steps to evaluate:**
1. Access user management
2. Create new user
3. Assign role
4. Set organization access
5. Send invitation

**Success Criteria:**
- Complete in < 3 minutes
- Correct permissions set
- Invitation sent

**Observation Points:**
- [ ] Permission system understood
- [ ] Role assignment clear
- [ ] Multi-tenant selection works
- [ ] Confirmation received

---

### Scenario 6: Mobile - Quick Status Update

**Device:** Mobile phone (iOS/Android)
**Goal:** Update delivery status on the go

**Steps to evaluate:**
1. Open mobile view
2. Find assigned delivery
3. Update status to "Delivered"
4. Add proof of delivery note

**Success Criteria:**
- Complete in < 1 minute
- Touch targets adequate
- Offline capability works

**Observation Points:**
- [ ] Mobile navigation clear
- [ ] Touch targets sufficient
- [ ] Forms usable on small screen
- [ ] Confirmation visible

---

## Measurement Framework

### Quantitative Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Task Success Rate | > 85% | Binary success/fail |
| Time on Task | < benchmark + 20% | Stopwatch |
| Error Rate | < 2 per task | Observer count |
| SUS Score | > 75 | Post-task survey |
| NPS | > 40 | Post-session survey |

### Qualitative Data

1. **Think-aloud transcripts**
   - Confusion points
   - Positive reactions
   - Feature requests

2. **Observation notes**
   - Body language
   - Hesitation moments
   - Workarounds used

3. **Post-task interviews**
   - Overall impressions
   - Comparison to current tools
   - Improvement suggestions

---

## Issue Severity Classification

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical (4)** | Prevents task completion | Fix before launch |
| **Major (3)** | Significant difficulty, workaround exists | Fix in first release |
| **Minor (2)** | Annoyance, doesn't block task | Add to backlog |
| **Cosmetic (1)** | Polish/preference issue | Consider for future |

---

## Reporting

### Deliverables

1. **Executive Summary** (1-2 pages)
   - Key findings
   - Top 5 issues
   - Recommendations

2. **Detailed Report** (15-20 pages)
   - Methodology
   - Task-by-task analysis
   - Participant quotes
   - Issue log with severity
   - Screenshots/recordings

3. **Issue Tracker Export**
   - All issues in Jira format
   - Severity, frequency, affected tasks
   - Suggested fixes

4. **Video Highlights**
   - 5-minute compilation
   - Key pain points
   - Success moments

---

## Timeline

```
Week 1:
├── Day 1-2: Finalize test plan, prepare materials
├── Day 3-4: Recruit participants, schedule sessions
└── Day 5: Pilot test (2 participants)

Week 2:
├── Day 1-3: Remote moderated sessions (8 participants)
├── Day 4: In-person lab sessions (4 participants)
└── Day 5: Analysis checkpoint

Week 3:
├── Day 1-2: Unmoderated testing deployment
├── Day 3-4: Collect unmoderated results
└── Day 5: Compile findings

Week 4:
├── Day 1-2: Write report
├── Day 3: Create video highlights
├── Day 4: Present to stakeholders
└── Day 5: Prioritize fixes
```

---

## Tools & Resources

### Testing Tools
- **Maze** - Unmoderated testing platform
- **Lookback** - Remote moderated sessions
- **Hotjar** - Session recordings, heatmaps
- **Optimal Workshop** - Card sorting, tree testing

### Analysis Tools
- **Dovetail** - Qualitative analysis
- **Excel/Sheets** - Quantitative data
- **Miro** - Affinity mapping
- **Loom** - Highlight clips

### Equipment
- MacBook Pro (moderator)
- External webcam
- Ring light
- Spare test devices (iPhone, Android, iPad)

---

## Appendices

### A. Consent Form Template
### B. Screening Questionnaire
### C. SUS Questionnaire
### D. Observer Note Template
### E. Issue Log Template

---

*Document created as part of Phase 6 - Validation & Testing Plan*
