"""
BlockchainSimulator - Simulates a minimal blockchain for the crypto demo.

Features:
- Block generation with SHA-256 hashing
- Transaction validation
- Ledger maintenance (who has how many tokens)
"""

from typing import Optional
from datetime import datetime
from ..models.blockchain import Block, Transaction, Blockchain


class BlockchainSimulator:
    """Simulates a minimal blockchain."""

    def __init__(self):
        self.blockchain = Blockchain()
        self.ledger: dict[str, float] = {}  # address -> balance
        self.block_time: float = 2.0  # seconds between blocks
        self.last_block_time: float = datetime.now().timestamp()

    def initialize(self, initial_distribution: dict[str, float]) -> None:
        """Initialize the blockchain with an initial token distribution."""
        self.ledger = initial_distribution.copy()

    def add_transaction(self, from_addr: str, to_addr: str, amount: float) -> Optional[Transaction]:
        """
        Add a new transaction to pending transactions.
        Returns the transaction if valid, None otherwise.
        """
        # Validate transaction
        if from_addr != "SYSTEM" and self.ledger.get(from_addr, 0) < amount:
            return None  # Insufficient balance

        if amount <= 0:
            return None  # Invalid amount

        # Create transaction
        tx = Transaction(
            from_address=from_addr,
            to_address=to_addr,
            amount=amount,
        )

        # Update ledger
        if from_addr != "SYSTEM":
            self.ledger[from_addr] = self.ledger.get(from_addr, 0) - amount
        self.ledger[to_addr] = self.ledger.get(to_addr, 0) + amount

        # Add to pending
        self.blockchain.add_transaction(tx)

        return tx

    def create_block(self) -> Block:
        """Create a new block with all pending transactions."""
        block = self.blockchain.create_block()
        self.last_block_time = datetime.now().timestamp()

        # Update transaction block indices
        for tx in block.transactions:
            tx.block_index = block.index

        return block

    def should_create_block(self) -> bool:
        """Check if it's time to create a new block."""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_block_time
        has_pending = len(self.blockchain.pending_transactions) > 0

        return time_since_last >= self.block_time and has_pending

    def get_chain(self) -> list[Block]:
        """Get the complete blockchain."""
        return self.blockchain.chain

    def get_balance(self, address: str) -> float:
        """Get the balance of an address."""
        return self.ledger.get(address, 0)

    def get_all_balances(self) -> dict[str, float]:
        """Get all address balances."""
        return self.ledger.copy()

    def get_total_transactions(self) -> int:
        """Get total number of transactions across all blocks."""
        return sum(len(block.transactions) for block in self.blockchain.chain)

    def get_pending_transactions(self) -> list[Transaction]:
        """Get pending transactions."""
        return self.blockchain.pending_transactions

    def is_valid(self) -> bool:
        """Validate the blockchain integrity."""
        return self.blockchain.is_valid()

    def get_stats(self) -> dict:
        """Get blockchain statistics."""
        return {
            "blocks": len(self.blockchain.chain),
            "total_transactions": self.get_total_transactions(),
            "pending_transactions": len(self.blockchain.pending_transactions),
            "unique_addresses": len(self.ledger),
            "is_valid": self.is_valid(),
        }
