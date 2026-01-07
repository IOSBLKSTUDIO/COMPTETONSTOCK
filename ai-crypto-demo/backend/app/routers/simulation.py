"""
Simulation Router - Endpoints for simulation control.
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from ..models import SimulationState, SimulationConfig, SimulationStatus
from ..modules import BlockchainSimulator, TokenomicsEngine, TransactionGenerator, PriceSimulator
from .crypto import get_crypto_data, cryptos

router = APIRouter(prefix="/api/simulation", tags=["simulation"])

# Active simulations
simulations: dict[str, SimulationState] = {}
simulation_tasks: dict[str, asyncio.Task] = {}


class StartSimulationRequest(BaseModel):
    """Request body for starting simulation."""
    duration_seconds: int = 60
    intensity: str = "medium"  # low, medium, high
    enable_ai_optimization: bool = False


class StartSimulationResponse(BaseModel):
    """Response for simulation start."""
    simulation_id: str
    crypto_id: str
    started_at: str
    duration_seconds: int
    status: str


class SimulationStateResponse(BaseModel):
    """Response for simulation state."""
    simulation_id: str
    crypto_id: str
    status: str
    progress: float
    elapsed_seconds: float
    transactions_generated: int
    blocks_created: int
    current_price: float


def get_intensity_params(intensity: str) -> dict:
    """Get simulation parameters based on intensity."""
    params = {
        "low": {"tx_per_second": 2, "volatility": 0.02},
        "medium": {"tx_per_second": 5, "volatility": 0.05},
        "high": {"tx_per_second": 10, "volatility": 0.10},
    }
    return params.get(intensity, params["medium"])


async def run_simulation(
    simulation_id: str,
    crypto_id: str,
    config: SimulationConfig
):
    """Background task to run the simulation."""
    if crypto_id not in cryptos:
        return

    data = cryptos[crypto_id]
    blockchain: BlockchainSimulator = data["blockchain"]
    tokenomics: TokenomicsEngine = data["tokenomics"]
    tx_generator: TransactionGenerator = data["tx_generator"]
    price_sim: PriceSimulator = data["price_sim"]

    sim_state = simulations[simulation_id]
    sim_state.status = SimulationStatus.RUNNING
    sim_state.started_at = datetime.now()

    params = get_intensity_params(config.intensity)
    tx_interval = 1.0 / params["tx_per_second"]
    price_sim.volatility = params["volatility"]

    start_time = datetime.now().timestamp()

    try:
        while sim_state.elapsed_seconds < config.duration_seconds:
            if sim_state.status != SimulationStatus.RUNNING:
                break

            current_time = datetime.now().timestamp()
            sim_state.elapsed_seconds = current_time - start_time

            # Generate transaction
            gen_tx = tx_generator.generate_transaction()
            tx = blockchain.add_transaction(
                from_addr=gen_tx.from_address,
                to_addr=gen_tx.to_address,
                amount=gen_tx.amount
            )

            if tx:
                sim_state.transactions_generated += 1

                # Update tokenomics based on transaction type
                if gen_tx.tx_type.value == "buy":
                    tokenomics.add_buy_pressure(gen_tx.amount)
                elif gen_tx.tx_type.value == "sell":
                    tokenomics.add_sell_pressure(gen_tx.amount)

            # Update price
            tokenomics.calculate_price(current_time)
            price_sim.add_market_impact(
                tokenomics.buy_pressure,
                tokenomics.sell_pressure,
                tokenomics.circulating_supply
            )
            new_price = price_sim.update_price(current_time)
            sim_state.current_price = new_price
            sim_state.price_history.append((current_time, new_price))

            # Create block if needed
            if blockchain.should_create_block():
                block = blockchain.create_block()
                sim_state.blocks_created += 1

                # Apply block reward
                reward = tokenomics.apply_block_reward("MINER")
                if reward > 0:
                    blockchain.add_transaction("SYSTEM", "MINER", reward)

            # Update holder count
            sim_state.holders_count = tx_generator.get_holder_count()

            await asyncio.sleep(tx_interval)

        sim_state.status = SimulationStatus.COMPLETED
        sim_state.ended_at = datetime.now()

    except asyncio.CancelledError:
        sim_state.status = SimulationStatus.PAUSED
    except Exception as e:
        sim_state.status = SimulationStatus.FAILED
        print(f"Simulation error: {e}")


@router.post("/start/{crypto_id}", response_model=StartSimulationResponse)
async def start_simulation(
    crypto_id: str,
    request: StartSimulationRequest,
    background_tasks: BackgroundTasks
):
    """Start a new simulation for a cryptocurrency."""
    if crypto_id not in cryptos:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

    # Check for existing running simulation
    for sim_id, sim in simulations.items():
        if sim.crypto_id == crypto_id and sim.status == SimulationStatus.RUNNING:
            raise HTTPException(
                status_code=400,
                detail=f"Simulation {sim_id} already running for this crypto"
            )

    # Create simulation config and state
    config = SimulationConfig(
        duration_seconds=request.duration_seconds,
        intensity=request.intensity,
        enable_ai_optimization=request.enable_ai_optimization,
    )

    sim_state = SimulationState(
        crypto_id=crypto_id,
        duration_seconds=request.duration_seconds,
        current_price=cryptos[crypto_id]["price_sim"].current_price,
    )

    simulations[sim_state.simulation_id] = sim_state

    # Start background task
    task = asyncio.create_task(
        run_simulation(sim_state.simulation_id, crypto_id, config)
    )
    simulation_tasks[sim_state.simulation_id] = task

    return StartSimulationResponse(
        simulation_id=sim_state.simulation_id,
        crypto_id=crypto_id,
        started_at=datetime.now().isoformat(),
        duration_seconds=request.duration_seconds,
        status="started",
    )


@router.get("/{simulation_id}", response_model=SimulationStateResponse)
async def get_simulation_state(simulation_id: str):
    """Get the current state of a simulation."""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations[simulation_id]
    return SimulationStateResponse(
        simulation_id=sim.simulation_id,
        crypto_id=sim.crypto_id,
        status=sim.status.value,
        progress=sim.progress,
        elapsed_seconds=sim.elapsed_seconds,
        transactions_generated=sim.transactions_generated,
        blocks_created=sim.blocks_created,
        current_price=sim.current_price,
    )


@router.post("/stop/{simulation_id}")
async def stop_simulation(simulation_id: str):
    """Stop a running simulation."""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations[simulation_id]

    if sim.status != SimulationStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Simulation is not running")

    # Cancel the background task
    if simulation_id in simulation_tasks:
        simulation_tasks[simulation_id].cancel()
        del simulation_tasks[simulation_id]

    sim.status = SimulationStatus.PAUSED
    sim.ended_at = datetime.now()

    # Get final state
    crypto_data = cryptos.get(sim.crypto_id, {})

    return {
        "status": "stopped",
        "simulation_id": simulation_id,
        "final_state": sim.to_state_dict(),
        "crypto_stats": crypto_data.get("blockchain", {}).get_stats() if crypto_data else {},
    }


@router.get("/{simulation_id}/summary")
async def get_simulation_summary(simulation_id: str):
    """Get a summary of a completed simulation."""
    if simulation_id not in simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations[simulation_id]
    crypto_data = cryptos.get(sim.crypto_id)

    if not crypto_data:
        raise HTTPException(status_code=404, detail="Crypto data not found")

    price_sim: PriceSimulator = crypto_data["price_sim"]
    tokenomics: TokenomicsEngine = crypto_data["tokenomics"]

    return {
        "simulation": sim.to_state_dict(),
        "performance": {
            "initial_price": price_sim.initial_price,
            "final_price": sim.current_price,
            "price_change_pct": ((sim.current_price - price_sim.initial_price) / price_sim.initial_price) * 100,
            "all_time_high": price_sim.all_time_high,
            "all_time_low": price_sim.all_time_low,
            "volatility_index": price_sim.get_volatility_index(),
        },
        "activity": {
            "total_transactions": sim.transactions_generated,
            "total_blocks": sim.blocks_created,
            "tx_per_second": sim.transactions_generated / max(1, sim.elapsed_seconds),
            "holders": sim.holders_count,
        },
        "market": {
            "market_cap": tokenomics.get_market_cap(),
            "circulating_supply": tokenomics.circulating_supply,
            "supply_ratio": tokenomics.get_supply_ratio(),
        },
    }


def get_simulation(simulation_id: str) -> Optional[SimulationState]:
    """Helper to get simulation from storage."""
    return simulations.get(simulation_id)
