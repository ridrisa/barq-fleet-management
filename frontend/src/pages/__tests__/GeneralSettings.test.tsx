import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import GeneralSettings from '../settings/GeneralSettings'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  settingsAPI: {
    getGeneral: vi.fn().mockResolvedValue({
      company_name: 'BARQ Fleet',
      company_email: 'info@barq.com',
      company_phone: '+966501234567',
      timezone: 'Asia/Riyadh',
      language: 'en',
      date_format: 'YYYY-MM-DD',
      time_format: '24h',
      currency: 'SAR',
      currency_symbol: 'ر.س',
    }),
    updateGeneral: vi.fn().mockResolvedValue({ success: true }),
  },
}))

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe('GeneralSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('General Settings')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<GeneralSettings />)

    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays Company Information section', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Company Information')).toBeInTheDocument()
      expect(screen.getByText('Company Name')).toBeInTheDocument()
      expect(screen.getByText('Company Email')).toBeInTheDocument()
      expect(screen.getByText('Company Phone')).toBeInTheDocument()
    })
  })

  it('displays Localization section', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Localization')).toBeInTheDocument()
      expect(screen.getByText('Timezone')).toBeInTheDocument()
      expect(screen.getByText('Language')).toBeInTheDocument()
    })
  })

  it('displays Date & Time Format section', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Date & Time Format')).toBeInTheDocument()
      expect(screen.getByText('Date Format')).toBeInTheDocument()
      expect(screen.getByText('Time Format')).toBeInTheDocument()
    })
  })

  it('displays Currency Settings section', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Currency Settings')).toBeInTheDocument()
      expect(screen.getByText('Currency')).toBeInTheDocument()
      expect(screen.getByText('Currency Symbol')).toBeInTheDocument()
    })
  })

  it('populates form with fetched settings', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('BARQ Fleet')).toBeInTheDocument()
      expect(screen.getByDisplayValue('info@barq.com')).toBeInTheDocument()
      expect(screen.getByDisplayValue('+966501234567')).toBeInTheDocument()
    })
  })

  it('renders Save Settings button', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save settings/i })).toBeInTheDocument()
    })
  })

  it('renders Reset to Defaults button', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /reset to defaults/i })).toBeInTheDocument()
    })
  })

  it('allows editing company name', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('BARQ Fleet')).toBeInTheDocument()
    })

    const companyNameInput = screen.getByDisplayValue('BARQ Fleet')
    fireEvent.change(companyNameInput, { target: { value: 'New Company Name' } })

    expect(screen.getByDisplayValue('New Company Name')).toBeInTheDocument()
  })

  it('allows editing company email', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('info@barq.com')).toBeInTheDocument()
    })

    const emailInput = screen.getByDisplayValue('info@barq.com')
    fireEvent.change(emailInput, { target: { value: 'newemail@barq.com' } })

    expect(screen.getByDisplayValue('newemail@barq.com')).toBeInTheDocument()
  })

  it('has timezone dropdown with options', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Timezone')).toBeInTheDocument()
    })

    // Check for timezone select
    const timezoneSelect = screen.getByDisplayValue(/Dubai/i)
    expect(timezoneSelect).toBeInTheDocument()
  })

  it('has language dropdown with options', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText('Language')).toBeInTheDocument()
    })

    // Check for language select with English selected
    const languageSelect = screen.getByDisplayValue('English')
    expect(languageSelect).toBeInTheDocument()
  })

  it('displays preview for date/time format', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByText(/preview:/i)).toBeInTheDocument()
    })
  })

  it('displays preview for currency format', async () => {
    render(<GeneralSettings />)

    await waitFor(() => {
      // Check for currency preview
      expect(screen.getByText(/1,234.56/)).toBeInTheDocument()
    })
  })

  it('submits form when Save Settings is clicked', async () => {
    const { settingsAPI } = await import('@/lib/api')
    render(<GeneralSettings />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save settings/i })).toBeInTheDocument()
    })

    const saveButton = screen.getByRole('button', { name: /save settings/i })
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(settingsAPI.updateGeneral).toHaveBeenCalled()
    })
  })
})
