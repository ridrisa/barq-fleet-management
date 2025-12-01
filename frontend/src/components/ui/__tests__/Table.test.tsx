import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@/tests/test-utils'
import userEvent from '@testing-library/user-event'
import { Table, Column } from '../Table'

interface TestData {
  id: number
  name: string
  email: string
  status: string
}

const mockData: TestData[] = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'active' },
]

const columns: Column<TestData>[] = [
  { key: 'id', header: 'ID', sortable: true },
  { key: 'name', header: 'Name', sortable: true },
  { key: 'email', header: 'Email' },
  { key: 'status', header: 'Status' },
]

describe('Table', () => {
  it('renders table with data', () => {
    render(<Table data={mockData} columns={columns} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument()
  })

  it('renders column headers', () => {
    render(<Table data={mockData} columns={columns} />)

    expect(screen.getByText('ID')).toBeInTheDocument()
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
  })

  it('displays empty message when no data', () => {
    render(<Table data={[]} columns={columns} />)

    expect(screen.getByText('No data available')).toBeInTheDocument()
  })

  it('displays custom empty message', () => {
    render(<Table data={[]} columns={columns} emptyMessage="No results found" />)

    expect(screen.getByText('No results found')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<Table data={mockData} columns={columns} isLoading />)

    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('calls onRowClick when row is clicked', async () => {
    const handleRowClick = vi.fn()
    const user = userEvent.setup()

    render(<Table data={mockData} columns={columns} onRowClick={handleRowClick} />)

    const firstRow = screen.getByText('John Doe').closest('tr')
    if (firstRow) {
      await user.click(firstRow)
      expect(handleRowClick).toHaveBeenCalledWith(mockData[0])
    }
  })

  it('calls onSort when sortable column is clicked', async () => {
    const handleSort = vi.fn()
    const user = userEvent.setup()

    render(<Table data={mockData} columns={columns} onSort={handleSort} />)

    const idHeader = screen.getByText('ID').closest('th')
    if (idHeader) {
      await user.click(idHeader)
      expect(handleSort).toHaveBeenCalledWith('id')
    }
  })

  it('displays sort indicators', () => {
    render(
      <Table
        data={mockData}
        columns={columns}
        sortColumn="name"
        sortDirection="asc"
        onSort={vi.fn()}
      />
    )

    const nameHeader = screen.getByText('Name')
    const headerCell = nameHeader.parentElement
    expect(headerCell?.querySelector('svg')).toBeInTheDocument()
  })

  it('renders custom cell content with render function', () => {
    const customColumns: Column<TestData>[] = [
      {
        key: 'status',
        header: 'Status',
        render: (row) => (
          <span className={row.status === 'active' ? 'text-green-600' : 'text-red-600'}>
            {row.status.toUpperCase()}
          </span>
        ),
      },
    ]

    render(<Table data={mockData} columns={customColumns} />)

    expect(screen.getByText('ACTIVE')).toBeInTheDocument()
    expect(screen.getByText('INACTIVE')).toBeInTheDocument()
  })

  it('applies hover styles to rows when onRowClick is provided', () => {
    render(<Table data={mockData} columns={columns} onRowClick={vi.fn()} />)

    const firstRow = screen.getByText('John Doe').closest('tr')
    expect(firstRow).toHaveClass('cursor-pointer')
  })

  it('does not apply cursor-pointer when onRowClick is not provided', () => {
    render(<Table data={mockData} columns={columns} />)

    const firstRow = screen.getByText('John Doe').closest('tr')
    expect(firstRow).not.toHaveClass('cursor-pointer')
  })
})
