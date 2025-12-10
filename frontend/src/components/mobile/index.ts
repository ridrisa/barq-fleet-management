// Mobile-specific components and utilities for BARQ Fleet Management
// These components are optimized for touch interactions and mobile viewports

// Hooks
export {
  useMobile,
  useBreakpoint,
  useTouchDevice,
  useSafeAreaInsets,
  useSwipe,
  useLockBodyScroll,
  useKeyboardVisible,
  BREAKPOINTS,
  type Breakpoint,
} from '@/hooks/useMobile'

// Layout Components
export { BottomNav, BottomNavSpacer, type BottomNavItem, type BottomNavProps } from '@/components/layouts/BottomNav'

// UI Components
export { FilterSheet, FilterGroup, FilterChip, FilterTrigger } from '@/components/ui/FilterSheet'
export type { FilterSheetProps, FilterGroupProps, FilterChipProps, FilterTriggerProps } from '@/components/ui/FilterSheet'

export { ActionSheet } from '@/components/ui/Modal'
export type { ActionSheetProps } from '@/components/ui/Modal'

// Form Components
export { MobileDatePicker } from '@/components/forms/MobileDatePicker'
export type { MobileDatePickerProps } from '@/components/forms/MobileDatePicker'

export { FormGrid, FormRow, FormDivider } from '@/components/forms/Form'
export type { FormGridProps, FormRowProps, FormDividerProps } from '@/components/forms/Form'
