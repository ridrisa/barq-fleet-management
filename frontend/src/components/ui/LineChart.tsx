import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent } from './Card'

interface LineChartProps {
  data: any[]
  xKey: string
  yKey: string | string[]
  title?: string
  height?: number
  colors?: string[]
  color?: string // Alias for single color
  showGrid?: boolean
  showLegend?: boolean
  formatYAxis?: (value: any) => string
  formatXAxis?: (value: any) => string
}

export function LineChart({
  data,
  xKey,
  yKey,
  title,
  height = 300,
  colors: colorsProp,
  color,
  showGrid = true,
  showLegend = true,
  formatYAxis,
  formatXAxis,
}: LineChartProps) {
  const colors = colorsProp || (color ? [color] : ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
  const lines = Array.isArray(yKey) ? yKey : [yKey]

  return (
    <Card>
      {title && (
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      )}
      <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={height}>
          <RechartsLineChart data={data}>
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
            {lines.map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                dot={{ fill: colors[index % colors.length], r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </RechartsLineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
