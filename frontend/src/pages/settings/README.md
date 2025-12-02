# Settings Module - BARQ Fleet Management System

## Overview

The Settings module provides comprehensive configuration and customization options for the BARQ Fleet Management System. It includes user profile management, application preferences, notification settings, and system-wide configurations.

## Module Structure

```
/frontend/src/pages/settings/
├── Profile.tsx                    # User profile editing (name, email, photo, password)
├── UserSettings.tsx              # User account settings (2FA, security, API access)
├── Preferences.tsx               # UI preferences (theme, language, date format)
├── NotificationSettings.tsx      # Notification channel preferences
├── GeneralSettings.tsx           # General application settings
├── SystemSettings.tsx            # System-wide settings (admin only)
└── README.md                     # This file
```

## Pages

### 1. Profile Settings (`/settings/profile`)

**Purpose:** Manage personal profile information and authentication

**Features:**
- **Profile Tab:**
  - Profile photo upload (JPG, PNG, GIF - max 5MB)
  - Full name editing
  - Email address update
  - Phone number
  - Language preference (English/Arabic)
  - Timezone selection
  - Date format preference

- **Security Tab:**
  - Change password with strength indicator
  - Current password verification
  - Password strength meter (Weak/Fair/Good/Strong)
  - Minimum 8 characters requirement

- **Notifications Tab:**
  - Email notifications toggle
  - SMS notifications toggle
  - Push notifications toggle

**API Endpoints:**
- `GET /api/v1/settings/user/profile` - Get user profile
- `PUT /api/v1/settings/user/profile` - Update profile
- `POST /api/v1/settings/user/profile/photo` - Upload profile photo
- `PUT /api/v1/settings/user/password` - Change password
- `GET /api/v1/settings/user/notifications` - Get notification preferences
- `PUT /api/v1/settings/user/notifications` - Update notification preferences

**Components Used:**
- Card, CardContent
- Button
- Input
- Select
- Spinner

**Validation:**
- Email format validation
- Password strength requirements (min 8 characters)
- Password confirmation matching
- Image file type validation (image/*)
- Image size validation (max 5MB)

---

### 2. User Settings (`/settings/user`)

**Purpose:** Advanced user account configuration and security settings

**Features:**
- **Account Tab:**
  - Username (read-only)
  - Email address editing
  - Phone number editing
  - Role display (read-only)

- **Security Tab:**
  - Two-factor authentication (2FA) enable/disable
  - Session timeout configuration (5-1440 minutes)
  - Active sessions viewer
  - Password change redirect
  - Last password change timestamp

- **Advanced Tab:**
  - API access enable/disable
  - Data export request
  - Account deletion (Danger Zone)

**API Endpoints:**
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/settings/user/profile` - Update account info

**Security Features:**
- Two-factor authentication setup
- Session management
- API access control
- Account deletion with confirmation ("DELETE" typing required)

**Icons Used:**
- User, Shield, Key (tab icons)
- Mail, Phone (input icons)
- Save, Trash2 (action icons)

---

### 3. Preferences (`/settings/preferences`)

**Purpose:** Customize the application interface and behavior

**Features:**
- **Display Settings:**
  - Theme: Light / Dark / Auto (System)
  - Language: English / Arabic (العربية)

- **Date & Time:**
  - Date Format: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
  - Time Format: 12-hour / 24-hour

- **Regional:**
  - Currency: SAR, USD, EUR, GBP

- **Table Settings:**
  - Default Page Size: 10, 25, 50, 100 rows

- **Export Settings:**
  - Default Export Format: Excel, PDF, CSV
  - Include Headers in Export: Toggle
  - Show Column Headers: Toggle

- **Preview Section:**
  - Live preview of date, time, currency formatting

**API Endpoints:**
- `GET /api/v1/settings/user/preferences` - Get preferences
- `PUT /api/v1/settings/user/preferences` - Update preferences
- `POST /api/v1/settings/user/preferences/reset` - Reset to defaults

**Default Preferences:**
```typescript
{
  theme: 'light',
  language: 'en',
  date_format: 'DD/MM/YYYY',
  time_format: '24h',
  currency: 'SAR',
  default_page_size: 25,
  show_column_headers: true,
  default_export_format: 'excel',
  include_export_headers: true
}
```

**Theme Implementation:**
- Applies theme immediately on change
- Uses `document.documentElement.classList` for dark mode
- Auto mode respects system preference via `prefers-color-scheme`

---

### 4. Notification Settings (`/settings/notifications`)

**Purpose:** Configure notification delivery channels for various events

**Features:**
- **Notification Matrix Table:**
  - Event types (rows) × Channels (columns)
  - Channels: Email, SMS, Push, WhatsApp
  - Toggle each combination independently

- **Event Types:**
  - Delivery Assigned
  - Delivery Completed
  - Vehicle Maintenance Due
  - Leave Request
  - Leave Approved/Rejected
  - COD Collection
  - Incident Reported
  - Attendance Anomaly
  - System Updates

- **Additional Options:**
  - Email Digest (daily summary)
  - Do Not Disturb (10 PM - 7 AM)
  - Marketing Notifications

**API Endpoints:**
- `GET /api/v1/settings/notifications` - Get notification settings
- `PUT /api/v1/settings/notifications` - Update notification settings

**Data Structure:**
```typescript
interface NotificationPreference {
  event_type: string
  email: boolean
  sms: boolean
  push: boolean
  whatsapp: boolean
}
```

**UI Components:**
- Responsive table with icons for each channel
- Checkbox toggles for each event/channel combination
- Additional option cards with descriptions

---

### 5. General Settings (`/settings/general`)

**Purpose:** Configure company information and system-wide defaults

**Features:**
- **Company Information:**
  - Company Name
  - Company Email
  - Company Phone

- **Localization:**
  - Timezone (UTC, America/New_York, Europe/London, Asia/Dubai, Asia/Tokyo, etc.)
  - Language (English, Arabic, Spanish, French, German)

- **Date & Time Format:**
  - Date Format with examples
  - Time Format (12-hour / 24-hour)
  - Live preview of current date/time

- **Currency Settings:**
  - Currency selection (USD, EUR, GBP, SAR, JPY)
  - Currency Symbol
  - Preview of formatted currency

**API Endpoints:**
- `GET /api/v1/settings/general` - Get general settings
- `PUT /api/v1/settings/general` - Update general settings

**Preview Features:**
- Real-time date/time preview based on selected timezone
- Currency formatting preview
- Updates immediately on selection

---

### 6. System Settings (`/settings/system`)

**Purpose:** System-wide configuration (Admin Only)

**Features:**
- **Company Information:**
  - Company Name *
  - Company Logo URL
  - Address *
  - Phone *
  - Email *

- **System Preferences:**
  - Timezone *
  - Language *
  - Currency *
  - Date Format *
  - Time Format *

- **Business Hours:**
  - Start Time *
  - End Time *
  - Info: Used for delivery estimates and SLA tracking

- **Feature Modules (Enable/Disable):**
  - Fleet Management
  - HR & Finance
  - Accommodation
  - Workflows & Automation
  - Analytics & Reporting

- **Integration Settings:**
  - Google OAuth (Enable/Disable with status badge)
  - SMS Provider (Twilio, AWS SNS, Nexmo, Disabled)
  - Email Service (SMTP, SendGrid, AWS SES, Mailgun, Disabled)

**API Endpoints:**
- `GET /api/v1/settings/system` - Get system settings
- `PUT /api/v1/settings/system` - Update system settings

**Access Control:**
- Admin role required
- Module toggles affect entire system
- Integration settings control external services

**Data Structure:**
```typescript
interface SystemSettingsData {
  id: number
  company_name: string
  company_logo_url: string | null
  company_address: string
  company_phone: string
  company_email: string
  timezone: string
  language: string
  currency: string
  date_format: string
  time_format: string
  business_hours_start: string
  business_hours_end: string
  module_fleet_enabled: boolean
  module_hr_finance_enabled: boolean
  module_accommodation_enabled: boolean
  module_workflows_enabled: boolean
  module_analytics_enabled: boolean
  integration_google_oauth: boolean
  integration_sms_provider: string
  integration_email_service: string
  updated_at: string
}
```

---

## Common Patterns

### State Management

All settings pages follow a consistent pattern:

```typescript
// 1. Query for data
const { data, isLoading } = useQuery({
  queryKey: ['settings-key'],
  queryFn: settingsAPI.getSettings,
})

// 2. Local state for form
const [formData, setFormData] = useState(defaultValues)

// 3. Sync with server data
useEffect(() => {
  if (data) {
    setFormData(data)
  }
}, [data])

// 4. Mutation for updates
const updateMutation = useMutation({
  mutationFn: settingsAPI.updateSettings,
  onSuccess: () => {
    toast.success('Settings updated')
    queryClient.invalidateQueries({ queryKey: ['settings-key'] })
  },
  onError: () => toast.error('Failed to update'),
})
```

### Form Submission

```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  updateMutation.mutate(formData)
}
```

### Loading States

```typescript
if (isLoading) {
  return (
    <div className="flex items-center justify-center h-64">
      <Spinner />
    </div>
  )
}
```

---

## Routing Configuration

Routes defined in `/frontend/src/router/routes.tsx`:

```typescript
// Settings routes
{ path: 'settings/profile', element: <Profile /> },
{ path: 'settings/user', element: <UserSettings /> },
{ path: 'settings/preferences', element: <Preferences /> },
{ path: 'settings/notifications', element: <NotificationSettings /> },
{ path: 'settings/general', element: <GeneralSettings /> },
{ path: 'settings/system', element: <SystemSettings /> },
```

---

## API Client Configuration

Located in `/frontend/src/lib/api.ts`:

### Profile API
```typescript
export const profileAPI = {
  get: async () => { ... },
  update: async (profileData: any) => { ... },
  uploadPhoto: async (file: File) => { ... },
  changePassword: async (passwordData: { current_password: string; new_password: string }) => { ... },
  getNotificationPreferences: async () => { ... },
  updateNotificationPreferences: async (preferences: any) => { ... },
}
```

### Preferences API
```typescript
export const preferencesAPI = {
  get: async () => { ... },
  update: async (preferences: any) => { ... },
  reset: async () => { ... },
}
```

### Settings API
```typescript
export const settingsAPI = {
  get: async () => { ... },
  update: async (settings: any) => { ... },
  getGeneral: async () => { ... },
  updateGeneral: async (settings: any) => { ... },
  getNotifications: async () => { ... },
  updateNotifications: async (settings: any) => { ... },
}
```

---

## UI Components Reference

### Core Components
- **Card, CardContent, CardHeader, CardTitle** - Container components
- **Button** - Actions (variants: primary, secondary, danger, success, ghost, outline)
- **Input** - Text inputs with label, error, helper text, icons
- **Select** - Dropdown selects with options
- **Spinner** - Loading indicator
- **Badge** - Status indicators

### Icons (lucide-react)
- User, Mail, Phone, Lock, Key
- Shield, Save, RotateCcw, Trash2
- Bell, Camera, Building, Globe, Clock, DollarSign
- MessageSquare, Smartphone, Settings

---

## Toast Notifications

Using `react-hot-toast`:

```typescript
import toast from 'react-hot-toast'

// Success
toast.success('Settings updated successfully')

// Error
toast.error('Failed to update settings')
```

---

## Accessibility Features

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Enter key submits forms

### ARIA Labels
- Checkboxes have associated labels
- Icons are decorative only
- Helper text provides context

### Screen Reader Support
- Semantic HTML structure
- Form labels properly associated
- Status messages announced

### Visual Indicators
- Focus states on interactive elements
- Error states with red borders and text
- Success feedback via toast notifications

---

## Form Validation

### Client-Side Validation

**Profile:**
- Email format: `type="email"`
- Password minimum length: 8 characters
- Password match validation
- Image file type and size

**User Settings:**
- Email required
- Phone optional
- Session timeout: 5-1440 minutes

**Preferences:**
- All selections from predefined options
- No free-text inputs to minimize errors

### Server-Side Validation
- All API endpoints perform validation
- Returns appropriate error messages
- Client displays errors via toast

---

## Responsive Design

All settings pages are responsive:

### Mobile (< 768px)
- Single column layouts
- Stacked form fields
- Horizontal scroll for notification table
- Collapsible sections

### Tablet (768px - 1024px)
- Two-column grids where appropriate
- Optimized spacing
- Touch-friendly controls

### Desktop (> 1024px)
- Multi-column layouts
- Side-by-side comparisons
- Maximum content width (max-w-4xl, max-w-5xl)

---

## Performance Optimization

### Code Splitting
- Lazy loaded via `lazyWithRetry()` utility
- Each settings page loaded on demand
- Reduces initial bundle size

### Query Caching
- React Query caches fetched data
- Automatic revalidation on refetch
- Optimistic updates where appropriate

### Debouncing
- Form inputs can be debounced for live updates
- Prevents excessive API calls

---

## Error Handling

### Network Errors
```typescript
onError: () => {
  toast.error('Failed to update settings')
}
```

### Loading States
- Spinner shown during data fetch
- Button disabled during mutation
- Loading text on buttons

### Validation Errors
- Client-side validation before submission
- Server errors displayed via toast
- Field-level error messages where applicable

---

## Testing Recommendations

### Unit Tests
- Test form validation logic
- Test state updates
- Test API client functions

### Integration Tests
- Test full form submission flow
- Test error handling
- Test success states

### E2E Tests
- Test complete user journeys
- Test photo upload
- Test password change
- Test preference changes and persistence

---

## Future Enhancements

### Planned Features
1. **Profile:**
   - Avatar crop/resize tool
   - Social media links
   - Custom user fields

2. **User Settings:**
   - Active sessions with location/device info
   - Login history
   - IP whitelisting

3. **Preferences:**
   - Custom themes builder
   - Keyboard shortcuts customization
   - Dashboard layout preferences

4. **Notifications:**
   - Notification scheduling
   - Quiet hours per weekday
   - Custom notification sounds

5. **System Settings:**
   - Multi-language support expansion
   - Custom branding (colors, logos)
   - Backup/restore settings

---

## Troubleshooting

### Common Issues

**Problem:** Settings not saving
- **Solution:** Check network tab for API errors, verify token is valid

**Problem:** Photo upload fails
- **Solution:** Verify file size < 5MB and type is image/*

**Problem:** Theme not applying
- **Solution:** Check browser localStorage, clear cache

**Problem:** Preferences reset on page reload
- **Solution:** Ensure mutations are invalidating queries properly

---

## Development Setup

### Prerequisites
- Node.js >= 18
- React 19
- TypeScript 5
- TanStack Query (React Query) v5

### Environment Variables
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Running Locally
```bash
cd frontend
npm install
npm run dev
```

### Building for Production
```bash
npm run build
npm run preview
```

---

## API Backend Requirements

### Endpoints Needed
All endpoints documented in respective page sections above.

### Authentication
- Bearer token in Authorization header
- Managed by axios interceptor in `api.ts`

### File Upload
- Multipart form data for profile photo
- Maximum file size enforced server-side

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Settings updated successfully"
}
```

---

## Contributing

### Code Style
- Use TypeScript for type safety
- Follow existing component patterns
- Use functional components with hooks
- Consistent naming conventions

### Pull Request Checklist
- [ ] Code follows existing patterns
- [ ] API endpoints documented
- [ ] Error handling implemented
- [ ] Loading states handled
- [ ] Responsive design tested
- [ ] Accessibility verified
- [ ] Toast notifications added
- [ ] Query invalidation correct

---

## License

Part of BARQ Fleet Management System - Proprietary

---

## Contact

For questions or issues with the Settings module:
- Developer: BARQ Development Team
- Documentation: This README
- API Docs: `/docs/api/settings.md`

---

**Last Updated:** December 2, 2025
**Version:** 1.0.0
**Maintainer:** Frontend Team
