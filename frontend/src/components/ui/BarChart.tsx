import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent } from './Card'

interface BarChartProps {
  data: Record<string, unknown>[]
  xKey: string
  yKey: string | string[]
  title?: string
  height?: number
  colors?: string[]
  color?: string // Alias for single color
  showGrid?: boolean
  showLegend?: boolean
  horizontal?: boolean
  formatYAxis?: (value: number | string) => string
  formatXAxis?: (value: number | string) => string
}

export function BarChart({
  data,
  xKey,
  yKey,
  title,
  height = 300,
  colors: colorsProp,
  color,
  showGrid = true,
  showLegend = true,
  horizontal = false,
  formatYAxis,
  formatXAxis,
}: BarChartProps) {
  const colors = colorsProp || (color ? [color] : ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
  const bars = Array.isArray(yKey) ? yKey : [yKey]

  return (
    <Card>
      {title && (
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      )}
      <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={height}>
          <RechartsBarChart
            data={data}
            layout={horizontal ? 'vertical' : 'horizontal'}
          >
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
            {horizontal ? (
              <>
                <XAxis
                  type="number"
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={formatXAxis}
                />
                <YAxis
                  type="category"
                  dataKey={xKey}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={formatYAxis}
                />
              </>
            ) : (
              <>
                <XAxis
                  dataKey={xKey}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={formatXAxis}
                />
                <YAxis
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={formatYAxis}
                />
              </>
            )}
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            {showLegend && <Legend />}
            {bars.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={colors[index % colors.length]}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </RechartsBarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
