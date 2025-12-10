import { useState } from 'react'
import {
  Car, FileText, DollarSign, Package, Clock,
  Wallet, ClipboardList, CheckCircle, Truck, Gift, CreditCard,
  Building, Radio, History, ChevronDown, ChevronRight
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

// Layout Option 1: Grouped Sections with Sub-tabs
const GroupedSectionsLayout = () => {
  const [activeGroup, setActiveGroup] = useState('tracking')
  const [activeSubTab, setActiveSubTab] = useState('live-location')

  const groups = [
    {
      id: 'tracking',
      label: 'Tracking & Vehicle',
      icon: <Car className="h-4 w-4" />,
      tabs: [
        { id: 'live-location', label: 'Live Location', icon: <Radio className="h-4 w-4" /> },
        { id: 'vehicle', label: 'Vehicle', icon: <Car className="h-4 w-4" /> },
        { id: 'vehicle-history', label: 'History', icon: <History className="h-4 w-4" /> },
        { id: 'logs', label: 'Logs', icon: <ClipboardList className="h-4 w-4" /> },
      ]
    },
    {
      id: 'hr',
      label: 'HR & Finance',
      icon: <DollarSign className="h-4 w-4" />,
      tabs: [
        { id: 'salaries', label: 'Salaries', icon: <Wallet className="h-4 w-4" /> },
        { id: 'loans', label: 'Loans', icon: <DollarSign className="h-4 w-4" /> },
        { id: 'bonuses', label: 'Bonuses', icon: <Gift className="h-4 w-4" /> },
        { id: 'leaves', label: 'Leaves', icon: <Clock className="h-4 w-4" /> },
        { id: 'attendance', label: 'Attendance', icon: <CheckCircle className="h-4 w-4" /> },
      ]
    },
    {
      id: 'operations',
      label: 'Operations',
      icon: <Truck className="h-4 w-4" />,
      tabs: [
        { id: 'deliveries', label: 'Deliveries', icon: <Truck className="h-4 w-4" /> },
        { id: 'assets', label: 'Assets', icon: <Package className="h-4 w-4" /> },
      ]
    },
    {
      id: 'info',
      label: 'Info & Documents',
      icon: <FileText className="h-4 w-4" />,
      tabs: [
        { id: 'documents', label: 'Documents', icon: <FileText className="h-4 w-4" /> },
        { id: 'banking', label: 'Banking', icon: <CreditCard className="h-4 w-4" /> },
        { id: 'accommodation', label: 'Accommodation', icon: <Building className="h-4 w-4" /> },
      ]
    },
  ]

  const currentGroup = groups.find(g => g.id === activeGroup)

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-blue-600">Option 1: Grouped Sections</h3>
      <p className="text-sm text-gray-500">Main category tabs on top, sub-tabs below</p>

      {/* Main Group Tabs */}
      <div className="flex gap-2 border-b pb-2">
        {groups.map(group => (
          <button
            key={group.id}
            onClick={() => {
              setActiveGroup(group.id)
              setActiveSubTab(group.tabs[0].id)
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors ${
              activeGroup === group.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {group.icon}
            {group.label}
          </button>
        ))}
      </div>

      {/* Sub Tabs */}
      <div className="flex gap-1 bg-gray-50 p-1 rounded-lg">
        {currentGroup?.tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors ${
              activeSubTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <Card>
        <CardContent className="p-6">
          <div className="h-32 flex items-center justify-center text-gray-400">
            Content for "{activeSubTab}" goes here
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Layout Option 2: Sidebar + Content
const SidebarLayout = () => {
  const [activeSection, setActiveSection] = useState('live-location')

  const sections = [
    {
      category: 'Tracking & Vehicle',
      items: [
        { id: 'live-location', label: 'Live Location', icon: <Radio className="h-4 w-4" /> },
        { id: 'vehicle', label: 'Current Vehicle', icon: <Car className="h-4 w-4" /> },
        { id: 'vehicle-history', label: 'Vehicle History', icon: <History className="h-4 w-4" /> },
        { id: 'logs', label: 'Vehicle Logs', icon: <ClipboardList className="h-4 w-4" /> },
      ]
    },
    {
      category: 'HR & Finance',
      items: [
        { id: 'salaries', label: 'Salaries', icon: <Wallet className="h-4 w-4" /> },
        { id: 'loans', label: 'Loans', icon: <DollarSign className="h-4 w-4" /> },
        { id: 'bonuses', label: 'Bonuses', icon: <Gift className="h-4 w-4" /> },
        { id: 'leaves', label: 'Leaves', icon: <Clock className="h-4 w-4" /> },
        { id: 'attendance', label: 'Attendance', icon: <CheckCircle className="h-4 w-4" /> },
      ]
    },
    {
      category: 'Operations',
      items: [
        { id: 'deliveries', label: 'Deliveries', icon: <Truck className="h-4 w-4" /> },
        { id: 'assets', label: 'Assets', icon: <Package className="h-4 w-4" /> },
      ]
    },
    {
      category: 'Documents & Info',
      items: [
        { id: 'documents', label: 'Documents', icon: <FileText className="h-4 w-4" /> },
        { id: 'banking', label: 'Banking', icon: <CreditCard className="h-4 w-4" /> },
        { id: 'accommodation', label: 'Accommodation', icon: <Building className="h-4 w-4" /> },
      ]
    },
  ]

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-green-600">Option 2: Sidebar + Content</h3>
      <p className="text-sm text-gray-500">Sidebar navigation on left, content on right</p>

      <div className="flex gap-4 border rounded-lg overflow-hidden">
        {/* Sidebar */}
        <div className="w-56 bg-gray-50 border-r p-3 space-y-4">
          {sections.map(section => (
            <div key={section.category}>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                {section.category}
              </p>
              <div className="space-y-1">
                {section.items.map(item => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded text-sm transition-colors ${
                      activeSection === item.id
                        ? 'bg-green-600 text-white'
                        : 'text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {item.icon}
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 p-6">
          <div className="h-48 flex items-center justify-center text-gray-400">
            Content for "{activeSection}" goes here
          </div>
        </div>
      </div>
    </div>
  )
}

// Layout Option 3: Accordion Layout
const AccordionLayout = () => {
  const [expanded, setExpanded] = useState<string[]>(['tracking'])

  const sections = [
    {
      id: 'tracking',
      label: 'Tracking & Vehicle',
      icon: <Car className="h-5 w-5" />,
      items: ['Live Location', 'Current Vehicle', 'Vehicle History', 'Vehicle Logs']
    },
    {
      id: 'hr',
      label: 'HR & Finance',
      icon: <DollarSign className="h-5 w-5" />,
      items: ['Salaries', 'Loans', 'Bonuses', 'Leaves', 'Attendance']
    },
    {
      id: 'operations',
      label: 'Operations',
      icon: <Truck className="h-5 w-5" />,
      items: ['Deliveries', 'Assets']
    },
    {
      id: 'info',
      label: 'Documents & Info',
      icon: <FileText className="h-5 w-5" />,
      items: ['Documents', 'Banking', 'Accommodation']
    },
  ]

  const toggleSection = (id: string) => {
    setExpanded(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-purple-600">Option 3: Accordion Layout</h3>
      <p className="text-sm text-gray-500">Collapsible sections, expand multiple at once</p>

      <div className="space-y-2">
        {sections.map(section => (
          <div key={section.id} className="border rounded-lg overflow-hidden">
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
                  {section.icon}
                </div>
                <span className="font-medium">{section.label}</span>
                <Badge variant="secondary" className="text-xs">
                  {section.items.length}
                </Badge>
              </div>
              {expanded.includes(section.id) ? (
                <ChevronDown className="h-5 w-5 text-gray-400" />
              ) : (
                <ChevronRight className="h-5 w-5 text-gray-400" />
              )}
            </button>
            {expanded.includes(section.id) && (
              <div className="p-4 bg-white border-t">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {section.items.map(item => (
                    <button
                      key={item}
                      className="p-3 text-left border rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors"
                    >
                      <span className="text-sm font-medium">{item}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Layout Option 4: Card Grid Dashboard
const CardGridLayout = () => {
  const [selectedCard, setSelectedCard] = useState<string | null>(null)

  const cards = [
    {
      id: 'tracking',
      label: 'Live Tracking',
      icon: <Radio className="h-6 w-6" />,
      color: 'bg-green-500',
      stats: 'Online • 45 km/h',
      items: ['GPS Location', 'Speed', 'Route History']
    },
    {
      id: 'vehicle',
      label: 'Vehicle',
      icon: <Car className="h-6 w-6" />,
      color: 'bg-blue-500',
      stats: 'Toyota Hilux • ABC-1234',
      items: ['Details', 'History', 'Logs', 'Maintenance']
    },
    {
      id: 'finance',
      label: 'Finance',
      icon: <Wallet className="h-6 w-6" />,
      color: 'bg-orange-500',
      stats: 'SAR 4,500 net salary',
      items: ['Salary', 'Loans', 'Bonuses', 'Deductions']
    },
    {
      id: 'hr',
      label: 'HR Records',
      icon: <Clock className="h-6 w-6" />,
      color: 'bg-purple-500',
      stats: '2 pending leaves',
      items: ['Leaves', 'Attendance', 'Documents']
    },
    {
      id: 'deliveries',
      label: 'Deliveries',
      icon: <Truck className="h-6 w-6" />,
      color: 'bg-red-500',
      stats: '156 completed',
      items: ['History', 'Performance', 'Rating']
    },
    {
      id: 'assets',
      label: 'Assets & Info',
      icon: <Package className="h-6 w-6" />,
      color: 'bg-teal-500',
      stats: '3 items assigned',
      items: ['Assets', 'Banking', 'Accommodation']
    },
  ]

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-teal-600">Option 4: Card Grid Dashboard</h3>
      <p className="text-sm text-gray-500">Summary cards with quick stats, click to expand</p>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map(card => (
          <div
            key={card.id}
            onClick={() => setSelectedCard(selectedCard === card.id ? null : card.id)}
            className={`cursor-pointer border rounded-xl overflow-hidden transition-all ${
              selectedCard === card.id ? 'ring-2 ring-teal-500' : 'hover:shadow-md'
            }`}
          >
            <div className={`${card.color} p-4 text-white`}>
              <div className="flex items-center justify-between">
                {card.icon}
                <ChevronRight className={`h-5 w-5 transition-transform ${
                  selectedCard === card.id ? 'rotate-90' : ''
                }`} />
              </div>
              <h4 className="font-semibold mt-2">{card.label}</h4>
              <p className="text-sm opacity-90">{card.stats}</p>
            </div>
            {selectedCard === card.id && (
              <div className="p-3 bg-gray-50">
                <div className="space-y-1">
                  {card.items.map(item => (
                    <button
                      key={item}
                      className="w-full text-left px-3 py-2 text-sm rounded hover:bg-white transition-colors"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Main Preview Component
export default function CourierProfileLayoutPreview() {
  return (
    <div className="p-6 space-y-12 max-w-5xl mx-auto">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Courier Profile Layout Options</h1>
        <p className="text-gray-500">Click through each option to see how it works</p>
      </div>

      <div className="space-y-12">
        <GroupedSectionsLayout />
        <hr />
        <SidebarLayout />
        <hr />
        <AccordionLayout />
        <hr />
        <CardGridLayout />
      </div>
    </div>
  )
}
