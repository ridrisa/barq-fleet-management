# UI Components Usage Examples

## Chart Components

### LineChart
```tsx
import { LineChart } from '@/components/ui'

// Single line
<LineChart
  data={[
    { month: 'Jan', revenue: 4000 },
    { month: 'Feb', revenue: 3000 },
    { month: 'Mar', revenue: 5000 },
  ]}
  xKey="month"
  yKey="revenue"
  title="Revenue Trend"
  height={300}
/>

// Multiple lines
<LineChart
  data={data}
  xKey="date"
  yKey={['active', 'completed', 'pending']}
  title="Delivery Status"
  colors={['#3b82f6', '#10b981', '#f59e0b']}
  height={400}
/>
```

### BarChart
```tsx
import { BarChart } from '@/components/ui'

// Vertical bars
<BarChart
  data={[
    { category: 'Sedans', count: 120 },
    { category: 'SUVs', count: 98 },
    { category: 'Vans', count: 45 },
  ]}
  xKey="category"
  yKey="count"
  title="Fleet by Category"
  height={300}
/>

// Horizontal bars
<BarChart
  data={data}
  xKey="driver"
  yKey="deliveries"
  title="Top Drivers"
  horizontal={true}
  colors={['#10b981']}
/>
```

### PieChart
```tsx
import { PieChart } from '@/components/ui'

// Regular pie chart
<PieChart
  data={[
    { status: 'Active', value: 45 },
    { status: 'Inactive', value: 15 },
    { status: 'Maintenance', value: 5 },
  ]}
  dataKey="value"
  nameKey="status"
  title="Vehicle Status Distribution"
  height={300}
/>

// Donut chart
<PieChart
  data={data}
  dataKey="amount"
  nameKey="category"
  title="Revenue by Category"
  innerRadius={60}
  showLabels={false}
/>
```

### AreaChart
```tsx
import { AreaChart } from '@/components/ui'

// Single area
<AreaChart
  data={[
    { time: '00:00', orders: 0 },
    { time: '06:00', orders: 10 },
    { time: '12:00', orders: 50 },
    { time: '18:00', orders: 30 },
  ]}
  xKey="time"
  yKey="orders"
  title="Orders by Time"
  height={300}
/>

// Stacked areas
<AreaChart
  data={data}
  xKey="week"
  yKey={['online', 'offline', 'phone']}
  title="Orders by Channel"
  stacked={true}
  colors={['#3b82f6', '#10b981', '#f59e0b']}
/>
```

## FileUpload Component

```tsx
import { FileUpload } from '@/components/ui'

// Basic usage
<FileUpload
  onFilesSelected={(files) => {
    console.log('Selected files:', files)
    // Handle file upload
  }}
  maxFiles={5}
  maxSize={5242880} // 5MB
/>

// Images only with preview
<FileUpload
  onFilesSelected={handleUpload}
  accept={{
    'image/*': ['.png', '.jpg', '.jpeg', '.gif']
  }}
  multiple={true}
  showPreview={true}
/>

// Single file, no preview
<FileUpload
  onFilesSelected={handleUpload}
  multiple={false}
  showPreview={false}
  accept={{
    'application/pdf': ['.pdf']
  }}
/>

// Documents only
<FileUpload
  onFilesSelected={handleUpload}
  accept={{
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc', '.docx'],
    'application/vnd.ms-excel': ['.xls', '.xlsx']
  }}
  maxFiles={3}
/>
```

## DateRangePicker Component

```tsx
import { DateRangePicker } from '@/components/ui'
import { DateRange } from 'react-day-picker'
import { useState } from 'react'

// Basic usage
const [dateRange, setDateRange] = useState<DateRange | undefined>()

<DateRangePicker
  value={dateRange}
  onChange={setDateRange}
  placeholder="Select date range"
/>

// In a form
const handleSubmit = () => {
  if (dateRange?.from && dateRange?.to) {
    console.log('Start:', dateRange.from)
    console.log('End:', dateRange.to)
  }
}

<div className="space-y-4">
  <DateRangePicker
    value={dateRange}
    onChange={setDateRange}
  />
  <button onClick={handleSubmit}>
    Apply Filter
  </button>
</div>

// With preset ranges (included by default)
// - Today
// - Last 7 days
// - Last 30 days
// - This Month
```

## Component Features

### Chart Components
- **Responsive**: Automatically adjust to container width
- **Dark Mode**: Support for dark theme
- **Accessible**: ARIA labels and semantic HTML
- **Customizable**: Colors, height, grid, legend options
- **Formatted Axes**: Custom formatters for X and Y axes

### FileUpload
- **Drag & Drop**: Native drag and drop support
- **Multiple Files**: Support for multiple file uploads
- **File Validation**: Type and size validation
- **Preview**: Image thumbnails
- **Progress**: Upload progress indicator
- **Accessible**: Keyboard navigation and ARIA labels

### DateRangePicker
- **Preset Ranges**: Quick selection options
- **Visual Calendar**: Interactive date selection
- **Range Selection**: Start and end dates
- **Accessible**: Keyboard navigation
- **Customizable**: Placeholder and styling options

## TypeScript Types

All components are fully typed with TypeScript:

```tsx
// Chart props are exported
import { LineChartProps, BarChartProps, PieChartProps, AreaChartProps } from '@/components/ui'

// FileUpload props
import { FileUploadProps } from '@/components/ui'

// DateRangePicker props
import { DateRangePickerProps } from '@/components/ui'
import { DateRange } from 'react-day-picker'
```

## Styling

All components use Tailwind CSS and follow the existing design system:

- Primary color: Blue (#3b82f6)
- Success color: Green (#10b981)
- Warning color: Amber (#f59e0b)
- Danger color: Red (#ef4444)
- Dark mode support included
