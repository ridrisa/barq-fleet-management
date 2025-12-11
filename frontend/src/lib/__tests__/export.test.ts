import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  exportToExcel,
  exportToCSV,
  exportToPDF,
  exportTableToPDF,
  printPage,
  copyToClipboard,
} from '../export'

// Mock XLSX
vi.mock('xlsx', () => ({
  utils: {
    book_new: vi.fn(() => ({})),
    json_to_sheet: vi.fn(() => ({})),
    book_append_sheet: vi.fn(),
  },
  writeFile: vi.fn(),
}))

// Mock jsPDF
vi.mock('jspdf', () => ({
  default: vi.fn().mockImplementation(() => ({
    setFontSize: vi.fn(),
    setFont: vi.fn(),
    text: vi.fn(),
    addImage: vi.fn(),
    addPage: vi.fn(),
    save: vi.fn(),
    internal: {
      pageSize: {
        getWidth: vi.fn(() => 210),
        getHeight: vi.fn(() => 297),
      },
    },
  })),
}))

// Mock html2canvas
vi.mock('html2canvas', () => ({
  default: vi.fn().mockResolvedValue({
    toDataURL: vi.fn(() => 'data:image/png;base64,mockdata'),
    width: 1000,
    height: 1500,
  }),
}))

// Mock DOM APIs
const mockElement = document.createElement('div')
mockElement.id = 'test-element'

const mockBlobUrl = 'blob:mock-url'

describe('Export Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    document.body.innerHTML = ''
    document.body.appendChild(mockElement)

    // Mock URL APIs
    global.URL.createObjectURL = vi.fn(() => mockBlobUrl)
    global.URL.revokeObjectURL = vi.fn()

    // Mock clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('exportToExcel', () => {
    it('should export data to Excel successfully', async () => {
      const XLSX = await import('xlsx')
      const data = [
        { id: 1, name: 'Item 1', value: 100 },
        { id: 2, name: 'Item 2', value: 200 },
      ]

      const result = exportToExcel(data, 'test-export')

      expect(result.success).toBe(true)
      expect(XLSX.utils.book_new).toHaveBeenCalled()
      expect(XLSX.utils.json_to_sheet).toHaveBeenCalledWith(data)
      expect(XLSX.writeFile).toHaveBeenCalledWith({}, 'test-export.xlsx')
    })

    it('should use custom sheet name', async () => {
      const XLSX = await import('xlsx')
      const data = [{ id: 1, name: 'Item 1' }]

      exportToExcel(data, 'test-export', 'CustomSheet')

      expect(XLSX.utils.book_append_sheet).toHaveBeenCalledWith({}, {}, 'CustomSheet')
    })

    it('should handle export errors', async () => {
      const XLSX = await import('xlsx')
      ;(XLSX.writeFile as ReturnType<typeof vi.fn>).mockImplementation(() => {
        throw new Error('Write failed')
      })

      const result = exportToExcel([{ id: 1 }], 'test')

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })

  describe('exportToCSV', () => {
    it('should export data to CSV successfully', () => {
      const data = [
        { id: 1, name: 'Item 1', value: 100 },
        { id: 2, name: 'Item 2', value: 200 },
      ]

      // Mock document.createElement and click
      const mockLink = document.createElement('a')
      mockLink.click = vi.fn()
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink)

      const result = exportToCSV(data, 'test-export')

      expect(result.success).toBe(true)
      expect(URL.createObjectURL).toHaveBeenCalled()
    })

    it('should handle empty data', () => {
      const result = exportToCSV([], 'test-export')

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should escape values with commas', () => {
      const data = [{ name: 'Item, with comma', description: 'Normal value' }]

      const mockLink = document.createElement('a')
      mockLink.click = vi.fn()
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink)

      const result = exportToCSV(data, 'test')

      expect(result.success).toBe(true)
    })

    it('should escape values with quotes', () => {
      const data = [{ name: 'Item "with quotes"', value: 100 }]

      const mockLink = document.createElement('a')
      mockLink.click = vi.fn()
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink)

      const result = exportToCSV(data, 'test')

      expect(result.success).toBe(true)
    })
  })

  describe('exportToPDF', () => {
    it('should export element to PDF successfully', async () => {
      const result = await exportToPDF('test-element', 'test-export')

      expect(result.success).toBe(true)
    })

    it('should handle missing element', async () => {
      const result = await exportToPDF('non-existent-element', 'test-export')

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should support landscape orientation', async () => {
      const result = await exportToPDF('test-element', 'test-export', 'landscape')

      expect(result.success).toBe(true)
    })
  })

  describe('exportTableToPDF', () => {
    it('should export table data to PDF successfully', () => {
      const data = [
        { id: 1, name: 'Item 1', value: 100 },
        { id: 2, name: 'Item 2', value: 200 },
      ]
      const columns = [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Name' },
        { key: 'value', label: 'Value' },
      ]

      const result = exportTableToPDF(data, columns, 'test-export')

      expect(result.success).toBe(true)
    })

    it('should add title when provided', () => {
      const data = [{ id: 1, name: 'Item 1' }]
      const columns = [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Name' },
      ]

      const result = exportTableToPDF(data, columns, 'test-export', 'Test Report')

      expect(result.success).toBe(true)
    })

    it('should handle empty data', () => {
      const columns = [{ key: 'id', label: 'ID' }]

      const result = exportTableToPDF([], columns, 'test-export')

      expect(result.success).toBe(true) // Empty table is still valid
    })
  })

  describe('printPage', () => {
    it('should trigger window.print()', () => {
      window.print = vi.fn()

      const result = printPage()

      expect(window.print).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('should handle print errors', () => {
      window.print = vi.fn(() => {
        throw new Error('Print failed')
      })

      const result = printPage()

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })
  })

  describe('copyToClipboard', () => {
    it('should copy data to clipboard successfully', async () => {
      const data = [
        { id: 1, name: 'Item 1' },
        { id: 2, name: 'Item 2' },
      ]

      const result = await copyToClipboard(data)

      expect(navigator.clipboard.writeText).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('should format data as tab-separated values', async () => {
      const data = [{ col1: 'A', col2: 'B' }]

      await copyToClipboard(data)

      const writtenContent = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0]
      expect(writtenContent).toContain('\t') // Tab-separated
    })

    it('should handle empty data', async () => {
      const result = await copyToClipboard([])

      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should handle clipboard errors', async () => {
      navigator.clipboard.writeText = vi.fn().mockRejectedValue(new Error('Clipboard error'))

      const data = [{ id: 1, name: 'Item 1' }]
      const result = await copyToClipboard(data)

      expect(result.success).toBe(false)
    })
  })
})
