import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { buildingsAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

export default function Occupancy() {
  const [_dateRange, _setDateRange] = useState({ start: '', end: '' })

  const { data: buildings = [], isLoading } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => buildingsAPI.getAll(0, 100),
  })

  if (isLoading) return <div className="flex items-center justify-center h-64"><Spinner /></div>

  const currentOccupancy = 78
  const avgOccupancy = 72
  const peakOccupancy = 94

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Occupancy Tracking</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-blue-600">{currentOccupancy}%</p><p className="text-sm text-gray-600">Current Occupancy</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-green-600">{avgOccupancy}%</p><p className="text-sm text-gray-600">Avg Occupancy</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-orange-600">{peakOccupancy}%</p><p className="text-sm text-gray-600">Peak Occupancy</p></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Building Occupancy</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            {buildings.map((building: any) => {
              const occupancy = building.occupied || 0
              const capacity = building.capacity || 1
              const percentage = Math.round((occupancy / capacity) * 100)
              return (
                <div key={building.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold">{building.name}</h3>
                    <span className="text-sm text-gray-600">{occupancy}/{capacity} beds</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-6">
                    <div className={`h-6 rounded-full flex items-center justify-center text-white text-sm font-medium ${percentage > 90 ? 'bg-red-500' : percentage > 75 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{ width: `${percentage}%` }}>
                      {percentage}%
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
