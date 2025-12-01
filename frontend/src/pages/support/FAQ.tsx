import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { faqAPI } from '@/lib/api'
import { Plus, Search, ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Edit, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface FAQ {
  id: number
  question: string
  answer: string
  category: string
  helpful_count: number
  not_helpful_count: number
  views: number
  created_at: string
  updated_at: string
}

const categories = ['General', 'Account & Billing', 'Technical Support', 'Features & Usage']

export default function FAQ() {
  const queryClient = useQueryClient()
  const [openFAQ, setOpenFAQ] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingFAQ, setEditingFAQ] = useState<FAQ | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    category: '',
  })

  // Fetch FAQs
  const { data: faqs, isLoading, error } = useQuery({
    queryKey: ['faqs', categoryFilter],
    queryFn: () =>
      faqAPI.getAll({
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
      }),
  })

  // Create FAQ mutation
  const createMutation = useMutation({
    mutationFn: faqAPI.create,
    onSuccess: () => {
      toast.success('FAQ created successfully')
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
      setShowCreateModal(false)
      resetForm()
    },
    onError: () => {
      toast.error('Failed to create FAQ')
    },
  })

  // Update FAQ mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<FAQ> }) =>
      faqAPI.update(id, data),
    onSuccess: () => {
      toast.success('FAQ updated successfully')
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
      setEditingFAQ(null)
      resetForm()
      setShowCreateModal(false)
    },
    onError: () => {
      toast.error('Failed to update FAQ')
    },
  })

  // Delete FAQ mutation
  const deleteMutation = useMutation({
    mutationFn: faqAPI.delete,
    onSuccess: () => {
      toast.success('FAQ deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
    },
    onError: () => {
      toast.error('Failed to delete FAQ')
    },
  })

  // Mark helpful mutation
  const markHelpfulMutation = useMutation({
    mutationFn: faqAPI.markHelpful,
    onSuccess: () => {
      toast.success('Thank you for your feedback!')
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
    },
  })

  const resetForm = () => {
    setFormData({
      question: '',
      answer: '',
      category: '',
    })
  }

  const toggleFAQ = (id: number) => {
    setOpenFAQ(openFAQ === id ? null : id)
  }

  const handleEdit = (faq: FAQ) => {
    setEditingFAQ(faq)
    setFormData({
      question: faq.question,
      answer: faq.answer,
      category: faq.category,
    })
    setShowCreateModal(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.question || !formData.answer || !formData.category) {
      toast.error('Please fill all required fields')
      return
    }

    if (editingFAQ) {
      updateMutation.mutate({ id: editingFAQ.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this FAQ?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleMarkHelpful = (id: number) => {
    markHelpfulMutation.mutate(id)
  }

  // Filter FAQs
  const filteredFAQs = faqs?.filter((faq: FAQ) =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  // Get popular FAQs (top 5 by views)
  const popularFAQs = [...(faqs || [])]
    .sort((a: FAQ, b: FAQ) => b.views - a.views)
    .slice(0, 5)

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
        Error loading FAQs: {(error as Error).message}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Frequently Asked Questions</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add FAQ
        </Button>
      </div>

      {/* Popular FAQs */}
      {popularFAQs.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Popular Questions</h3>
            <div className="space-y-2">
              {popularFAQs.map((faq: FAQ) => (
                <button
                  key={faq.id}
                  onClick={() => toggleFAQ(faq.id)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-blue-600">{faq.question}</span>
                    <Badge variant="outline" size="sm">
                      {faq.views} views
                    </Badge>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <Input
                placeholder="Search FAQs..."
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
          </div>
        </CardContent>
      </Card>

      {/* FAQs List */}
      <Card>
        <CardContent className="pt-6">
          {filteredFAQs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No FAQs found</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Add your first FAQ
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredFAQs.map((faq: FAQ) => (
                <div key={faq.id} className="border-b last:border-b-0">
                  <button
                    onClick={() => toggleFAQ(faq.id)}
                    className="w-full py-4 px-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <span className="font-semibold">{faq.question}</span>
                      <Badge variant="outline" size="sm">{faq.category}</Badge>
                    </div>
                    {openFAQ === faq.id ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </button>
                  {openFAQ === faq.id && (
                    <div className="px-4 pb-4 space-y-4">
                      <p className="text-gray-600">{faq.answer}</p>

                      {/* Helpful buttons */}
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-500">Was this helpful?</span>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleMarkHelpful(faq.id)}
                            className="flex items-center gap-1"
                          >
                            <ThumbsUp className="w-4 h-4" />
                            <span>{faq.helpful_count}</span>
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex items-center gap-1"
                          >
                            <ThumbsDown className="w-4 h-4" />
                            <span>{faq.not_helpful_count}</span>
                          </Button>
                        </div>

                        {/* Admin controls */}
                        <div className="ml-auto flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(faq)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(faq.id)}
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit FAQ Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setEditingFAQ(null)
          resetForm()
        }}
        title={editingFAQ ? 'Edit FAQ' : 'Add FAQ'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Question <span className="text-red-500">*</span>
            </label>
            <Input
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              placeholder="Enter question"
              required
            />
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
              Answer <span className="text-red-500">*</span>
            </label>
            <textarea
              className="w-full border rounded-md p-2 min-h-[150px]"
              value={formData.answer}
              onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
              placeholder="Enter answer"
              required
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowCreateModal(false)
                setEditingFAQ(null)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editingFAQ ? 'Update FAQ' : 'Create FAQ'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
