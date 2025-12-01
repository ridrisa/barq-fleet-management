import { useState } from 'react'
import { SummaryCard, BarChart, PieChart, DateRangePicker, Input, Select } from '@/components/ui'

export default function CourierPerformance() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [_sortBy, setSortBy] = useState('deliveries')

  // Mock data
  const courierData = [
    { id: 1, name: 'Ahmed Ali', deliveries: 156, onTimeRate: 94.2, rating: 4.8, codCollected: 45600 },
    { id: 2, name: 'Mohammed Hassan', deliveries: 142, onTimeRate: 92.1, rating: 4.7, codCollected: 42300 },
    { id: 3, name: 'Khaled Ibrahim', deliveries: 138, onTimeRate: 95.6, rating: 4.9, codCollected: 41200 },
    { id: 4, name: 'Omar Youssef', deliveries: 129, onTimeRate: 91.5, rating: 4.6, codCollected: 38500 },
    { id: 5, name: 'Abdullah Mahmoud', deliveries: 121, onTimeRate: 93.8, rating: 4.7, codCollected: 36200 },
    { id: 6, name: 'Youssef Ahmed', deliveries: 118, onTimeRate: 90.2, rating: 4.5, codCollected: 35100 },
    { id: 7, name: 'Hassan Ali', deliveries: 115, onTimeRate: 94.1, rating: 4.8, codCollected: 34300 },
    { id: 8, name: 'Ali Mohammed', deliveries: 108, onTimeRate: 89.7, rating: 4.4, codCollected: 32200 },
    { id: 9, name: 'Mahmoud Khaled', deliveries: 102, onTimeRate: 92.3, rating: 4.6, codCollected: 30400 },
    { id: 10, name: 'Ibrahim Omar', deliveries: 98, onTimeRate: 91.8, rating: 4.5, codCollected: 29200 },
  ]

  const topPerformersData = courierData.slice(0, 10).map(c => ({ name: c.name.split(' ')[0], deliveries: c.deliveries }))

  const performanceDistributionData = [
    { range: 'Excellent', value: 42 },
    { range: 'Good', value: 28 },
    { range: 'Average', value: 15 },
    { range: 'Below Average', value: 8 },
  ]

  const filteredCouriers = courierData.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Courier Performance</h1>
        <DateRangePicker
          startDate={dateRange.start}
          endDate={dateRange.end}
          onRangeChange={(start, end) => setDateRange({ start, end })}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Total Couriers" value="93" color="blue" trend={{ value: 5.2, label: 'vs last month' }} />
        <SummaryCard title="Avg Deliveries/Courier" value="118" color="green" trend={{ value: 8.3, label: 'vs last month' }} />
        <SummaryCard title="Avg On-Time Rate" value="92.4%" color="purple" trend={{ value: 2.1, label: 'vs last month' }} />
        <SummaryCard title="Avg Rating" value="4.6" color="yellow" trend={{ value: 3.5, label: 'vs last month' }} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChart data={topPerformersData} xKey="name" yKey="deliveries" title="Top 10 Performers" height={300} />
        <PieChart data={performanceDistributionData} dataKey="value" nameKey="range" title="Performance Distribution" height={300} showLabels={false} />
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Courier Leaderboard</h3>
        </div>
        <div className="p-4">
          <div className="flex items-center gap-4 mb-4">
            <Input type="text" placeholder="Search couriers..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
            <Select value={_sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="deliveries">Sort by Deliveries</option>
              <option value="onTimeRate">Sort by On-Time Rate</option>
              <option value="rating">Sort by Rating</option>
              <option value="codCollected">Sort by COD Collected</option>
            </Select>
          </div>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Courier Name</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Deliveries</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">On-Time Rate</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Rating</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">COD Collected</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCouriers.map((courier, index) => (
                <tr key={courier.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2">
                    <span className={"font-bold " + (index < 3 ? "text-yellow-600" : "")}>
                      {"#" + (index + 1)}
                    </span>
                  </td>
                  <td className="px-4 py-2">{courier.name}</td>
                  <td className="px-4 py-2 text-right">{courier.deliveries}</td>
                  <td className="px-4 py-2 text-right">
                    <span className={courier.onTimeRate >= 90 ? 'text-green-600' : 'text-yellow-600'}>
                      {courier.onTimeRate}%
                    </span>
                  </td>
                  <td className="px-4 py-2 text-right">{courier.rating}</td>
                  <td className="px-4 py-2 text-right">{courier.codCollected.toLocaleString()} SAR</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
