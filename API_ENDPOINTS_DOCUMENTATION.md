# BARQ Fleet Management - Complete API Endpoints Documentation

**Base URL:** `/api/v1`

**Authentication:** All endpoints require JWT Bearer token (except login, google auth, register, and root endpoints)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Dashboard](#health--dashboard)
3. [Admin Management](#admin-management)
   - [Roles](#roles)
   - [Permissions](#permissions)
   - [Audit Logs](#audit-logs)
   - [Users](#users)
4. [Fleet Management](#fleet-management)
   - [Vehicles](#vehicles)
   - [Couriers](#couriers)
   - [Assignments](#assignments)
   - [Maintenance](#maintenance)
   - [Inspections](#inspections)
   - [Accident Logs](#accident-logs)
   - [Vehicle Logs](#vehicle-logs)
5. [HR Management](#hr-management)
   - [Attendance](#attendance)
   - [Leave](#leave)
   - [Salary](#salary)
   - [Loans](#loans)
   - [Assets](#assets)
6. [Operations Management](#operations-management)
   - [Deliveries](#deliveries)
   - [Routes](#routes)
   - [COD (Cash On Delivery)](#cod-cash-on-delivery)
   - [Incidents](#incidents)
7. [Workflow Management](#workflow-management)
   - [Templates](#templates)
   - [Instances](#instances)

---

## Authentication

### POST /auth/login
**Description:** OAuth2 compatible token login with email/password
**Authentication:** None (Public)
**Request Body:**
- `username` (string): Email address
- `password` (string): Password
**Response:** Token object with access_token and token_type

### POST /auth/google
**Description:** Google OAuth2 authentication
**Authentication:** None (Public)
**Request Body:**
- `credential` (string): Google ID token
**Response:** Token object with access_token and token_type

### POST /auth/register
**Description:** Public registration endpoint (first user becomes admin)
**Authentication:** None (Public)
**Request Body:**
- `email` (string): Email address
- `password` (string): Password
- `full_name` (string): User's full name
**Response:** Token object with access_token and token_type

---

## Health & Dashboard

### GET / (Root)
**Description:** API root information
**Authentication:** None
**Response:** Message, version, and docs URL

### GET /health
**Description:** Health check endpoint
**Authentication:** None
**Response:** Status, version, and database status

### GET /health/
**Description:** Health check with database connectivity test
**Authentication:** Required
**Response:** Status, version, and detailed database status

### GET /dashboard/stats
**Description:** Get dashboard statistics (total users and vehicles)
**Authentication:** Required
**Response:** Total users and total vehicles count

---

## Admin Management

### Roles

#### GET /admin/roles
**Description:** List all roles with optional filtering
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 100): Maximum records to return (1-100)
- `is_active` (bool, optional): Filter by active status
- `search` (string, optional): Search in name and display_name
**Response:** List of RoleResponse

#### GET /admin/roles/{role_id}
**Description:** Get a specific role by ID
**Authentication:** Required (Superuser)
**Response:** RoleResponse

#### POST /admin/roles
**Description:** Create a new role
**Authentication:** Required (Superuser)
**Request Body:**
- `name` (string): Unique role identifier
- `display_name` (string): Human-readable role name
- `description` (string, optional): Role description
- `is_active` (bool): Active status
- `permission_ids` (List[int], optional): Permission IDs to assign
**Response:** RoleResponse (HTTP 201)

#### PATCH /admin/roles/{role_id}
**Description:** Update an existing role
**Authentication:** Required (Superuser)
**Request Body:**
- `name` (string, optional): Role name
- `display_name` (string, optional): Display name
- `description` (string, optional): Description
- `is_active` (bool, optional): Active status
- `permission_ids` (List[int], optional): Permission IDs
**Response:** RoleResponse

#### DELETE /admin/roles/{role_id}
**Description:** Delete a role
**Authentication:** Required (Superuser)
**Response:** 204 No Content

#### GET /admin/roles/{role_id}/permissions
**Description:** Get all permissions assigned to a role
**Authentication:** Required (Superuser)
**Response:** List of PermissionResponse

#### POST /admin/roles/{role_id}/permissions
**Description:** Assign permissions to a role (replaces existing)
**Authentication:** Required (Superuser)
**Request Body:**
- `permission_ids` (List[int]): Permission IDs to assign
**Response:** RoleResponse

---

### Permissions

#### GET /admin/permissions
**Description:** List all permissions with optional filtering
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 100): Maximum records to return
- `resource` (string, optional): Filter by resource type
- `action` (string, optional): Filter by action type
- `search` (string, optional): Search in name and description
**Response:** List of PermissionResponse

#### GET /admin/permissions/{permission_id}
**Description:** Get a specific permission by ID
**Authentication:** Required (Superuser)
**Response:** PermissionResponse

#### POST /admin/permissions
**Description:** Create a new permission
**Authentication:** Required (Superuser)
**Request Body:**
- `name` (string): Unique identifier (format: "resource:action")
- `resource` (string): Resource type
- `action` (string): Action type
- `description` (string, optional): Description
**Response:** PermissionResponse (HTTP 201)

#### PATCH /admin/permissions/{permission_id}
**Description:** Update a permission's description
**Authentication:** Required (Superuser)
**Request Body:**
- `description` (string, optional): New description
**Response:** PermissionResponse

#### DELETE /admin/permissions/{permission_id}
**Description:** Delete a permission
**Authentication:** Required (Superuser)
**Response:** 204 No Content

#### GET /admin/permissions/resources/list
**Description:** Get list of all unique resource types
**Authentication:** Required (Superuser)
**Response:** List[string]

#### GET /admin/permissions/actions/list
**Description:** Get list of all unique action types
**Authentication:** Required (Superuser)
**Response:** List[string]

---

### Audit Logs

#### GET /admin/audit-logs
**Description:** List audit logs with comprehensive filtering
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 100): Maximum records to return
- `action` (AuditAction, optional): Filter by action type
- `user_id` (int, optional): Filter by user
- `resource_type` (string, optional): Filter by resource type
- `resource_id` (int, optional): Filter by resource ID
- `start_date` (datetime, optional): Filter by start date
- `end_date` (datetime, optional): Filter by end date
- `ip_address` (string, optional): Filter by IP address
- `search` (string, optional): Search in description and username
**Response:** List of AuditLogResponse

#### GET /admin/audit-logs/summary
**Description:** Get summary statistics for audit logs
**Authentication:** Required (Superuser)
**Query Parameters:**
- `start_date` (datetime, optional): Start date filter
- `end_date` (datetime, optional): End date filter
**Response:** AuditLogSummary (total_logs, actions_breakdown, resources_breakdown, top_users, recent_activities)

#### GET /admin/audit-logs/{audit_log_id}
**Description:** Get a specific audit log by ID
**Authentication:** Required (Superuser)
**Response:** AuditLogResponse

#### GET /admin/audit-logs/resource/{resource_type}/{resource_id}
**Description:** Get complete audit trail for a specific resource
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50)
**Response:** List of AuditLogResponse

#### GET /admin/audit-logs/actions/types
**Description:** Get list of all available action types
**Authentication:** Required (Superuser)
**Response:** List[string]

#### GET /admin/audit-logs/resources/types
**Description:** Get list of all resource types with audit logs
**Authentication:** Required (Superuser)
**Response:** List[string]

---

### Users

#### GET /admin/users
**Description:** List all users with optional filtering
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `is_active` (bool, optional): Filter by active status
- `is_superuser` (bool, optional): Filter by superuser status
- `role_id` (int, optional): Filter by role
- `search` (string, optional): Search in email and full_name
**Response:** List of User

#### GET /admin/users/{user_id}
**Description:** Get a specific user by ID
**Authentication:** Required (Superuser)
**Response:** User

#### PATCH /admin/users/{user_id}
**Description:** Update a user
**Authentication:** Required (Superuser)
**Request Body:**
- `email` (string, optional)
- `full_name` (string, optional)
- `is_active` (bool, optional)
**Response:** User

#### POST /admin/users/{user_id}/deactivate
**Description:** Deactivate a user account
**Authentication:** Required (Superuser)
**Response:** User

#### POST /admin/users/{user_id}/activate
**Description:** Activate a deactivated user account
**Authentication:** Required (Superuser)
**Response:** User

#### GET /admin/users/{user_id}/roles
**Description:** Get all roles assigned to a user
**Authentication:** Required (Superuser)
**Response:** List of RoleResponse

#### POST /admin/users/{user_id}/roles
**Description:** Assign roles to a user (replaces existing)
**Authentication:** Required (Superuser)
**Request Body:**
- `role_ids` (List[int]): Role IDs to assign
**Response:** User

#### GET /admin/users/{user_id}/activity
**Description:** Get activity logs for a specific user
**Authentication:** Required (Superuser)
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50)
**Response:** List of AuditLogResponse

#### DELETE /admin/users/{user_id}/roles/{role_id}
**Description:** Remove a specific role from a user
**Authentication:** Required (Superuser)
**Response:** 204 No Content

---

## Fleet Management

### Vehicles

#### GET /fleet/vehicles
**Description:** Get list of vehicles with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100): Max 1000
- `status` (VehicleStatus, optional): Filter by status
- `vehicle_type` (VehicleType, optional): Filter by type
- `city` (string, optional): Filter by assigned city
- `search` (string, optional): Search by plate number or other fields
**Response:** List of VehicleList

#### GET /fleet/vehicles/active
**Description:** Get active vehicles
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_type` (VehicleType, optional)
**Response:** List of VehicleList

#### GET /fleet/vehicles/available
**Description:** Get available vehicles (not assigned)
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_type` (VehicleType, optional)
**Response:** List of VehicleList

#### GET /fleet/vehicles/due-for-service
**Description:** Get vehicles due for service
**Authentication:** Required
**Query Parameters:**
- `days` (int, default: 7): Days threshold
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of VehicleList

#### GET /fleet/vehicles/options
**Description:** Get vehicle options for dropdowns
**Authentication:** Required
**Query Parameters:**
- `status` (VehicleStatus, optional)
**Response:** List of VehicleOption

#### GET /fleet/vehicles/statistics
**Description:** Get vehicle statistics
**Authentication:** Required
**Response:** Vehicle statistics object

#### GET /fleet/vehicles/documents/expiring
**Description:** Get vehicles with documents expiring soon
**Authentication:** Required
**Query Parameters:**
- `days` (int, default: 30): Days threshold
**Response:** List of VehicleDocumentStatus

#### GET /fleet/vehicles/{vehicle_id}
**Description:** Get vehicle by ID
**Authentication:** Required
**Response:** VehicleResponse

#### POST /fleet/vehicles
**Description:** Create new vehicle
**Authentication:** Required
**Request Body:** VehicleCreate
**Response:** VehicleResponse (HTTP 201)

#### PUT /fleet/vehicles/{vehicle_id}
**Description:** Update vehicle
**Authentication:** Required
**Request Body:** VehicleUpdate
**Response:** VehicleResponse

#### DELETE /fleet/vehicles/{vehicle_id}
**Description:** Delete vehicle
**Authentication:** Required
**Response:** 204 No Content

#### POST /fleet/vehicles/{vehicle_id}/update-mileage
**Description:** Update vehicle mileage
**Authentication:** Required
**Query Parameters:**
- `new_mileage` (float): New mileage value
**Response:** Success message

#### POST /fleet/vehicles/{vehicle_id}/update-status
**Description:** Update vehicle status
**Authentication:** Required
**Query Parameters:**
- `new_status` (VehicleStatus): New status
**Response:** Success message

#### POST /fleet/vehicles/bulk-update
**Description:** Bulk update vehicles
**Authentication:** Required
**Request Body:**
- `vehicle_ids` (List[int]): Vehicle IDs to update
- `status` (VehicleStatus, optional)
- `assigned_to_city` (string, optional)
**Response:** Update count message

---

### Couriers

#### GET /fleet/couriers
**Description:** Get list of couriers with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `status` (CourierStatus, optional)
- `city` (string, optional)
- `search` (string, optional): Search by name, email, or BARQ ID
**Response:** List of CourierList

#### GET /fleet/couriers/active
**Description:** Get active couriers
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `city` (string, optional)
**Response:** List of CourierList

#### GET /fleet/couriers/without-vehicle
**Description:** Get couriers without assigned vehicle
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of CourierList

#### GET /fleet/couriers/options
**Description:** Get courier options for dropdowns
**Authentication:** Required
**Query Parameters:**
- `status` (CourierStatus, optional)
**Response:** List of CourierOption

#### GET /fleet/couriers/statistics
**Description:** Get courier statistics
**Authentication:** Required
**Response:** Courier statistics object

#### GET /fleet/couriers/documents/expiring
**Description:** Get couriers with documents expiring soon
**Authentication:** Required
**Query Parameters:**
- `days` (int, default: 30)
**Response:** List of CourierDocumentStatus

#### GET /fleet/couriers/by-barq-id/{barq_id}
**Description:** Get courier by BARQ ID
**Authentication:** Required
**Response:** CourierResponse

#### GET /fleet/couriers/{courier_id}
**Description:** Get courier by ID
**Authentication:** Required
**Response:** CourierResponse

#### POST /fleet/couriers
**Description:** Create new courier
**Authentication:** Required
**Request Body:** CourierCreate
**Response:** CourierResponse (HTTP 201)

#### PUT /fleet/couriers/{courier_id}
**Description:** Update courier
**Authentication:** Required
**Request Body:** CourierUpdate
**Response:** CourierResponse

#### DELETE /fleet/couriers/{courier_id}
**Description:** Delete courier
**Authentication:** Required
**Response:** 204 No Content

#### POST /fleet/couriers/{courier_id}/assign-vehicle
**Description:** Assign vehicle to courier
**Authentication:** Required
**Query Parameters:**
- `vehicle_id` (int): Vehicle ID to assign
**Response:** Success message

#### POST /fleet/couriers/{courier_id}/unassign-vehicle
**Description:** Unassign vehicle from courier
**Authentication:** Required
**Response:** Success message

#### POST /fleet/couriers/{courier_id}/update-status
**Description:** Update courier status
**Authentication:** Required
**Query Parameters:**
- `new_status` (CourierStatus): New status
- `last_working_day` (string, optional): Date in YYYY-MM-DD format
**Response:** Success message

#### POST /fleet/couriers/bulk-update
**Description:** Bulk update couriers
**Authentication:** Required
**Request Body:**
- `courier_ids` (List[int]): Courier IDs to update
- `status` (CourierStatus, optional)
- `city` (string, optional)
**Response:** Update count message

---

### Assignments

#### GET /fleet/assignments
**Description:** Get assignments
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `vehicle_id` (int, optional)
**Response:** List of AssignmentList

#### GET /fleet/assignments/{assignment_id}
**Description:** Get assignment by ID
**Authentication:** Required
**Response:** AssignmentResponse

#### POST /fleet/assignments
**Description:** Create new assignment
**Authentication:** Required
**Request Body:** AssignmentCreate
**Response:** AssignmentResponse (HTTP 201)

#### PUT /fleet/assignments/{assignment_id}
**Description:** Update assignment
**Authentication:** Required
**Request Body:** AssignmentUpdate
**Response:** AssignmentResponse

#### DELETE /fleet/assignments/{assignment_id}
**Description:** Delete assignment
**Authentication:** Required
**Response:** 204 No Content

---

### Maintenance

#### GET /fleet/maintenance
**Description:** Get maintenance records
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_id` (int, optional): Filter by vehicle
**Response:** List of MaintenanceList

#### GET /fleet/maintenance/scheduled
**Description:** Get scheduled maintenance
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of MaintenanceList

#### GET /fleet/maintenance/overdue
**Description:** Get overdue maintenance
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of MaintenanceList

#### GET /fleet/maintenance/{maintenance_id}
**Description:** Get maintenance record by ID
**Authentication:** Required
**Response:** MaintenanceResponse

#### POST /fleet/maintenance
**Description:** Create new maintenance record
**Authentication:** Required
**Request Body:** MaintenanceCreate
**Response:** MaintenanceResponse (HTTP 201)

#### PUT /fleet/maintenance/{maintenance_id}
**Description:** Update maintenance record
**Authentication:** Required
**Request Body:** MaintenanceUpdate
**Response:** MaintenanceResponse

#### DELETE /fleet/maintenance/{maintenance_id}
**Description:** Delete maintenance record
**Authentication:** Required
**Response:** 204 No Content

---

### Inspections

#### GET /fleet/inspections
**Description:** Get inspections
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_id` (int, optional): Filter by vehicle
**Response:** List of InspectionList

#### GET /fleet/inspections/failed
**Description:** Get failed inspections
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of InspectionList

#### GET /fleet/inspections/follow-up
**Description:** Get inspections requiring follow-up
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of InspectionList

#### GET /fleet/inspections/{inspection_id}
**Description:** Get inspection by ID
**Authentication:** Required
**Response:** InspectionResponse

#### POST /fleet/inspections
**Description:** Create new inspection
**Authentication:** Required
**Request Body:** InspectionCreate
**Response:** InspectionResponse (HTTP 201)

#### PUT /fleet/inspections/{inspection_id}
**Description:** Update inspection
**Authentication:** Required
**Request Body:** InspectionUpdate
**Response:** InspectionResponse

#### DELETE /fleet/inspections/{inspection_id}
**Description:** Delete inspection
**Authentication:** Required
**Response:** 204 No Content

---

### Accident Logs

#### GET /fleet/accident-logs
**Description:** Get accident logs
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_id` (int, optional)
- `courier_id` (int, optional)
**Response:** List of AccidentLogList

#### GET /fleet/accident-logs/open
**Description:** Get open accident cases
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of AccidentLogList

#### GET /fleet/accident-logs/{accident_id}
**Description:** Get accident log by ID
**Authentication:** Required
**Response:** AccidentLogResponse

#### POST /fleet/accident-logs
**Description:** Create new accident log
**Authentication:** Required
**Request Body:** AccidentLogCreate
**Response:** AccidentLogResponse (HTTP 201)

#### PUT /fleet/accident-logs/{accident_id}
**Description:** Update accident log
**Authentication:** Required
**Request Body:** AccidentLogUpdate
**Response:** AccidentLogResponse

#### DELETE /fleet/accident-logs/{accident_id}
**Description:** Delete accident log
**Authentication:** Required
**Response:** 204 No Content

---

### Vehicle Logs

#### GET /fleet/vehicle-logs
**Description:** Get vehicle logs
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `vehicle_id` (int, optional)
- `courier_id` (int, optional)
**Response:** List of VehicleLogList

#### GET /fleet/vehicle-logs/{log_id}
**Description:** Get vehicle log by ID
**Authentication:** Required
**Response:** VehicleLogResponse

#### POST /fleet/vehicle-logs
**Description:** Create new vehicle log
**Authentication:** Required
**Request Body:** VehicleLogCreate
**Response:** VehicleLogResponse (HTTP 201)

#### PUT /fleet/vehicle-logs/{log_id}
**Description:** Update vehicle log
**Authentication:** Required
**Request Body:** VehicleLogUpdate
**Response:** VehicleLogResponse

#### DELETE /fleet/vehicle-logs/{log_id}
**Description:** Delete vehicle log
**Authentication:** Required
**Response:** 204 No Content

---

## HR Management

### Attendance

#### GET /hr/attendance
**Description:** Get attendance records with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `status` (AttendanceStatus, optional)
- `date_from` (date, optional)
- `date_to` (date, optional)
**Response:** List of AttendanceResponse

#### POST /hr/attendance
**Description:** Create new attendance record
**Authentication:** Required
**Request Body:** AttendanceCreate
**Response:** AttendanceResponse (HTTP 201)

#### GET /hr/attendance/{attendance_id}
**Description:** Get attendance record by ID
**Authentication:** Required
**Response:** AttendanceResponse

#### PUT /hr/attendance/{attendance_id}
**Description:** Update attendance record
**Authentication:** Required
**Request Body:** AttendanceUpdate
**Response:** AttendanceResponse

#### DELETE /hr/attendance/{attendance_id}
**Description:** Delete attendance record
**Authentication:** Required
**Response:** 204 No Content

#### GET /hr/attendance/courier/{courier_id}
**Description:** Get all attendance records for a specific courier
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of AttendanceResponse

#### POST /hr/attendance/check-in
**Description:** Check in a courier for the day
**Authentication:** Required
**Request Body:**
- `courier_id` (int)
**Response:** AttendanceResponse

#### POST /hr/attendance/{attendance_id}/check-out
**Description:** Check out a courier
**Authentication:** Required
**Response:** AttendanceResponse

#### GET /hr/attendance/statistics
**Description:** Get attendance statistics
**Authentication:** Required
**Query Parameters:**
- `date_from` (date, optional)
- `date_to` (date, optional)
**Response:** Statistics object (total, present, absent, late, on_leave)

---

### Leave

#### GET /hr/leave
**Description:** Get leave requests with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `status` (LeaveStatus, optional)
- `leave_type` (LeaveType, optional)
- `courier_id` (int, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** List of LeaveResponse

#### POST /hr/leave
**Description:** Create new leave request
**Authentication:** Required
**Request Body:** LeaveCreate
**Response:** LeaveResponse (HTTP 201)

#### GET /hr/leave/{leave_id}
**Description:** Get leave request by ID
**Authentication:** Required
**Response:** LeaveResponse

#### PUT /hr/leave/{leave_id}
**Description:** Update leave request
**Authentication:** Required
**Request Body:** LeaveUpdate
**Response:** LeaveResponse

#### DELETE /hr/leave/{leave_id}
**Description:** Delete leave request
**Authentication:** Required
**Response:** 204 No Content

#### GET /hr/leave/courier/{courier_id}
**Description:** Get all leave requests for a specific courier
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of LeaveResponse

#### POST /hr/leave/{leave_id}/approve
**Description:** Approve a leave request
**Authentication:** Required
**Query Parameters:**
- `notes` (string, optional)
**Response:** LeaveResponse

#### POST /hr/leave/{leave_id}/reject
**Description:** Reject a leave request
**Authentication:** Required
**Query Parameters:**
- `reason` (string, optional)
**Response:** LeaveResponse

#### GET /hr/leave/statistics
**Description:** Get leave statistics
**Authentication:** Required
**Response:** Statistics object (total, pending, approved, rejected)

---

### Salary

#### GET /hr/salary
**Description:** Get salary records with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `month` (int, optional): 1-12
- `year` (int, optional)
- `is_paid` (bool, optional)
**Response:** List of SalaryResponse

#### POST /hr/salary
**Description:** Create new salary record
**Authentication:** Required
**Request Body:** SalaryCreate
**Response:** SalaryResponse (HTTP 201)

#### GET /hr/salary/{salary_id}
**Description:** Get salary record by ID
**Authentication:** Required
**Response:** SalaryResponse

#### PUT /hr/salary/{salary_id}
**Description:** Update salary record
**Authentication:** Required
**Request Body:** SalaryUpdate
**Response:** SalaryResponse

#### DELETE /hr/salary/{salary_id}
**Description:** Delete salary record
**Authentication:** Required
**Response:** 204 No Content

#### GET /hr/salary/courier/{courier_id}
**Description:** Get all salary records for a specific courier
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of SalaryResponse

#### POST /hr/salary/calculate
**Description:** Calculate and create salary for a courier for a specific month
**Authentication:** Required
**Request Body:**
- `courier_id` (int)
- `month` (int): 1-12
- `year` (int)
**Response:** SalaryResponse (HTTP 201)

#### POST /hr/salary/{salary_id}/mark-paid
**Description:** Mark a salary as paid
**Authentication:** Required
**Request Body:**
- `payment_date` (date, optional): Defaults to today
**Response:** SalaryResponse

#### GET /hr/salary/statistics
**Description:** Get salary statistics
**Authentication:** Required
**Query Parameters:**
- `month` (int, optional): 1-12
- `year` (int, optional)
**Response:** Statistics object (total_salaries, paid_count, unpaid_count, total_gross, total_net, total_deductions)

---

### Loans

#### GET /hr/loan
**Description:** Get loans with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `status` (LoanStatus, optional)
**Response:** List of LoanResponse

#### POST /hr/loan
**Description:** Create new loan request
**Authentication:** Required
**Request Body:** LoanCreate
**Response:** LoanResponse (HTTP 201)

#### GET /hr/loan/{loan_id}
**Description:** Get loan by ID
**Authentication:** Required
**Response:** LoanResponse

#### PUT /hr/loan/{loan_id}
**Description:** Update loan
**Authentication:** Required
**Request Body:** LoanUpdate
**Response:** LoanResponse

#### DELETE /hr/loan/{loan_id}
**Description:** Delete loan
**Authentication:** Required
**Response:** 204 No Content

#### GET /hr/loan/courier/{courier_id}
**Description:** Get all loans for a specific courier
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of LoanResponse

#### POST /hr/loan/{loan_id}/payment
**Description:** Make a payment towards a loan
**Authentication:** Required
**Request Body:**
- `amount` (Decimal): Payment amount (must be > 0)
**Response:** LoanResponse

#### POST /hr/loan/{loan_id}/approve
**Description:** Approve a loan request
**Authentication:** Required
**Request Body:**
- `notes` (string, optional)
**Response:** LoanResponse

#### GET /hr/loan/statistics
**Description:** Get loan statistics
**Authentication:** Required
**Response:** Statistics object (total, active, paid, pending, total_amount, total_outstanding)

---

### Assets

#### GET /hr/asset
**Description:** Get assets with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `asset_type` (AssetType, optional)
- `status` (AssetStatus, optional)
**Response:** List of AssetResponse

#### POST /hr/asset
**Description:** Create new asset assignment
**Authentication:** Required
**Request Body:** AssetCreate
**Response:** AssetResponse (HTTP 201)

#### GET /hr/asset/{asset_id}
**Description:** Get asset by ID
**Authentication:** Required
**Response:** AssetResponse

#### PUT /hr/asset/{asset_id}
**Description:** Update asset
**Authentication:** Required
**Request Body:** AssetUpdate
**Response:** AssetResponse

#### DELETE /hr/asset/{asset_id}
**Description:** Delete asset
**Authentication:** Required
**Response:** 204 No Content

#### GET /hr/asset/courier/{courier_id}
**Description:** Get all assets assigned to a specific courier
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of AssetResponse

#### POST /hr/asset/{asset_id}/return
**Description:** Mark an asset as returned
**Authentication:** Required
**Request Body:**
- `return_date` (date, optional): Defaults to today
- `notes` (string, optional)
**Response:** AssetResponse

#### POST /hr/asset/{asset_id}/mark-damaged
**Description:** Mark an asset as damaged
**Authentication:** Required
**Request Body:**
- `damage_date` (date, optional): Defaults to today
- `notes` (string, optional)
**Response:** AssetResponse

#### POST /hr/asset/{asset_id}/mark-lost
**Description:** Mark an asset as lost
**Authentication:** Required
**Request Body:**
- `lost_date` (date, optional): Defaults to today
- `notes` (string, optional)
**Response:** AssetResponse

#### GET /hr/asset/statistics
**Description:** Get asset statistics
**Authentication:** Required
**Response:** Statistics object (total, assigned, returned, damaged, lost, by_type)

---

## Operations Management

### Deliveries

#### GET /operations/deliveries
**Description:** Get deliveries with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `status` (DeliveryStatus, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
- `tracking_number` (string, optional): Search by tracking number
**Response:** List of DeliveryResponse

#### POST /operations/deliveries
**Description:** Create new delivery
**Authentication:** Required
**Request Body:** DeliveryCreate
**Response:** DeliveryResponse (HTTP 201)

#### GET /operations/deliveries/pending
**Description:** Get pending deliveries
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of DeliveryResponse

#### GET /operations/deliveries/cod
**Description:** Get deliveries with COD amount
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `status` (DeliveryStatus, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of DeliveryResponse

#### GET /operations/deliveries/statistics
**Description:** Get delivery statistics
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** Statistics object

#### GET /operations/deliveries/{delivery_id}
**Description:** Get delivery by ID
**Authentication:** Required
**Response:** DeliveryResponse

#### PUT /operations/deliveries/{delivery_id}
**Description:** Update delivery
**Authentication:** Required
**Request Body:** DeliveryUpdate
**Response:** DeliveryResponse

#### DELETE /operations/deliveries/{delivery_id}
**Description:** Delete delivery
**Authentication:** Required
**Response:** 204 No Content

#### PATCH /operations/deliveries/{delivery_id}/status
**Description:** Update delivery status
**Authentication:** Required
**Request Body:**
- `status_update` (DeliveryStatus)
- `notes` (string, optional)
**Response:** DeliveryResponse

#### PATCH /operations/deliveries/{delivery_id}/assign
**Description:** Assign delivery to a courier
**Authentication:** Required
**Request Body:**
- `courier_id` (int)
**Response:** DeliveryResponse

---

### Routes

#### GET /operations/routes
**Description:** Get routes with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `route_date` (date, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** List of RouteResponse

#### POST /operations/routes
**Description:** Create new route
**Authentication:** Required
**Request Body:** RouteCreate
**Response:** RouteResponse (HTTP 201)

#### GET /operations/routes/upcoming
**Description:** Get upcoming routes (today and future)
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of RouteResponse

#### GET /operations/routes/statistics
**Description:** Get route statistics
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** Statistics object

#### GET /operations/routes/{route_id}
**Description:** Get route by ID
**Authentication:** Required
**Response:** RouteResponse

#### PUT /operations/routes/{route_id}
**Description:** Update route
**Authentication:** Required
**Request Body:** RouteUpdate
**Response:** RouteResponse

#### DELETE /operations/routes/{route_id}
**Description:** Delete route
**Authentication:** Required
**Response:** 204 No Content

#### PATCH /operations/routes/{route_id}/optimize
**Description:** Update route with optimized waypoints
**Authentication:** Required
**Request Body:**
- `optimized_waypoints` (List[Dict])
**Response:** RouteResponse

#### POST /operations/routes/{route_id}/waypoints
**Description:** Add a waypoint to route
**Authentication:** Required
**Request Body:**
- `waypoint` (Dict)
**Response:** RouteResponse

#### DELETE /operations/routes/{route_id}/waypoints/{waypoint_index}
**Description:** Remove a waypoint from route
**Authentication:** Required
**Response:** RouteResponse

---

### COD (Cash On Delivery)

#### GET /operations/cod
**Description:** Get COD transactions with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `status` (CODStatus, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** List of CODResponse

#### POST /operations/cod
**Description:** Create new COD transaction
**Authentication:** Required
**Request Body:** CODCreate
**Response:** CODResponse (HTTP 201)

#### GET /operations/cod/pending
**Description:** Get pending COD transactions
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of CODResponse

#### GET /operations/cod/statistics
**Description:** Get COD statistics
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** Statistics object

#### GET /operations/cod/balance/{courier_id}
**Description:** Get courier's COD balance
**Authentication:** Required
**Response:** Balance object

#### GET /operations/cod/{cod_id}
**Description:** Get COD transaction by ID
**Authentication:** Required
**Response:** CODResponse

#### PUT /operations/cod/{cod_id}
**Description:** Update COD transaction
**Authentication:** Required
**Request Body:** CODUpdate
**Response:** CODResponse

#### DELETE /operations/cod/{cod_id}
**Description:** Delete COD transaction
**Authentication:** Required
**Response:** 204 No Content

#### PATCH /operations/cod/{cod_id}/collect
**Description:** Mark COD as collected
**Authentication:** Required
**Request Body:**
- `reference_number` (string, optional)
- `notes` (string, optional)
**Response:** CODResponse

#### PATCH /operations/cod/{cod_id}/deposit
**Description:** Mark COD as deposited
**Authentication:** Required
**Request Body:**
- `deposit_date` (date, optional)
- `reference_number` (string, optional)
- `notes` (string, optional)
**Response:** CODResponse

#### PATCH /operations/cod/{cod_id}/reconcile
**Description:** Mark COD as reconciled
**Authentication:** Required
**Request Body:**
- `notes` (string, optional)
**Response:** CODResponse

#### POST /operations/cod/bulk-deposit
**Description:** Mark multiple COD transactions as deposited
**Authentication:** Required
**Request Body:**
- `cod_ids` (List[int])
- `deposit_date` (date, optional)
- `reference_number` (string, optional)
**Response:** Success message with updated count

#### POST /operations/cod/settle/{courier_id}
**Description:** Settle all pending and collected COD for a courier
**Authentication:** Required
**Request Body:**
- `deposit_date` (date, optional)
- `reference_number` (string, optional)
**Response:** Settlement details

---

### Incidents

#### GET /operations/incidents
**Description:** Get incidents with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `courier_id` (int, optional)
- `vehicle_id` (int, optional)
- `incident_type` (IncidentType, optional)
- `status` (IncidentStatus, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** List of IncidentResponse

#### POST /operations/incidents
**Description:** Create new incident
**Authentication:** Required
**Request Body:** IncidentCreate
**Response:** IncidentResponse (HTTP 201)

#### GET /operations/incidents/open
**Description:** Get open incidents (reported or investigating)
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `vehicle_id` (int, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of IncidentResponse

#### GET /operations/incidents/recent
**Description:** Get recent incidents within specified days
**Authentication:** Required
**Query Parameters:**
- `days` (int, default: 30): 1-365
- `courier_id` (int, optional)
- `vehicle_id` (int, optional)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of IncidentResponse

#### GET /operations/incidents/high-cost
**Description:** Get incidents with high costs
**Authentication:** Required
**Query Parameters:**
- `min_cost` (int, default: 1000)
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of IncidentResponse

#### GET /operations/incidents/statistics
**Description:** Get incident statistics
**Authentication:** Required
**Query Parameters:**
- `courier_id` (int, optional)
- `vehicle_id` (int, optional)
- `start_date` (date, optional)
- `end_date` (date, optional)
**Response:** Statistics object

#### GET /operations/incidents/{incident_id}
**Description:** Get incident by ID
**Authentication:** Required
**Response:** IncidentResponse

#### PUT /operations/incidents/{incident_id}
**Description:** Update incident
**Authentication:** Required
**Request Body:** IncidentUpdate
**Response:** IncidentResponse

#### DELETE /operations/incidents/{incident_id}
**Description:** Delete incident
**Authentication:** Required
**Response:** 204 No Content

#### PATCH /operations/incidents/{incident_id}/status
**Description:** Update incident status
**Authentication:** Required
**Request Body:**
- `status_update` (IncidentStatus)
- `resolution` (string, optional)
**Response:** IncidentResponse

#### PATCH /operations/incidents/{incident_id}/resolve
**Description:** Mark incident as resolved
**Authentication:** Required
**Request Body:**
- `resolution` (string)
- `cost` (int, optional)
**Response:** IncidentResponse

#### PATCH /operations/incidents/{incident_id}/close
**Description:** Close incident
**Authentication:** Required
**Request Body:**
- `resolution` (string, optional)
**Response:** IncidentResponse

---

## Workflow Management

### Templates

#### GET /workflow/template
**Description:** Get workflow templates with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `is_active` (bool, optional)
- `category` (string, optional)
**Response:** List of WorkflowTemplateResponse

#### POST /workflow/template
**Description:** Create new workflow template
**Authentication:** Required
**Request Body:** WorkflowTemplateCreate
**Response:** WorkflowTemplateResponse (HTTP 201)

#### GET /workflow/template/{template_id}
**Description:** Get workflow template by ID
**Authentication:** Required
**Response:** WorkflowTemplateResponse

#### PUT /workflow/template/{template_id}
**Description:** Update workflow template
**Authentication:** Required
**Request Body:** WorkflowTemplateUpdate
**Response:** WorkflowTemplateResponse

#### DELETE /workflow/template/{template_id}
**Description:** Delete workflow template
**Authentication:** Required
**Response:** 204 No Content

#### POST /workflow/template/{template_id}/activate
**Description:** Activate a workflow template
**Authentication:** Required
**Response:** WorkflowTemplateResponse

#### POST /workflow/template/{template_id}/deactivate
**Description:** Deactivate a workflow template
**Authentication:** Required
**Response:** WorkflowTemplateResponse

#### GET /workflow/template/categories/list
**Description:** Get all unique template categories
**Authentication:** Required
**Response:** List[string]

#### GET /workflow/template/statistics/summary
**Description:** Get workflow template statistics
**Authentication:** Required
**Response:** Statistics object (total, active, inactive, categories)

---

### Instances

#### GET /workflow/instance
**Description:** Get workflow instances with filtering
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `status` (WorkflowStatus, optional)
- `template_id` (int, optional)
- `initiated_by` (int, optional)
**Response:** List of WorkflowInstanceResponse

#### POST /workflow/instance
**Description:** Create new workflow instance
**Authentication:** Required
**Request Body:** WorkflowInstanceCreate
**Response:** WorkflowInstanceResponse (HTTP 201)

#### GET /workflow/instance/{instance_id}
**Description:** Get workflow instance by ID
**Authentication:** Required
**Response:** WorkflowInstanceResponse

#### PUT /workflow/instance/{instance_id}
**Description:** Update workflow instance
**Authentication:** Required
**Request Body:** WorkflowInstanceUpdate
**Response:** WorkflowInstanceResponse

#### DELETE /workflow/instance/{instance_id}
**Description:** Delete workflow instance
**Authentication:** Required
**Response:** 204 No Content

#### POST /workflow/instance/{instance_id}/start
**Description:** Start a workflow instance
**Authentication:** Required
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/complete-step
**Description:** Complete current step and move to next
**Authentication:** Required
**Request Body:**
- `step_data` (Dict, optional)
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/complete
**Description:** Complete a workflow instance
**Authentication:** Required
**Request Body:**
- `notes` (string, optional)
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/cancel
**Description:** Cancel a workflow instance
**Authentication:** Required
**Request Body:**
- `reason` (string, optional)
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/submit-approval
**Description:** Submit workflow instance for approval
**Authentication:** Required
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/approve
**Description:** Approve a workflow instance
**Authentication:** Required
**Request Body:**
- `notes` (string, optional)
**Response:** WorkflowInstanceResponse

#### POST /workflow/instance/{instance_id}/reject
**Description:** Reject a workflow instance
**Authentication:** Required
**Request Body:**
- `reason` (string, optional)
**Response:** WorkflowInstanceResponse

#### GET /workflow/instance/user/{user_id}
**Description:** Get all workflow instances initiated by a specific user
**Authentication:** Required
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
**Response:** List of WorkflowInstanceResponse

#### GET /workflow/instance/statistics/summary
**Description:** Get workflow instance statistics
**Authentication:** Required
**Response:** Statistics object (total, draft, in_progress, pending_approval, approved, completed, rejected, cancelled)

---

## Summary Statistics

**Total Endpoints:** 200+

**By Category:**
- Authentication: 3
- Health & Dashboard: 3
- Admin (Roles): 8
- Admin (Permissions): 6
- Admin (Audit Logs): 6
- Admin (Users): 9
- Fleet (Vehicles): 15
- Fleet (Couriers): 14
- Fleet (Assignments): 5
- Fleet (Maintenance): 7
- Fleet (Inspections): 7
- Fleet (Accident Logs): 7
- Fleet (Vehicle Logs): 6
- HR (Attendance): 8
- HR (Leave): 8
- HR (Salary): 8
- HR (Loans): 7
- HR (Assets): 9
- Operations (Deliveries): 9
- Operations (Routes): 10
- Operations (COD): 13
- Operations (Incidents): 13
- Workflow (Templates): 8
- Workflow (Instances): 15

**Authentication Requirements:**
- All endpoints except `/`, `/health`, `/auth/login`, `/auth/google`, `/auth/register` require JWT Bearer token authentication
- Superuser-only endpoints: All `/admin/*` routes

**Rate Limiting:**
- Standard pagination: skip (offset), limit (max results)
- Typical limit: 100 records, max 1000
- Some endpoints have specific limits (e.g., audit logs max 100)

---

**Generated:** 2025-11-13
**API Version:** 1.0.0
