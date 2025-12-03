import { useState } from 'react'
import {
  LineChart,
  AreaChart,
  Button,
  Select,
  Input,
  Card,
  CardContent,
} from '@/components/ui'
import {
  Download,
  TrendingUp,
  AlertCircle,
  Settings,
  BarChart3,
  Package,
  DollarSign,
  Users,
} from 'lucide-react'

type ForecastAlgorithm = 'linear' | 'exponential' | 'seasonal' | 'arima'
type ForecastPeriod = 7 | 14 | 30 | 60 | 90

export default function Forecasting() {
  const [forecastPeriod, setForecastPeriod] = useState<ForecastPeriod>(30)
  const [algorithm, setAlgorithm] = useState<ForecastAlgorithm>('seasonal')
  const [confidenceLevel, setConfidenceLevel] = useState(95)
  const [showConfidenceInterval, setShowConfidenceInterval] = useState(true)
  const [forecastGenerated, setForecastGenerated] = useState(false)

  // Mock historical data (last 60 days)
  const historicalDeliveryData = Array.from({ length: 60 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (60 - i))
    const baseValue = 180
    const trend = i * 0.5
    const seasonal = Math.sin((i / 7) * Math.PI) * 20
    const noise = (Math.random() - 0.5) * 15
    return {
      date: date.toISOString().split('T')[0],
      deliveries: Math.round(baseValue + trend + seasonal + noise),
      actual: true,
    }
  })

  // Generate forecast data
  const generateForecast = () => {
    const lastValue = historicalDeliveryData[historicalDeliveryData.length - 1].deliveries
    return Array.from({ length: forecastPeriod }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() + i + 1)
      const trend = i * 0.6
      const seasonal = Math.sin(((60 + i) / 7) * Math.PI) * 20
      const predicted = lastValue + trend + seasonal
      const variance = predicted * 0.15

      return {
        date: date.toISOString().split('T')[0],
        deliveries: Math.round(predicted),
        lower: Math.round(predicted - variance),
        upper: Math.round(predicted + variance),
        actual: false,
      }
    })
  }

  const forecastData = forecastGenerated ? generateForecast() : []
  const combinedDeliveryData = [...historicalDeliveryData.slice(-30), ...forecastData]

  // Mock revenue forecast
  const historicalRevenueData = Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (30 - i))
    const baseValue = 15000
    const trend = i * 200
    const noise = (Math.random() - 0.5) * 2000
    return {
      date: date.toISOString().split('T')[0],
      revenue: Math.round(baseValue + trend + noise),
      actual: true,
    }
  })

  const generateRevenueForecast = () => {
    const lastValue = historicalRevenueData[historicalRevenueData.length - 1].revenue
    return Array.from({ length: forecastPeriod }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() + i + 1)
      const predicted = lastValue + i * 250 + (Math.random() - 0.5) * 1000
      const variance = predicted * 0.12

      return {
        date: date.toISOString().split('T')[0],
        revenue: Math.round(predicted),
        lower: Math.round(predicted - variance),
        upper: Math.round(predicted + variance),
        actual: false,
      }
    })
  }

  const revenueForecastData = forecastGenerated ? generateRevenueForecast() : []
  const combinedRevenueData = [...historicalRevenueData.slice(-15), ...revenueForecastData]

  // Mock resource requirements forecast
  const generateResourceForecast = () => {
    return Array.from({ length: forecastPeriod }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() + i + 1)
      const baseDrivers = 42
      const basevehicles = 35
      const growth = i * 0.3

      return {
        date: date.toISOString().split('T')[0],
        drivers: Math.round(baseDrivers + growth),
        vehicles: Math.round(basevehicles + growth * 0.8),
      }
    })
  }

  const resourceForecastData = forecastGenerated ? generateResourceForecast() : []

  // Historical accuracy metrics
  const accuracyMetrics = {
    mape: 4.2, // Mean Absolute Percentage Error
    rmse: 12.5, // Root Mean Square Error
    r2: 0.87, // R-squared
    lastMonthAccuracy: 95.8,
  }

  const handleGenerateForecast = () => {
    setForecastGenerated(true)
  }

  const handleExportForecast = () => {
    alert(
      'Exporting Forecast Data...\n\n' +
      'This would generate a file with:\n' +
      '- Forecast parameters and settings\n' +
      '- Delivery volume predictions with confidence intervals\n' +
      '- Revenue forecasts\n' +
      '- Resource requirement projections\n' +
      '- Historical accuracy metrics'
    )
  }

  const resetForecast = () => {
    setForecastGenerated(false)
    setForecastPeriod(30)
    setAlgorithm('seasonal')
    setConfidenceLevel(95)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Forecasting & Predictions</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Predictive analytics for delivery volume, revenue, and resource planning
          </p>
        </div>

        <div className="flex items-center gap-3">
          {forecastGenerated && (
            <Button
              variant="primary"
              onClick={handleExportForecast}
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Forecast
            </Button>
          )}
        </div>
      </div>

      {/* Forecast Parameters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 mb-4">
            <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Forecast Parameters
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Forecast Period
              </label>
              <Select
                value={forecastPeriod.toString()}
                onChange={(e) => setForecastPeriod(Number(e.target.value) as ForecastPeriod)}
                className="w-full"
              >
                <option value="7">7 days</option>
                <option value="14">14 days</option>
                <option value="30">30 days</option>
                <option value="60">60 days</option>
                <option value="90">90 days</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Algorithm
              </label>
              <Select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as ForecastAlgorithm)}
                className="w-full"
              >
                <option value="linear">Linear Regression</option>
                <option value="exponential">Exponential Smoothing</option>
                <option value="seasonal">Seasonal ARIMA</option>
                <option value="arima">ARIMA</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Confidence Level (%)
              </label>
              <Input
                type="number"
                min="80"
                max="99"
                value={confidenceLevel}
                onChange={(e) => setConfidenceLevel(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showConfidenceInterval}
                  onChange={(e) => setShowConfidenceInterval(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Show Confidence Interval
                </span>
              </label>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <Button variant="primary" onClick={handleGenerateForecast}>
              <BarChart3 className="w-4 h-4 mr-2" />
              Generate Forecast
            </Button>
            {forecastGenerated && (
              <Button variant="outline" onClick={resetForecast}>
                Reset
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Forecast Results */}
      {forecastGenerated ? (
        <>
          {/* Key Forecast Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Predicted Deliveries ({forecastPeriod} days)
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                      {forecastData.reduce((sum, d) => sum + d.deliveries, 0).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Avg: {Math.round(forecastData.reduce((sum, d) => sum + d.deliveries, 0) / forecastPeriod)} per day
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400">
                    <Package className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Projected Revenue
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                      {revenueForecastData.reduce((sum, d) => sum + d.revenue, 0).toLocaleString()} SAR
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      +18.5% growth expected
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400">
                    <DollarSign className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Required Resources (Peak)
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                      {resourceForecastData[resourceForecastData.length - 1]?.drivers || 0} Drivers
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {resourceForecastData[resourceForecastData.length - 1]?.vehicles || 0} Vehicles needed
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400">
                    <Users className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Forecast Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Delivery Volume Forecast */}
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Delivery Volume Forecast ({forecastPeriod} Days)
                </h3>
                <div className="space-y-4">
                  <LineChart
                    data={combinedDeliveryData}
                    xKey="date"
                    yKey="deliveries"
                    height={280}
                    formatXAxis={(value) =>
                      new Date(value).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })
                    }
                  />
                  {showConfidenceInterval && (
                    <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                      <p className="text-xs font-medium text-blue-900 dark:text-blue-100 mb-1">
                        {confidenceLevel}% Confidence Interval
                      </p>
                      <p className="text-xs text-blue-700 dark:text-blue-300">
                        Predictions range from {Math.min(...forecastData.map(d => d.lower))} to{' '}
                        {Math.max(...forecastData.map(d => d.upper))} deliveries per day
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Revenue Forecast */}
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Revenue Forecast
                </h3>
                <div className="space-y-4">
                  <AreaChart
                    data={combinedRevenueData}
                    xKey="date"
                    yKey={['revenue']}
                    height={280}
                    colors={['#10b981']}
                    formatXAxis={(value) =>
                      new Date(value).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })
                    }
                    formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
                  />
                  {showConfidenceInterval && (
                    <div className="bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 rounded-lg p-3">
                      <p className="text-xs font-medium text-green-900 dark:text-green-100 mb-1">
                        {confidenceLevel}% Confidence Interval
                      </p>
                      <p className="text-xs text-green-700 dark:text-green-300">
                        Daily revenue expected between{' '}
                        {(Math.min(...revenueForecastData.map(d => d.lower)) / 1000).toFixed(1)}K and{' '}
                        {(Math.max(...revenueForecastData.map(d => d.upper)) / 1000).toFixed(1)}K SAR
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Resource Requirements Forecast */}
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Resource Requirements Forecast
                </h3>
                <LineChart
                  data={resourceForecastData}
                  xKey="date"
                  yKey="drivers"
                  height={280}
                  color="#8b5cf6"
                  formatXAxis={(value) =>
                    new Date(value).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })
                  }
                />
                <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-purple-50 dark:bg-purple-900/10 rounded p-2">
                    <p className="text-xs text-gray-600 dark:text-gray-400">Current Drivers</p>
                    <p className="text-lg font-semibold text-purple-600 dark:text-purple-400">42</p>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/10 rounded p-2">
                    <p className="text-xs text-gray-600 dark:text-gray-400">Peak Requirement</p>
                    <p className="text-lg font-semibold text-purple-600 dark:text-purple-400">
                      {resourceForecastData[resourceForecastData.length - 1]?.drivers || 0}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Historical Accuracy */}
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Historical Forecast Accuracy
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Last Month Accuracy
                      </span>
                      <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                        {accuracyMetrics.lastMonthAccuracy}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${accuracyMetrics.lastMonthAccuracy}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mt-6">
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">MAPE</p>
                      <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {accuracyMetrics.mape}%
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">RMSE</p>
                      <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {accuracyMetrics.rmse}
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">R²</p>
                      <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                        {accuracyMetrics.r2}
                      </p>
                    </div>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mt-4">
                    <p className="text-xs text-blue-700 dark:text-blue-300">
                      The model has shown consistent accuracy over the past 3 months with MAPE under 5%.
                      Seasonal patterns are well captured using the {algorithm.toUpperCase()} algorithm.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <div className="bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
                  Action Recommendations
                </h3>
                <ul className="space-y-1 text-sm text-yellow-700 dark:text-yellow-300">
                  <li>
                    • Plan to onboard {resourceForecastData[resourceForecastData.length - 1]?.drivers - 42 || 0} additional drivers by day {forecastPeriod}
                  </li>
                  <li>
                    • Ensure vehicle maintenance schedule aligns with projected {resourceForecastData[resourceForecastData.length - 1]?.vehicles || 0} vehicle requirement
                  </li>
                  <li>
                    • Revenue growth of 18.5% suggests opportunity for pricing optimization
                  </li>
                  <li>
                    • Monitor daily actuals vs forecast to refine model accuracy
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                No Forecast Generated
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Configure your forecast parameters above and click "Generate Forecast" to see predictions.
              </p>
              <Button variant="primary" onClick={handleGenerateForecast}>
                <BarChart3 className="w-4 h-4 mr-2" />
                Generate Forecast
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
