import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

/**
 * Export data to Excel file (.xlsx)
 *
 * @param data - Array of objects to export
 * @param filename - Name of the file (without extension)
 * @param sheetName - Name of the worksheet
 *
 * @example
 * ```typescript
 * const data = [
 *   { name: 'John', age: 30, email: 'john@example.com' },
 *   { name: 'Jane', age: 25, email: 'jane@example.com' }
 * ]
 * exportToExcel(data, 'users', 'User List')
 * ```
 */
export const exportToExcel = (
  data: any[],
  filename: string,
  sheetName: string = 'Sheet1'
): void => {
  try {
    // Create a new workbook
    const workbook = XLSX.utils.book_new()

    // Convert data to worksheet
    const worksheet = XLSX.utils.json_to_sheet(data)

    // Auto-size columns
    const maxWidth = 50
    const columnWidths: { [key: string]: number } = {}

    // Calculate column widths based on content
    data.forEach((row) => {
      Object.keys(row).forEach((key) => {
        const value = String(row[key] || '')
        const currentWidth = columnWidths[key] || key.length
        columnWidths[key] = Math.min(
          Math.max(currentWidth, value.length),
          maxWidth
        )
      })
    })

    // Set column widths
    worksheet['!cols'] = Object.keys(columnWidths).map((key) => ({
      wch: columnWidths[key] + 2, // Add padding
    }))

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

    // Generate Excel file and trigger download
    XLSX.writeFile(workbook, `${filename}.xlsx`)
  } catch (error) {
    console.error('Error exporting to Excel:', error)
    throw new Error('Failed to export data to Excel')
  }
}

/**
 * Export multiple sheets to a single Excel file
 *
 * @param sheets - Array of sheet configurations
 * @param filename - Name of the file (without extension)
 *
 * @example
 * ```typescript
 * exportToExcelMultiSheet([
 *   { name: 'Users', data: usersData },
 *   { name: 'Orders', data: ordersData }
 * ], 'report')
 * ```
 */
export const exportToExcelMultiSheet = (
  sheets: Array<{ name: string; data: any[] }>,
  filename: string
): void => {
  try {
    const workbook = XLSX.utils.book_new()

    sheets.forEach(({ name, data }) => {
      const worksheet = XLSX.utils.json_to_sheet(data)
      XLSX.utils.book_append_sheet(workbook, worksheet, name)
    })

    XLSX.writeFile(workbook, `${filename}.xlsx`)
  } catch (error) {
    console.error('Error exporting to Excel (multi-sheet):', error)
    throw new Error('Failed to export data to Excel')
  }
}

/**
 * Export data to CSV file
 *
 * @param data - Array of objects to export
 * @param filename - Name of the file (without extension)
 *
 * @example
 * ```typescript
 * const data = [
 *   { name: 'John', age: 30 },
 *   { name: 'Jane', age: 25 }
 * ]
 * exportToCSV(data, 'users')
 * ```
 */
export const exportToCSV = (data: any[], filename: string): void => {
  try {
    if (!data || data.length === 0) {
      throw new Error('No data to export')
    }

    // Get headers from first object
    const headers = Object.keys(data[0])

    // Create CSV content
    const csvContent = [
      // Header row
      headers.map((header) => escapeCSVValue(header)).join(','),
      // Data rows
      ...data.map((row) =>
        headers
          .map((header) => escapeCSVValue(row[header]))
          .join(',')
      ),
    ].join('\n')

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}.csv`)
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Cleanup
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting to CSV:', error)
    throw new Error('Failed to export data to CSV')
  }
}

/**
 * Helper function to escape CSV values
 */
const escapeCSVValue = (value: any): string => {
  if (value === null || value === undefined) {
    return ''
  }

  const stringValue = String(value)

  // If value contains comma, newline, or quote, wrap in quotes and escape quotes
  if (
    stringValue.includes(',') ||
    stringValue.includes('\n') ||
    stringValue.includes('"')
  ) {
    return `"${stringValue.replace(/"/g, '""')}"`
  }

  return stringValue
}

/**
 * Export HTML element to PDF
 *
 * @param elementId - ID of the HTML element to export
 * @param filename - Name of the file (without extension)
 * @param options - Additional PDF options
 *
 * @example
 * ```typescript
 * exportToPDF('report-container', 'monthly-report', {
 *   orientation: 'landscape',
 *   format: 'a4'
 * })
 * ```
 */
export interface ExportToPDFOptions {
  orientation?: 'portrait' | 'landscape'
  format?: 'a4' | 'letter' | 'legal'
  quality?: number
  scale?: number
  title?: string
  margin?: {
    top?: number
    right?: number
    bottom?: number
    left?: number
  }
}

export const exportToPDF = async (
  elementId: string,
  filename: string,
  options: ExportToPDFOptions = {}
): Promise<void> => {
  try {
    const element = document.getElementById(elementId)

    if (!element) {
      throw new Error(`Element with ID "${elementId}" not found`)
    }

    // Default options
    const {
      orientation = 'portrait',
      format = 'a4',
      quality = 0.95,
      scale = 2,
      title,
      margin = { top: 10, right: 10, bottom: 10, left: 10 },
    } = options

    // Capture element as canvas
    const canvas = await html2canvas(element, {
      scale,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    })

    // Calculate PDF dimensions
    const imgWidth = orientation === 'portrait' ? 210 : 297 // A4 width in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    // Create PDF
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format,
    })

    // Add title if provided
    if (title) {
      pdf.setFontSize(16)
      pdf.text(title, margin.left || 10, margin.top || 10)
    }

    // Add image to PDF
    const imgData = canvas.toDataURL('image/png', quality)
    const yOffset = title ? (margin.top || 10) + 10 : margin.top || 10

    pdf.addImage(
      imgData,
      'PNG',
      margin.left || 10,
      yOffset,
      imgWidth - (margin.left || 10) - (margin.right || 10),
      imgHeight
    )

    // Save PDF
    pdf.save(`${filename}.pdf`)
  } catch (error) {
    console.error('Error exporting to PDF:', error)
    throw new Error('Failed to export to PDF')
  }
}

/**
 * Export data to JSON file
 *
 * @param data - Data to export (any JSON-serializable value)
 * @param filename - Name of the file (without extension)
 * @param pretty - Whether to format JSON with indentation
 *
 * @example
 * ```typescript
 * exportToJSON({ users: data, timestamp: Date.now() }, 'backup', true)
 * ```
 */
export const exportToJSON = (
  data: any,
  filename: string,
  pretty: boolean = true
): void => {
  try {
    const jsonContent = pretty
      ? JSON.stringify(data, null, 2)
      : JSON.stringify(data)

    const blob = new Blob([jsonContent], { type: 'application/json' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}.json`)
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error exporting to JSON:', error)
    throw new Error('Failed to export data to JSON')
  }
}

/**
 * Export table element to Excel
 *
 * @param tableId - ID of the HTML table element
 * @param filename - Name of the file (without extension)
 *
 * @example
 * ```typescript
 * exportTableToExcel('data-table', 'table-export')
 * ```
 */
export const exportTableToExcel = (
  tableId: string,
  filename: string
): void => {
  try {
    const table = document.getElementById(tableId)

    if (!table || table.tagName !== 'TABLE') {
      throw new Error(`Table element with ID "${tableId}" not found`)
    }

    const workbook = XLSX.utils.book_new()
    const worksheet = XLSX.utils.table_to_sheet(table)

    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
    XLSX.writeFile(workbook, `${filename}.xlsx`)
  } catch (error) {
    console.error('Error exporting table to Excel:', error)
    throw new Error('Failed to export table to Excel')
  }
}

/**
 * Download file from URL
 *
 * @param url - URL of the file to download
 * @param filename - Name of the file
 *
 * @example
 * ```typescript
 * downloadFile('https://example.com/report.pdf', 'report.pdf')
 * ```
 */
export const downloadFile = async (
  url: string,
  filename: string
): Promise<void> => {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    const link = document.createElement('a')
    const objectUrl = URL.createObjectURL(blob)

    link.setAttribute('href', objectUrl)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(objectUrl)
  } catch (error) {
    console.error('Error downloading file:', error)
    throw new Error('Failed to download file')
  }
}
