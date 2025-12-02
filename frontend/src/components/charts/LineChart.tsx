import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface LineChartProps {
  data: Record<string, any>[]
  xKey: string
  yKeys: string[]
  colors?: string[]
  height?: number
}

const DEFAULT_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6']

export function LineChart({
  data,
  xKey,
  yKeys,
  colors = DEFAULT_COLORS,
  height = 300,
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#6b7280" />
        <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
        />
        <Legend />
        {yKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colors[index % colors.length]}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  )
}
