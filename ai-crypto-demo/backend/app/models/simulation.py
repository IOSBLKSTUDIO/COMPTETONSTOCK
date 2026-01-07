from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class SimulationStatus(str, Enum):
    """Simulation status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationConfig(BaseModel):
    """Configuration for a simulation run."""

    duration_seconds: int = 60
    intensity: str = "medium"  # low, medium, high
    transactions_per_second: float = 5.0
    price_volatility: float = 0.05  # 5% max change per tick
    enable_ai_optimization: bool = True


class SimulationState(BaseModel):
    """Current state of a simulation."""

    simulation_id: str = Field(default_factory=lambda: f"sim_{uuid.uuid4().hex[:8]}")
    crypto_id: str
    status: SimulationStatus = SimulationStatus.PENDING
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 60
    elapsed_seconds: float = 0.0
    transactions_generated: int = 0
    blocks_created: int = 0
    current_price: float = 0.0
    price_history: list[tuple[float, float]] = Field(default_factory=list)
    holders_count: int = 0

    @property
    def progress(self) -> float:
        """Calculate simulation progress (0-1)."""
        if self.duration_seconds == 0:
            return 1.0
        return min(1.0, self.elapsed_seconds / self.duration_seconds)

    def to_state_dict(self) -> dict:
        """Convert to state dictionary for API response."""
        return {
            "simulation_id": self.simulation_id,
            "crypto_id": self.crypto_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "duration_seconds": self.duration_seconds,
            "elapsed_seconds": self.elapsed_seconds,
            "progress": self.progress,
            "transactions_generated": self.transactions_generated,
            "blocks_created": self.blocks_created,
            "current_price": self.current_price,
            "holders_count": self.holders_count,
        }
