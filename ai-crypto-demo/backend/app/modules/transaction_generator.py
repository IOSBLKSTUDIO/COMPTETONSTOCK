"""
TransactionGenerator - Generates simulated transactions.

Features:
- Fictive wallet generation
- Simulated trading (buys/sells)
- Random but coherent distribution
"""

import random
import hashlib
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class TransactionType(Enum):
    """Type of transaction."""
    BUY = "buy"
    SELL = "sell"
    TRANSFER = "transfer"


@dataclass
class GeneratedTransaction:
    """A generated transaction ready to be processed."""
    tx_type: TransactionType
    from_address: str
    to_address: str
    amount: float


class TransactionGenerator:
    """Generates simulated transactions for the blockchain."""

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

        self.wallets: list[str] = []
        self.wallet_balances: dict[str, float] = {}
        self.exchange_address = self._generate_address("EXCHANGE")
        self.treasury_address = self._generate_address("TREASURY")

        # Transaction generation parameters
        self.buy_probability: float = 0.45
        self.sell_probability: float = 0.35
        self.transfer_probability: float = 0.20

        # Amount distribution parameters
        self.min_amount: float = 1.0
        self.max_amount: float = 10000.0
        self.whale_threshold: float = 0.1  # 10% chance of whale transaction

    def _generate_address(self, prefix: str = "") -> str:
        """Generate a random wallet address."""
        seed_data = f"{prefix}{random.random()}{random.random()}"
        return "0x" + hashlib.sha256(seed_data.encode()).hexdigest()[:40]

    def initialize_wallets(self, count: int, initial_supply: float) -> dict[str, float]:
        """
        Initialize wallets with initial token distribution.
        Returns the initial distribution.
        """
        self.wallets = [self._generate_address(f"W{i}") for i in range(count)]

        # Distribute tokens with some whales
        remaining = initial_supply
        distribution: dict[str, float] = {}

        # Create a few whale wallets (10% of wallets hold 60% of tokens)
        whale_count = max(1, count // 10)
        whale_share = initial_supply * 0.6 / whale_count

        for i, wallet in enumerate(self.wallets[:whale_count]):
            amount = whale_share * (0.8 + random.random() * 0.4)  # Vary by +/- 20%
            distribution[wallet] = amount
            remaining -= amount

        # Distribute rest to regular wallets
        regular_wallets = self.wallets[whale_count:]
        if regular_wallets:
            share = remaining / len(regular_wallets)
            for wallet in regular_wallets:
                amount = share * (0.5 + random.random())  # Vary by 50-150%
                distribution[wallet] = max(0, amount)

        # Add exchange and treasury
        distribution[self.exchange_address] = initial_supply * 0.1
        distribution[self.treasury_address] = initial_supply * 0.05

        self.wallet_balances = distribution.copy()
        return distribution

    def get_random_wallet(self, exclude: Optional[str] = None) -> str:
        """Get a random wallet address."""
        candidates = [w for w in self.wallets if w != exclude]
        if not candidates:
            return self._generate_address("NEW")
        return random.choice(candidates)

    def generate_transaction(self) -> GeneratedTransaction:
        """
        Generate a single random transaction.
        Returns a GeneratedTransaction instance.
        """
        # Determine transaction type
        rand = random.random()
        if rand < self.buy_probability:
            tx_type = TransactionType.BUY
        elif rand < self.buy_probability + self.sell_probability:
            tx_type = TransactionType.SELL
        else:
            tx_type = TransactionType.TRANSFER

        # Determine amount
        if random.random() < self.whale_threshold:
            # Whale transaction
            amount = random.uniform(self.max_amount * 0.5, self.max_amount)
        else:
            # Normal transaction
            amount = random.uniform(self.min_amount, self.max_amount * 0.1)

        amount = round(amount, 2)

        # Determine addresses based on type
        if tx_type == TransactionType.BUY:
            from_addr = self.exchange_address
            to_addr = self.get_random_wallet()
        elif tx_type == TransactionType.SELL:
            from_addr = self.get_random_wallet()
            to_addr = self.exchange_address
        else:
            from_addr = self.get_random_wallet()
            to_addr = self.get_random_wallet(exclude=from_addr)

        return GeneratedTransaction(
            tx_type=tx_type,
            from_address=from_addr,
            to_address=to_addr,
            amount=amount,
        )

    def generate_batch(self, count: int) -> list[GeneratedTransaction]:
        """Generate multiple transactions."""
        return [self.generate_transaction() for _ in range(count)]

    def update_balance(self, address: str, amount: float, is_add: bool = True) -> None:
        """Update a wallet's balance."""
        current = self.wallet_balances.get(address, 0)
        if is_add:
            self.wallet_balances[address] = current + amount
        else:
            self.wallet_balances[address] = max(0, current - amount)

    def get_holder_count(self) -> int:
        """Get number of wallets with positive balance."""
        return sum(1 for bal in self.wallet_balances.values() if bal > 0)

    def get_distribution_stats(self) -> dict:
        """Get token distribution statistics."""
        balances = list(self.wallet_balances.values())
        if not balances:
            return {"holders": 0, "total": 0, "average": 0, "max": 0, "min": 0}

        return {
            "holders": self.get_holder_count(),
            "total": sum(balances),
            "average": sum(balances) / len(balances),
            "max": max(balances),
            "min": min(b for b in balances if b > 0) if any(b > 0 for b in balances) else 0,
        }
