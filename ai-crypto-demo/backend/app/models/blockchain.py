from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import hashlib
import json


class Transaction(BaseModel):
    """A single transaction on the blockchain."""

    tx_hash: str = Field(default="")
    from_address: str
    to_address: str
    amount: float
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    block_index: Optional[int] = None

    def model_post_init(self, __context) -> None:
        """Generate transaction hash after initialization."""
        if not self.tx_hash:
            self.tx_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate SHA-256 hash for the transaction."""
        data = f"{self.from_address}{self.to_address}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class Block(BaseModel):
    """A block in the blockchain."""

    index: int
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    transactions: list[Transaction] = Field(default_factory=list)
    previous_hash: str
    hash: str = Field(default="")
    nonce: int = 0

    def model_post_init(self, __context) -> None:
        """Generate block hash after initialization."""
        if not self.hash:
            self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate SHA-256 hash for the block."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.model_dump() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain(BaseModel):
    """The complete blockchain."""

    chain: list[Block] = Field(default_factory=list)
    pending_transactions: list[Transaction] = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        """Create genesis block if chain is empty."""
        if not self.chain:
            genesis = Block(
                index=0,
                previous_hash="0" * 64,
                transactions=[],
            )
            self.chain.append(genesis)

    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain."""
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to pending transactions."""
        self.pending_transactions.append(transaction)

    def create_block(self, transactions: Optional[list[Transaction]] = None) -> Block:
        """Create a new block with pending or provided transactions."""
        txs = transactions if transactions is not None else self.pending_transactions
        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=txs,
        )
        self.chain.append(new_block)
        if transactions is None:
            self.pending_transactions = []
        return new_block

    def is_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check hash integrity
            if current.previous_hash != previous.hash:
                return False

            # Verify block hash
            expected_hash = current._generate_hash()
            if current.hash != expected_hash:
                return False

        return True
