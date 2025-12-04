import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

/**
 * Export data to Excel file
 * @param data - Array of objects to export
 * @param filename - Name of the file (without extension)
 * @param sheetName - Name of the sheet (optional)
 */
export const exportToExcel = (
  data: Record<string, any>[],
  filename: string,
  sheetName: string = 'Sheet1'
) => {
  try {
    // Create a new workbook
    const wb = XLSX.utils.book_new()

    // Convert data to worksheet
    const ws = XLSX.utils.json_to_sheet(data)

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, sheetName)

    // Generate Excel file and trigger download
    XLSX.writeFile(wb, `${filename}.xlsx`)

    return { success: true }
  } catch (error) {
    console.error('Export to Excel failed:', error)
    return { success: false, error }
  }
}

/**
 * Export HTML element to PDF
 * @param elementId - ID of the HTML element to convert
 * @param filename - Name of the PDF file (without extension)
 * @param orientation - Page orientation ('portrait' or 'landscape')
 */
export const exportToPDF = async (
  elementId: string,
  filename: string,
  orientation: 'portrait' | 'landscape' = 'portrait'
) => {
  try {
    const element = document.getElementById(elementId)

    if (!element) {
      throw new Error(`Element with ID '${elementId}' not found`)
    }

    // Convert HTML element to canvas
    const canvas = await html2canvas(element, {
      scale: 2,
      logging: false,
      useCORS: true,
    })

    const imgData = canvas.toDataURL('image/png')

    // Calculate PDF dimensions
    const imgWidth = orientation === 'portrait' ? 210 : 297 // A4 width in mm
    const imgHeight = orientation === 'portrait' ? 297 : 210 // A4 height in mm
    const pageWidth = imgWidth
    const pageHeight = (canvas.height * pageWidth) / canvas.width

    // Create PDF
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format: 'a4',
    })

    let heightLeft = pageHeight
    let position = 0

    // Add image to PDF
    pdf.addImage(imgData, 'PNG', 0, position, pageWidth, pageHeight)
    heightLeft -= imgHeight

    // Add more pages if content is longer than one page
    while (heightLeft > 0) {
      position = heightLeft - pageHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pageWidth, pageHeight)
      heightLeft -= imgHeight
    }

    // Save PDF
    pdf.save(`${filename}.pdf`)

    return { success: true }
  } catch (error) {
    console.error('Export to PDF failed:', error)
    return { success: false, error }
  }
}

/**
 * Export table data to PDF
 * @param data - Array of objects representing table rows
 * @param columns - Array of column definitions
 * @param filename - Name of the PDF file
 * @param title - Title of the document
 */
export const exportTableToPDF = (
  data: Record<string, any>[],
  columns: { key: string; label: string }[],
  filename: string,
  title?: string
) => {
  try {
    const pdf = new jsPDF()

    // Add title if provided
    if (title) {
      pdf.setFontSize(16)
      pdf.text(title, 14, 15)
    }

    // Starting position
    let yPosition = title ? 25 : 15

    // Add table headers
    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'bold')

    let xPosition = 14
    const columnWidth = (pdf.internal.pageSize.getWidth() - 28) / columns.length

    columns.forEach((col) => {
      pdf.text(col.label, xPosition, yPosition)
      xPosition += columnWidth
    })

    // Add table rows
    pdf.setFont('helvetica', 'normal')
    yPosition += 7

    data.forEach((row) => {
      xPosition = 14

      columns.forEach((col) => {
        const value = String(row[col.key] || '')
        pdf.text(value.substring(0, 25), xPosition, yPosition) // Truncate long values
        xPosition += columnWidth
      })

      yPosition += 7

      // Add new page if needed
      if (yPosition > pdf.internal.pageSize.getHeight() - 20) {
        pdf.addPage()
        yPosition = 15
      }
    })

    // Save PDF
    pdf.save(`${filename}.pdf`)

    return { success: true }
  } catch (error) {
    console.error('Export table to PDF failed:', error)
    return { success: false, error }
  }
}

/**
 * Print the current page with optimized print layout
 */
export const printPage = () => {
  try {
    window.print()
    return { success: true }
  } catch (error) {
    console.error('Print failed:', error)
    return { success: false, error }
  }
}

/**
 * Export data to CSV file
 * @param data - Array of objects to export
 * @param filename - Name of the file (without extension)
 */
export const exportToCSV = (data: Record<string, any>[], filename: string) => {
  try {
    if (data.length === 0) {
      throw new Error('No data to export')
    }

    // Get column headers
    const headers = Object.keys(data[0])

    // Create CSV content
    const csvContent = [
      headers.join(','), // Header row
      ...data.map((row) =>
        headers
          .map((header) => {
            const value = row[header]
            // Handle values with commas or quotes
            const stringValue = String(value || '')
            if (stringValue.includes(',') || stringValue.includes('"')) {
              return `"${stringValue.replace(/"/g, '""')}"`
            }
            return stringValue
          })
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

    return { success: true }
  } catch (error) {
    console.error('Export to CSV failed:', error)
    return { success: false, error }
  }
}

/**
 * Copy table data to clipboard
 * @param data - Array of objects to copy
 */
export const copyToClipboard = async (data: Record<string, any>[]) => {
  try {
    if (data.length === 0) {
      throw new Error('No data to copy')
    }

    // Convert to tab-separated values (TSV) for better Excel pasting
    const headers = Object.keys(data[0])
    const tsvContent = [
      headers.join('\t'),
      ...data.map((row) => headers.map((header) => row[header] || '').join('\t')),
    ].join('\n')

    await navigator.clipboard.writeText(tsvContent)

    return { success: true }
  } catch (error) {
    console.error('Copy to clipboard failed:', error)
    return { success: false, error }
  }
}
