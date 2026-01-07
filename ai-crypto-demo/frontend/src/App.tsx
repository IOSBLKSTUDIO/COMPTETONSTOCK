import { useEffect } from 'react'
import { useStore } from './store/useStore'
import Header from './components/Header'
import PriceChart from './components/PriceChart'
import TokenomicsPanel from './components/TokenomicsPanel'
import TransactionLog from './components/TransactionLog'
import AIPromptDisplay from './components/AIPromptDisplay'
import Controls from './components/Controls'
import StatsGrid from './components/StatsGrid'

function App() {
  const { cryptoId, connectWebSocket, disconnectWebSocket } = useStore()

  useEffect(() => {
    if (cryptoId) {
      connectWebSocket(cryptoId)
      return () => disconnectWebSocket()
    }
  }, [cryptoId, connectWebSocket, disconnectWebSocket])

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Controls */}
        <Controls />

        {/* Stats Grid */}
        <StatsGrid />

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left Column - Chart */}
          <div className="lg:col-span-2 space-y-6">
            <PriceChart />
            <AIPromptDisplay />
          </div>

          {/* Right Column - Info Panels */}
          <div className="space-y-6">
            <TokenomicsPanel />
            <TransactionLog />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-dark-border py-4 mt-8">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          AI Crypto Demo - Technical demonstration for TikTok
        </div>
      </footer>
    </div>
  )
}

export default App
