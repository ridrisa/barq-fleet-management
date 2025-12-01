import { describe, it, expect } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../Card'

describe('Card Components', () => {
  describe('Card', () => {
    it('renders children', () => {
      render(<Card>Card content</Card>)
      expect(screen.getByText('Card content')).toBeInTheDocument()
    })

    it('applies default styles', () => {
      const { container } = render(<Card>Content</Card>)
      const card = container.firstChild as HTMLElement

      expect(card).toHaveClass('bg-white')
      expect(card).toHaveClass('rounded-lg')
      expect(card).toHaveClass('border')
      expect(card).toHaveClass('border-gray-200')
    })

    it('applies custom className', () => {
      const { container } = render(<Card className="custom-class">Content</Card>)
      const card = container.firstChild as HTMLElement

      expect(card).toHaveClass('custom-class')
    })

    it('forwards props to div element', () => {
      const { container } = render(<Card data-testid="card">Content</Card>)
      expect(container.querySelector('[data-testid="card"]')).toBeInTheDocument()
    })
  })

  describe('CardHeader', () => {
    it('renders children', () => {
      render(<CardHeader>Header content</CardHeader>)
      expect(screen.getByText('Header content')).toBeInTheDocument()
    })

    it('applies default styles', () => {
      const { container } = render(<CardHeader>Header</CardHeader>)
      const header = container.firstChild as HTMLElement

      expect(header).toHaveClass('px-6')
      expect(header).toHaveClass('py-4')
      expect(header).toHaveClass('border-b')
    })

    it('applies custom className', () => {
      const { container } = render(
        <CardHeader className="custom-header">Header</CardHeader>
      )
      const header = container.firstChild as HTMLElement

      expect(header).toHaveClass('custom-header')
    })
  })

  describe('CardTitle', () => {
    it('renders children', () => {
      render(<CardTitle>Title text</CardTitle>)
      expect(screen.getByText('Title text')).toBeInTheDocument()
    })

    it('renders as h3 element', () => {
      render(<CardTitle>Title</CardTitle>)
      const title = screen.getByText('Title')

      expect(title.tagName).toBe('H3')
    })

    it('applies default styles', () => {
      render(<CardTitle>Title</CardTitle>)
      const title = screen.getByText('Title')

      expect(title).toHaveClass('text-lg')
      expect(title).toHaveClass('font-semibold')
      expect(title).toHaveClass('text-gray-900')
    })

    it('applies custom className', () => {
      render(<CardTitle className="custom-title">Title</CardTitle>)
      const title = screen.getByText('Title')

      expect(title).toHaveClass('custom-title')
    })
  })

  describe('CardContent', () => {
    it('renders children', () => {
      render(<CardContent>Content text</CardContent>)
      expect(screen.getByText('Content text')).toBeInTheDocument()
    })

    it('applies default styles', () => {
      const { container } = render(<CardContent>Content</CardContent>)
      const content = container.firstChild as HTMLElement

      expect(content).toHaveClass('px-6')
      expect(content).toHaveClass('py-4')
    })

    it('applies custom className', () => {
      const { container } = render(
        <CardContent className="custom-content">Content</CardContent>
      )
      const content = container.firstChild as HTMLElement

      expect(content).toHaveClass('custom-content')
    })
  })

  describe('CardFooter', () => {
    it('renders children', () => {
      render(<CardFooter>Footer content</CardFooter>)
      expect(screen.getByText('Footer content')).toBeInTheDocument()
    })

    it('applies default styles', () => {
      const { container } = render(<CardFooter>Footer</CardFooter>)
      const footer = container.firstChild as HTMLElement

      expect(footer).toHaveClass('px-6')
      expect(footer).toHaveClass('py-4')
      expect(footer).toHaveClass('border-t')
      expect(footer).toHaveClass('bg-gray-50')
    })

    it('applies custom className', () => {
      const { container } = render(
        <CardFooter className="custom-footer">Footer</CardFooter>
      )
      const footer = container.firstChild as HTMLElement

      expect(footer).toHaveClass('custom-footer')
    })
  })

  describe('Composite Card', () => {
    it('renders complete card with all parts', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
          <CardContent>Card content goes here</CardContent>
          <CardFooter>Footer actions</CardFooter>
        </Card>
      )

      expect(screen.getByText('Card Title')).toBeInTheDocument()
      expect(screen.getByText('Card content goes here')).toBeInTheDocument()
      expect(screen.getByText('Footer actions')).toBeInTheDocument()
    })
  })
})
