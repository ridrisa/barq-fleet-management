import { useState, ReactNode } from 'react'
import {
  ChevronDown,
  ChevronRight,
  Settings,
} from 'lucide-react'
// Card not used directly but kept for future expansion
import { Badge } from '@/components/ui/Badge'

// Types
export type LayoutType = 'grouped' | 'sidebar' | 'accordion' | 'cards'

export interface TabItem {
  id: string
  label: string
  icon: ReactNode
  content: ReactNode
  count?: number
}

export interface TabGroup {
  id: string
  label: string
  icon: ReactNode
  color: string
  stats?: string
  tabs: TabItem[]
}

interface LayoutProps {
  groups: TabGroup[]
  defaultTab?: string
}

// Layout Option 1: Grouped Sections with Sub-tabs
export const GroupedSectionsLayout = ({ groups, defaultTab }: LayoutProps) => {
  const [activeGroup, setActiveGroup] = useState(groups[0]?.id || '')
  const [activeTab, setActiveTab] = useState(defaultTab || groups[0]?.tabs[0]?.id || '')

  const currentGroup = groups.find(g => g.id === activeGroup)
  const currentTab = currentGroup?.tabs.find(t => t.id === activeTab)

  return (
    <div className="space-y-4">
      {/* Main Group Tabs */}
      <div className="flex flex-wrap gap-2 border-b pb-3">
        {groups.map(group => (
          <button
            key={group.id}
            onClick={() => {
              setActiveGroup(group.id)
              setActiveTab(group.tabs[0]?.id || '')
            }}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
              activeGroup === group.id
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {group.icon}
            <span className="hidden sm:inline">{group.label}</span>
          </button>
        ))}
      </div>

      {/* Sub Tabs */}
      {currentGroup && (
        <div className="flex flex-wrap gap-1 bg-gray-50 p-1.5 rounded-lg">
          {currentGroup.tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.count !== undefined && tab.count > 0 && (
                <Badge variant="secondary" className="ml-1 text-xs px-1.5 py-0">
                  {tab.count}
                </Badge>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Content Area */}
      <div className="mt-4">
        {currentTab?.content}
      </div>
    </div>
  )
}

// Layout Option 2: Sidebar + Content
export const SidebarLayout = ({ groups, defaultTab }: LayoutProps) => {
  const [activeTab, setActiveTab] = useState(defaultTab || groups[0]?.tabs[0]?.id || '')

  const currentTab = groups.flatMap(g => g.tabs).find(t => t.id === activeTab)

  return (
    <div className="flex gap-6">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0">
        <div className="sticky top-4 space-y-6 bg-gray-50 rounded-xl p-4">
          {groups.map(group => (
            <div key={group.id}>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">
                {group.label}
              </p>
              <div className="space-y-1">
                {group.tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'text-gray-600 hover:bg-white hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {tab.icon}
                      <span>{tab.label}</span>
                    </div>
                    {tab.count !== undefined && tab.count > 0 && (
                      <Badge
                        variant={activeTab === tab.id ? "default" : "secondary"}
                        className="text-xs px-1.5 py-0"
                      >
                        {tab.count}
                      </Badge>
                    )}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {currentTab?.content}
      </div>
    </div>
  )
}

// Layout Option 3: Accordion Layout
export const AccordionLayout = ({ groups, defaultTab }: LayoutProps) => {
  const [expanded, setExpanded] = useState<string[]>([groups[0]?.id || ''])
  const [activeTab, setActiveTab] = useState(defaultTab || groups[0]?.tabs[0]?.id || '')

  const toggleGroup = (id: string) => {
    setExpanded(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const currentTab = groups.flatMap(g => g.tabs).find(t => t.id === activeTab)

  return (
    <div className="space-y-3">
      {groups.map(group => {
        const isExpanded = expanded.includes(group.id)
        const groupTabCount = group.tabs.reduce((sum, t) => sum + (t.count || 0), 0)

        return (
          <div key={group.id} className="border rounded-xl overflow-hidden">
            <button
              onClick={() => toggleGroup(group.id)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${group.color}`}>
                  {group.icon}
                </div>
                <span className="font-semibold text-gray-800">{group.label}</span>
                {groupTabCount > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    {groupTabCount} items
                  </Badge>
                )}
              </div>
              {isExpanded ? (
                <ChevronDown className="h-5 w-5 text-gray-400" />
              ) : (
                <ChevronRight className="h-5 w-5 text-gray-400" />
              )}
            </button>

            {isExpanded && (
              <div className="border-t">
                {/* Tab buttons */}
                <div className="flex flex-wrap gap-2 p-3 bg-white border-b">
                  {group.tabs.map(tab => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        activeTab === tab.id
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {tab.icon}
                      <span>{tab.label}</span>
                      {tab.count !== undefined && tab.count > 0 && (
                        <Badge
                          variant={activeTab === tab.id ? "default" : "secondary"}
                          className="ml-1 text-xs px-1.5 py-0"
                        >
                          {tab.count}
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>

                {/* Content for active tab in this group */}
                {group.tabs.find(t => t.id === activeTab) && (
                  <div className="p-4 bg-white">
                    {currentTab?.content}
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// Layout Option 4: Card Grid Dashboard
export const CardGridLayout = ({ groups, defaultTab }: LayoutProps) => {
  const [activeTab, setActiveTab] = useState(defaultTab || '')
  const [expandedCard, setExpandedCard] = useState<string | null>(null)

  const currentTab = groups.flatMap(g => g.tabs).find(t => t.id === activeTab)

  return (
    <div className="space-y-6">
      {/* Card Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {groups.map(group => {
          const isExpanded = expandedCard === group.id
          const groupTabCount = group.tabs.reduce((sum, t) => sum + (t.count || 0), 0)

          return (
            <div
              key={group.id}
              className={`border rounded-xl overflow-hidden transition-all cursor-pointer ${
                isExpanded ? 'ring-2 ring-blue-500 col-span-1 sm:col-span-2 lg:col-span-3' : 'hover:shadow-lg'
              }`}
            >
              <div
                onClick={() => setExpandedCard(isExpanded ? null : group.id)}
                className={`p-4 text-white ${group.color}`}
              >
                <div className="flex items-center justify-between">
                  <div className="p-2 bg-white/20 rounded-lg">
                    {group.icon}
                  </div>
                  <ChevronRight className={`h-5 w-5 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
                </div>
                <h4 className="font-semibold mt-3 text-lg">{group.label}</h4>
                <p className="text-sm opacity-90 mt-1">
                  {group.stats || `${group.tabs.length} sections`}
                  {groupTabCount > 0 && ` • ${groupTabCount} items`}
                </p>
              </div>

              {isExpanded && (
                <div className="bg-white">
                  {/* Tab buttons */}
                  <div className="flex flex-wrap gap-2 p-3 border-b bg-gray-50">
                    {group.tabs.map(tab => (
                      <button
                        key={tab.id}
                        onClick={(e) => {
                          e.stopPropagation()
                          setActiveTab(tab.id)
                        }}
                        className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                          activeTab === tab.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-100 border'
                        }`}
                      >
                        {tab.icon}
                        <span>{tab.label}</span>
                        {tab.count !== undefined && tab.count > 0 && (
                          <Badge
                            variant={activeTab === tab.id ? "default" : "secondary"}
                            className="ml-1 text-xs px-1.5 py-0"
                          >
                            {tab.count}
                          </Badge>
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Content */}
                  {group.tabs.find(t => t.id === activeTab) && (
                    <div className="p-4" onClick={(e) => e.stopPropagation()}>
                      {currentTab?.content}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Layout Selector Component (for quick switching)
interface LayoutSelectorProps {
  currentLayout: LayoutType
  onLayoutChange: (layout: LayoutType) => void
  compact?: boolean
}

export const LayoutSelector = ({ currentLayout, onLayoutChange, compact = false }: LayoutSelectorProps) => {
  const layouts: { id: LayoutType; label: string; description: string }[] = [
    { id: 'grouped', label: 'Grouped Tabs', description: 'Category tabs with sub-navigation' },
    { id: 'sidebar', label: 'Sidebar', description: 'Left sidebar navigation' },
    { id: 'accordion', label: 'Accordion', description: 'Collapsible sections' },
    { id: 'cards', label: 'Card Grid', description: 'Dashboard-style cards' },
  ]

  if (compact) {
    return (
      <div className="relative group">
        <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <Settings className="h-5 w-5 text-gray-500" />
        </button>
        <div className="absolute right-0 top-full mt-1 w-48 bg-white border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
          <div className="p-2">
            <p className="text-xs font-semibold text-gray-400 uppercase px-2 mb-2">Layout</p>
            {layouts.map(layout => (
              <button
                key={layout.id}
                onClick={() => onLayoutChange(layout.id)}
                className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                  currentLayout === layout.id
                    ? 'bg-blue-50 text-blue-600'
                    : 'hover:bg-gray-50'
                }`}
              >
                {layout.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-2 p-1 bg-gray-100 rounded-lg">
      {layouts.map(layout => (
        <button
          key={layout.id}
          onClick={() => onLayoutChange(layout.id)}
          className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${
            currentLayout === layout.id
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          title={layout.description}
        >
          {layout.label}
        </button>
      ))}
    </div>
  )
}

// Main Layout Wrapper that renders the appropriate layout
interface CourierProfileLayoutProps {
  layout: LayoutType
  groups: TabGroup[]
  defaultTab?: string
}

export const CourierProfileLayout = ({ layout, groups, defaultTab }: CourierProfileLayoutProps) => {
  switch (layout) {
    case 'grouped':
      return <GroupedSectionsLayout groups={groups} defaultTab={defaultTab} />
    case 'sidebar':
      return <SidebarLayout groups={groups} defaultTab={defaultTab} />
    case 'accordion':
      return <AccordionLayout groups={groups} defaultTab={defaultTab} />
    case 'cards':
      return <CardGridLayout groups={groups} defaultTab={defaultTab} />
    default:
      return <GroupedSectionsLayout groups={groups} defaultTab={defaultTab} />
  }
}
