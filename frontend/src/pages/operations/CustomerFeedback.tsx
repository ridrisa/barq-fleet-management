import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Star, MessageSquare, Search, Filter, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { feedbackAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function CustomerFeedback() {
  const { t: _t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedFeedback, setSelectedFeedback] = useState<any>(null)
  const [ratingFilter, setRatingFilter] = useState<string>('all')
  const [responseStatus, setResponseStatus] = useState<string>('all')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'customer-feedback',
    queryFn: feedbackAPI.getAll,
    pageSize: 10,
  })

  const { isLoading: isMutating } = useCRUD({
    queryKey: 'customer-feedback',
    entityName: 'Feedback',
    update: feedbackAPI.addResponse,
  })

  const handleOpenResponseModal = (feedback: any) => {
    setSelectedFeedback(feedback)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedFeedback(null)
  }

  const handleSubmitResponse = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const response = formData.get('response') as string

    await feedbackAPI.addResponse(selectedFeedback.id, response)
    handleCloseModal()
  }

  // Apply filters
  let displayData = filteredData
  if (ratingFilter !== 'all') {
    displayData = displayData.filter((f: any) => f.rating === parseInt(ratingFilter))
  }
  if (responseStatus !== 'all') {
    if (responseStatus === 'responded') {
      displayData = displayData.filter((f: any) => f.response)
    } else {
      displayData = displayData.filter((f: any) => !f.response)
    }
  }

  // Calculate stats
  const totalFeedback = filteredData.length
  const avgRating = filteredData.length > 0
    ? (filteredData.reduce((sum: number, f: any) => sum + (f.rating || 0), 0) / filteredData.length).toFixed(1)
    : '0.0'
  const fiveStarCount = filteredData.filter((f: any) => f.rating === 5).length
  const fiveStarPercentage = totalFeedback > 0 ? ((fiveStarCount / totalFeedback) * 100).toFixed(1) : '0.0'
  const respondedCount = filteredData.filter((f: any) => f.response).length
  const responseRate = totalFeedback > 0 ? ((respondedCount / totalFeedback) * 100).toFixed(1) : '0.0'

  // Rating distribution
  const ratingDistribution = [
    { rating: '5 Stars', count: filteredData.filter((f: any) => f.rating === 5).length },
    { rating: '4 Stars', count: filteredData.filter((f: any) => f.rating === 4).length },
    { rating: '3 Stars', count: filteredData.filter((f: any) => f.rating === 3).length },
    { rating: '2 Stars', count: filteredData.filter((f: any) => f.rating === 2).length },
    { rating: '1 Star', count: filteredData.filter((f: any) => f.rating === 1).length },
  ]

  const StarRating = ({ rating }: { rating: number }) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  const columns = [
    {
      key: 'delivery_id',
      header: 'Tracking #',
      render: (row: any) => (
        <div className="font-mono text-sm text-blue-600">
          {row.tracking_number || `TRK-${row.delivery_id?.toString().padStart(6, '0')}`}
        </div>
      ),
    },
    {
      key: 'courier_name',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id}`,
    },
    {
      key: 'rating',
      header: 'Rating',
      sortable: true,
      render: (row: any) => <StarRating rating={row.rating || 0} />,
    },
    {
      key: 'comment',
      header: 'Comment',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.comment || '-'}
        </div>
      ),
    },
    {
      key: 'feedback_date',
      header: 'Date',
      render: (row: any) => {
        const date = row.feedback_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'response',
      header: 'Response Status',
      render: (row: any) => (
        <Badge variant={row.response ? 'success' : 'warning'}>
          {row.response ? 'Responded' : 'Pending'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          {!row.response && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleOpenResponseModal(row)}
              title="Add response"
            >
              <MessageSquare className="h-4 w-4 text-blue-600" />
            </Button>
          )}
          {row.response && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleOpenResponseModal(row)}
              title="View response"
            >
              <MessageSquare className="h-4 w-4 text-green-600" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading feedback: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Customer Feedback</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">{totalFeedback}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-yellow-600">{avgRating}</p>
                  <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                </div>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">5-Star %</p>
                <p className="text-2xl font-bold text-green-600">{fiveStarPercentage}%</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 text-xl">★</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Response Rate</p>
                <p className="text-2xl font-bold text-purple-600">{responseRate}%</p>
              </div>
              <MessageSquare className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Rating Distribution Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Rating Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={ratingDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="rating" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Feedback Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Feedback</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by tracking number, courier, comment..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-32">
                <Select
                  value={ratingFilter}
                  onChange={(e) => setRatingFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Ratings' },
                    { value: '5', label: '5 Stars' },
                    { value: '4', label: '4 Stars' },
                    { value: '3', label: '3 Stars' },
                    { value: '2', label: '2 Stars' },
                    { value: '1', label: '1 Star' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={responseStatus}
                  onChange={(e) => setResponseStatus(e.target.value)}
                  options={[
                    { value: 'all', label: 'All' },
                    { value: 'responded', label: 'Responded' },
                    { value: 'pending', label: 'Pending' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
            </div>

            <Table
              data={displayData.slice((currentPage - 1) * pageSize, currentPage * pageSize)}
              columns={columns}
            />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(displayData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={displayData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>

      {/* Response Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={selectedFeedback?.response ? 'View Response' : 'Add Response'}
        size="lg"
      >
        {selectedFeedback && (
          <div className="space-y-4">
            {/* Feedback Details */}
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm text-blue-600">
                  {selectedFeedback.tracking_number || `TRK-${selectedFeedback.delivery_id?.toString().padStart(6, '0')}`}
                </div>
                <StarRating rating={selectedFeedback.rating || 0} />
              </div>
              <div className="text-sm">
                <span className="font-medium">Courier:</span> {selectedFeedback.courier_name || `Courier #${selectedFeedback.courier_id}`}
              </div>
              <div className="text-sm">
                <span className="font-medium">Date:</span> {new Date(selectedFeedback.feedback_date || selectedFeedback.created_at).toLocaleString()}
              </div>
              {selectedFeedback.comment && (
                <div className="text-sm">
                  <span className="font-medium">Comment:</span>
                  <p className="mt-1 text-gray-700">{selectedFeedback.comment}</p>
                </div>
              )}
            </div>

            {/* Response Form or Display */}
            {selectedFeedback.response ? (
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-gray-700 mb-2">Our Response:</div>
                <p className="text-gray-900">{selectedFeedback.response}</p>
                {selectedFeedback.response_date && (
                  <div className="text-xs text-gray-500 mt-2">
                    Responded on: {new Date(selectedFeedback.response_date).toLocaleString()}
                  </div>
                )}
              </div>
            ) : (
              <form onSubmit={handleSubmitResponse} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Your Response *
                  </label>
                  <textarea
                    name="response"
                    required
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Write your response to the customer..."
                  />
                </div>

                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={handleCloseModal}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isMutating}>
                    {isMutating ? 'Submitting...' : 'Submit Response'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
