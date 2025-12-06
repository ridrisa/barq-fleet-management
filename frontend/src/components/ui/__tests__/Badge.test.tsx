import { describe, it, expect } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import { Badge } from '../Badge'

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Badge text</Badge>)
    expect(screen.getByText('Badge text')).toBeInTheDocument()
  })

  it('applies default variant styles', () => {
    render(<Badge>Default</Badge>)
    const badge = screen.getByText('Default')

    expect(badge).toHaveClass('bg-gray-100')
    expect(badge).toHaveClass('text-gray-800')
  })

  it('applies success variant styles', () => {
    render(<Badge variant="success">Success</Badge>)
    const badge = screen.getByText('Success')

    expect(badge).toHaveClass('bg-green-100')
    expect(badge).toHaveClass('text-green-800')
  })

  it('applies warning variant styles', () => {
    render(<Badge variant="warning">Warning</Badge>)
    const badge = screen.getByText('Warning')

    expect(badge).toHaveClass('bg-yellow-100')
    expect(badge).toHaveClass('text-yellow-800')
  })

  it('applies danger variant styles', () => {
    render(<Badge variant="danger">Danger</Badge>)
    const badge = screen.getByText('Danger')

    expect(badge).toHaveClass('bg-red-100')
    expect(badge).toHaveClass('text-red-800')
  })

  it('applies info variant styles', () => {
    render(<Badge variant="info">Info</Badge>)
    const badge = screen.getByText('Info')

    expect(badge).toHaveClass('bg-blue-100')
    expect(badge).toHaveClass('text-blue-800')
  })

  it('applies small size styles', () => {
    render(<Badge size="sm">Small</Badge>)
    const badge = screen.getByText('Small')

    expect(badge).toHaveClass('px-2')
    expect(badge).toHaveClass('py-0.5')
    expect(badge).toHaveClass('text-xs')
  })

  it('applies medium size styles by default', () => {
    render(<Badge>Medium</Badge>)
    const badge = screen.getByText('Medium')

    expect(badge).toHaveClass('px-2.5')
    expect(badge).toHaveClass('py-1')
    expect(badge).toHaveClass('text-sm')
  })

  it('applies small size styles', () => {
    render(<Badge size="sm">Small</Badge>)
    const badge = screen.getByText('Small')

    expect(badge).toHaveClass('h-5')
    expect(badge).toHaveClass('px-2')
  })

  it('applies base styles', () => {
    render(<Badge>Badge</Badge>)
    const badge = screen.getByText('Badge')

    expect(badge).toHaveClass('inline-flex')
    expect(badge).toHaveClass('items-center')
    expect(badge).toHaveClass('font-medium')
    expect(badge).toHaveClass('rounded-full')
  })

  it('applies custom className', () => {
    render(<Badge className="custom-badge">Custom</Badge>)
    const badge = screen.getByText('Custom')

    expect(badge).toHaveClass('custom-badge')
  })

  it('renders as span element', () => {
    render(<Badge>Badge</Badge>)
    const badge = screen.getByText('Badge')

    expect(badge.tagName).toBe('SPAN')
  })

  it('forwards props to span element', () => {
    render(<Badge data-testid="test-badge">Badge</Badge>)
    expect(screen.getByTestId('test-badge')).toBeInTheDocument()
  })

  it('combines variant and size correctly', () => {
    render(<Badge variant="success" size="sm">Small Success</Badge>)
    const badge = screen.getByText('Small Success')

    // Check that small size classes are applied
    expect(badge).toHaveClass('h-5')
    expect(badge).toHaveClass('px-2')
  })
})
