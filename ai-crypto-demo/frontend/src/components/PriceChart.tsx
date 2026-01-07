import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { useStore } from '../store/useStore'

export default function PriceChart() {
  const { priceHistory, currentPrice, priceChange, symbol } = useStore()

  const isPositive = priceChange >= 0
  const chartColor = isPositive ? '#00ff88' : '#ff4444'

  const formatPrice = (price: number) => {
    if (price < 0.01) return price.toFixed(6)
    if (price < 1) return price.toFixed(4)
    return price.toFixed(2)
  }

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  // Calculate min/max for better chart scaling
  const prices = priceHistory.map((p) => p.price)
  const minPrice = prices.length > 0 ? Math.min(...prices) * 0.95 : 0
  const maxPrice = prices.length > 0 ? Math.max(...prices) * 1.05 : 1

  return (
    <div className="bg-dark-card rounded-xl p-6 border border-dark-border">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-300">Price Chart</h2>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-mono font-bold">
              ${formatPrice(currentPrice)}
            </span>
            <span
              className={`text-sm font-medium ${
                isPositive ? 'text-crypto-green' : 'text-crypto-red'
              }`}
            >
              {isPositive ? '+' : ''}
              {priceChange.toFixed(2)}%
            </span>
          </div>
        </div>
        <div className="text-right text-sm text-gray-400">
          <div>{symbol || 'N/A'}</div>
          <div>{priceHistory.length} data points</div>
        </div>
      </div>

      <div className="h-64">
        {priceHistory.length > 1 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={priceHistory}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={chartColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatTime}
                stroke="#4a4a5a"
                fontSize={10}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={[minPrice, maxPrice]}
                tickFormatter={(v) => `$${formatPrice(v)}`}
                stroke="#4a4a5a"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                width={70}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#12121a',
                  border: '1px solid #1f1f2e',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                labelFormatter={formatTime}
                formatter={(value: number) => [`$${formatPrice(value)}`, 'Price']}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke={chartColor}
                strokeWidth={2}
                fill="url(#priceGradient)"
                dot={false}
                activeDot={{ r: 4, fill: chartColor }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <svg
                className="w-12 h-12 mx-auto mb-2 opacity-50"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
              <p>Start simulation to see price data</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
