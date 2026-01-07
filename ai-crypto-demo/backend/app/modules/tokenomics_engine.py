"""
TokenomicsEngine - Manages the token economics.

Features:
- Supply management (fixed or inflationary)
- Price calculation based on supply/demand
- Inflation schedule
- Holder distribution tracking
"""

from typing import Optional
from ..models.cryptocurrency import TokenomicsConfig, Cryptocurrency


class TokenomicsEngine:
    """Manages token economics and price dynamics."""

    def __init__(self, config: Optional[TokenomicsConfig] = None):
        self.config = config or TokenomicsConfig()
        self.circulating_supply: float = 0.0
        self.total_supply: float = self.config.total_supply
        self.current_price: float = self.config.initial_price
        self.buy_pressure: float = 0.0
        self.sell_pressure: float = 0.0
        self.price_history: list[tuple[float, float]] = []  # (timestamp, price)

    def initialize(self, crypto: Cryptocurrency) -> None:
        """Initialize tokenomics for a cryptocurrency."""
        self.total_supply = crypto.total_supply
        self.current_price = crypto.current_price
        self.circulating_supply = crypto.circulating_supply

    def update_supply(self, amount: float, is_mint: bool = True) -> float:
        """
        Update circulating supply.
        Returns the new circulating supply.
        """
        if is_mint:
            self.circulating_supply = min(
                self.circulating_supply + amount,
                self.total_supply
            )
        else:
            self.circulating_supply = max(0, self.circulating_supply - amount)

        return self.circulating_supply

    def add_buy_pressure(self, amount: float) -> None:
        """Add buying pressure to the market."""
        self.buy_pressure += amount

    def add_sell_pressure(self, amount: float) -> None:
        """Add selling pressure to the market."""
        self.sell_pressure += amount

    def calculate_price(self, timestamp: float) -> float:
        """
        Calculate current price based on supply/demand dynamics.
        Uses a simple model: price = base_price * (1 + net_pressure * stability_factor)
        """
        net_pressure = self.buy_pressure - self.sell_pressure

        # Normalize pressure relative to circulating supply
        if self.circulating_supply > 0:
            pressure_ratio = net_pressure / self.circulating_supply
        else:
            pressure_ratio = 0

        # Apply stability factor to dampen volatility
        price_change = pressure_ratio * self.config.stability_factor

        # Calculate new price with bounds
        new_price = self.current_price * (1 + price_change)
        new_price = max(self.config.min_price, min(self.config.max_price, new_price))

        # Update state
        self.current_price = new_price
        self.price_history.append((timestamp, new_price))

        # Decay pressure over time
        self.buy_pressure *= 0.9
        self.sell_pressure *= 0.9

        return new_price

    def get_inflation(self) -> float:
        """Get current inflation rate."""
        return self.config.inflation_rate

    def apply_block_reward(self, miner_address: str) -> float:
        """
        Apply block reward (minting new tokens).
        Returns the reward amount.
        """
        reward = self.config.block_reward

        # Check if we can mint more tokens
        if self.circulating_supply + reward > self.total_supply:
            reward = self.total_supply - self.circulating_supply

        if reward > 0:
            self.update_supply(reward, is_mint=True)

        return reward

    def get_market_cap(self) -> float:
        """Calculate current market capitalization."""
        return self.circulating_supply * self.current_price

    def get_fully_diluted_valuation(self) -> float:
        """Calculate fully diluted valuation."""
        return self.total_supply * self.current_price

    def get_supply_ratio(self) -> float:
        """Get ratio of circulating to total supply."""
        if self.total_supply == 0:
            return 0
        return self.circulating_supply / self.total_supply

    def get_stats(self) -> dict:
        """Get tokenomics statistics."""
        return {
            "total_supply": self.total_supply,
            "circulating_supply": self.circulating_supply,
            "current_price": self.current_price,
            "market_cap": self.get_market_cap(),
            "fdv": self.get_fully_diluted_valuation(),
            "supply_ratio": self.get_supply_ratio(),
            "inflation_rate": self.get_inflation(),
            "buy_pressure": self.buy_pressure,
            "sell_pressure": self.sell_pressure,
        }
