# AI Crypto Demo

A technical demonstration showing AI generating and managing a simulated cryptocurrency in real-time. Perfect for creating viral TikTok content showcasing AI capabilities.

## Overview

This project creates a 60-second demo where:
1. **AI generates** a complete cryptocurrency configuration (name, tokenomics, rules)
2. **Simulation runs** with real-time transactions and price movements
3. **Dashboard displays** live charts, transactions, and metrics

## Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **Anthropic SDK** (Claude) / OpenAI SDK for AI integration
- **WebSockets** for real-time updates
- Custom blockchain simulation modules

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Recharts** for live price charts
- **Tailwind CSS** for styling
- **Zustand** for state management

## Project Structure

```
ai-crypto-demo/
├── backend/
│   ├── app/
│   │   ├── models/          # Data models (Block, Transaction, Crypto)
│   │   ├── modules/         # Core logic modules
│   │   │   ├── blockchain_simulator.py
│   │   │   ├── tokenomics_engine.py
│   │   │   ├── transaction_generator.py
│   │   │   ├── price_simulator.py
│   │   │   └── ai_integration.py
│   │   ├── routers/         # API endpoints
│   │   │   ├── crypto.py
│   │   │   ├── simulation.py
│   │   │   ├── ai.py
│   │   │   └── websocket.py
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   │   ├── Header.tsx
    │   │   ├── Controls.tsx
    │   │   ├── PriceChart.tsx
    │   │   ├── TokenomicsPanel.tsx
    │   │   ├── TransactionLog.tsx
    │   │   ├── AIPromptDisplay.tsx
    │   │   └── StatsGrid.tsx
    │   ├── store/           # Zustand store
    │   ├── hooks/           # Custom React hooks
    │   ├── utils/           # API client
    │   └── styles/          # CSS
    ├── package.json
    └── vite.config.ts
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key (or OpenAI API key)

### Backend Setup

```bash
cd ai-crypto-demo/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run server
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd ai-crypto-demo/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

## API Endpoints

### Crypto Management
- `POST /api/crypto/initialize` - Create a new cryptocurrency
- `GET /api/crypto/{id}/state` - Get current state
- `GET /api/crypto/{id}/price-history` - Get price history

### Simulation
- `POST /api/simulation/start/{crypto_id}` - Start simulation
- `POST /api/simulation/stop/{simulation_id}` - Stop simulation
- `GET /api/simulation/{id}/summary` - Get simulation summary

### AI Integration
- `POST /api/ai/generate-code` - Generate crypto with AI
- `POST /api/ai/generate-code/stream` - Stream AI generation
- `GET /api/ai/status` - Check AI availability

### WebSocket
- `WS /ws/crypto/{crypto_id}` - Real-time crypto updates
- `WS /ws/transactions/{crypto_id}` - Transaction stream
- `WS /ws/price/{crypto_id}` - Price stream

## Features

### Blockchain Simulation
- SHA-256 hashed blocks
- Transaction validation
- Ledger management
- Block rewards

### Tokenomics Engine
- Supply management (fixed/inflationary)
- Price calculation based on supply/demand
- Market cap tracking
- Holder distribution

### Price Simulation
- Brownian motion price movements
- Mean reversion
- Support/resistance levels
- Volatility index

### AI Integration
- Generates complete crypto configuration
- Creates tokenomics parameters
- Supports Claude and GPT models
- Streaming responses for visual effect

## TikTok Video Format

**Recommended timeline (60 seconds):**
- [0-5s] Hook: "AI creates its own crypto in 60 seconds"
- [5-25s] AI generates code + economic structure
- [25-50s] Dashboard shows live transactions & price
- [50-60s] Final results + key metrics

**Recording tips:**
- Use 1080x1920 (portrait) resolution
- Record at 60fps for smooth animations
- Use dark theme for better visibility
- Add captions/overlays in post-production

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Backend - use production ASGI server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Debug mode | true |
| `DEFAULT_SIMULATION_DURATION` | Default duration (s) | 60 |
| `MAX_TRANSACTIONS_PER_SECOND` | Max TPS | 10 |

## License

MIT License - Feel free to use for your own viral demos!
