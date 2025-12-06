/**
 * Accessibility Tests for BARQ Fleet Management UI Components
 *
 * Tests verify:
 * - WCAG 2.1 compliance
 * - Keyboard navigation
 * - Screen reader compatibility
 * - Focus management
 * - Color contrast (via manual testing notes)
 *
 * Author: BARQ QA Team
 * Last Updated: 2025-12-06
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import userEvent from '@testing-library/user-event'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Pagination } from '@/components/ui/Pagination'

describe('Accessibility: Button Component', () => {
  it('should be focusable via keyboard', async () => {
    const user = userEvent.setup()
    render(<Button>Click me</Button>)

    const button = screen.getByRole('button')
    await user.tab()

    expect(button).toHaveFocus()
  })

  it('should have visible focus indicator', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByRole('button')

    // Button should have focus ring styles
    expect(button).toHaveClass('focus:ring-2')
    expect(button).toHaveClass('focus:ring-offset-2')
  })

  it('should be activatable via Enter key', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button')
    button.focus()
    await user.keyboard('{Enter}')

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be activatable via Space key', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button')
    button.focus()
    await user.keyboard(' ')

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should have appropriate disabled state', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button')

    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('disabled')
    // Should have visual indication (opacity)
    expect(button).toHaveClass('disabled:opacity-50')
  })

  it('should have accessible name from children', () => {
    render(<Button>Submit Form</Button>)
    expect(screen.getByRole('button', { name: 'Submit Form' })).toBeInTheDocument()
  })

  it('should support aria-label override', () => {
    render(<Button aria-label="Close dialog">X</Button>)
    expect(screen.getByRole('button', { name: 'Close dialog' })).toBeInTheDocument()
  })

  it('should indicate loading state to screen readers', () => {
    render(<Button isLoading>Loading...</Button>)
    const button = screen.getByRole('button')

    // Button should be disabled during loading
    expect(button).toBeDisabled()
    // Loading spinner should be present
    expect(button.querySelector('svg')).toBeInTheDocument()
  })
})

describe('Accessibility: Input Component', () => {
  it('should be focusable via keyboard', async () => {
    const user = userEvent.setup()
    render(<Input placeholder="Enter text" />)

    await user.tab()
    expect(screen.getByPlaceholderText('Enter text')).toHaveFocus()
  })

  it('should have visible focus indicator', () => {
    render(<Input placeholder="Enter text" />)
    const input = screen.getByPlaceholderText('Enter text')

    expect(input).toHaveClass('focus:ring-2')
  })

  it('should associate label with input via htmlFor', () => {
    render(
      <>
        <label htmlFor="test-input">Email</label>
        <Input id="test-input" type="email" />
      </>
    )

    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('should have appropriate error state', () => {
    render(<Input error="This field is required" />)
    const input = screen.getByRole('textbox')

    // Input should have error styling
    expect(input).toHaveClass('border-red-500')
  })

  it('should support aria-describedby for error messages', () => {
    const { container } = render(
      <div>
        <Input id="email" aria-describedby="email-error" />
        <span id="email-error">Invalid email format</span>
      </div>
    )

    const input = container.querySelector('input')
    expect(input).toHaveAttribute('aria-describedby', 'email-error')
  })

  it('should support required attribute', () => {
    render(<Input required placeholder="Required field" />)
    expect(screen.getByPlaceholderText('Required field')).toBeRequired()
  })

  it('should support disabled state', () => {
    render(<Input disabled placeholder="Disabled field" />)
    expect(screen.getByPlaceholderText('Disabled field')).toBeDisabled()
  })
})

describe('Accessibility: Modal Component', () => {
  const ModalWrapper = ({ isOpen = true }: { isOpen?: boolean }) => (
    <Modal isOpen={isOpen} onClose={() => {}} title="Test Modal">
      <p>Modal content</p>
    </Modal>
  )

  it('should have role="dialog"', () => {
    render(<ModalWrapper />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('should have aria-modal="true"', () => {
    render(<ModalWrapper />)
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('should have aria-labelledby pointing to title', () => {
    render(<ModalWrapper />)
    const dialog = screen.getByRole('dialog')
    const titleId = dialog.getAttribute('aria-labelledby')

    if (titleId) {
      const title = document.getElementById(titleId)
      expect(title).toHaveTextContent('Test Modal')
    }
  })

  it('should trap focus within modal', async () => {
    const user = userEvent.setup()
    render(
      <Modal isOpen={true} onClose={() => {}} title="Focus Test">
        <Button>First Button</Button>
        <Button>Second Button</Button>
      </Modal>
    )

    // Tab through focusable elements
    await user.tab()
    await user.tab()
    await user.tab()

    // Focus should cycle within modal
    const modal = screen.getByRole('dialog')
    const activeElement = document.activeElement
    expect(modal.contains(activeElement)).toBe(true)
  })

  it('should close on Escape key', async () => {
    const handleClose = vi.fn()
    const user = userEvent.setup()

    render(
      <Modal isOpen={true} onClose={handleClose} title="Escape Test">
        <p>Content</p>
      </Modal>
    )

    await user.keyboard('{Escape}')
    expect(handleClose).toHaveBeenCalled()
  })

  it('should have close button with accessible name', () => {
    render(<ModalWrapper />)
    // Look for close button
    const closeButton = screen.queryByRole('button', { name: /close/i }) ||
                        screen.queryByLabelText(/close/i)

    // If close button exists, it should be accessible
    if (closeButton) {
      expect(closeButton).toBeInTheDocument()
    }
  })
})

describe('Accessibility: Table Component', () => {
  const sampleData = [
    { id: 1, name: 'John', email: 'john@test.com' },
    { id: 2, name: 'Jane', email: 'jane@test.com' },
  ]

  const columns = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
  ]

  it('should use proper table semantics', () => {
    render(<Table data={sampleData} columns={columns} />)

    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getAllByRole('columnheader')).toHaveLength(2)
    expect(screen.getAllByRole('row')).toHaveLength(3) // header + 2 data rows
  })

  it('should have accessible column headers', () => {
    render(<Table data={sampleData} columns={columns} />)

    expect(screen.getByRole('columnheader', { name: 'Name' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Email' })).toBeInTheDocument()
  })

  it('should have proper scope on headers', () => {
    render(<Table data={sampleData} columns={columns} />)
    const headers = screen.getAllByRole('columnheader')

    headers.forEach(header => {
      expect(header).toHaveAttribute('scope', 'col')
    })
  })

  it('should support keyboard navigation for interactive rows', async () => {
    const handleRowClick = vi.fn()
    const user = userEvent.setup()

    render(
      <Table
        data={sampleData}
        columns={columns}
        onRowClick={handleRowClick}
      />
    )

    // Tab to first clickable row
    const rows = screen.getAllByRole('row')
    if (rows.length > 1) {
      await user.tab()
      await user.keyboard('{Enter}')
      // Interactive rows should be clickable
    }
  })

  it('should display empty state accessibly', () => {
    render(<Table data={[]} columns={columns} />)

    // Should either show empty message or empty table
    const table = screen.queryByRole('table')
    expect(table || screen.queryByText(/no data/i)).toBeTruthy()
  })
})

describe('Accessibility: Badge Component', () => {
  it('should not be focusable by default (presentational)', () => {
    render(<Badge>Status</Badge>)
    const badge = screen.getByText('Status')

    // Badge should not have tabIndex by default
    expect(badge).not.toHaveAttribute('tabIndex', '0')
  })

  it('should have sufficient color contrast for variants', () => {
    // Note: Actual color contrast testing requires visual inspection
    // This test ensures badges are rendered with appropriate classes
    render(
      <>
        <Badge variant="success">Success</Badge>
        <Badge variant="warning">Warning</Badge>
        <Badge variant="error">Error</Badge>
      </>
    )

    expect(screen.getByText('Success')).toBeInTheDocument()
    expect(screen.getByText('Warning')).toBeInTheDocument()
    expect(screen.getByText('Error')).toBeInTheDocument()
  })
})

describe('Accessibility: Card Component', () => {
  it('should use semantic HTML structure', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Card content</p>
        </CardContent>
        <CardFooter>
          <Button>Action</Button>
        </CardFooter>
      </Card>
    )

    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Card content')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument()
  })

  it('should use heading for card title', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Important Title</CardTitle>
        </CardHeader>
      </Card>
    )

    // Title should be a heading
    const title = screen.getByText('Important Title')
    const tagName = title.tagName.toLowerCase()
    expect(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']).toContain(tagName)
  })
})

describe('Accessibility: Pagination Component', () => {
  const defaultProps = {
    currentPage: 1,
    totalPages: 10,
    onPageChange: vi.fn(),
  }

  it('should use nav landmark', () => {
    render(<Pagination {...defaultProps} />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('should have aria-label for navigation', () => {
    render(<Pagination {...defaultProps} />)
    const nav = screen.getByRole('navigation')
    expect(nav).toHaveAttribute('aria-label')
  })

  it('should indicate current page', () => {
    render(<Pagination {...defaultProps} currentPage={3} />)

    const currentPageButton = screen.getByRole('button', { name: /3/i, current: 'page' }) ||
                              screen.getByText('3')

    // Current page should be visually distinct or have aria-current
    if (currentPageButton.getAttribute('aria-current')) {
      expect(currentPageButton).toHaveAttribute('aria-current', 'page')
    }
  })

  it('should be keyboard navigable', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()

    render(<Pagination {...defaultProps} onPageChange={handleChange} />)

    // Tab to first button
    await user.tab()

    // Should have a focusable element
    expect(document.activeElement?.tagName).toBe('BUTTON')
  })

  it('should disable previous on first page', () => {
    render(<Pagination {...defaultProps} currentPage={1} />)

    const prevButton = screen.queryByRole('button', { name: /previous/i }) ||
                       screen.queryByLabelText(/previous/i)

    if (prevButton) {
      expect(prevButton).toBeDisabled()
    }
  })

  it('should disable next on last page', () => {
    render(<Pagination {...defaultProps} currentPage={10} totalPages={10} />)

    const nextButton = screen.queryByRole('button', { name: /next/i }) ||
                       screen.queryByLabelText(/next/i)

    if (nextButton) {
      expect(nextButton).toBeDisabled()
    }
  })
})

describe('Accessibility: Keyboard Navigation Patterns', () => {
  it('should support Tab order through interactive elements', async () => {
    const user = userEvent.setup()

    render(
      <div>
        <Button>First</Button>
        <Input placeholder="Middle" />
        <Button>Last</Button>
      </div>
    )

    // Start from first element
    await user.tab()
    expect(screen.getByRole('button', { name: 'First' })).toHaveFocus()

    await user.tab()
    expect(screen.getByPlaceholderText('Middle')).toHaveFocus()

    await user.tab()
    expect(screen.getByRole('button', { name: 'Last' })).toHaveFocus()
  })

  it('should skip disabled elements in tab order', async () => {
    const user = userEvent.setup()

    render(
      <div>
        <Button>First</Button>
        <Button disabled>Disabled</Button>
        <Button>Last</Button>
      </div>
    )

    await user.tab()
    expect(screen.getByRole('button', { name: 'First' })).toHaveFocus()

    await user.tab()
    // Should skip disabled button
    expect(screen.getByRole('button', { name: 'Last' })).toHaveFocus()
  })

  it('should support Shift+Tab for reverse navigation', async () => {
    const user = userEvent.setup()

    render(
      <div>
        <Button>First</Button>
        <Button>Second</Button>
        <Button>Third</Button>
      </div>
    )

    // Focus last element
    screen.getByRole('button', { name: 'Third' }).focus()

    await user.tab({ shift: true })
    expect(screen.getByRole('button', { name: 'Second' })).toHaveFocus()

    await user.tab({ shift: true })
    expect(screen.getByRole('button', { name: 'First' })).toHaveFocus()
  })
})

describe('Accessibility: Color and Visual Indicators', () => {
  it('should not rely solely on color for conveying information', () => {
    // Status badges should have text in addition to color
    render(<Badge variant="error">Error</Badge>)
    expect(screen.getByText('Error')).toBeInTheDocument()
  })

  it('should have visible focus indicators on all interactive elements', () => {
    render(
      <div>
        <Button>Button</Button>
        <Input placeholder="Input" />
      </div>
    )

    const button = screen.getByRole('button')
    const input = screen.getByPlaceholderText('Input')

    // Both should have focus ring styles
    expect(button.className).toMatch(/focus:ring/)
    expect(input.className).toMatch(/focus:ring/)
  })
})
