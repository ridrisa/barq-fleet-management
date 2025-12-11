# SYNC Fleet Management Platform

## Complete Product Documentation

**Version:** 2.0
**Last Updated:** December 11, 2025
**Status:** Production-Ready

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Platform Overview](#2-platform-overview)
3. [Technology Stack](#3-technology-stack)
4. [Web Application (SYNC Fleet Management)](#4-web-application-sync-fleet-management)
5. [Mobile Application (SYNC Driver App)](#5-mobile-application-sync-driver-app)
6. [System Architecture](#6-system-architecture)
7. [Security & Compliance](#7-security--compliance)
8. [API Reference](#8-api-reference)
9. [Deployment & Infrastructure](#9-deployment--infrastructure)
10. [Integration Guide](#10-integration-guide)
11. [Performance & Scalability](#11-performance--scalability)
12. [Support & Maintenance](#12-support--maintenance)

---

## 1. Executive Summary

### What is SYNC?

**SYNC** is an enterprise-grade fleet management and delivery operations platform designed for logistics companies operating in Saudi Arabia and the Middle East. The platform provides end-to-end management of delivery operations, fleet tracking, HR management, and business analytics.

### Key Value Propositions

| Capability | Description |
|------------|-------------|
| **Ultra-Fast Delivery** | Support for BARQ (15-30 min) and BULLET (2-4 hours) delivery tiers |
| **Complete Fleet Visibility** | Real-time GPS tracking, maintenance scheduling, fuel monitoring |
| **Points-Based Performance** | Gamified driver performance system with leaderboards |
| **Multi-Tenant Architecture** | Serve multiple organizations from a single deployment |
| **Offline-First Mobile** | Driver app works without connectivity, syncs when online |
| **Saudi Compliance** | GOSI, ZATCA, and Saudi labor law compliant HR features |

### Platform Statistics

| Metric | Value | Verified |
|--------|-------|----------|
| API Endpoints | 763 | ✅ |
| Database Tables | 93 | ✅ |
| Web Pages | 117 | ✅ |
| Mobile Screens | 140 | ✅ |
| Reusable Components | 83 | ✅ |
| Test Coverage Target | 95% | - |

---

## 2. Platform Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SYNC PLATFORM                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │  SYNC Web App    │    │  SYNC Driver App │    │  External     │ │
│  │  (React 18)      │    │  (React Native)  │    │  Integrations │ │
│  │                  │    │                  │    │               │ │
│  │  • Fleet Mgmt    │    │  • Order Mgmt    │    │  • Jahez      │ │
│  │  • HR & Payroll  │    │  • Navigation    │    │  • BARQ       │ │
│  │  • Operations    │    │  • Performance   │    │  • SANED      │ │
│  │  • Analytics     │    │  • Offline Sync  │    │  • BigQuery   │ │
│  │  • Workflows     │    │  • Push Notifs   │    │  • FMS        │ │
│  └────────┬─────────┘    └────────┬─────────┘    └───────┬───────┘ │
│           │                       │                       │         │
│           └───────────────────────┼───────────────────────┘         │
│                                   │                                  │
│                          ┌────────▼────────┐                        │
│                          │  SYNC API       │                        │
│                          │  (FastAPI)      │                        │
│                          │                 │                        │
│                          │  • REST API     │                        │
│                          │  • GraphQL      │                        │
│                          │  • WebSocket    │                        │
│                          └────────┬────────┘                        │
│                                   │                                  │
│           ┌───────────────────────┼───────────────────────┐         │
│           │                       │                       │         │
│  ┌────────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐ │
│  │  PostgreSQL     │    │  Redis          │    │  Cloud Storage  │ │
│  │  (Cloud SQL)    │    │  (Upstash)      │    │  (GCS)          │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### User Roles

| Role | Access Level | Typical Users |
|------|--------------|---------------|
| **Owner** | Full system access, billing, organization settings | Business owners, C-level executives |
| **Admin** | All operational features, user management | Operations managers, IT administrators |
| **Manager** | Department-specific features, reporting | Fleet managers, HR managers, supervisors |
| **Viewer** | Read-only access to relevant data | Analysts, support staff |
| **Driver** | Mobile app access only | Delivery couriers |

---

## 3. Technology Stack

### Backend

| Component | Technology | Version | Verified |
|-----------|------------|---------|----------|
| Framework | FastAPI | 0.104.1 | ✅ |
| Language | Python | 3.11+ | ✅ |
| ORM | SQLAlchemy | 2.0.23 | ✅ |
| Database | PostgreSQL | 16+ | ✅ |
| Cache | Redis (Upstash) | 7+ | ✅ |
| Task Queue | Celery | Latest | - |
| Validation | Pydantic | 2.5.0 | ✅ |
| GraphQL | Strawberry | 0.217.1 | ✅ |

### Frontend (Web)

| Component | Technology | Version | Verified |
|-----------|------------|---------|----------|
| Framework | React | 18.2.0 | ✅ |
| Language | TypeScript | 5.3.3 | ✅ |
| Build Tool | Vite | 5.0.7 | ✅ |
| State Management | Zustand | 4.4.7 | ✅ |
| Data Fetching | React Query | 5.12.0 | ✅ |
| Forms | React Hook Form | 7.66.0 | ✅ |
| Validation | Zod | 4.1.12 | ✅ |
| Styling | Tailwind CSS | 3.3.6 | ✅ |
| Charts | Recharts | 3.3.0 | ✅ |
| HTTP Client | Axios | 1.6.2 | ✅ |

### Mobile (Driver App)

| Component | Technology | Version | Verified |
|-----------|------------|---------|----------|
| Framework | React Native | 0.81.5 | ✅ |
| Platform | Expo | 54.0.25 | ✅ |
| Language | TypeScript | 5.9.2 | ✅ |
| State Management | Zustand | 5.0.8 | ✅ |
| Navigation | Expo Router | 6.0.15 | ✅ |
| GraphQL | Apollo Client | 4.0.9 | ✅ |
| Maps | Google Maps SDK | Native | ✅ |
| Push Notifications | OneSignal | - | - |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Cloud Platform | Google Cloud Platform |
| Container Runtime | Cloud Run |
| Database | Cloud SQL (PostgreSQL) |
| CI/CD | Cloud Build + GitHub Actions |
| Monitoring | Sentry, Prometheus |
| Secrets | Google Secret Manager |
| CDN | Cloud CDN |

---

## 4. Web Application (SYNC Fleet Management)

### 4.1 Dashboard

The main dashboard provides a comprehensive overview of fleet operations:

- **Key Metrics**: Active deliveries, available couriers, vehicles in use
- **Real-Time Charts**: Delivery trends, revenue, SLA compliance
- **Alerts Panel**: Maintenance due, SLA breaches, incidents
- **Quick Actions**: Common tasks accessible in one click

### 4.2 Fleet Management Module

#### Courier Management
- Complete courier lifecycle (onboarding → active → suspended → terminated)
- Document management (ID, license, insurance)
- Performance tracking with BigQuery integration
- Attendance and working hours
- Asset allocation (devices, uniforms)

#### Vehicle Management
- Vehicle registry with maintenance schedules
- Real-time GPS tracking via FMS integration
- Fuel consumption monitoring
- Insurance and registration tracking
- Inspection checklists

#### Assignments
- Courier-vehicle assignment workflow
- Automatic assignment suggestions
- Assignment history and audit trail

### 4.3 Operations Module

#### Delivery Management
- End-to-end delivery lifecycle tracking
- Multi-platform order aggregation (Jahez, BARQ, etc.)
- Real-time status updates
- Customer feedback collection

#### Dispatch Console
- Real-time dispatch with route optimization
- Auto-dispatch based on proximity and capacity
- Manual override capabilities
- Batch order processing

#### Route Optimization
- Google Maps API integration
- Multi-stop route planning
- Traffic-aware ETA calculation
- Alternative route suggestions

#### SLA Management
- Configurable SLA definitions
- Real-time compliance monitoring
- Automatic escalation workflows
- Penalty calculation

### 4.4 HR & Payroll Module

#### Leave Management
- Leave request and approval workflow
- Balance tracking (annual, sick, emergency)
- Holiday calendar integration
- Leave encashment

#### Payroll Processing
- Automated salary calculation
- Bonus and penalty integration
- GOSI contribution calculation
- End of Service (EOS) benefits
- Payslip generation

#### Attendance
- Clock in/out tracking
- Overtime calculation
- Shift management
- Absence reporting

#### Loans & Advances
- Loan request workflow
- Automatic salary deductions
- Repayment tracking

### 4.5 Accommodation Module

- Building and room management
- Bed-level occupancy tracking
- Employee allocation workflow
- Maintenance requests
- Utility tracking

### 4.6 Workflow Engine

- Visual workflow builder
- Multi-level approval chains
- SLA tracking per workflow
- Automated triggers
- Email/SMS notifications
- Complete audit trail

### 4.7 Analytics & Reporting

#### Pre-Built Dashboards
- Fleet Analytics: Utilization, efficiency, costs
- HR Analytics: Workforce metrics, attendance, turnover
- Operations Analytics: Delivery performance, SLA compliance
- Financial Analytics: Revenue, costs, profitability

#### Custom Reports
- Drag-and-drop report builder
- Scheduled report delivery
- Export to Excel, PDF, CSV
- BigQuery integration for advanced analytics

### 4.8 Support System

- Multi-channel ticket management
- Live chat integration
- Knowledge base with search
- FAQ management
- SLA tracking for support tickets

### 4.9 Admin Panel

- User management with RBAC
- Role and permission configuration
- API key management
- System audit logs
- Backup and restore
- Integration settings

---

## 5. Mobile Application (SYNC Driver App)

### 5.1 Overview

The SYNC Driver App is a React Native application designed for delivery couriers with **140 screen components**. It focuses on:

- **Mandatory Order Acceptance**: Orders auto-accept after 15-second countdown
- **Points-Based Performance**: Gamified earnings system
- **Offline-First**: Full functionality without internet
- **Privacy-Conscious**: Proximity-based contact information reveal

### 5.1.1 App Screens (Verified)

| Screen | File | Description |
|--------|------|-------------|
| Home | `app/(tabs)/index.tsx` | Main dashboard with stats |
| Orders | `app/(tabs)/orders.tsx` | Active orders list |
| Maps | `app/(tabs)/maps.tsx` | Real-time navigation |
| Performance | `app/(tabs)/performance.tsx` | Points & metrics |
| Earnings | `app/(tabs)/earnings.tsx` | Daily/weekly earnings |
| Profile | `app/(tabs)/profile.tsx` | Driver profile |
| Settings | `app/(tabs)/settings.tsx` | App settings |
| Support | `app/(tabs)/support.tsx` | Help & support |
| Order Detail | `app/order/[id].tsx` | Single order view |
| Order Guidance | `app/order-guidance/[id].tsx` | Navigation guidance |
| Leaderboard | `app/leaderboard.tsx` | Performance ranking |
| Challenges | `app/challenges.tsx` | Active challenges |
| Rewards | `app/rewards.tsx` | Earned rewards |
| Leave Request | `app/leave-request.tsx` | Request time off |
| HR Services | `app/hr-services.tsx` | HR features |
| Bonuses/Penalties | `app/bonuses-penalties.tsx` | Earnings breakdown |
| Driver Wellness | `app/driver-wellness.tsx` | Health features |
| Emergency | `app/emergency.tsx` | SOS features |
| Available Shipments | `app/available-shipments.tsx` | New orders |
| Batch Orders | `app/batch-orders.tsx` | Multi-stop orders |
| Route Guide | `app/route-guide.tsx` | Navigation help |
| Live Chat | `app/live-chat.tsx` | Support chat |
| Help Center | `app/help-center.tsx` | FAQ & guides |
| Report Issue | `app/report-issue.tsx` | Problem reporting |
| Vehicle Settings | `app/vehicle-settings.tsx` | Vehicle config |
| Driver License | `app/drivers-license.tsx` | License info |
| Target Details | `app/target-details.tsx` | Performance targets |
| Performance History | `app/performance-history.tsx` | Historical data |
| Performance Detail | `app/performance-detail/[id].tsx` | Detailed metrics |

### 5.2 Main Screens

#### Home Screen
```
┌─────────────────────────────────┐
│  SYNC Driver                 ⚙️ │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │  🟢 ONLINE              │   │
│  │  Mohammed Ahmed         │   │
│  │  Good morning!          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────┬─────────┬──────┐  │
│  │ 156 pts │  24     │ #3   │  │
│  │ Today   │ Orders  │ Rank │  │
│  └─────────┴─────────┴──────┘  │
│                                 │
│  ┌─────────────────────────┐   │
│  │  📦 Active Orders (2)    │   │
│  │  ├─ ORD-1234 - Pickup   │   │
│  │  └─ ORD-1235 - Delivery │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │  📋 Available (5)        │   │
│  │  View available orders → │   │
│  └─────────────────────────┘   │
│                                 │
├─────────────────────────────────┤
│  🏠   📦   🗺️   📊   👤       │
└─────────────────────────────────┘
```

#### Order Detail Screen
- Complete order information
- Status timeline with timestamps
- Pickup/delivery addresses with navigation
- Customer contact (unlocks at 500m proximity)
- Photo proof capture
- Exception reporting
- ETA display

#### Performance Screen
- Points dashboard with targets
- Weekly/monthly progress
- Leaderboard (Top 5 + current position)
- Achievements and badges
- Challenge participation

#### Maps Screen
- Full-screen Google Maps
- Active order markers
- Real-time location tracking
- Traffic overlay
- Emergency SOS button

### 5.3 Key Features

#### Order Notification System
```
┌─────────────────────────────────┐
│                                 │
│        🚀 NEW ORDER!            │
│                                 │
│  ┌─────────────────────────┐   │
│  │  BARQ Delivery          │   │
│  │  Al Olaya → Al Malqa    │   │
│  │  3.2 km • 15 min        │   │
│  │  +12 points             │   │
│  └─────────────────────────┘   │
│                                 │
│       Auto-accept in: 12s       │
│       ████████░░░░░░░░         │
│                                 │
│  ┌─────────────────────────┐   │
│  │     ✓ ACCEPT NOW        │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

#### Offline Capabilities
| Feature | Offline Support |
|---------|-----------------|
| View current orders | ✅ Full |
| Status transitions | ✅ Queued |
| Photo capture | ✅ Queued |
| Navigation | ✅ Cached tiles |
| Accept new orders | ❌ Requires connection |
| Push notifications | ❌ Requires connection |

#### Proximity-Based Privacy
- Merchant contact: Unlocked at 500m from pickup
- Customer contact: Unlocked at 500m from delivery
- Visual indicators show lock status
- Distance countdown display

### 5.4 Driver Wellness Features

- Break reminders after continuous work
- Hydration notifications
- Fatigue detection
- Weather alerts
- Rest area recommendations

### 5.5 Safety Features

- Emergency SOS button (always visible)
- Automatic location sharing in emergencies
- Dangerous zone warnings
- Incident reporting
- Safety tips contextual to location/time

---

## 6. System Architecture

### 6.1 Database Schema (Key Tables)

#### Core Entities
```sql
-- Users and Authentication
users                    -- System users
organizations           -- Multi-tenant organizations
organization_users      -- User-organization membership
roles                   -- RBAC roles
permissions             -- Permission definitions

-- Fleet Management
couriers                -- Delivery drivers
vehicles                -- Fleet vehicles
assignments             -- Courier-vehicle assignments
maintenance             -- Maintenance records
inspections             -- Vehicle inspections
fuel_logs               -- Fuel consumption

-- Operations
deliveries              -- Delivery orders
dispatch                -- Dispatch assignments
routes                  -- Route definitions
cod                     -- Cash on delivery
incidents               -- Incident reports
sla                     -- SLA definitions

-- HR & Payroll
leave                   -- Leave requests
loans                   -- Employee loans
salary                  -- Salary records
attendance              -- Clock in/out
bonuses                 -- Bonus allocations
penalties               -- Penalty records

-- Workflow Engine
workflow_templates      -- Workflow definitions
workflow_instances      -- Active workflows
approval_chains         -- Approval levels
workflow_history        -- Audit trail
```

### 6.2 Multi-Tenancy Model

```
Organization (Tenant)
    │
    ├── Users (with roles: owner, admin, manager, viewer)
    │
    ├── Fleet
    │   ├── Couriers
    │   ├── Vehicles
    │   └── Assignments
    │
    ├── Operations
    │   ├── Deliveries
    │   ├── Routes
    │   └── SLA Definitions
    │
    └── HR
        ├── Leave Balances
        ├── Payroll
        └── Attendance
```

**Row-Level Security (RLS)** ensures data isolation between organizations. Each query is automatically filtered by `organization_id`.

### 6.3 API Architecture

```
                    ┌─────────────────────────────┐
                    │        Load Balancer        │
                    │      (Cloud Run Ingress)    │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │       SYNC API Server       │
                    │         (FastAPI)           │
                    ├─────────────────────────────┤
                    │                             │
                    │  ┌─────────────────────┐   │
                    │  │   Middleware Stack   │   │
                    │  │  • CORS             │   │
                    │  │  • Authentication   │   │
                    │  │  • Rate Limiting    │   │
                    │  │  • Request Logging  │   │
                    │  │  • RLS Context      │   │
                    │  └─────────────────────┘   │
                    │                             │
                    │  ┌─────────────────────┐   │
                    │  │   API Routers       │   │
                    │  │  • /auth            │   │
                    │  │  • /fleet           │   │
                    │  │  • /operations      │   │
                    │  │  • /hr              │   │
                    │  │  • /analytics       │   │
                    │  │  • /admin           │   │
                    │  │  • /graphql         │   │
                    │  └─────────────────────┘   │
                    │                             │
                    │  ┌─────────────────────┐   │
                    │  │   Service Layer     │   │
                    │  │  (Business Logic)   │   │
                    │  └─────────────────────┘   │
                    │                             │
                    └─────────────┬───────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐   ┌────────▼────────┐   ┌─────────▼─────────┐
│    PostgreSQL     │   │      Redis      │   │     BigQuery      │
│    (Cloud SQL)    │   │    (Upstash)    │   │   (Analytics)     │
└───────────────────┘   └─────────────────┘   └───────────────────┘
```

---

## 7. Security & Compliance

### 7.1 Authentication

| Method | Description |
|--------|-------------|
| JWT Tokens | Primary authentication with configurable expiration |
| Google OAuth 2.0 | Social login for convenience |
| Biometric | Fingerprint/Face ID on mobile |
| API Keys | For system-to-system integration |

### 7.2 Authorization

- **Role-Based Access Control (RBAC)**: Predefined roles with permissions
- **Row-Level Security (RLS)**: Database-level tenant isolation
- **Resource-Level Permissions**: Fine-grained access control

### 7.3 Data Protection

| Feature | Implementation |
|---------|----------------|
| Password Hashing | Argon2 (OWASP recommended) |
| Data Encryption | AES-256 for sensitive fields |
| TLS/SSL | Enforced HTTPS in production |
| Token Security | JWT with audience/issuer validation |

### 7.4 Compliance

| Regulation | Status |
|------------|--------|
| GOSI (Saudi Social Insurance) | ✅ Automated calculation |
| Saudi Labor Law | ✅ Leave, EOS, working hours |
| ZATCA (Tax Authority) | ✅ Tax reporting ready |
| PDPL (Data Protection) | ✅ Data handling compliant |

### 7.5 Audit Trail

All sensitive operations are logged:
- User authentication events
- Data modifications
- Permission changes
- API key usage
- System configuration changes

---

## 8. API Reference

### 8.1 Authentication

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secret

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "organization_id": 1,
  "organization_name": "SYNC Logistics",
  "organization_role": "admin"
}
```

```http
POST /api/v1/auth/google
Content-Type: application/json

{
  "credential": "google_id_token..."
}
```

### 8.2 Fleet Management

```http
# List Couriers
GET /api/v1/fleet/couriers/?limit=20&offset=0&status=active

# Get Courier Details
GET /api/v1/fleet/couriers/{id}

# Create Courier
POST /api/v1/fleet/couriers/
{
  "employee_id": "EMP001",
  "name": "Mohammed Ahmed",
  "phone": "+966501234567",
  "email": "mohammed@example.com",
  "status": "active"
}

# Update Courier Status
PATCH /api/v1/fleet/couriers/{id}/status
{
  "status": "on_leave"
}
```

### 8.3 Operations

```http
# List Deliveries
GET /api/v1/operations/deliveries/?status=in_progress

# Create Delivery
POST /api/v1/operations/deliveries/
{
  "pickup_address": "Al Olaya, Riyadh",
  "delivery_address": "Al Malqa, Riyadh",
  "customer_phone": "+966501234567",
  "service_type": "BARQ"
}

# Update Delivery Status
PATCH /api/v1/operations/deliveries/{id}/status
{
  "status": "delivered",
  "proof_photo_url": "https://..."
}

# Auto-Dispatch
POST /api/v1/operations/dispatch/auto-dispatch
{
  "delivery_id": 123
}
```

### 8.4 HR

```http
# Request Leave
POST /api/v1/hr/leave/
{
  "leave_type": "annual",
  "start_date": "2025-01-15",
  "end_date": "2025-01-20",
  "reason": "Family vacation"
}

# Approve Leave
POST /api/v1/hr/leave/{id}/approve

# Calculate Salary
GET /api/v1/hr/salary/calculate?employee_id=123&month=12&year=2025
```

### 8.5 Analytics

```http
# Dashboard Stats
GET /api/v1/dashboard/stats

# Fleet Analytics
GET /api/v1/analytics/fleet?period=monthly

# Performance Metrics (BigQuery)
GET /api/v1/analytics/performance?courier_id=123
```

### 8.6 Error Responses

```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE",
  "field": "affected_field"  // Optional
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/expired token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid data format |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error |

---

## 9. Deployment & Infrastructure

### 9.1 Production URLs

| Service | URL |
|---------|-----|
| Web App | https://sync-web-869422381378.me-central1.run.app |
| API | https://sync-api-869422381378.me-central1.run.app |
| API Docs | https://sync-api-869422381378.me-central1.run.app/api/v1/docs |
| Health Check | https://sync-api-869422381378.me-central1.run.app/health |

### 9.2 Cloud Build Pipeline

```yaml
# Simplified cloudbuild.yaml flow
steps:
  1. Install Dependencies (npm ci)
  2. Lint + Type Check (parallel)
  3. Build Docker Images (parallel)
  4. Push to Artifact Registry
  5. Deploy to Cloud Run
  6. Smoke Tests
```

### 9.3 Environment Variables

#### Backend
| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | development, staging, production |
| `POSTGRES_SERVER` | Database host or Cloud SQL socket |
| `POSTGRES_DB` | Database name |
| `SECRET_KEY` | JWT signing key |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `UPSTASH_REDIS_REST_URL` | Redis URL |
| `SENTRY_DSN` | Error tracking DSN |

#### Frontend
| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |

#### Mobile
| Variable | Description |
|----------|-------------|
| `EXPO_PUBLIC_API_URL` | Backend API URL |
| `EXPO_PUBLIC_BACKEND_TYPE` | barqfleet or saned |
| `EXPO_PUBLIC_GOOGLE_MAPS_API_KEY` | Maps API key |
| `EXPO_PUBLIC_ONESIGNAL_APP_ID` | Push notifications |

### 9.4 Scaling Configuration

| Service | Min Instances | Max Instances | CPU | Memory |
|---------|---------------|---------------|-----|--------|
| sync-api | 1 | 50 | 2 | 2Gi |
| sync-web | 1 | 20 | 1 | 512Mi |

---

## 10. Integration Guide

### 10.1 Third-Party Platforms

#### Jahez Integration
```python
# Order sync from Jahez
POST /api/v1/platforms/orders/sync
{
  "platform": "jahez",
  "orders": [...]
}
```

#### BARQ Platform
```python
# Internal BARQ order integration
POST /api/v1/platforms/orders/sync
{
  "platform": "barq",
  "orders": [...]
}
```

#### SANED Backend (Driver App)
The driver app can connect to SANED backend for legacy support:
- Gateway: `gateway.saned.io`
- Location Gateway: `gateway-cars.saned.io`
- Push Notifications: OneSignal

### 10.2 FMS (Fleet Management System)

```python
# Sync vehicle data from FMS
POST /api/v1/fms/sync
{
  "vehicles": [...],
  "locations": [...]
}

# Get real-time tracking
GET /api/v1/fms/tracking?vehicle_ids=1,2,3
```

### 10.3 BigQuery Analytics

```python
# Performance data from BigQuery
GET /api/v1/analytics/bigquery/performance
{
  "courier_id": 123,
  "period": "monthly"
}
```

### 10.4 Webhooks

Configure webhooks for real-time events:

```json
{
  "url": "https://your-server.com/webhook",
  "events": [
    "delivery.created",
    "delivery.completed",
    "courier.status_changed",
    "order.dispatched"
  ],
  "secret": "webhook_secret_for_verification"
}
```

---

## 11. Performance & Scalability

### 11.1 Backend Performance

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (P95) | <100ms | ~80ms |
| Database Query Time | <50ms | ~30ms |
| Concurrent Users | 10,000+ | Tested to 5,000 |
| Requests/Second | 1,000+ | Cloud Run auto-scales |

### 11.2 Frontend Performance

| Metric | Target | Current |
|--------|--------|---------|
| First Contentful Paint | <1.5s | ~1.2s |
| Time to Interactive | <3s | ~2.5s |
| Lighthouse Score | >90 | 85+ |

### 11.3 Mobile Performance

| Metric | Target | Current |
|--------|--------|---------|
| App Launch Time | <2s | ~1.5s |
| Memory Usage | <200MB | ~185MB |
| Battery Impact | Low | 90% reduction achieved |
| Offline Sync Queue | 1000 items | Supported |

### 11.4 Caching Strategy

| Cache Layer | Technology | TTL |
|-------------|------------|-----|
| API Response | Redis | 5-60 min |
| Session Data | Redis | 15 min |
| Static Assets | CDN | 1 year |
| Database Queries | Connection Pool | Per-request |

---

## 12. Support & Maintenance

### 12.1 Monitoring

| Tool | Purpose |
|------|---------|
| Sentry | Error tracking, performance monitoring |
| Cloud Monitoring | Infrastructure metrics |
| Cloud Logging | Centralized logs |
| Health Endpoints | Service availability |

### 12.2 Backup Strategy

| Data | Frequency | Retention |
|------|-----------|-----------|
| Database | Daily | 30 days |
| Configuration | On change | Versioned |
| Audit Logs | Continuous | 1 year |

### 12.3 Incident Response

1. **Detection**: Automated alerts via Sentry/Cloud Monitoring
2. **Triage**: Severity classification (P1-P4)
3. **Response**: On-call engineer notification
4. **Resolution**: Fix deployment via Cloud Build
5. **Post-mortem**: RCA and prevention measures

### 12.4 Contact Information

| Purpose | Contact |
|---------|---------|
| Technical Support | support@syncfleet.com |
| Security Issues | security@syncfleet.com |
| API Access | api@syncfleet.com |
| Documentation | docs.syncfleet.com |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **BARQ** | Ultra-fast delivery tier (15-30 minutes) |
| **BULLET** | Same-day delivery tier (2-4 hours) |
| **COD** | Cash on Delivery |
| **EOS** | End of Service benefits |
| **FMS** | Fleet Management System (GPS tracking) |
| **GOSI** | General Organization for Social Insurance (Saudi) |
| **RLS** | Row-Level Security |
| **SLA** | Service Level Agreement |
| **ZATCA** | Zakat, Tax and Customs Authority (Saudi) |

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Dec 2025 | Multi-tenant, workflow engine, BigQuery |
| 1.5 | Oct 2025 | Driver app v2, offline sync |
| 1.0 | Aug 2025 | Initial production release |

---

## Appendix C: License

Copyright 2025 SYNC Fleet Management. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

**Document Generated:** December 11, 2025
**Platform Version:** 2.0
**Documentation Version:** 1.0
