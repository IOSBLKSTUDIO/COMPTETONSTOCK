import { useStore } from '../store/useStore'

export default function StatsGrid() {
  const {
    currentPrice,
    priceChange,
    marketCap,
    transactionsCount,
    blocks,
    holders,
    simulationElapsed,
    simulationStatus,
  } = useStore()

  const formatPrice = (price: number) => {
    if (price < 0.01) return price.toFixed(6)
    if (price < 1) return price.toFixed(4)
    return price.toFixed(2)
  }

  const formatNumber = (num: number) => {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(2)}M`
    if (num >= 1_000) return `${(num / 1_000).toFixed(2)}K`
    return num.toString()
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const stats = [
    {
      label: 'Price',
      value: `$${formatPrice(currentPrice)}`,
      change: priceChange,
      showChange: true,
    },
    {
      label: 'Market Cap',
      value: `$${formatNumber(marketCap)}`,
    },
    {
      label: 'Transactions',
      value: formatNumber(transactionsCount),
    },
    {
      label: 'Blocks',
      value: blocks.toString(),
    },
    {
      label: 'Holders',
      value: holders.toString(),
    },
    {
      label: 'Time',
      value: formatTime(simulationElapsed),
      sublabel: simulationStatus === 'running' ? 'Running' : '',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mt-6">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="bg-dark-card rounded-xl p-4 border border-dark-border card-hover"
        >
          <div className="text-xs text-gray-500 uppercase tracking-wider">
            {stat.label}
          </div>
          <div className="mt-1 flex items-baseline space-x-2">
            <span className="text-xl font-mono font-bold">{stat.value}</span>
            {stat.showChange && (
              <span
                className={`text-xs font-medium ${
                  stat.change >= 0 ? 'text-crypto-green' : 'text-crypto-red'
                }`}
              >
                {stat.change >= 0 ? '+' : ''}
                {stat.change.toFixed(2)}%
              </span>
            )}
          </div>
          {stat.sublabel && (
            <div className="text-xs text-crypto-green mt-1">{stat.sublabel}</div>
          )}
        </div>
      ))}
    </div>
  )
}
