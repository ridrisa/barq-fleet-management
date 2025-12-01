import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiKeysAPI } from '@/lib/adminAPI'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

interface APIKey {
  id: number
  name: string
  key_prefix: string
  description?: string
  rate_limit: number
  is_active: boolean
  last_used?: string
  created_at: string
  created_by: string
}

export default function APIKeys() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showKeyModal, setShowKeyModal] = useState(false)
  const [newAPIKey, setNewAPIKey] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rate_limit: 1000,
  })

  const queryClient = useQueryClient()

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeysAPI.getAll(),
  })

  const createMutation = useMutation({
    mutationFn: (data: typeof formData) => apiKeysAPI.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setShowCreateModal(false)
      setNewAPIKey(data.api_key)
      setShowKeyModal(true)
      setFormData({ name: '', description: '', rate_limit: 1000 })
    },
    onError: () => {
      alert('Failed to create API key')
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (id: number) => apiKeysAPI.revoke(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      alert('API key revoked successfully')
    },
    onError: () => {
      alert('Failed to revoke API key')
    },
  })

  const updateRateLimitMutation = useMutation({
    mutationFn: ({ id, rateLimit }: { id: number; rateLimit: number }) =>
      apiKeysAPI.updateRateLimit(id, rateLimit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      alert('Rate limit updated successfully')
    },
    onError: () => {
      alert('Failed to update rate limit')
    },
  })

  const handleRevoke = (apiKey: APIKey) => {
    if (confirm(`Revoke API key "${apiKey.name}"? This action cannot be undone.`)) {
      revokeMutation.mutate(apiKey.id)
    }
  }

  const handleUpdateRateLimit = (apiKey: APIKey) => {
    const newLimit = prompt(`Enter new rate limit for "${apiKey.name}":`, apiKey.rate_limit.toString())
    if (newLimit) {
      const limit = parseInt(newLimit)
      if (!isNaN(limit) && limit > 0) {
        updateRateLimitMutation.mutate({ id: apiKey.id, rateLimit: limit })
      } else {
        alert('Invalid rate limit')
      }
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard')
  }

  const maskKey = (keyPrefix: string) => {
    return `${keyPrefix}...************************`
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading API keys...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">API Keys Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Generate and manage API keys for system integrations. Monitor usage and configure rate limits.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <Button
            onClick={() => setShowCreateModal(true)}
            className="bg-primary-600 text-white hover:bg-primary-500"
          >
            Generate New API Key
          </Button>
        </div>
      </div>

      {/* API Keys List */}
      <div className="mt-8 space-y-4">
        {apiKeys && apiKeys.length > 0 ? (
          apiKeys.map((apiKey: APIKey) => (
            <Card key={apiKey.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-semibold text-gray-900">{apiKey.name}</h3>
                      <Badge variant={apiKey.is_active ? 'success' : 'error'}>
                        {apiKey.is_active ? 'Active' : 'Revoked'}
                      </Badge>
                    </div>
                    {apiKey.description && (
                      <p className="text-sm text-gray-600 mt-1">{apiKey.description}</p>
                    )}
                    <div className="mt-4 bg-gray-50 rounded-md p-3 font-mono text-sm">
                      {maskKey(apiKey.key_prefix)}
                    </div>
                    <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Rate Limit:</span>
                        <span className="ml-2 text-gray-900">{apiKey.rate_limit} req/hour</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Created:</span>
                        <span className="ml-2 text-gray-900">
                          {new Date(apiKey.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Last Used:</span>
                        <span className="ml-2 text-gray-900">
                          {apiKey.last_used ? new Date(apiKey.last_used).toLocaleString() : 'Never'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex flex-col space-y-2">
                    <Button
                      onClick={() => handleUpdateRateLimit(apiKey)}
                      variant="outline"
                      size="sm"
                      disabled={!apiKey.is_active}
                    >
                      Update Limit
                    </Button>
                    <Button
                      onClick={() => handleRevoke(apiKey)}
                      className="bg-red-600 text-white hover:bg-red-500"
                      size="sm"
                      disabled={!apiKey.is_active}
                    >
                      Revoke
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="pt-6">
              <p className="text-gray-500 text-center py-8">
                No API keys created yet. Generate your first API key to get started.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Create API Key Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setFormData({ name: '', description: '', rate_limit: 1000 })
        }}
        title="Generate New API Key"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault()
            createMutation.mutate(formData)
          }}
          className="mt-4 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Key Name
            </label>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              placeholder="e.g., Mobile App Integration"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <Input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the integration"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rate Limit (requests per hour)
            </label>
            <Input
              type="number"
              min="1"
              value={formData.rate_limit}
              onChange={(e) => setFormData({ ...formData, rate_limit: parseInt(e.target.value) })}
              required
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              onClick={() => setShowCreateModal(false)}
              variant="outline"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="bg-primary-600 text-white hover:bg-primary-500"
            >
              Generate Key
            </Button>
          </div>
        </form>
      </Modal>

      {/* Show New API Key Modal */}
      <Modal
        isOpen={showKeyModal}
        onClose={() => {
          setShowKeyModal(false)
          setNewAPIKey(null)
        }}
        title="API Key Generated"
      >
        <div className="mt-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
            <h4 className="text-sm font-semibold text-yellow-900">IMPORTANT</h4>
            <p className="mt-2 text-sm text-yellow-800">
              This is the only time you will see this API key. Please copy it now and store it securely.
            </p>
          </div>

          <div className="bg-gray-50 rounded-md p-4 font-mono text-sm break-all">
            {newAPIKey}
          </div>

          <div className="mt-4 flex justify-end space-x-3">
            <Button
              onClick={() => {
                if (newAPIKey) copyToClipboard(newAPIKey)
              }}
              className="bg-primary-600 text-white hover:bg-primary-500"
            >
              Copy to Clipboard
            </Button>
            <Button
              onClick={() => {
                setShowKeyModal(false)
                setNewAPIKey(null)
              }}
              variant="outline"
            >
              Done
            </Button>
          </div>
        </div>
      </Modal>

      {/* Security Information */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Security Best Practices</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Never share API keys in public repositories</li>
              <li>Rotate API keys regularly (recommended: every 90 days)</li>
              <li>Use separate API keys for different integrations</li>
              <li>Revoke compromised keys immediately</li>
              <li>Monitor API key usage for unusual activity</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">API Key Format</h3>
            <p className="text-sm text-gray-700 mb-2">
              API keys follow the format: <code className="bg-gray-100 px-1">sk-[32 characters]</code>
            </p>
            <p className="text-sm text-gray-700 mb-2">
              Include the key in your requests using the Authorization header:
            </p>
            <div className="bg-gray-50 rounded-md p-2 font-mono text-xs">
              Authorization: Bearer your-api-key
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
