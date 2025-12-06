import { ReactNode, useEffect, useRef } from 'react'
import { cn } from '@/lib/cn'
import { X } from 'lucide-react'
import { Button } from './Button'
import { useMobile, useLockBodyScroll, useSwipe } from '@/hooks/useMobile'

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeOnOverlayClick?: boolean
  // Mobile-specific props
  mobileFullScreen?: boolean
  showMobileHandle?: boolean
  swipeToClose?: boolean
}

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnOverlayClick = true,
  mobileFullScreen = true,
  showMobileHandle = true,
  swipeToClose = true,
}: ModalProps) => {
  const isMobile = useMobile('sm') // < 640px
  const modalRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)

  // Lock body scroll when modal is open
  useLockBodyScroll(isOpen)

  // Swipe to close on mobile
  const { onTouchStart, onTouchEnd } = useSwipe(
    undefined,
    undefined,
    undefined,
    swipeToClose && isMobile ? onClose : undefined,
    100
  )

  // Handle focus trap and escape key
  useEffect(() => {
    if (!isOpen) return

    // Store the element that opened the modal
    previousActiveElement.current = document.activeElement as HTMLElement

    // Handle escape key
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    // Handle focus trap
    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab' || !modalRef.current) return

      const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault()
        lastElement?.focus()
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault()
        firstElement?.focus()
      }
    }

    document.addEventListener('keydown', handleEscape)
    document.addEventListener('keydown', handleTabKey)

    // Focus the first focusable element
    setTimeout(() => {
      const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      firstFocusable?.focus()
    }, 0)

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('keydown', handleTabKey)

      // Return focus to the element that opened the modal
      previousActiveElement.current?.focus()
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  }

  // Mobile full-screen variant
  const isMobileFullScreen = isMobile && mobileFullScreen

  return (
    <div
      ref={modalRef}
      className={cn(
        'fixed inset-0 z-50',
        isMobileFullScreen
          ? 'flex flex-col justify-end'
          : 'flex items-center justify-center'
      )}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {/* Overlay */}
      <div
        className={cn(
          'fixed inset-0 bg-black transition-opacity duration-300',
          isOpen ? 'bg-opacity-50' : 'bg-opacity-0'
        )}
        onClick={closeOnOverlayClick ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className={cn(
          'relative bg-white shadow-xl w-full',
          // Desktop styles
          !isMobileFullScreen && [
            'rounded-lg mx-4',
            sizes[size],
            'animate-in fade-in zoom-in-95 duration-200',
          ],
          // Mobile full-screen styles
          isMobileFullScreen && [
            'rounded-t-2xl',
            'max-h-[95vh]',
            'animate-in slide-in-from-bottom duration-300',
            // Safe area padding for notched devices
            'pb-[env(safe-area-inset-bottom)]',
          ]
        )}
        role="document"
        onTouchStart={(e) => onTouchStart(e.nativeEvent)}
        onTouchEnd={(e) => onTouchEnd(e.nativeEvent)}
      >
        {/* Mobile swipe handle */}
        {isMobileFullScreen && showMobileHandle && (
          <div className="flex justify-center pt-3 pb-2">
            <div className="w-10 h-1 bg-gray-300 rounded-full" />
          </div>
        )}

        {/* Header */}
        {title && (
          <div
            className={cn(
              'flex items-center justify-between border-b border-gray-200',
              isMobileFullScreen ? 'px-4 py-3' : 'px-6 py-4'
            )}
          >
            <h2
              id="modal-title"
              className={cn(
                'font-semibold text-gray-900',
                isMobileFullScreen ? 'text-lg' : 'text-xl'
              )}
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              className={cn(
                'text-gray-400 hover:text-gray-600 transition-colors',
                // Touch-friendly size on mobile
                'min-w-[44px] min-h-[44px] flex items-center justify-center -mr-2'
              )}
              aria-label="Close modal"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        )}

        {/* Close button when no title */}
        {!title && (
          <button
            onClick={onClose}
            className={cn(
              'absolute top-3 right-3 z-10',
              'text-gray-400 hover:text-gray-600 transition-colors',
              'min-w-[44px] min-h-[44px] flex items-center justify-center',
              'bg-white/80 backdrop-blur-sm rounded-full shadow-sm'
            )}
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        {/* Content */}
        <div
          className={cn(
            'overflow-y-auto',
            isMobileFullScreen
              ? 'px-4 py-4 max-h-[calc(95vh-120px)]'
              : 'px-6 py-4 max-h-[70vh]'
          )}
        >
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div
            className={cn(
              'border-t border-gray-200 bg-gray-50',
              isMobileFullScreen
                ? 'px-4 py-4 rounded-b-none'
                : 'px-6 py-4 rounded-b-lg'
            )}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}

export interface ConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'primary'
  isLoading?: boolean
}

export const ConfirmModal = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'primary',
  isLoading = false,
}: ConfirmModalProps) => {
  const isMobile = useMobile('sm')

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      mobileFullScreen={false}
      footer={
        <div
          className={cn(
            'flex gap-3',
            isMobile ? 'flex-col-reverse' : 'justify-end'
          )}
        >
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={isLoading}
            fullWidth={isMobile}
            className={cn(isMobile && 'min-h-[48px]')}
          >
            {cancelText}
          </Button>
          <Button
            variant={variant}
            onClick={onConfirm}
            isLoading={isLoading}
            disabled={isLoading}
            fullWidth={isMobile}
            className={cn(isMobile && 'min-h-[48px]')}
          >
            {confirmText}
          </Button>
        </div>
      }
    >
      <p className="text-gray-700">{message}</p>
    </Modal>
  )
}

// Action Sheet variant for mobile (iOS-style action menu)
export interface ActionSheetProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  actions: {
    label: string
    onClick: () => void
    variant?: 'default' | 'danger'
    icon?: ReactNode
  }[]
  cancelLabel?: string
}

export const ActionSheet = ({
  isOpen,
  onClose,
  title,
  actions,
  cancelLabel = 'Cancel',
}: ActionSheetProps) => {
  useLockBodyScroll(isOpen)

  const { onTouchStart, onTouchEnd } = useSwipe(
    undefined,
    undefined,
    undefined,
    onClose,
    100
  )

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 animate-in fade-in duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Action Sheet */}
      <div
        className="relative animate-in slide-in-from-bottom duration-300"
        onTouchStart={(e) => onTouchStart(e.nativeEvent)}
        onTouchEnd={(e) => onTouchEnd(e.nativeEvent)}
      >
        {/* Swipe handle */}
        <div className="flex justify-center pb-2">
          <div className="w-10 h-1 bg-gray-400 rounded-full" />
        </div>

        <div className="bg-white rounded-t-2xl overflow-hidden pb-[env(safe-area-inset-bottom)]">
          {title && (
            <div className="px-4 py-3 text-center border-b border-gray-100">
              <p className="text-sm text-gray-500">{title}</p>
            </div>
          )}

          <div className="divide-y divide-gray-100">
            {actions.map((action, index) => (
              <button
                key={index}
                onClick={() => {
                  action.onClick()
                  onClose()
                }}
                className={cn(
                  'w-full px-4 py-4 flex items-center justify-center gap-3',
                  'min-h-[56px] text-base font-medium',
                  'active:bg-gray-100 transition-colors',
                  action.variant === 'danger' ? 'text-red-600' : 'text-gray-900'
                )}
              >
                {action.icon}
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* Cancel button - separate section */}
        <div className="mt-2 mx-4 mb-4">
          <button
            onClick={onClose}
            className={cn(
              'w-full bg-white rounded-xl px-4 py-4',
              'min-h-[56px] text-base font-semibold text-blue-600',
              'active:bg-gray-100 transition-colors'
            )}
          >
            {cancelLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
