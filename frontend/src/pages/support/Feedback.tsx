import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { Table } from '@/components/ui/Table'
import { Pagination } from '@/components/ui/Pagination'
import { feedbackAPI } from '@/lib/api'
import { Star, Plus, Search, Filter, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface Feedback {
  id: number
  user: string
  rating: number
  category: string
  comments: string
  sentiment?: 'positive' | 'neutral' | 'negative'
  created_at: string
}

const categories = ['App Performance', 'Feature Request', 'Bug Report', 'User Experience', 'Other']
const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6']

export default function Feedback() {
  const [page, setPage] = useState(1)
  const [limit] = useState(20)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [ratingFilter, setRatingFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    rating: 5,
    category: '',
    comments: '',
  })

  // Fetch feedback
  const { data, isLoading, error } = useQuery({
    queryKey: ['feedback', page, limit, categoryFilter, ratingFilter],
    queryFn: () =>
      feedbackAPI.getAll((page - 1) * limit, limit),
  })

  // Fetch rating summary
  const { data: summary } = useQuery({
    queryKey: ['feedback-summary'],
    queryFn: () => feedbackAPI.getRatingSummary(),
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.category || !formData.comments) {
      toast.error('Please fill all required fields')
      return
    }

    try {
      // In real app, this would call feedbackAPI.create
      toast.success('Thank you for your feedback!')
      setShowCreateModal(false)
      resetForm()
    } catch (error) {
      toast.error('Failed to submit feedback')
    }
  }

  const resetForm = () => {
    setFormData({
      rating: 5,
      category: '',
      comments: '',
    })
  }

  // Filter feedback
  const filteredFeedback = data?.feedback?.filter((fb: Feedback) => {
    const matchesSearch = fb.comments.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         fb.user.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || fb.category === categoryFilter
    const matchesRating = ratingFilter === 'all' || fb.rating.toString() === ratingFilter
    return matchesSearch && matchesCategory && matchesRating
  }) || []

  // Calculate stats
  const avgRating = summary?.avg_rating || 0
  const totalFeedback = data?.total || 0
  const positiveFeedback = filteredFeedback.filter((fb: Feedback) => fb.rating >= 4).length
  const positivePercent = totalFeedback > 0 ? ((positiveFeedback / totalFeedback) * 100).toFixed(1) : 0

  // Sentiment data for pie chart
  const sentimentData = [
    { name: 'Positive', value: filteredFeedback.filter((fb: Feedback) => fb.rating >= 4).length },
    { name: 'Neutral', value: filteredFeedback.filter((fb: Feedback) => fb.rating === 3).length },
    { name: 'Negative', value: filteredFeedback.filter((fb: Feedback) => fb.rating <= 2).length },
  ]

  // Category distribution for bar chart
  const categoryData = categories.map(cat => ({
    category: cat,
    count: filteredFeedback.filter((fb: Feedback) => fb.category === cat).length,
  }))

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  const getSentimentBadge = (rating: number) => {
    if (rating >= 4) return <Badge variant="success">Positive</Badge>
    if (rating === 3) return <Badge variant="warning">Neutral</Badge>
    return <Badge variant="danger">Negative</Badge>
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'user', label: 'User' },
    {
      key: 'rating',
      label: 'Rating',
      render: (fb: Feedback) => renderStars(fb.rating),
    },
    {
      key: 'sentiment',
      label: 'Sentiment',
      render: (fb: Feedback) => getSentimentBadge(fb.rating),
    },
    {
      key: 'category',
      label: 'Category',
      render: (fb: Feedback) => <Badge variant="outline">{fb.category}</Badge>,
    },
    {
      key: 'comments',
      label: 'Comments',
      render: (fb: Feedback) => (
        <div className="max-w-xs truncate" title={fb.comments}>
          {fb.comments}
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Date',
      render: (fb: Feedback) => new Date(fb.created_at).toLocaleDateString(),
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
      <div className="text-center text-red-600">
        Error loading feedback: {(error as Error).message}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Customer Feedback</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Submit Feedback
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Rating</p>
                <p className="text-2xl font-bold mt-2">{avgRating.toFixed(1)}</p>
                {renderStars(Math.round(avgRating))}
              </div>
              <Star className="w-8 h-8 text-yellow-400 fill-yellow-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold mt-2">{totalFeedback}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Positive %</p>
                <p className="text-2xl font-bold text-green-600 mt-2">{positivePercent}%</p>
              </div>
              <ThumbsUp className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Issues Reported</p>
                <p className="text-2xl font-bold text-red-600 mt-2">
                  {filteredFeedback.filter((fb: Feedback) => fb.category === 'Bug Report').length}
                </p>
              </div>
              <ThumbsDown className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Search</label>
                <Input
                  placeholder="Search feedback..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="w-4 h-4" />}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Categories' },
                    ...categories.map(cat => ({ value: cat, label: cat })),
                  ]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Rating</label>
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
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Category Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Feedback Table */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold mb-4">Recent Feedback</h3>
          {filteredFeedback.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No feedback found</p>
            </div>
          ) : (
            <>
              <Table data={filteredFeedback} columns={columns} />
              <div className="mt-4">
                <Pagination
                  currentPage={page}
                  totalPages={Math.ceil((data?.total || 0) / limit)}
                  onPageChange={setPage}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Create Feedback Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          resetForm()
        }}
        title="Submit Feedback"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Rating <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map(star => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setFormData({ ...formData, rating: star })}
                  className="transition-transform hover:scale-110"
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= formData.rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <Select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              options={[
                { value: '', label: 'Select Category' },
                ...categories.map(cat => ({ value: cat, label: cat })),
              ]}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Comments <span className="text-red-500">*</span>
            </label>
            <textarea
              className="w-full border rounded-md p-2 min-h-[120px]"
              value={formData.comments}
              onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
              placeholder="Tell us about your experience..."
              required
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowCreateModal(false)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button type="submit">
              Submit Feedback
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
