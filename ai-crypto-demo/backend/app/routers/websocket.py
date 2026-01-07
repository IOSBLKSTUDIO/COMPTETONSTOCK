"""
WebSocket Router - Real-time updates for the frontend.
"""

import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional

from .crypto import cryptos
from .simulation import simulations
from ..models import SimulationStatus
from ..modules import BlockchainSimulator, PriceSimulator, TokenomicsEngine, TransactionGenerator

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, crypto_id: str):
        await websocket.accept()
        if crypto_id not in self.active_connections:
            self.active_connections[crypto_id] = []
        self.active_connections[crypto_id].append(websocket)

    def disconnect(self, websocket: WebSocket, crypto_id: str):
        if crypto_id in self.active_connections:
            if websocket in self.active_connections[crypto_id]:
                self.active_connections[crypto_id].remove(websocket)

    async def broadcast(self, crypto_id: str, message: dict):
        if crypto_id not in self.active_connections:
            return
        for connection in self.active_connections[crypto_id]:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


def get_current_state(crypto_id: str) -> Optional[dict]:
    """Get current state for a crypto."""
    if crypto_id not in cryptos:
        return None

    data = cryptos[crypto_id]
    blockchain: BlockchainSimulator = data["blockchain"]
    tokenomics: TokenomicsEngine = data["tokenomics"]
    price_sim: PriceSimulator = data["price_sim"]
    tx_generator: TransactionGenerator = data["tx_generator"]

    # Find active simulation
    active_sim = None
    for sim_id, sim in simulations.items():
        if sim.crypto_id == crypto_id:
            active_sim = sim
            break

    return {
        "type": "state_update",
        "timestamp": datetime.now().isoformat(),
        "crypto": {
            "id": crypto_id,
            "name": data["crypto"].name,
            "symbol": data["crypto"].symbol,
        },
        "price": {
            "current": price_sim.current_price,
            "change_pct": price_sim.get_price_change_24h(),
            "high": price_sim.all_time_high,
            "low": price_sim.all_time_low,
        },
        "market": {
            "market_cap": tokenomics.get_market_cap(),
            "circulating_supply": tokenomics.circulating_supply,
            "total_supply": tokenomics.total_supply,
        },
        "blockchain": {
            "blocks": len(blockchain.get_chain()),
            "transactions": blockchain.get_total_transactions(),
            "pending": len(blockchain.get_pending_transactions()),
        },
        "holders": tx_generator.get_holder_count(),
        "simulation": {
            "id": active_sim.simulation_id if active_sim else None,
            "status": active_sim.status.value if active_sim else "none",
            "progress": active_sim.progress if active_sim else 0,
            "elapsed": active_sim.elapsed_seconds if active_sim else 0,
        } if active_sim else None,
    }


@router.websocket("/ws/crypto/{crypto_id}")
async def websocket_crypto(websocket: WebSocket, crypto_id: str):
    """WebSocket endpoint for real-time crypto updates."""
    await manager.connect(websocket, crypto_id)

    try:
        # Send initial state
        state = get_current_state(crypto_id)
        if state:
            await websocket.send_json(state)

        # Keep connection alive and send updates
        while True:
            try:
                # Wait for messages (or timeout for periodic updates)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.5  # 500ms update interval
                )

                # Handle client messages
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                # Send state update on timeout
                state = get_current_state(crypto_id)
                if state:
                    await websocket.send_json(state)

    except WebSocketDisconnect:
        manager.disconnect(websocket, crypto_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, crypto_id)


@router.websocket("/ws/transactions/{crypto_id}")
async def websocket_transactions(websocket: WebSocket, crypto_id: str):
    """WebSocket endpoint for transaction stream."""
    await manager.connect(websocket, f"{crypto_id}_tx")

    try:
        last_tx_count = 0

        while True:
            await asyncio.sleep(0.2)  # 200ms update interval

            if crypto_id not in cryptos:
                continue

            blockchain: BlockchainSimulator = cryptos[crypto_id]["blockchain"]
            current_tx_count = blockchain.get_total_transactions()

            # Check for new transactions
            if current_tx_count > last_tx_count:
                # Get recent transactions from latest block
                chain = blockchain.get_chain()
                if chain:
                    latest_block = chain[-1]
                    for tx in latest_block.transactions[-5:]:  # Last 5 transactions
                        await websocket.send_json({
                            "type": "transaction",
                            "tx_hash": tx.tx_hash,
                            "from": tx.from_address[:10] + "...",
                            "to": tx.to_address[:10] + "...",
                            "amount": tx.amount,
                            "timestamp": datetime.fromtimestamp(tx.timestamp).isoformat(),
                            "block": tx.block_index,
                        })

                last_tx_count = current_tx_count

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"{crypto_id}_tx")
    except Exception as e:
        print(f"Transaction WebSocket error: {e}")
        manager.disconnect(websocket, f"{crypto_id}_tx")


@router.websocket("/ws/price/{crypto_id}")
async def websocket_price(websocket: WebSocket, crypto_id: str):
    """WebSocket endpoint for price stream."""
    await manager.connect(websocket, f"{crypto_id}_price")

    try:
        while True:
            await asyncio.sleep(0.1)  # 100ms update interval

            if crypto_id not in cryptos:
                continue

            price_sim: PriceSimulator = cryptos[crypto_id]["price_sim"]
            tokenomics: TokenomicsEngine = cryptos[crypto_id]["tokenomics"]

            await websocket.send_json({
                "type": "price_update",
                "timestamp": datetime.now().timestamp(),
                "price": price_sim.current_price,
                "change_pct": price_sim.get_price_change_24h(),
                "market_cap": tokenomics.get_market_cap(),
                "volume": abs(tokenomics.buy_pressure + tokenomics.sell_pressure),
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, f"{crypto_id}_price")
    except Exception as e:
        print(f"Price WebSocket error: {e}")
        manager.disconnect(websocket, f"{crypto_id}_price")
