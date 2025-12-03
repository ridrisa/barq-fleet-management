import { AreaChart as RechartsAreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent } from './Card'

interface AreaChartProps {
  data: Record<string, unknown>[]
  xKey: string
  yKey: string | string[]
  title?: string
  height?: number
  colors?: string[]
  showGrid?: boolean
  showLegend?: boolean
  stacked?: boolean
  formatYAxis?: (value: number | string) => string
  formatXAxis?: (value: number | string) => string
}

export function AreaChart({
  data,
  xKey,
  yKey,
  title,
  height = 300,
  colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
  showGrid = true,
  showLegend = true,
  stacked = false,
  formatYAxis,
  formatXAxis,
}: AreaChartProps) {
  const areas = Array.isArray(yKey) ? yKey : [yKey]

  return (
    <Card>
      {title && (
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      )}
      <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={height}>
          <RechartsAreaChart data={data}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
            <XAxis
              dataKey={xKey}
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={formatXAxis}
            />
            <YAxis
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={formatYAxis}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            {showLegend && <Legend />}
            {areas.map((key, index) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stackId={stacked ? '1' : undefined}
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={0.6}
              />
            ))}
          </RechartsAreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
