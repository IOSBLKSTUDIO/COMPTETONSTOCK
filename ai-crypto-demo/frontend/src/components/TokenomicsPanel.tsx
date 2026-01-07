import { useStore } from '../store/useStore'

export default function TokenomicsPanel() {
  const { totalSupply, circulatingSupply, marketCap, holders, blocks } = useStore()

  const formatNumber = (num: number) => {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(2)}M`
    if (num >= 1_000) return `${(num / 1_000).toFixed(2)}K`
    return num.toFixed(2)
  }

  const formatCurrency = (num: number) => {
    if (num >= 1_000_000) return `$${(num / 1_000_000).toFixed(2)}M`
    if (num >= 1_000) return `$${(num / 1_000).toFixed(2)}K`
    return `$${num.toFixed(2)}`
  }

  const supplyRatio = totalSupply > 0 ? (circulatingSupply / totalSupply) * 100 : 0

  const metrics = [
    {
      label: 'Total Supply',
      value: formatNumber(totalSupply),
      icon: '🪙',
    },
    {
      label: 'Circulating',
      value: formatNumber(circulatingSupply),
      sublabel: `${supplyRatio.toFixed(1)}%`,
      icon: '📊',
    },
    {
      label: 'Market Cap',
      value: formatCurrency(marketCap),
      icon: '💰',
    },
    {
      label: 'Holders',
      value: holders.toString(),
      icon: '👥',
    },
    {
      label: 'Blocks',
      value: blocks.toString(),
      icon: '⛓️',
    },
  ]

  return (
    <div className="bg-dark-card rounded-xl p-6 border border-dark-border">
      <h2 className="text-lg font-semibold text-gray-300 mb-4">Tokenomics</h2>

      <div className="space-y-4">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="flex items-center justify-between py-2 border-b border-dark-border last:border-0"
          >
            <div className="flex items-center space-x-2">
              <span className="text-lg">{metric.icon}</span>
              <span className="text-gray-400 text-sm">{metric.label}</span>
            </div>
            <div className="text-right">
              <span className="font-mono font-semibold">{metric.value}</span>
              {metric.sublabel && (
                <span className="text-gray-500 text-xs ml-1">({metric.sublabel})</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Supply Progress Bar */}
      <div className="mt-6">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Supply Released</span>
          <span>{supplyRatio.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-dark-bg rounded-full h-2">
          <div
            className="bg-gradient-to-r from-crypto-blue to-crypto-purple h-2 rounded-full transition-all duration-500"
            style={{ width: `${supplyRatio}%` }}
          />
        </div>
      </div>
    </div>
  )
}
