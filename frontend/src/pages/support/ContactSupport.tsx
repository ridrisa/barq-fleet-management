import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { contactSupportAPI } from '@/lib/api'
import { Send, Paperclip, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ContactSupport() {
  const [submitted, setSubmitted] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: '',
    priority: 'medium',
    message: '',
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const submitMutation = useMutation({
    mutationFn: contactSupportAPI.submit,
    onSuccess: () => {
      toast.success('Support request submitted successfully')
      setSubmitted(true)
      setTimeout(() => {
        resetForm()
        setSubmitted(false)
      }, 5000)
    },
    onError: () => {
      toast.error('Failed to submit support request')
    },
  })

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      subject: '',
      category: '',
      priority: 'medium',
      message: '',
    })
    setSelectedFile(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
      toast.error('Please fill all required fields')
      return
    }
    submitMutation.mutate(formData)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
            <h2 className="text-2xl font-bold mb-2">Request Submitted Successfully!</h2>
            <p className="text-gray-600 mb-6">
              Thank you for contacting us. We'll get back to you within 24 hours.
            </p>
            <p className="text-sm text-gray-500">
              You'll receive a confirmation email shortly with your ticket number.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Contact Support</h1>
        <p className="text-gray-600">
          Have a question or need help? Fill out the form below and our support team will get back
          to you as soon as possible.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Contact Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Your Name <span className="text-red-500">*</span>
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="John Doe"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>

            {/* Subject */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Subject <span className="text-red-500">*</span>
              </label>
              <Input
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="Brief description of your issue"
                required
              />
            </div>

            {/* Category and Priority */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  options={[
                    { value: '', label: 'Select Category' },
                    { value: 'technical', label: 'Technical Issue' },
                    { value: 'billing', label: 'Billing Question' },
                    { value: 'feature', label: 'Feature Request' },
                    { value: 'bug', label: 'Bug Report' },
                    { value: 'general', label: 'General Inquiry' },
                    { value: 'other', label: 'Other' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Priority</label>
                <Select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  options={[
                    { value: 'low', label: 'Low' },
                    { value: 'medium', label: 'Medium' },
                    { value: 'high', label: 'High' },
                    { value: 'urgent', label: 'Urgent' },
                  ]}
                />
              </div>
            </div>

            {/* Message */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Message <span className="text-red-500">*</span>
              </label>
              <textarea
                className="w-full border rounded-md p-3 min-h-[200px]"
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                placeholder="Please provide as much detail as possible..."
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Minimum 50 characters ({formData.message.length}/50)
              </p>
            </div>

            {/* File Attachment */}
            <div>
              <label className="block text-sm font-medium mb-2">Attachment (Optional)</label>
              <div className="flex items-center gap-3">
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  accept=".jpg,.jpeg,.png,.pdf,.doc,.docx"
                />
                <label htmlFor="file-upload">
                  <Button type="button" variant="outline" as="span">
                    <Paperclip className="w-4 h-4 mr-2" />
                    Choose File
                  </Button>
                </label>
                {selectedFile && (
                  <span className="text-sm text-gray-600">
                    {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Max file size: 10MB. Supported: JPG, PNG, PDF, DOC, DOCX
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 justify-end border-t pt-6">
              <Button type="button" variant="outline" onClick={resetForm}>
                Reset Form
              </Button>
              <Button
                type="submit"
                disabled={submitMutation.isPending || formData.message.length < 50}
              >
                <Send className="w-4 h-4 mr-2" />
                {submitMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Help Information */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="font-semibold mb-3">Other Ways to Get Help</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="border-l-2 border-blue-500 pl-3">
              <h4 className="font-medium mb-1">Knowledge Base</h4>
              <p className="text-gray-600">Find answers in our comprehensive documentation</p>
            </div>
            <div className="border-l-2 border-green-500 pl-3">
              <h4 className="font-medium mb-1">Live Chat</h4>
              <p className="text-gray-600">Chat with our support team in real-time</p>
            </div>
            <div className="border-l-2 border-purple-500 pl-3">
              <h4 className="font-medium mb-1">Email Us</h4>
              <p className="text-gray-600">support@sync-fleet.com</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
