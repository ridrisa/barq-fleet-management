# BARQ Fleet Management - Design System Quick Reference

Quick reference guide for common design system patterns and components.

---

## Import Pattern

```tsx
import { Button, Input, Card, Badge } from '@/components/ui'
```

---

## Buttons

```tsx
// Primary action
<Button variant="primary">Save</Button>

// Secondary action
<Button variant="secondary">Cancel</Button>

// Destructive action
<Button variant="destructive">Delete</Button>

// Success action
<Button variant="success">Approve</Button>

// Subtle action
<Button variant="ghost">Learn More</Button>

// Outlined
<Button variant="outline">Add New</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// Loading state
<Button isLoading>Saving...</Button>

// Full width
<Button fullWidth>Submit</Button>
```

---

## Form Inputs

### Input

```tsx
// Basic
<Input label="Email" type="email" placeholder="Enter email" />

// Required
<Input label="Name" required />

// With error
<Input label="Email" error="Invalid email address" />

// With helper text
<Input label="Password" helperText="At least 8 characters" />

// With icon
<Input
  label="Search"
  leftIcon={<Search className="w-4 h-4" />}
  placeholder="Search..."
/>

// Sizes
<Input size="sm" label="Small" />
<Input size="md" label="Medium" />
<Input size="lg" label="Large" />
```

### Select

```tsx
// Basic
<Select
  label="Status"
  options={[
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' }
  ]}
/>

// With placeholder
<Select
  label="Choose..."
  placeholder="Select an option"
  options={options}
/>

// Required with error
<Select
  label="Role"
  required
  error="Role is required"
  options={roles}
/>
```

### Textarea

```tsx
// Basic
<Textarea label="Description" placeholder="Enter description" />

// With resize control
<Textarea resize="vertical" />
<Textarea resize="none" />

// Required
<Textarea label="Notes" required />

// With error
<Textarea label="Comments" error="Too short" />
```

---

## Cards

```tsx
// Basic card
<Card>
  <CardContent>
    Content here
  </CardContent>
</Card>

// Full structure
<Card variant="elevated">
  <CardHeader>
    <CardTitle subtitle="Optional subtitle">
      Card Title
    </CardTitle>
  </CardHeader>
  <CardContent>
    Main content
  </CardContent>
  <CardFooter>
    <Button variant="secondary">Cancel</Button>
    <Button variant="primary">Save</Button>
  </CardFooter>
</Card>

// With actions in header
<Card>
  <CardHeader actions={<Button size="sm">Edit</Button>}>
    <CardTitle>Settings</CardTitle>
  </CardHeader>
  <CardContent>...</CardContent>
</Card>

// Hoverable card
<Card hoverable onClick={handleClick}>
  <CardContent>Clickable card</CardContent>
</Card>

// Variants
<Card variant="default">Default</Card>
<Card variant="elevated">Elevated</Card>
<Card variant="outlined">Outlined</Card>
<Card variant="glass">Glass effect</Card>
```

---

## Badges

```tsx
// Status badges
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
<Badge variant="info">New</Badge>

// Brand badge
<Badge variant="brand">Premium</Badge>

// With dot indicator
<Badge variant="success" dot>Online</Badge>

// Sizes
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>
```

---

## Common Patterns

### Form with Validation

```tsx
function UserForm() {
  const [errors, setErrors] = useState({})

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          label="Email"
          type="email"
          required
          error={errors.email}
        />
        <Select
          label="Role"
          options={roles}
          required
          error={errors.role}
        />
        <Textarea
          label="Bio"
          resize="vertical"
          helperText="Tell us about yourself"
        />
      </CardContent>
      <CardFooter className="flex justify-end gap-3">
        <Button variant="secondary">Cancel</Button>
        <Button variant="primary">Save</Button>
      </CardFooter>
    </Card>
  )
}
```

### Status Display

```tsx
function StatusIndicator({ status }) {
  const variants = {
    active: 'success',
    pending: 'warning',
    failed: 'error',
    completed: 'info'
  }

  return (
    <Badge variant={variants[status]} dot>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  )
}
```

### Action Buttons Row

```tsx
<div className="flex items-center gap-2">
  <Button variant="ghost" size="sm">
    <Edit className="w-4 h-4" />
  </Button>
  <Button variant="ghost" size="sm">
    <Trash2 className="w-4 h-4 text-red-600" />
  </Button>
</div>
```

### Responsive Form Layout

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <Input label="First Name" required />
  <Input label="Last Name" required />
  <Input label="Email" type="email" required className="md:col-span-2" />
  <Select label="Country" options={countries} className="md:col-span-2" />
</div>
```

---

## Design Tokens Usage

### Colors

```tsx
// Use in className
className="bg-[var(--barq-amber)] text-[var(--text-on-brand)]"

// Border
className="border border-[var(--border-default)]"

// Shadows
className="shadow-[var(--shadow-md)]"
```

### Spacing

```tsx
// Padding
className="p-[var(--space-4)]"

// Margin
className="mt-[var(--space-6)]"

// Gap
className="gap-[var(--space-3)]"
```

### Typography

```tsx
// Font size
className="text-[var(--font-size-lg)]"

// Font weight
className="font-[var(--font-weight-semibold)]"
```

### Border Radius

```tsx
className="rounded-[var(--radius-lg)]"
```

---

## Accessibility Checklist

### Forms
- ✅ All inputs have labels
- ✅ Required fields marked with asterisk
- ✅ Error messages visible and announced
- ✅ Helper text associated with inputs

### Buttons
- ✅ Clear, descriptive text
- ✅ Icon-only buttons have aria-label
- ✅ Disabled state clear
- ✅ Focus visible

### Colors
- ✅ Sufficient contrast (4.5:1 for text)
- ✅ Don't rely on color alone
- ✅ Focus indicators visible

### Keyboard
- ✅ All interactive elements tabbable
- ✅ Focus order logical
- ✅ Enter/Space activates buttons
- ✅ Escape closes modals

---

## Component Sizes

| Component | Small | Medium | Large |
|-----------|-------|--------|-------|
| Button | 32px | 40px | 48px |
| Input | 32px | 40px | 48px |
| Select | 32px | 40px | 48px |
| Badge | 20px | 24px | - |

---

## Color Reference

| Color | Value | Usage |
|-------|-------|-------|
| BARQ Amber | #FFB81C | Primary actions, brand |
| Success | #10B981 | Positive states |
| Warning | #F59E0B | Warning states |
| Error | #EF4444 | Error states |
| Info | #3B82F6 | Information |

---

## Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight spacing |
| space-2 | 8px | Icon gaps |
| space-3 | 12px | Small gaps |
| space-4 | 16px | Standard gaps |
| space-6 | 24px | Section gaps |
| space-8 | 32px | Large gaps |

---

## Common Classnames

```tsx
// Flex layouts
"flex items-center gap-2"
"flex justify-between items-center"
"flex flex-col md:flex-row gap-4"

// Grid layouts
"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

// Spacing
"space-y-4"  // Vertical spacing between children
"space-x-2"  // Horizontal spacing between children

// Responsive
"hidden md:block"  // Hide on mobile, show on desktop
"block md:hidden"  // Show on mobile, hide on desktop

// Text
"text-[var(--font-size-lg)] font-semibold text-[var(--text-primary)]"
```

---

## Pro Tips

1. **Use semantic variants**: Choose `success`, `warning`, `error` based on meaning, not color preference
2. **Required fields**: Always use `required` prop, shows asterisk automatically
3. **Error messages**: Be specific, e.g., "Email is required" not "Invalid"
4. **Helper text**: Provide context before errors occur
5. **Button text**: Use action verbs, e.g., "Save Changes" not "Submit"
6. **Loading states**: Show feedback during async operations
7. **Responsive**: Test on mobile, use `fullWidth` or responsive classes
8. **Accessibility**: Test with keyboard, verify focus order

---

## Need More Help?

- Full documentation: [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)
- Implementation guide: [DESIGN_SYSTEM_SUMMARY.md](./DESIGN_SYSTEM_SUMMARY.md)
- Component source: `/src/components/ui/`
- Design tokens: `/src/styles/variables.css`
