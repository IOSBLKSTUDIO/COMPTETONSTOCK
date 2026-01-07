"""
Crypto Router - Endpoints for cryptocurrency management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..models import Cryptocurrency, TokenomicsConfig
from ..modules import BlockchainSimulator, TokenomicsEngine, TransactionGenerator, PriceSimulator

router = APIRouter(prefix="/api/crypto", tags=["crypto"])

# In-memory storage for cryptos
cryptos: dict[str, dict] = {}


class InitializeRequest(BaseModel):
    """Request body for crypto initialization."""
    name: str
    symbol: str
    total_supply: float = 1_000_000
    initial_price: float = 0.01
    inflation_rate: float = 0.02
    block_reward: float = 50.0


class InitializeResponse(BaseModel):
    """Response for crypto initialization."""
    crypto_id: str
    status: str
    message: str


class CryptoStateResponse(BaseModel):
    """Response for crypto state."""
    crypto_id: str
    name: str
    symbol: str
    current_price: float
    circulating_supply: float
    total_supply: float
    market_cap: float
    transactions_count: int
    blocks: int
    holders: int
    price_change_pct: float


@router.post("/initialize", response_model=InitializeResponse)
async def initialize_crypto(request: InitializeRequest):
    """Initialize a new cryptocurrency."""
    # Create tokenomics config
    tokenomics_config = TokenomicsConfig(
        total_supply=request.total_supply,
        initial_price=request.initial_price,
        inflation_rate=request.inflation_rate,
        block_reward=request.block_reward,
    )

    # Create cryptocurrency
    crypto = Cryptocurrency(
        name=request.name,
        symbol=request.symbol,
        total_supply=request.total_supply,
        current_price=request.initial_price,
        tokenomics=tokenomics_config,
    )

    # Initialize modules
    blockchain = BlockchainSimulator()
    tokenomics = TokenomicsEngine(tokenomics_config)
    tx_generator = TransactionGenerator()
    price_sim = PriceSimulator(initial_price=request.initial_price)

    # Initialize with distribution
    initial_distribution = tx_generator.initialize_wallets(
        count=100,
        initial_supply=request.total_supply * 0.5  # 50% initial circulation
    )
    blockchain.initialize(initial_distribution)
    crypto.circulating_supply = sum(initial_distribution.values())
    tokenomics.initialize(crypto)

    # Store everything
    cryptos[crypto.id] = {
        "crypto": crypto,
        "blockchain": blockchain,
        "tokenomics": tokenomics,
        "tx_generator": tx_generator,
        "price_sim": price_sim,
        "created_at": datetime.now(),
    }

    return InitializeResponse(
        crypto_id=crypto.id,
        status="ready",
        message=f"Cryptocurrency {request.name} ({request.symbol}) initialized successfully"
    )


@router.get("/{crypto_id}/state", response_model=CryptoStateResponse)
async def get_crypto_state(crypto_id: str):
    """Get the current state of a cryptocurrency."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    data = cryptos[crypto_id]
    crypto: Cryptocurrency = data["crypto"]
    blockchain: BlockchainSimulator = data["blockchain"]
    tokenomics: TokenomicsEngine = data["tokenomics"]
    tx_generator: TransactionGenerator = data["tx_generator"]
    price_sim: PriceSimulator = data["price_sim"]

    return CryptoStateResponse(
        crypto_id=crypto.id,
        name=crypto.name,
        symbol=crypto.symbol,
        current_price=price_sim.current_price,
        circulating_supply=tokenomics.circulating_supply,
        total_supply=tokenomics.total_supply,
        market_cap=tokenomics.get_market_cap(),
        transactions_count=blockchain.get_total_transactions(),
        blocks=len(blockchain.get_chain()),
        holders=tx_generator.get_holder_count(),
        price_change_pct=price_sim.get_price_change_24h(),
    )


@router.get("/{crypto_id}/blockchain")
async def get_blockchain(crypto_id: str, limit: int = 10):
    """Get recent blocks from the blockchain."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    blockchain: BlockchainSimulator = cryptos[crypto_id]["blockchain"]
    chain = blockchain.get_chain()

    blocks = []
    for block in chain[-limit:]:
        blocks.append({
            "index": block.index,
            "hash": block.hash[:16] + "...",
            "previous_hash": block.previous_hash[:16] + "...",
            "transactions_count": len(block.transactions),
            "timestamp": block.timestamp,
        })

    return {"blocks": blocks, "total": len(chain)}


@router.get("/{crypto_id}/price-history")
async def get_price_history(crypto_id: str, limit: int = 100):
    """Get price history for charts."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    price_sim: PriceSimulator = cryptos[crypto_id]["price_sim"]
    return {"history": price_sim.get_chart_data(limit)}


@router.get("/{crypto_id}/stats")
async def get_crypto_stats(crypto_id: str):
    """Get comprehensive statistics."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    data = cryptos[crypto_id]
    blockchain: BlockchainSimulator = data["blockchain"]
    tokenomics: TokenomicsEngine = data["tokenomics"]
    price_sim: PriceSimulator = data["price_sim"]
    tx_generator: TransactionGenerator = data["tx_generator"]

    return {
        "blockchain": blockchain.get_stats(),
        "tokenomics": tokenomics.get_stats(),
        "price": price_sim.get_stats(),
        "distribution": tx_generator.get_distribution_stats(),
    }


@router.delete("/{crypto_id}")
async def delete_crypto(crypto_id: str):
    """Delete a cryptocurrency."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    del cryptos[crypto_id]
    return {"status": "deleted", "crypto_id": crypto_id}


def get_crypto_data(crypto_id: str) -> Optional[dict]:
    """Helper to get crypto data from storage."""
    return cryptos.get(crypto_id)
