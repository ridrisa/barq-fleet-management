import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import userEvent from '@testing-library/user-event'
import { Pagination } from '../Pagination'

describe('Pagination', () => {
  it('renders page numbers', () => {
    render(<Pagination currentPage={1} totalPages={5} onPageChange={vi.fn()} />)

    expect(screen.getByRole('button', { name: '1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '2' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '3' })).toBeInTheDocument()
  })

  it('highlights current page', () => {
    render(<Pagination currentPage={2} totalPages={5} onPageChange={vi.fn()} />)

    const currentPageButton = screen.getByRole('button', { name: '2' })
    expect(currentPageButton).toHaveClass('bg-blue-600')
    expect(currentPageButton).toHaveClass('text-white')
  })

  it('calls onPageChange when page number is clicked', async () => {
    const handlePageChange = vi.fn()
    const user = userEvent.setup()

    render(<Pagination currentPage={1} totalPages={5} onPageChange={handlePageChange} />)

    await user.click(screen.getByRole('button', { name: '3' }))
    expect(handlePageChange).toHaveBeenCalledWith(3)
  })

  it('disables previous button on first page', () => {
    const { container } = render(
      <Pagination currentPage={1} totalPages={5} onPageChange={vi.fn()} />
    )

    const prevButton = container.querySelector('button[disabled]')
    expect(prevButton).toBeInTheDocument()
    expect(prevButton).toHaveClass('opacity-50')
  })

  it('enables previous button when not on first page', () => {
    const { container } = render(
      <Pagination currentPage={2} totalPages={5} onPageChange={vi.fn()} />
    )

    const buttons = container.querySelectorAll('button')
    const prevButton = buttons[0]
    expect(prevButton).not.toBeDisabled()
  })

  it('disables next button on last page', () => {
    const { container } = render(
      <Pagination currentPage={5} totalPages={5} onPageChange={vi.fn()} />
    )

    const buttons = container.querySelectorAll('button')
    const nextButton = buttons[buttons.length - 1]
    expect(nextButton).toBeDisabled()
    expect(nextButton).toHaveClass('opacity-50')
  })

  it('enables next button when not on last page', () => {
    const { container } = render(
      <Pagination currentPage={2} totalPages={5} onPageChange={vi.fn()} />
    )

    const buttons = container.querySelectorAll('button')
    const nextButton = buttons[buttons.length - 1]
    expect(nextButton).not.toBeDisabled()
  })

  it('calls onPageChange with previous page when previous button clicked', async () => {
    const handlePageChange = vi.fn()
    const user = userEvent.setup()
    const { container } = render(
      <Pagination currentPage={3} totalPages={5} onPageChange={handlePageChange} />
    )

    const buttons = container.querySelectorAll('button')
    const prevButton = buttons[0]
    await user.click(prevButton)

    expect(handlePageChange).toHaveBeenCalledWith(2)
  })

  it('calls onPageChange with next page when next button clicked', async () => {
    const handlePageChange = vi.fn()
    const user = userEvent.setup()
    const { container } = render(
      <Pagination currentPage={2} totalPages={5} onPageChange={handlePageChange} />
    )

    const buttons = container.querySelectorAll('button')
    const nextButton = buttons[buttons.length - 1]
    await user.click(nextButton)

    expect(handlePageChange).toHaveBeenCalledWith(3)
  })

  it('displays info text when pageSize and totalItems are provided', () => {
    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        pageSize={10}
        totalItems={50}
        onPageChange={vi.fn()}
      />
    )

    expect(screen.getByText(/Showing/)).toBeInTheDocument()
    expect(screen.getByText(/11/)).toBeInTheDocument()
    expect(screen.getByText(/20/)).toBeInTheDocument()
    expect(screen.getByText(/50/)).toBeInTheDocument()
  })

  it('calculates correct item range for first page', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        pageSize={10}
        totalItems={50}
        onPageChange={vi.fn()}
      />
    )

    expect(screen.getByText(/1/)).toBeInTheDocument()
    expect(screen.getByText(/10/)).toBeInTheDocument()
  })

  it('calculates correct item range for last page', () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={5}
        pageSize={10}
        totalItems={45}
        onPageChange={vi.fn()}
      />
    )

    expect(screen.getByText(/41/)).toBeInTheDocument()
    expect(screen.getByText(/45/)).toBeInTheDocument()
  })

  it('shows ellipsis for large page ranges', () => {
    render(<Pagination currentPage={5} totalPages={10} onPageChange={vi.fn()} />)

    const ellipsis = screen.getAllByText('...')
    expect(ellipsis.length).toBeGreaterThan(0)
  })

  it('always shows first and last page numbers', () => {
    render(<Pagination currentPage={5} totalPages={10} onPageChange={vi.fn()} />)

    expect(screen.getByRole('button', { name: '1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '10' })).toBeInTheDocument()
  })

  it('shows pages around current page', () => {
    render(<Pagination currentPage={5} totalPages={10} onPageChange={vi.fn()} />)

    expect(screen.getByRole('button', { name: '4' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '5' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '6' })).toBeInTheDocument()
  })
})
