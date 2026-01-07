import { useStore } from '../store/useStore'

export default function Header() {
  const { name, symbol, currentPrice, priceChange, simulationStatus } = useStore()

  const formatPrice = (price: number) => {
    if (price < 0.01) return price.toFixed(6)
    if (price < 1) return price.toFixed(4)
    return price.toFixed(2)
  }

  const isPositive = priceChange >= 0

  return (
    <header className="border-b border-dark-border bg-dark-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-crypto-blue to-crypto-purple flex items-center justify-center">
              <span className="text-lg font-bold">AI</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">AI Crypto Demo</h1>
              <p className="text-gray-400 text-sm">
                Real-time AI-generated cryptocurrency
              </p>
            </div>
          </div>

          {/* Crypto Info (if active) */}
          {name && (
            <div className="flex items-center space-x-8">
              <div className="text-right">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold">{name}</span>
                  <span className="text-gray-400 text-sm">{symbol}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-mono font-bold">
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

              {/* Status Indicator */}
              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    simulationStatus === 'running'
                      ? 'bg-crypto-green animate-pulse'
                      : simulationStatus === 'paused'
                      ? 'bg-yellow-500'
                      : 'bg-gray-500'
                  }`}
                />
                <span className="text-sm text-gray-400 capitalize">
                  {simulationStatus === 'none' ? 'Ready' : simulationStatus}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
