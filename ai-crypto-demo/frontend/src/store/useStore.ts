import { create } from 'zustand'
import { api } from '../utils/api'

interface PricePoint {
  timestamp: number
  price: number
}

interface Transaction {
  tx_hash: string
  from: string
  to: string
  amount: number
  timestamp: string
  block?: number
}

interface CryptoState {
  // Crypto info
  cryptoId: string | null
  name: string
  symbol: string

  // Market data
  currentPrice: number
  priceHistory: PricePoint[]
  priceChange: number
  marketCap: number

  // Supply
  totalSupply: number
  circulatingSupply: number

  // Blockchain
  blocks: number
  transactionsCount: number
  holders: number

  // Simulation
  simulationId: string | null
  simulationStatus: 'none' | 'running' | 'paused' | 'completed'
  simulationProgress: number
  simulationElapsed: number

  // AI
  aiPrompt: string
  aiResponse: string
  isGenerating: boolean

  // Transactions log
  recentTransactions: Transaction[]

  // WebSocket
  ws: WebSocket | null

  // Actions
  initializeCrypto: (name: string, symbol: string, totalSupply: number, initialPrice: number) => Promise<void>
  generateWithAI: (requirements?: string[]) => Promise<void>
  startSimulation: (duration: number, intensity: string) => Promise<void>
  stopSimulation: () => Promise<void>
  connectWebSocket: (cryptoId: string) => void
  disconnectWebSocket: () => void
  updateFromWebSocket: (data: any) => void
  addTransaction: (tx: Transaction) => void
  reset: () => void
}

const initialState = {
  cryptoId: null,
  name: '',
  symbol: '',
  currentPrice: 0,
  priceHistory: [],
  priceChange: 0,
  marketCap: 0,
  totalSupply: 0,
  circulatingSupply: 0,
  blocks: 0,
  transactionsCount: 0,
  holders: 0,
  simulationId: null,
  simulationStatus: 'none' as const,
  simulationProgress: 0,
  simulationElapsed: 0,
  aiPrompt: '',
  aiResponse: '',
  isGenerating: false,
  recentTransactions: [],
  ws: null,
}

export const useStore = create<CryptoState>((set, get) => ({
  ...initialState,

  initializeCrypto: async (name, symbol, totalSupply, initialPrice) => {
    try {
      const response = await api.post('/api/crypto/initialize', {
        name,
        symbol,
        total_supply: totalSupply,
        initial_price: initialPrice,
      })

      set({
        cryptoId: response.crypto_id,
        name,
        symbol,
        totalSupply,
        currentPrice: initialPrice,
        circulatingSupply: totalSupply * 0.5,
        marketCap: totalSupply * 0.5 * initialPrice,
      })
    } catch (error) {
      console.error('Failed to initialize crypto:', error)
      throw error
    }
  },

  generateWithAI: async (requirements = []) => {
    set({ isGenerating: true, aiPrompt: 'Generating cryptocurrency with AI...' })

    try {
      const response = await api.post('/api/ai/generate-code', { requirements })

      set({
        aiResponse: response.raw_code,
        isGenerating: false,
      })

      // Initialize with AI-generated parameters
      await get().initializeCrypto(
        response.name,
        response.symbol,
        response.total_supply,
        response.initial_price
      )
    } catch (error) {
      console.error('AI generation failed:', error)
      set({ isGenerating: false })
      throw error
    }
  },

  startSimulation: async (duration, intensity) => {
    const { cryptoId } = get()
    if (!cryptoId) return

    try {
      const response = await api.post(`/api/simulation/start/${cryptoId}`, {
        duration_seconds: duration,
        intensity,
      })

      set({
        simulationId: response.simulation_id,
        simulationStatus: 'running',
        simulationProgress: 0,
        simulationElapsed: 0,
      })
    } catch (error) {
      console.error('Failed to start simulation:', error)
      throw error
    }
  },

  stopSimulation: async () => {
    const { simulationId } = get()
    if (!simulationId) return

    try {
      await api.post(`/api/simulation/stop/${simulationId}`)
      set({ simulationStatus: 'paused' })
    } catch (error) {
      console.error('Failed to stop simulation:', error)
    }
  },

  connectWebSocket: (cryptoId) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/crypto/${cryptoId}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      get().updateFromWebSocket(data)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    set({ ws })
  },

  disconnectWebSocket: () => {
    const { ws } = get()
    if (ws) {
      ws.close()
      set({ ws: null })
    }
  },

  updateFromWebSocket: (data) => {
    if (data.type === 'state_update') {
      const newPricePoint: PricePoint = {
        timestamp: Date.now(),
        price: data.price.current,
      }

      set((state) => ({
        currentPrice: data.price.current,
        priceChange: data.price.change_pct,
        marketCap: data.market.market_cap,
        circulatingSupply: data.market.circulating_supply,
        totalSupply: data.market.total_supply,
        blocks: data.blockchain.blocks,
        transactionsCount: data.blockchain.transactions,
        holders: data.holders,
        priceHistory: [...state.priceHistory.slice(-99), newPricePoint],
        simulationStatus: data.simulation?.status || 'none',
        simulationProgress: data.simulation?.progress || 0,
        simulationElapsed: data.simulation?.elapsed || 0,
      }))
    }
  },

  addTransaction: (tx) => {
    set((state) => ({
      recentTransactions: [tx, ...state.recentTransactions.slice(0, 49)],
    }))
  },

  reset: () => {
    get().disconnectWebSocket()
    set(initialState)
  },
}))
