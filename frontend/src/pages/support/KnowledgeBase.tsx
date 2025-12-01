import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { knowledgeBaseAPI } from '@/lib/api'
import { Plus, Search, Eye, Edit, Trash, Tag, Star } from 'lucide-react'
import toast from 'react-hot-toast'

interface Article {
  id: number
  title: string
  content: string
  category: string
  tags: string[]
  author: string
  views: number
  rating: number
  created_at: string
  updated_at: string
}

const categories = ['Getting Started', 'Features', 'Troubleshooting', 'Best Practices', 'FAQs']

export default function KnowledgeBase() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [tagFilter, setTagFilter] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingArticle, setEditingArticle] = useState<Article | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    tags: '',
  })

  // Fetch articles
  const { data: articles, isLoading, error } = useQuery({
    queryKey: ['knowledge-base', categoryFilter],
    queryFn: () =>
      knowledgeBaseAPI.getAll({
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
      }),
  })

  // Fetch all tags
  const { data: allTags } = useQuery({
    queryKey: ['knowledge-base-tags'],
    queryFn: knowledgeBaseAPI.getTags,
  })

  // Create article mutation
  const createMutation = useMutation({
    mutationFn: knowledgeBaseAPI.create,
    onSuccess: () => {
      toast.success('Article created successfully')
      queryClient.invalidateQueries({ queryKey: ['knowledge-base'] })
      setShowCreateModal(false)
      resetForm()
    },
    onError: () => {
      toast.error('Failed to create article')
    },
  })

  // Update article mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Article> }) =>
      knowledgeBaseAPI.update(id, data),
    onSuccess: () => {
      toast.success('Article updated successfully')
      queryClient.invalidateQueries({ queryKey: ['knowledge-base'] })
      setEditingArticle(null)
      resetForm()
      setShowCreateModal(false)
    },
    onError: () => {
      toast.error('Failed to update article')
    },
  })

  // Delete article mutation
  const deleteMutation = useMutation({
    mutationFn: knowledgeBaseAPI.delete,
    onSuccess: () => {
      toast.success('Article deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['knowledge-base'] })
    },
    onError: () => {
      toast.error('Failed to delete article')
    },
  })

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      category: '',
      tags: '',
    })
  }

  const handleEdit = (article: Article) => {
    setEditingArticle(article)
    setFormData({
      title: article.title,
      content: article.content,
      category: article.category,
      tags: article.tags.join(', '),
    })
    setShowCreateModal(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.content || !formData.category) {
      toast.error('Please fill all required fields')
      return
    }

    const dataToSend = {
      ...formData,
      tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
    }

    if (editingArticle) {
      updateMutation.mutate({ id: editingArticle.id, data: dataToSend })
    } else {
      createMutation.mutate(dataToSend)
    }
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this article?')) {
      deleteMutation.mutate(id)
    }
  }

  // Filter articles
  const filteredArticles = articles?.filter((article: Article) => {
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTag = !tagFilter || article.tags.includes(tagFilter)
    return matchesSearch && matchesTag
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
        Error loading knowledge base: {(error as Error).message}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Article
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <Input
                placeholder="Search articles..."
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
              <label className="block text-sm font-medium mb-2">Tag</label>
              <Select
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Tags' },
                  ...(allTags || []).map((tag: string) => ({ value: tag, label: tag })),
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="pt-6 text-center py-12">
              <p className="text-gray-500">No articles found</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Add your first article
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredArticles.map((article: Article) => (
            <Card key={article.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div>
                    <Badge variant="default" className="mb-2">{article.category}</Badge>
                    <h3 className="font-semibold text-lg mb-2">{article.title}</h3>
                    <p className="text-sm text-gray-600 line-clamp-3">
                      {article.content.substring(0, 150)}...
                    </p>
                  </div>

                  {article.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {article.tags.map(tag => (
                        <Badge key={tag} variant="outline" size="sm">
                          <Tag className="w-3 h-3 mr-1" />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        <span>{article.views}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-500" />
                        <span>{article.rating.toFixed(1)}</span>
                      </div>
                    </div>
                    <span>{new Date(article.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleEdit(article)}
                    >
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(article.id)}
                    >
                      <Trash className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Create/Edit Article Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setEditingArticle(null)
          resetForm()
        }}
        title={editingArticle ? 'Edit Article' : 'Add Article'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Article title"
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
              Content <span className="text-red-500">*</span>
            </label>
            <textarea
              className="w-full border rounded-md p-2 min-h-[200px]"
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="Article content (supports markdown)"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Tags <span className="text-gray-500 text-xs">(comma-separated)</span>
            </label>
            <Input
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="e.g. setup, api, integration"
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowCreateModal(false)
                setEditingArticle(null)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editingArticle ? 'Update Article' : 'Create Article'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
