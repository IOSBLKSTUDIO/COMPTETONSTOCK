const BASE_URL = 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `HTTP error ${response.status}`)
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export const api = new ApiClient(BASE_URL)

// API functions
export const cryptoApi = {
  initialize: (data: {
    name: string
    symbol: string
    total_supply: number
    initial_price: number
  }) => api.post<{ crypto_id: string; status: string }>('/api/crypto/initialize', data),

  getState: (cryptoId: string) => api.get(`/api/crypto/${cryptoId}/state`),

  getPriceHistory: (cryptoId: string, limit = 100) =>
    api.get(`/api/crypto/${cryptoId}/price-history?limit=${limit}`),

  getStats: (cryptoId: string) => api.get(`/api/crypto/${cryptoId}/stats`),
}

export const simulationApi = {
  start: (cryptoId: string, data: { duration_seconds: number; intensity: string }) =>
    api.post(`/api/simulation/start/${cryptoId}`, data),

  stop: (simulationId: string) => api.post(`/api/simulation/stop/${simulationId}`),

  getState: (simulationId: string) => api.get(`/api/simulation/${simulationId}`),

  getSummary: (simulationId: string) => api.get(`/api/simulation/${simulationId}/summary`),
}

export const aiApi = {
  generateCode: (data: { requirements?: string[] }) =>
    api.post('/api/ai/generate-code', data),

  getStatus: () => api.get('/api/ai/status'),

  getLastInteraction: () => api.get('/api/ai/last-interaction'),
}
