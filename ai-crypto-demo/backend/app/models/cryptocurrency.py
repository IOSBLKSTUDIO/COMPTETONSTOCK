from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class TokenomicsConfig(BaseModel):
    """Configuration for token economics."""

    total_supply: float = 1_000_000
    initial_price: float = 0.01
    inflation_rate: float = 0.02  # 2% annual
    block_reward: float = 50.0
    holder_distribution: dict[str, float] = Field(default_factory=dict)
    stability_factor: float = 0.1  # How much supply/demand affects price
    min_price: float = 0.0001
    max_price: float = 1000.0


class Cryptocurrency(BaseModel):
    """A cryptocurrency instance."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    symbol: str
    total_supply: float
    circulating_supply: float = 0.0
    current_price: float
    created_at: datetime = Field(default_factory=datetime.now)
    tokenomics: Optional[TokenomicsConfig] = None

    @property
    def market_cap(self) -> float:
        """Calculate market capitalization."""
        return self.circulating_supply * self.current_price

    def to_state_dict(self) -> dict:
        """Convert to state dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "total_supply": self.total_supply,
            "circulating_supply": self.circulating_supply,
            "current_price": self.current_price,
            "market_cap": self.market_cap,
            "created_at": self.created_at.isoformat(),
        }
