import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import userEvent from '@testing-library/user-event'
import { Modal, ConfirmModal } from '../Modal'

describe('Modal', () => {
  it('does not render when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    )

    expect(screen.queryByText('Modal content')).not.toBeInTheDocument()
  })

  it('renders when isOpen is true', () => {
    render(
      <Modal isOpen onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    )

    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(
      <Modal isOpen onClose={vi.fn()} title="Test Modal">
        <div>Modal content</div>
      </Modal>
    )

    expect(screen.getByText('Test Modal')).toBeInTheDocument()
  })

  it('renders footer when provided', () => {
    render(
      <Modal isOpen onClose={vi.fn()} footer={<div>Footer content</div>}>
        <div>Modal content</div>
      </Modal>
    )

    expect(screen.getByText('Footer content')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const handleClose = vi.fn()
    const user = userEvent.setup()

    render(
      <Modal isOpen onClose={handleClose} title="Test Modal">
        <div>Modal content</div>
      </Modal>
    )

    const closeButton = screen.getByRole('button')
    await user.click(closeButton)

    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when overlay is clicked and closeOnOverlayClick is true', async () => {
    const handleClose = vi.fn()
    const user = userEvent.setup()

    render(
      <Modal isOpen onClose={handleClose} closeOnOverlayClick>
        <div>Modal content</div>
      </Modal>
    )

    const overlay = document.querySelector('.bg-black.bg-opacity-50')
    if (overlay) {
      await user.click(overlay)
      expect(handleClose).toHaveBeenCalledTimes(1)
    }
  })

  it('does not call onClose when overlay is clicked and closeOnOverlayClick is false', async () => {
    const handleClose = vi.fn()
    const user = userEvent.setup()

    render(
      <Modal isOpen onClose={handleClose} closeOnOverlayClick={false}>
        <div>Modal content</div>
      </Modal>
    )

    const overlay = document.querySelector('.bg-black.bg-opacity-50')
    if (overlay) {
      await user.click(overlay)
      expect(handleClose).not.toHaveBeenCalled()
    }
  })

  it('applies small size class', () => {
    render(
      <Modal isOpen onClose={vi.fn()} size="sm">
        <div>Modal content</div>
      </Modal>
    )

    const modal = document.querySelector('.max-w-md')
    expect(modal).toBeInTheDocument()
  })

  it('applies medium size class by default', () => {
    render(
      <Modal isOpen onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    )

    const modal = document.querySelector('.max-w-lg')
    expect(modal).toBeInTheDocument()
  })

  it('applies large size class', () => {
    render(
      <Modal isOpen onClose={vi.fn()} size="lg">
        <div>Modal content</div>
      </Modal>
    )

    const modal = document.querySelector('.max-w-2xl')
    expect(modal).toBeInTheDocument()
  })

  it('applies extra large size class', () => {
    render(
      <Modal isOpen onClose={vi.fn()} size="xl">
        <div>Modal content</div>
      </Modal>
    )

    const modal = document.querySelector('.max-w-4xl')
    expect(modal).toBeInTheDocument()
  })
})

describe('ConfirmModal', () => {
  it('renders with title and message', () => {
    render(
      <ConfirmModal
        isOpen
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Confirm Action"
        message="Are you sure you want to proceed?"
      />
    )

    expect(screen.getByText('Confirm Action')).toBeInTheDocument()
    expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument()
  })

  it('renders default button text', () => {
    render(
      <ConfirmModal
        isOpen
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Confirm"
        message="Confirm?"
      />
    )

    expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
  })

  it('renders custom button text', () => {
    render(
      <ConfirmModal
        isOpen
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Delete item?"
        confirmText="Delete"
        cancelText="Keep"
      />
    )

    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /keep/i })).toBeInTheDocument()
  })

  it('calls onConfirm when confirm button is clicked', async () => {
    const handleConfirm = vi.fn()
    const user = userEvent.setup()

    render(
      <ConfirmModal
        isOpen
        onClose={vi.fn()}
        onConfirm={handleConfirm}
        title="Confirm"
        message="Confirm?"
      />
    )

    await user.click(screen.getByRole('button', { name: /confirm/i }))
    expect(handleConfirm).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when cancel button is clicked', async () => {
    const handleClose = vi.fn()
    const user = userEvent.setup()

    render(
      <ConfirmModal
        isOpen
        onClose={handleClose}
        onConfirm={vi.fn()}
        title="Confirm"
        message="Confirm?"
      />
    )

    await user.click(screen.getByRole('button', { name: /cancel/i }))
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  it('disables buttons when isLoading is true', () => {
    render(
      <ConfirmModal
        isOpen
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Confirm"
        message="Confirm?"
        isLoading
      />
    )

    const confirmButton = screen.getByRole('button', { name: /confirm/i })
    const cancelButton = screen.getByRole('button', { name: /cancel/i })

    expect(confirmButton).toBeDisabled()
    expect(cancelButton).toBeDisabled()
  })
})
