import { useStore } from '../store/useStore'

export default function TransactionLog() {
  const { recentTransactions, transactionsCount } = useStore()

  const formatAmount = (amount: number) => {
    if (amount >= 1000) return `${(amount / 1000).toFixed(2)}K`
    return amount.toFixed(2)
  }

  return (
    <div className="bg-dark-card rounded-xl p-6 border border-dark-border">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-300">Transactions</h2>
        <span className="text-sm text-gray-400">
          Total: {transactionsCount.toLocaleString()}
        </span>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {recentTransactions.length > 0 ? (
          recentTransactions.map((tx, index) => (
            <div
              key={tx.tx_hash + index}
              className="transaction-enter bg-dark-bg rounded-lg p-3 text-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-crypto-green" />
                  <span className="font-mono text-xs text-gray-400">
                    {tx.tx_hash.slice(0, 8)}...
                  </span>
                </div>
                <span className="font-mono font-semibold text-crypto-green">
                  +{formatAmount(tx.amount)}
                </span>
              </div>
              <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
                <span>
                  {tx.from} → {tx.to}
                </span>
                <span>Block #{tx.block}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-10 h-10 mx-auto mb-2 opacity-50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p>No transactions yet</p>
            <p className="text-xs mt-1">Start simulation to see activity</p>
          </div>
        )}
      </div>
    </div>
  )
}
