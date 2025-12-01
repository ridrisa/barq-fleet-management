/**
 * Usage examples for UI components
 *
 * This file demonstrates how to use FileUpload, DateRangePicker,
 * and export utilities
 */

import { useState } from 'react'
import { FileUpload } from '@/components/ui/FileUpload'
import { DateRangePicker } from '@/components/ui/DateRangePicker'
import { DateRange } from 'react-day-picker'
import { Button } from '@/components/ui/Button'
import {
  exportToExcel,
  exportToCSV,
  exportToPDF,
  exportToJSON,
} from '@/utils/export'

// Example 1: File Upload - Single File
export function SingleFileUploadExample() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setSelectedFile(files[0])
      console.log('Selected file:', files[0])
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Profile Picture</h3>
      <FileUpload
        onFilesSelected={handleFileSelect}
        accept={{
          'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
        }}
        maxFiles={1}
        maxSize={2 * 1024 * 1024} // 2MB
        multiple={false}
        showPreview={true}
      />
      {selectedFile && (
        <p className="text-sm text-gray-600">
          Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
        </p>
      )}
    </div>
  )
}

// Example 2: File Upload - Multiple Files
export function MultipleFileUploadExample() {
  const [files, setFiles] = useState<File[]>([])

  const handleFilesSelect = (newFiles: File[]) => {
    setFiles((prev) => [...prev, ...newFiles])
    console.log('All files:', [...files, ...newFiles])
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Documents</h3>
      <FileUpload
        onFilesSelected={handleFilesSelect}
        accept={{
          'application/pdf': ['.pdf'],
          'application/msword': ['.doc', '.docx'],
          'application/vnd.ms-excel': ['.xls', '.xlsx'],
        }}
        maxFiles={5}
        maxSize={10 * 1024 * 1024} // 10MB
        multiple={true}
        showPreview={true}
      />
      <div className="text-sm text-gray-600">
        <p>Total files: {files.length}</p>
        <p>Accepted formats: PDF, Word, Excel</p>
      </div>
    </div>
  )
}

// Example 3: File Upload - Image Gallery
export function ImageGalleryUploadExample() {
  const [images, setImages] = useState<File[]>([])

  const handleImageUpload = (files: File[]) => {
    setImages((prev) => [...prev, ...files])
    // Here you would typically upload to server
    console.log('Uploading images:', files)
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Upload Gallery Images</h3>
      <FileUpload
        onFilesSelected={handleImageUpload}
        accept={{
          'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
        }}
        maxFiles={10}
        maxSize={5 * 1024 * 1024} // 5MB per image
        multiple={true}
        showPreview={true}
      />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {images.map((file, index) => (
          <div key={index} className="relative aspect-square">
            <img
              src={URL.createObjectURL(file)}
              alt={file.name}
              className="w-full h-full object-cover rounded-lg"
            />
          </div>
        ))}
      </div>
    </div>
  )
}

// Example 4: Date Range Picker - Basic
export function DateRangePickerBasicExample() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>()

  const handleDateChange = (range: DateRange | undefined) => {
    setDateRange(range)
    console.log('Selected range:', range)
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Select Report Period</h3>
      <DateRangePicker
        value={dateRange}
        onChange={handleDateChange}
        placeholder="Choose date range"
      />
      {dateRange?.from && dateRange?.to && (
        <p className="text-sm text-gray-600">
          Selected: {dateRange.from.toLocaleDateString()} -{' '}
          {dateRange.to.toLocaleDateString()}
        </p>
      )}
    </div>
  )
}

// Example 5: Date Range Picker - With Data Fetching
export function DateRangePickerWithDataExample() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>()
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any[]>([])

  const handleDateChange = async (range: DateRange | undefined) => {
    setDateRange(range)

    if (range?.from && range?.to) {
      setLoading(true)
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))
        // Fetch data for the selected range
        setData([
          /* ... fetched data ... */
        ])
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Analytics Dashboard</h3>
      <DateRangePicker
        value={dateRange}
        onChange={handleDateChange}
        placeholder="Select date range"
      />
      {loading && <p className="text-sm text-gray-600">Loading data...</p>}
      {data.length > 0 && (
        <div className="text-sm text-gray-600">
          Loaded {data.length} records
        </div>
      )}
    </div>
  )
}

// Example 6: Export to Excel
export function ExportToExcelExample() {
  const sampleData = [
    { id: 1, name: 'Ahmed Ali', orders: 45, revenue: 2500, rating: 4.8 },
    { id: 2, name: 'Sarah Hassan', orders: 38, revenue: 2100, rating: 4.9 },
    { id: 3, name: 'Mohammed Khalid', orders: 52, revenue: 2900, rating: 4.7 },
    { id: 4, name: 'Fatima Ahmed', orders: 41, revenue: 2300, rating: 4.8 },
    { id: 5, name: 'Omar Ibrahim', orders: 35, revenue: 1950, rating: 4.6 },
  ]

  const handleExportExcel = () => {
    exportToExcel(sampleData, 'courier-performance', 'Couriers')
  }

  const handleExportCSV = () => {
    exportToCSV(sampleData, 'courier-performance')
  }

  const handleExportJSON = () => {
    exportToJSON(
      {
        data: sampleData,
        exportDate: new Date().toISOString(),
        totalRecords: sampleData.length,
      },
      'courier-performance',
      true
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Courier Performance Report</h3>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Orders
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Revenue
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Rating
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sampleData.map((row) => (
              <tr key={row.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row.orders}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${row.revenue}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {row.rating}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex gap-2">
        <Button onClick={handleExportExcel} variant="primary">
          Export to Excel
        </Button>
        <Button onClick={handleExportCSV} variant="secondary">
          Export to CSV
        </Button>
        <Button onClick={handleExportJSON} variant="secondary">
          Export to JSON
        </Button>
      </div>
    </div>
  )
}

// Example 7: Export to PDF
export function ExportToPDFExample() {
  const handleExportPDF = async () => {
    try {
      await exportToPDF('report-content', 'monthly-report', {
        orientation: 'portrait',
        format: 'a4',
        title: 'Monthly Performance Report',
      })
    } catch (error) {
      console.error('Failed to export PDF:', error)
    }
  }

  return (
    <div className="space-y-4">
      <div id="report-content" className="bg-white p-8 rounded-lg border">
        <h2 className="text-2xl font-bold mb-4">Monthly Performance Report</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Summary</h3>
            <p className="text-gray-600">
              This month we completed 1,247 deliveries with a success rate of 94.8%.
              Revenue increased by 15.3% compared to last month.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="border rounded p-4">
              <p className="text-sm text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold">1,247</p>
            </div>
            <div className="border rounded p-4">
              <p className="text-sm text-gray-600">Revenue</p>
              <p className="text-2xl font-bold">$45,678</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Top Performers</h3>
            <ul className="space-y-2">
              <li className="text-gray-600">1. Ahmed Ali - 89 deliveries</li>
              <li className="text-gray-600">2. Sarah Hassan - 76 deliveries</li>
              <li className="text-gray-600">3. Mohammed Khalid - 72 deliveries</li>
            </ul>
          </div>
        </div>
      </div>

      <Button onClick={handleExportPDF} variant="primary">
        Download as PDF
      </Button>
    </div>
  )
}

// Example 8: Complete Form with File Upload and Date Range
export function CompleteFormExample() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>()
  const [files, setFiles] = useState<File[]>([])
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      ...formData,
      dateRange,
      files: files.map((f) => f.name),
    }

    console.log('Form submitted:', data)

    // Here you would upload files and submit form
    // await uploadFiles(files)
    // await submitForm(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      <h3 className="text-lg font-semibold">Create Campaign Report</h3>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Report Title
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          rows={4}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Report Period
        </label>
        <DateRangePicker
          value={dateRange}
          onChange={setDateRange}
          placeholder="Select date range"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Supporting Documents
        </label>
        <FileUpload
          onFilesSelected={(newFiles) => setFiles([...files, ...newFiles])}
          accept={{
            'application/pdf': ['.pdf'],
            'image/*': ['.png', '.jpg', '.jpeg'],
          }}
          maxFiles={5}
          maxSize={10 * 1024 * 1024}
          multiple={true}
        />
      </div>

      <Button type="submit" variant="primary" className="w-full">
        Create Report
      </Button>
    </form>
  )
}
