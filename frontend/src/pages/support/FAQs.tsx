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
import { Plus, Search, ThumbsUp, ChevronDown, ChevronUp, Edit, Trash } from 'lucide-react'
import toast from 'react-hot-toast'

interface FAQ {
  id: number
  category: string
  question: string
  answer: string
  views: number
  helpful_count: number
  created_at: string
  updated_at: string
}

const categories = ['General', 'Fleet', 'HR', 'Operations', 'Technical']

export default function FAQs() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingFaq, setEditingFaq] = useState<FAQ | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    category: '',
    question: '',
    answer: '',
  })

  // Fetch FAQs
  const { data: faqs, isLoading, error } = useQuery({
    queryKey: ['faqs', categoryFilter],
    queryFn: () => faqAPI.getAll({ category: categoryFilter !== 'all' ? categoryFilter : undefined }),
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
    mutationFn: ({ id, data }: { id: number; data: Partial<FAQ> }) => faqAPI.update(id, data),
    onSuccess: () => {
      toast.success('FAQ updated successfully')
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
      setEditingFaq(null)
      resetForm()
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

  // Mark as helpful mutation
  const markHelpfulMutation = useMutation({
    mutationFn: (id: number) => faqAPI.markHelpful(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['faqs'] })
      toast.success('Thank you for your feedback!')
    },
  })

  const resetForm = () => {
    setFormData({
      category: '',
      question: '',
      answer: '',
    })
  }

  const handleEdit = (faq: FAQ) => {
    setEditingFaq(faq)
    setFormData({
      category: faq.category,
      question: faq.question,
      answer: faq.answer,
    })
    setShowCreateModal(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.category || !formData.question || !formData.answer) {
      toast.error('Please fill all required fields')
      return
    }

    if (editingFaq) {
      updateMutation.mutate({ id: editingFaq.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this FAQ?')) {
      deleteMutation.mutate(id)
    }
  }

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id)
  }

  // Filter FAQs based on search query
  const filteredFaqs = faqs?.filter((faq: FAQ) => {
    const matchesSearch =
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  }) || []

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

      {/* FAQ List */}
      <div className="space-y-4">
        {filteredFaqs.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center py-12">
              <p className="text-gray-500">No FAQs found</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Add your first FAQ
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredFaqs.map((faq: FAQ) => (
            <Card key={faq.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="default">{faq.category}</Badge>
                        <span className="text-sm text-gray-500">{faq.views} views</span>
                      </div>
                      <button
                        onClick={() => toggleExpand(faq.id)}
                        className="flex items-start justify-between w-full text-left"
                      >
                        <h3 className="text-lg font-semibold pr-4">{faq.question}</h3>
                        {expandedId === faq.id ? (
                          <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        )}
                      </button>
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(faq)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(faq.id)}
                      >
                        <Trash className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {expandedId === faq.id && (
                    <div className="space-y-4 pt-4 border-t">
                      <p className="text-gray-700 whitespace-pre-wrap">{faq.answer}</p>
                      <div className="flex items-center gap-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => markHelpfulMutation.mutate(faq.id)}
                          disabled={markHelpfulMutation.isPending}
                        >
                          <ThumbsUp className="w-4 h-4 mr-2" />
                          Helpful ({faq.helpful_count})
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Create/Edit FAQ Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setEditingFaq(null)
          resetForm()
        }}
        title={editingFaq ? 'Edit FAQ' : 'Add FAQ'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
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
              Question <span className="text-red-500">*</span>
            </label>
            <Input
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              placeholder="What is your question?"
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
              placeholder="Provide a detailed answer"
              required
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowCreateModal(false)
                setEditingFaq(null)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editingFaq ? 'Update FAQ' : 'Create FAQ'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
