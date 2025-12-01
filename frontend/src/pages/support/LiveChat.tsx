import { useState, useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Send, Paperclip, X, MessageCircle, Users } from 'lucide-react'
import toast from 'react-hot-toast'

interface Message {
  id: number
  sender: string
  content: string
  timestamp: Date
  isAgent: boolean
}

interface Agent {
  id: number
  name: string
  status: 'online' | 'busy' | 'offline'
}

export default function LiveChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: 'Support Agent',
      content: 'Hello! How can I help you today?',
      timestamp: new Date(),
      isAgent: true,
    },
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isChatActive, setIsChatActive] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Mock online agents
  const [onlineAgents] = useState<Agent[]>([
    { id: 1, name: 'Sarah Johnson', status: 'online' },
    { id: 2, name: 'Mike Chen', status: 'online' },
    { id: 3, name: 'Emily Davis', status: 'busy' },
  ])

  // KPI Stats
  const stats = {
    activeChats: 12,
    avgResponseTime: '2.5 min',
    agentsOnline: onlineAgents.filter(a => a.status === 'online').length,
    resolvedToday: 45,
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim()) return

    // Add user message
    const newMessage: Message = {
      id: messages.length + 1,
      sender: 'You',
      content: inputMessage,
      timestamp: new Date(),
      isAgent: false,
    }

    setMessages([...messages, newMessage])
    setInputMessage('')

    // Simulate agent typing
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      // Simulate agent response
      const agentResponse: Message = {
        id: messages.length + 2,
        sender: 'Support Agent',
        content: 'Thank you for your message. Let me help you with that.',
        timestamp: new Date(),
        isAgent: true,
      }
      setMessages(prev => [...prev, agentResponse])
    }, 2000)
  }

  const handleEndChat = () => {
    if (window.confirm('Are you sure you want to end this chat?')) {
      setIsChatActive(false)
      toast.success('Chat ended. Thank you!')
    }
  }

  const handleFileAttach = () => {
    toast('File attachment feature coming soon')
  }

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'busy':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Live Chat Support</h1>
        <Badge variant={isChatActive ? 'success' : 'default'}>
          {isChatActive ? 'Active' : 'Inactive'}
        </Badge>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <MessageCircle className="w-8 h-8 mx-auto mb-2 text-blue-600" />
              <p className="text-2xl font-bold text-gray-900">{stats.activeChats}</p>
              <p className="text-sm text-gray-600">Active Chats</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-2 text-green-600" />
              <p className="text-2xl font-bold text-gray-900">{stats.agentsOnline}</p>
              <p className="text-sm text-gray-600">Agents Online</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{stats.avgResponseTime}</p>
              <p className="text-sm text-gray-600">Avg Response Time</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">{stats.resolvedToday}</p>
              <p className="text-sm text-gray-600">Resolved Today</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Online Agents Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Users className="w-5 h-5" />
                Support Agents
              </h3>
              <div className="space-y-3">
                {onlineAgents.map(agent => (
                  <div key={agent.id} className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {agent.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <span
                        className={`absolute bottom-0 right-0 w-3 h-3 ${getStatusColor(agent.status)} rounded-full border-2 border-white`}
                      />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{agent.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{agent.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col h-[600px]">
                {/* Chat Header */}
                <div className="flex items-center justify-between pb-4 border-b">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <MessageCircle className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Support Chat</h3>
                      <p className="text-xs text-gray-500">
                        {onlineAgents.filter(a => a.status === 'online').length} agents available
                      </p>
                    </div>
                  </div>
                  {isChatActive && (
                    <Button size="sm" variant="outline" onClick={handleEndChat}>
                      <X className="w-4 h-4 mr-2" />
                      End Chat
                    </Button>
                  )}
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto py-4 space-y-4">
                  {!isChatActive && (
                    <div className="text-center py-12">
                      <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                      <p className="text-gray-500 mb-4">
                        Start a new conversation with our support team
                      </p>
                      <Button onClick={() => setIsChatActive(true)}>
                        Start New Chat
                      </Button>
                    </div>
                  )}

                  {isChatActive && messages.map(message => (
                    <div
                      key={message.id}
                      className={`flex ${message.isAgent ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg px-4 py-2 ${
                          message.isAgent
                            ? 'bg-gray-100 text-gray-900'
                            : 'bg-blue-600 text-white'
                        }`}
                      >
                        <p className="text-xs font-semibold mb-1">
                          {message.sender}
                        </p>
                        <p className="text-sm">{message.content}</p>
                        <p
                          className={`text-xs mt-1 ${
                            message.isAgent ? 'text-gray-500' : 'text-blue-100'
                          }`}
                        >
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg px-4 py-2">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75" />
                          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Chat Input */}
                {isChatActive && (
                  <div className="border-t pt-4">
                    <form onSubmit={handleSendMessage} className="flex gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleFileAttach}
                      >
                        <Paperclip className="w-4 h-4" />
                      </Button>
                      <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1"
                      />
                      <Button type="submit" disabled={!inputMessage.trim()}>
                        <Send className="w-4 h-4 mr-2" />
                        Send
                      </Button>
                    </form>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Chat History Note */}
          <Card className="mt-4">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <MessageCircle className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-semibold mb-2">Chat History</h4>
                  <p className="text-sm text-gray-600">
                    Your chat history is saved automatically. You can access previous conversations
                    from your support ticket dashboard.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
