"""
PriceSimulator - Simulates realistic price dynamics.

Features:
- Initial price based on tokenomics
- Realistic fluctuations (Brownian motion)
- Supply/demand impact
- Auto-stabilization
"""

import random
import math
from typing import Optional
from datetime import datetime


class PriceSimulator:
    """Simulates realistic cryptocurrency price movements."""

    def __init__(
        self,
        initial_price: float = 0.01,
        volatility: float = 0.05,
        seed: Optional[int] = None
    ):
        if seed is not None:
            random.seed(seed)

        self.initial_price = initial_price
        self.current_price = initial_price
        self.volatility = volatility  # Max % change per tick

        # Price history: (timestamp, price)
        self.price_history: list[tuple[float, float]] = [
            (datetime.now().timestamp(), initial_price)
        ]

        # Trend parameters
        self.trend: float = 0.0  # Current trend direction (-1 to 1)
        self.trend_strength: float = 0.3
        self.trend_decay: float = 0.95

        # Mean reversion parameters
        self.mean_price: float = initial_price
        self.reversion_strength: float = 0.1

        # Support/resistance levels
        self.support_levels: list[float] = []
        self.resistance_levels: list[float] = []

        # Statistics
        self.all_time_high: float = initial_price
        self.all_time_low: float = initial_price
        self.price_changes: list[float] = []

    def set_initial_price(self, price: float) -> None:
        """Set initial price."""
        self.initial_price = price
        self.current_price = price
        self.mean_price = price
        self.all_time_high = price
        self.all_time_low = price
        self.price_history = [(datetime.now().timestamp(), price)]

    def add_market_impact(self, buy_volume: float, sell_volume: float, total_supply: float) -> float:
        """
        Apply market impact from buy/sell volumes.
        Returns the impact factor.
        """
        if total_supply == 0:
            return 0

        net_flow = buy_volume - sell_volume
        impact = (net_flow / total_supply) * 0.1  # Scale factor

        # Update trend based on market impact
        self.trend = self.trend * self.trend_decay + impact * (1 - self.trend_decay)

        return impact

    def _brownian_motion(self) -> float:
        """Generate Brownian motion component."""
        return random.gauss(0, self.volatility)

    def _mean_reversion(self) -> float:
        """Calculate mean reversion force."""
        if self.mean_price == 0:
            return 0
        deviation = (self.mean_price - self.current_price) / self.mean_price
        return deviation * self.reversion_strength

    def _trend_component(self) -> float:
        """Calculate trend component."""
        return self.trend * self.trend_strength

    def _support_resistance_effect(self) -> float:
        """Calculate effect of support/resistance levels."""
        effect = 0.0

        # Check proximity to support levels
        for support in self.support_levels:
            if 0.95 * support <= self.current_price <= support:
                # Near support, add upward pressure
                effect += 0.02

        # Check proximity to resistance levels
        for resistance in self.resistance_levels:
            if resistance <= self.current_price <= 1.05 * resistance:
                # Near resistance, add downward pressure
                effect -= 0.02

        return effect

    def update_price(self, timestamp: Optional[float] = None) -> float:
        """
        Update price with all components.
        Returns the new price.
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        # Combine all price movement components
        brownian = self._brownian_motion()
        reversion = self._mean_reversion()
        trend = self._trend_component()
        sr_effect = self._support_resistance_effect()

        # Calculate total change
        total_change = brownian + reversion + trend + sr_effect

        # Apply change with volatility cap
        change_factor = max(-self.volatility, min(self.volatility, total_change))
        new_price = self.current_price * (1 + change_factor)

        # Ensure price stays positive
        new_price = max(0.0001, new_price)

        # Update statistics
        price_change = (new_price - self.current_price) / self.current_price if self.current_price > 0 else 0
        self.price_changes.append(price_change)

        # Update state
        self.current_price = new_price
        self.price_history.append((timestamp, new_price))

        # Update all-time stats
        self.all_time_high = max(self.all_time_high, new_price)
        self.all_time_low = min(self.all_time_low, new_price)

        # Update mean price (exponential moving average)
        self.mean_price = self.mean_price * 0.99 + new_price * 0.01

        # Decay trend
        self.trend *= self.trend_decay

        return new_price

    def get_current_price(self) -> float:
        """Get current price."""
        return self.current_price

    def get_price_change_24h(self) -> float:
        """Calculate 24h price change percentage (simulated)."""
        if len(self.price_history) < 2:
            return 0
        old_price = self.price_history[0][1]
        if old_price == 0:
            return 0
        return ((self.current_price - old_price) / old_price) * 100

    def add_support_level(self, price: float) -> None:
        """Add a support level."""
        self.support_levels.append(price)

    def add_resistance_level(self, price: float) -> None:
        """Add a resistance level."""
        self.resistance_levels.append(price)

    def get_volatility_index(self) -> float:
        """Calculate volatility index based on recent price changes."""
        if len(self.price_changes) < 2:
            return 0

        recent_changes = self.price_changes[-20:]  # Last 20 changes
        variance = sum(c ** 2 for c in recent_changes) / len(recent_changes)
        return math.sqrt(variance) * 100  # Return as percentage

    def get_stats(self) -> dict:
        """Get price statistics."""
        return {
            "current_price": self.current_price,
            "initial_price": self.initial_price,
            "all_time_high": self.all_time_high,
            "all_time_low": self.all_time_low,
            "price_change_pct": self.get_price_change_24h(),
            "volatility_index": self.get_volatility_index(),
            "trend": self.trend,
            "data_points": len(self.price_history),
        }

    def get_chart_data(self, limit: int = 100) -> list[dict]:
        """Get price history formatted for charts."""
        history = self.price_history[-limit:] if limit else self.price_history
        return [
            {"timestamp": ts, "price": price}
            for ts, price in history
        ]
