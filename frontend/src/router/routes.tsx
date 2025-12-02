import { RouteObject } from 'react-router-dom'
import { lazyWithRetry } from '@/utils/lazyWithRetry'
import Layout from '@/components/Layout'

// Lazy load all pages with retry mechanism
const Landing = lazyWithRetry(() => import('@/pages/Landing'))
const Dashboard = lazyWithRetry(() => import('@/pages/Dashboard'))
const Login = lazyWithRetry(() => import('@/pages/Login'))
const Users = lazyWithRetry(() => import('@/pages/Users'))
const Couriers = lazyWithRetry(() => import('@/pages/Couriers'))
const Vehicles = lazyWithRetry(() => import('@/pages/Vehicles'))

// Fleet Module
const CouriersList = lazyWithRetry(() => import('@/pages/fleet/CouriersList'))
const CourierProfile = lazyWithRetry(() => import('@/pages/fleet/CourierProfile'))
const VehiclesList = lazyWithRetry(() => import('@/pages/fleet/VehiclesList'))
const VehicleAssignments = lazyWithRetry(() => import('@/pages/fleet/VehicleAssignments'))
const FuelTracking = lazyWithRetry(() => import('@/pages/fleet/FuelTracking'))
const MaintenanceSchedule = lazyWithRetry(() => import('@/pages/fleet/MaintenanceSchedule'))
const CourierPerformance = lazyWithRetry(() => import('@/pages/fleet/CourierPerformance'))
const CourierDocuments = lazyWithRetry(() => import('@/pages/fleet/CourierDocuments'))
const VehicleHistory = lazyWithRetry(() => import('@/pages/fleet/VehicleHistory'))
const LiveTracking = lazyWithRetry(() => import('@/pages/fleet/LiveTracking'))

// HR & Finance Module
const LeaveManagement = lazyWithRetry(() => import('@/pages/hr-finance/LeaveManagement'))
const LoanManagement = lazyWithRetry(() => import('@/pages/hr-finance/LoanManagement'))
const AttendanceTracking = lazyWithRetry(() => import('@/pages/hr-finance/AttendanceTracking'))
const SalaryCalculation = lazyWithRetry(() => import('@/pages/hr-finance/SalaryCalculation'))
const AssetManagement = lazyWithRetry(() => import('@/pages/hr-finance/AssetManagement'))
const Payroll = lazyWithRetry(() => import('@/pages/hr-finance/Payroll'))
const Bonuses = lazyWithRetry(() => import('@/pages/hr-finance/Bonuses'))
const Penalties = lazyWithRetry(() => import('@/pages/hr-finance/Penalties'))
const GOSI = lazyWithRetry(() => import('@/pages/hr-finance/GOSI'))
const EOSCalculation = lazyWithRetry(() => import('@/pages/hr-finance/EOSCalculation'))
const FinancialReports = lazyWithRetry(() => import('@/pages/hr-finance/FinancialReports'))
const ExpenseTracking = lazyWithRetry(() => import('@/pages/hr-finance/ExpenseTracking'))
const BudgetManagement = lazyWithRetry(() => import('@/pages/hr-finance/BudgetManagement'))
const TaxReporting = lazyWithRetry(() => import('@/pages/hr-finance/TaxReporting'))
const FinancialDashboard = lazyWithRetry(() => import('@/pages/hr-finance/FinancialDashboard'))

// Operations Module
const CODManagement = lazyWithRetry(() => import('@/pages/operations/CODManagement'))
const CODReconciliation = lazyWithRetry(() => import('@/pages/operations/CODReconciliation'))
const Documents = lazyWithRetry(() => import('@/pages/operations/Documents'))
const PerformanceTracking = lazyWithRetry(() => import('@/pages/operations/PerformanceTracking'))
const PerformanceMetrics = lazyWithRetry(() => import('@/pages/operations/PerformanceMetrics'))
const Deliveries = lazyWithRetry(() => import('@/pages/operations/Deliveries'))
const DeliveryHistory = lazyWithRetry(() => import('@/pages/operations/DeliveryHistory'))
const DeliveryTracking = lazyWithRetry(() => import('@/pages/operations/DeliveryTracking'))
const ScheduledDeliveries = lazyWithRetry(() => import('@/pages/operations/ScheduledDeliveries'))
const Routes = lazyWithRetry(() => import('@/pages/operations/Routes'))
const RouteOptimization = lazyWithRetry(() => import('@/pages/operations/RouteOptimization'))
const Incidents = lazyWithRetry(() => import('@/pages/operations/Incidents'))
const IncidentReporting = lazyWithRetry(() => import('@/pages/operations/IncidentReporting'))
const QualityControl = lazyWithRetry(() => import('@/pages/operations/QualityControl'))
const CustomerFeedback = lazyWithRetry(() => import('@/pages/operations/CustomerFeedback'))
const ServiceLevels = lazyWithRetry(() => import('@/pages/operations/ServiceLevels'))
const ZoneManagement = lazyWithRetry(() => import('@/pages/operations/ZoneManagement'))
const PriorityQueue = lazyWithRetry(() => import('@/pages/operations/PriorityQueue'))
const OperationsSettings = lazyWithRetry(() => import('@/pages/operations/OperationsSettings'))
const OperationsDashboard = lazyWithRetry(() => import('@/pages/operations/OperationsDashboard'))

// Accommodation Module
const Buildings = lazyWithRetry(() => import('@/pages/accommodation/Buildings'))
const Rooms = lazyWithRetry(() => import('@/pages/accommodation/Rooms'))
const Beds = lazyWithRetry(() => import('@/pages/accommodation/Beds'))
const BedAssignment = lazyWithRetry(() => import('@/pages/accommodation/BedAssignment'))
const Allocations = lazyWithRetry(() => import('@/pages/accommodation/Allocations'))
const Occupancy = lazyWithRetry(() => import('@/pages/accommodation/Occupancy'))
const AccommodationMaintenance = lazyWithRetry(() => import('@/pages/accommodation/Maintenance'))
const MaintenanceRequests = lazyWithRetry(() => import('@/pages/accommodation/MaintenanceRequests'))
const Utilities = lazyWithRetry(() => import('@/pages/accommodation/Utilities'))
const Inventory = lazyWithRetry(() => import('@/pages/accommodation/Inventory'))
const Contracts = lazyWithRetry(() => import('@/pages/accommodation/Contracts'))
const TransferHistory = lazyWithRetry(() => import('@/pages/accommodation/TransferHistory'))
const AccommodationReports = lazyWithRetry(() => import('@/pages/accommodation/AccommodationReports'))

// Workflows Module
const Templates = lazyWithRetry(() => import('@/pages/workflows/Templates'))
const Instances = lazyWithRetry(() => import('@/pages/workflows/Instances'))
const ApprovalChains = lazyWithRetry(() => import('@/pages/workflows/ApprovalChains'))
const SLATracking = lazyWithRetry(() => import('@/pages/workflows/SLATracking'))
const Automations = lazyWithRetry(() => import('@/pages/workflows/Automations'))
const Triggers = lazyWithRetry(() => import('@/pages/workflows/Triggers'))
const History = lazyWithRetry(() => import('@/pages/workflows/History'))
const WorkflowAnalytics = lazyWithRetry(() => import('@/pages/workflows/Analytics'))
const WorkflowSettings = lazyWithRetry(() => import('@/pages/workflows/Settings'))
const WorkflowsDashboard = lazyWithRetry(() => import('@/pages/workflows/WorkflowsDashboard'))
const WorkflowBuilder = lazyWithRetry(() => import('@/pages/workflows/WorkflowBuilder'))
const ActiveWorkflows = lazyWithRetry(() => import('@/pages/workflows/ActiveWorkflows'))
const PendingApprovals = lazyWithRetry(() => import('@/pages/workflows/PendingApprovals'))
const WorkflowNotifications = lazyWithRetry(() => import('@/pages/workflows/WorkflowNotifications'))

// Support Module
const Tickets = lazyWithRetry(() => import('@/pages/support/Tickets'))
const TicketDetails = lazyWithRetry(() => import('@/pages/support/TicketDetails'))
const KnowledgeBase = lazyWithRetry(() => import('@/pages/support/KnowledgeBase'))
const FAQ = lazyWithRetry(() => import('@/pages/support/FAQ'))
const FAQs = lazyWithRetry(() => import('@/pages/support/FAQs'))
const LiveChat = lazyWithRetry(() => import('@/pages/support/LiveChat'))
const Feedback = lazyWithRetry(() => import('@/pages/support/Feedback'))
const SupportAnalytics = lazyWithRetry(() => import('@/pages/support/SupportAnalytics'))
const ContactSupport = lazyWithRetry(() => import('@/pages/support/ContactSupport'))
const Documentation = lazyWithRetry(() => import('@/pages/support/Documentation'))

// Analytics Module - Lazy load on demand (heavy charts dependency)
const AnalyticsOverview = lazyWithRetry(() => import('@/pages/analytics/AnalyticsOverview'))
const FleetAnalytics = lazyWithRetry(() => import('@/pages/analytics/FleetAnalytics'))
const HRAnalytics = lazyWithRetry(() => import('@/pages/analytics/HRAnalytics'))
const FinancialAnalytics = lazyWithRetry(() => import('@/pages/analytics/FinancialAnalytics'))
const OperationsAnalytics = lazyWithRetry(() => import('@/pages/analytics/OperationsAnalytics'))
const CustomReports = lazyWithRetry(() => import('@/pages/analytics/CustomReports'))
const KPIDashboard = lazyWithRetry(() => import('@/pages/analytics/KPIDashboard'))
const Forecasting = lazyWithRetry(() => import('@/pages/analytics/Forecasting'))
const CourierPerformanceAnalytics = lazyWithRetry(() => import('@/pages/analytics/CourierPerformance'))
const DeliveryAnalytics = lazyWithRetry(() => import('@/pages/analytics/DeliveryAnalytics'))
const PerformanceReports = lazyWithRetry(() => import('@/pages/analytics/PerformanceReports'))

// Admin Module
const UserManagement = lazyWithRetry(() => import('@/pages/admin/UserManagement'))
const RoleManagement = lazyWithRetry(() => import('@/pages/admin/RoleManagement'))
const Permissions = lazyWithRetry(() => import('@/pages/admin/Permissions'))
const AuditLogs = lazyWithRetry(() => import('@/pages/admin/AuditLogs'))
const SystemMonitoring = lazyWithRetry(() => import('@/pages/admin/SystemMonitoring'))
const Backups = lazyWithRetry(() => import('@/pages/admin/Backups'))
const Integrations = lazyWithRetry(() => import('@/pages/admin/Integrations'))
const APIKeys = lazyWithRetry(() => import('@/pages/admin/APIKeys'))

// Settings Module
const UserSettings = lazyWithRetry(() => import('@/pages/settings/UserSettings'))
const SystemSettings = lazyWithRetry(() => import('@/pages/settings/SystemSettings'))
const GeneralSettings = lazyWithRetry(() => import('@/pages/settings/GeneralSettings'))
const NotificationSettings = lazyWithRetry(() => import('@/pages/settings/NotificationSettings'))
const Preferences = lazyWithRetry(() => import('@/pages/settings/Preferences'))
const Profile = lazyWithRetry(() => import('@/pages/settings/Profile'))

export const routes: RouteObject[] = [
  {
    path: '/landing',
    element: <Landing />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'users', element: <Users /> },
      { path: 'couriers', element: <Couriers /> },
      { path: 'vehicles', element: <Vehicles /> },

      // Fleet routes
      { path: 'fleet/couriers', element: <CouriersList /> },
      { path: 'fleet/couriers/:id', element: <CourierProfile /> },
      { path: 'fleet/vehicles', element: <VehiclesList /> },
      { path: 'fleet/assignments', element: <VehicleAssignments /> },
      { path: 'fleet/fuel', element: <FuelTracking /> },
      { path: 'fleet/maintenance', element: <MaintenanceSchedule /> },
      { path: 'fleet/performance', element: <CourierPerformance /> },
      { path: 'fleet/documents', element: <CourierDocuments /> },
      { path: 'fleet/vehicle-history', element: <VehicleHistory /> },
      { path: 'fleet/live-tracking', element: <LiveTracking /> },

      // HR & Finance routes
      { path: 'hr/leave', element: <LeaveManagement /> },
      { path: 'hr/loans', element: <LoanManagement /> },
      { path: 'hr/attendance', element: <AttendanceTracking /> },
      { path: 'hr/salary', element: <SalaryCalculation /> },
      { path: 'hr/assets', element: <AssetManagement /> },
      { path: 'hr/payroll', element: <Payroll /> },
      { path: 'hr/bonuses', element: <Bonuses /> },
      { path: 'hr/penalties', element: <Penalties /> },
      { path: 'hr/gosi', element: <GOSI /> },
      { path: 'hr/eos', element: <EOSCalculation /> },
      { path: 'finance/reports', element: <FinancialReports /> },
      { path: 'finance/expenses', element: <ExpenseTracking /> },
      { path: 'finance/budget', element: <BudgetManagement /> },
      { path: 'finance/tax', element: <TaxReporting /> },
      { path: 'finance/dashboard', element: <FinancialDashboard /> },

      // Operations routes
      { path: 'ops/cod', element: <CODManagement /> },
      { path: 'ops/cod-reconciliation', element: <CODReconciliation /> },
      { path: 'ops/documents', element: <Documents /> },
      { path: 'ops/performance', element: <PerformanceTracking /> },
      { path: 'ops/performance-metrics', element: <PerformanceMetrics /> },
      { path: 'ops/deliveries', element: <Deliveries /> },
      { path: 'ops/delivery-history', element: <DeliveryHistory /> },
      { path: 'ops/delivery-tracking', element: <DeliveryTracking /> },
      { path: 'ops/scheduled-deliveries', element: <ScheduledDeliveries /> },
      { path: 'ops/routes', element: <Routes /> },
      { path: 'ops/route-optimization', element: <RouteOptimization /> },
      { path: 'ops/incidents', element: <Incidents /> },
      { path: 'ops/incident-reporting', element: <IncidentReporting /> },
      { path: 'ops/quality', element: <QualityControl /> },
      { path: 'ops/feedback', element: <CustomerFeedback /> },
      { path: 'ops/sla', element: <ServiceLevels /> },
      { path: 'ops/zones', element: <ZoneManagement /> },
      { path: 'ops/priority-queue', element: <PriorityQueue /> },
      { path: 'ops/settings', element: <OperationsSettings /> },
      { path: 'ops/dashboard', element: <OperationsDashboard /> },

      // Accommodation routes
      { path: 'accommodation/buildings', element: <Buildings /> },
      { path: 'accommodation/rooms', element: <Rooms /> },
      { path: 'accommodation/beds', element: <Beds /> },
      { path: 'accommodation/bed-assignment', element: <BedAssignment /> },
      { path: 'accommodation/allocations', element: <Allocations /> },
      { path: 'accommodation/occupancy', element: <Occupancy /> },
      { path: 'accommodation/maintenance', element: <AccommodationMaintenance /> },
      { path: 'accommodation/maintenance-requests', element: <MaintenanceRequests /> },
      { path: 'accommodation/utilities', element: <Utilities /> },
      { path: 'accommodation/inventory', element: <Inventory /> },
      { path: 'accommodation/contracts', element: <Contracts /> },
      { path: 'accommodation/transfer-history', element: <TransferHistory /> },
      { path: 'accommodation/reports', element: <AccommodationReports /> },

      // Workflows routes
      { path: 'workflows/templates', element: <Templates /> },
      { path: 'workflows/builder', element: <WorkflowBuilder /> },
      { path: 'workflows/instances', element: <Instances /> },
      { path: 'workflows/active', element: <ActiveWorkflows /> },
      { path: 'workflows/approvals', element: <ApprovalChains /> },
      { path: 'workflows/pending-approvals', element: <PendingApprovals /> },
      { path: 'workflows/sla', element: <SLATracking /> },
      { path: 'workflows/automations', element: <Automations /> },
      { path: 'workflows/triggers', element: <Triggers /> },
      { path: 'workflows/history', element: <History /> },
      { path: 'workflows/analytics', element: <WorkflowAnalytics /> },
      { path: 'workflows/notifications', element: <WorkflowNotifications /> },
      { path: 'workflows/settings', element: <WorkflowSettings /> },
      { path: 'workflows/dashboard', element: <WorkflowsDashboard /> },

      // Support routes
      { path: 'support/tickets', element: <Tickets /> },
      { path: 'support/tickets/:id', element: <TicketDetails /> },
      { path: 'support/kb', element: <KnowledgeBase /> },
      { path: 'support/faq', element: <FAQ /> },
      { path: 'support/faqs', element: <FAQs /> },
      { path: 'support/chat', element: <LiveChat /> },
      { path: 'support/feedback', element: <Feedback /> },
      { path: 'support/contact', element: <ContactSupport /> },
      { path: 'support/docs', element: <Documentation /> },
      { path: 'support/analytics', element: <SupportAnalytics /> },

      // Analytics routes
      { path: 'analytics/overview', element: <AnalyticsOverview /> },
      { path: 'analytics/fleet', element: <FleetAnalytics /> },
      { path: 'analytics/hr', element: <HRAnalytics /> },
      { path: 'analytics/financial', element: <FinancialAnalytics /> },
      { path: 'analytics/operations', element: <OperationsAnalytics /> },
      { path: 'analytics/custom', element: <CustomReports /> },
      { path: 'analytics/kpi', element: <KPIDashboard /> },
      { path: 'analytics/forecasting', element: <Forecasting /> },
      { path: 'analytics/courier-performance', element: <CourierPerformanceAnalytics /> },
      { path: 'analytics/deliveries', element: <DeliveryAnalytics /> },
      { path: 'analytics/performance-reports', element: <PerformanceReports /> },

      // Admin routes
      { path: 'admin/users', element: <UserManagement /> },
      { path: 'admin/roles', element: <RoleManagement /> },
      { path: 'admin/permissions', element: <Permissions /> },
      { path: 'admin/audit', element: <AuditLogs /> },
      { path: 'admin/monitoring', element: <SystemMonitoring /> },
      { path: 'admin/backups', element: <Backups /> },
      { path: 'admin/integrations', element: <Integrations /> },
      { path: 'admin/api-keys', element: <APIKeys /> },

      // Settings routes
      { path: 'settings/user', element: <UserSettings /> },
      { path: 'settings/system', element: <SystemSettings /> },
      { path: 'settings/general', element: <GeneralSettings /> },
      { path: 'settings/notifications', element: <NotificationSettings /> },
      { path: 'settings/preferences', element: <Preferences /> },
      { path: 'settings/profile', element: <Profile /> },
    ],
  },
]

// Export route import functions for prefetching
export const routeImports = {
  dashboard: () => import('@/pages/Dashboard'),
  fleet: {
    couriers: () => import('@/pages/fleet/CouriersList'),
    vehicles: () => import('@/pages/fleet/VehiclesList'),
    // Add more as needed
  },
  analytics: {
    overview: () => import('@/pages/analytics/Overview'),
    // Add more as needed
  },
}
