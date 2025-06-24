"""
Happy Paisa Blockchain Gateway Service
Bridges traditional backend with Polkadot/Substrate blockchain for Happy Paisa operations
"""
import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from ..services.database import get_collection
from ..models.user import User

logger = logging.getLogger(__name__)

class TransactionType(str, Enum):
    MINT = "mint"
    BURN = "burn"
    TRANSFER = "transfer"
    
class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    FINALIZED = "finalized"

class ChainStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    ERROR = "error"

@dataclass
class BlockchainAddress:
    """Represents a Substrate address"""
    address: str
    public_key: str
    network: str = "happy-paisa-chain"
    
    def to_dict(self):
        return {
            "address": self.address,
            "public_key": self.public_key,
            "network": self.network
        }

@dataclass
class ChainTransaction:
    """Represents a blockchain transaction (extrinsic)"""
    hash: str
    block_number: Optional[int]
    block_hash: Optional[str]
    transaction_type: TransactionType
    from_address: str
    to_address: str
    amount_hp: float
    amount_planck: int  # Smallest unit on chain (1 HP = 1_000_000_000_000 planck)
    status: TransactionStatus
    timestamp: datetime
    gas_fee: float = 0.0
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return {
            "hash": self.hash,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "transaction_type": self.transaction_type,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount_hp": self.amount_hp,
            "amount_planck": self.amount_planck,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "gas_fee": self.gas_fee,
            "metadata": self.metadata or {}
        }

class MockSubstrateChain:
    """
    Mock Substrate chain implementation for development/demo
    In production, this would be replaced with actual Substrate RPC calls
    """
    
    def __init__(self):
        self.current_block = 1000000  # Starting block number
        self.chain_id = "happy-paisa-mainnet"
        self.decimals = 12  # 1 HP = 10^12 planck units
        self.symbol = "HP"
        self.balances = {}  # address -> balance in planck
        self.transactions = {}  # tx_hash -> transaction
        self.pending_transactions = []
        self.block_time = 6  # 6 second block time like Polkadot
        
        # Axzora operational addresses
        self.treasury_address = "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty"
        self.mint_authority = "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty"
        
    async def get_chain_info(self) -> Dict[str, Any]:
        """Get basic chain information"""
        return {
            "chain": self.chain_id,
            "currentBlock": self.current_block,
            "decimals": self.decimals,
            "symbol": self.symbol,
            "blockTime": self.block_time,
            "status": ChainStatus.CONNECTED,
            "treasuryAddress": self.treasury_address,
            "totalSupply": sum(self.balances.values()) / (10 ** self.decimals)
        }
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get account balance"""
        balance_planck = self.balances.get(address, 0)
        balance_hp = balance_planck / (10 ** self.decimals)
        
        return {
            "address": address,
            "balance_planck": balance_planck,
            "balance_hp": balance_hp,
            "balance_inr_equiv": balance_hp * 1000,
            "nonce": 0,  # Simplified
            "is_active": balance_planck > 0
        }
    
    async def submit_extrinsic(self, extrinsic_data: Dict[str, Any]) -> str:
        """Submit a transaction to the chain"""
        tx_hash = f"0x{secrets.token_hex(32)}"
        
        # Create transaction
        transaction = ChainTransaction(
            hash=tx_hash,
            block_number=None,  # Will be set when included in block
            block_hash=None,
            transaction_type=TransactionType(extrinsic_data["type"]),
            from_address=extrinsic_data["from"],
            to_address=extrinsic_data["to"],
            amount_hp=extrinsic_data["amount_hp"],
            amount_planck=int(extrinsic_data["amount_hp"] * (10 ** self.decimals)),
            status=TransactionStatus.PENDING,
            timestamp=datetime.utcnow(),
            gas_fee=0.001,  # Fixed gas fee for demo
            metadata=extrinsic_data.get("metadata", {})
        )
        
        self.transactions[tx_hash] = transaction
        self.pending_transactions.append(tx_hash)
        
        # Simulate block inclusion after a delay
        asyncio.create_task(self._process_pending_transaction(tx_hash))
        
        logger.info(f"Submitted extrinsic {tx_hash} of type {transaction.transaction_type}")
        return tx_hash
    
    async def _process_pending_transaction(self, tx_hash: str):
        """Process a pending transaction (simulate block inclusion)"""
        # Wait for block time
        await asyncio.sleep(self.block_time)
        
        if tx_hash not in self.transactions:
            return
            
        transaction = self.transactions[tx_hash]
        
        try:
            # Validate and execute transaction
            if transaction.transaction_type == TransactionType.MINT:
                # Mint new tokens to treasury/target address
                self.balances[transaction.to_address] = (
                    self.balances.get(transaction.to_address, 0) + transaction.amount_planck
                )
                
            elif transaction.transaction_type == TransactionType.BURN:
                # Burn tokens from address
                current_balance = self.balances.get(transaction.from_address, 0)
                if current_balance >= transaction.amount_planck:
                    self.balances[transaction.from_address] = current_balance - transaction.amount_planck
                else:
                    raise ValueError("Insufficient balance for burn")
                    
            elif transaction.transaction_type == TransactionType.TRANSFER:
                # Transfer between addresses
                from_balance = self.balances.get(transaction.from_address, 0)
                if from_balance >= transaction.amount_planck:
                    self.balances[transaction.from_address] = from_balance - transaction.amount_planck
                    self.balances[transaction.to_address] = (
                        self.balances.get(transaction.to_address, 0) + transaction.amount_planck
                    )
                else:
                    raise ValueError("Insufficient balance for transfer")
            
            # Update transaction status
            self.current_block += 1
            transaction.block_number = self.current_block
            transaction.block_hash = f"0x{secrets.token_hex(32)}"
            transaction.status = TransactionStatus.CONFIRMED
            
            # Remove from pending
            if tx_hash in self.pending_transactions:
                self.pending_transactions.remove(tx_hash)
                
            logger.info(f"Transaction {tx_hash} confirmed in block {self.current_block}")
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            transaction.metadata = transaction.metadata or {}
            transaction.metadata["error"] = str(e)
            logger.error(f"Transaction {tx_hash} failed: {e}")
    
    async def get_transaction(self, tx_hash: str) -> Optional[ChainTransaction]:
        """Get transaction by hash"""
        return self.transactions.get(tx_hash)
    
    async def get_transactions_by_address(self, address: str, limit: int = 50) -> List[ChainTransaction]:
        """Get transactions for an address"""
        address_transactions = []
        for tx in self.transactions.values():
            if tx.from_address == address or tx.to_address == address:
                address_transactions.append(tx)
        
        # Sort by timestamp, newest first
        address_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        return address_transactions[:limit]

class HappyPaisaBlockchainGateway:
    """
    Gateway service that bridges traditional backend with Happy Paisa blockchain
    """
    
    def __init__(self):
        self.chain = MockSubstrateChain()
        self.user_addresses = {}  # user_id -> BlockchainAddress
        self._initialize_system_accounts()
    
    def _initialize_system_accounts(self):
        """Initialize system accounts with some balance"""
        # Set initial treasury balance
        initial_supply_planck = int(1000000 * (10 ** self.chain.decimals))  # 1M HP
        self.chain.balances[self.chain.treasury_address] = initial_supply_planck
    
    async def get_chain_status(self) -> Dict[str, Any]:
        """Get blockchain network status"""
        chain_info = await self.chain.get_chain_info()
        return {
            "status": "operational",
            "network": "happy-paisa-mainnet",
            "chain_info": chain_info,
            "connected_nodes": 5,  # Mock
            "latest_block": chain_info["currentBlock"],
            "block_time_seconds": chain_info["blockTime"],
            "total_supply_hp": chain_info["totalSupply"]
        }
    
    async def get_or_create_user_address(self, user_id: str) -> BlockchainAddress:
        """Get or create a blockchain address for a user"""
        if user_id in self.user_addresses:
            return self.user_addresses[user_id]
        
        # Generate new address (simplified - in production use proper key generation)
        address = f"5{secrets.token_hex(24)}"
        public_key = f"0x{secrets.token_hex(32)}"
        
        blockchain_address = BlockchainAddress(
            address=address,
            public_key=public_key
        )
        
        self.user_addresses[user_id] = blockchain_address
        
        # Store in database
        addresses_collection = await get_collection("blockchain_addresses")
        await addresses_collection.insert_one({
            "user_id": user_id,
            "address": address,
            "public_key": public_key,
            "network": "happy-paisa-chain",
            "created_at": datetime.utcnow()
        })
        
        logger.info(f"Created blockchain address {address} for user {user_id}")
        return blockchain_address
    
    async def get_user_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's Happy Paisa balance on blockchain"""
        address = await self.get_or_create_user_address(user_id)
        balance_info = await self.chain.get_balance(address.address)
        
        return {
            "user_id": user_id,
            "address": address.address,
            "balance_hp": balance_info["balance_hp"],
            "balance_inr_equiv": balance_info["balance_inr_equiv"],
            "balance_planck": balance_info["balance_planck"],
            "network": "happy-paisa-mainnet"
        }
    
    async def mint_happy_paisa(self, user_id: str, amount_hp: float, reference_id: str = None) -> str:
        """Mint new Happy Paisa tokens for a user (INR -> HP conversion)"""
        user_address = await self.get_or_create_user_address(user_id)
        
        extrinsic_data = {
            "type": TransactionType.MINT,
            "from": self.chain.mint_authority,
            "to": user_address.address,
            "amount_hp": amount_hp,
            "metadata": {
                "user_id": user_id,
                "reference_id": reference_id,
                "conversion_rate": 1000,  # 1 HP = 1000 INR
                "inr_amount": amount_hp * 1000
            }
        }
        
        tx_hash = await self.chain.submit_extrinsic(extrinsic_data)
        
        # Store transaction record
        await self._store_transaction_record(tx_hash, user_id, TransactionType.MINT, amount_hp)
        
        logger.info(f"Minted {amount_hp} HP for user {user_id}, tx: {tx_hash}")
        return tx_hash
    
    async def burn_happy_paisa(self, user_id: str, amount_hp: float, reference_id: str = None) -> str:
        """Burn Happy Paisa tokens for a user (HP -> INR conversion)"""
        user_address = await self.get_or_create_user_address(user_id)
        
        # Check if user has sufficient balance
        balance_info = await self.chain.get_balance(user_address.address)
        if balance_info["balance_hp"] < amount_hp:
            raise ValueError(f"Insufficient balance. Available: {balance_info['balance_hp']} HP")
        
        extrinsic_data = {
            "type": TransactionType.BURN,
            "from": user_address.address,
            "to": self.chain.treasury_address,  # Burned tokens go to treasury
            "amount_hp": amount_hp,
            "metadata": {
                "user_id": user_id,
                "reference_id": reference_id,
                "conversion_rate": 1000,
                "inr_amount": amount_hp * 1000
            }
        }
        
        tx_hash = await self.chain.submit_extrinsic(extrinsic_data)
        
        # Store transaction record
        await self._store_transaction_record(tx_hash, user_id, TransactionType.BURN, amount_hp)
        
        logger.info(f"Burned {amount_hp} HP for user {user_id}, tx: {tx_hash}")
        return tx_hash
    
    async def transfer_happy_paisa(self, from_user_id: str, to_user_id: str, amount_hp: float, description: str = None) -> str:
        """Transfer Happy Paisa between users on blockchain"""
        from_address = await self.get_or_create_user_address(from_user_id)
        to_address = await self.get_or_create_user_address(to_user_id)
        
        # Check balance
        balance_info = await self.chain.get_balance(from_address.address)
        if balance_info["balance_hp"] < amount_hp:
            raise ValueError(f"Insufficient balance. Available: {balance_info['balance_hp']} HP")
        
        extrinsic_data = {
            "type": TransactionType.TRANSFER,
            "from": from_address.address,
            "to": to_address.address,
            "amount_hp": amount_hp,
            "metadata": {
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "description": description or "P2P Transfer"
            }
        }
        
        tx_hash = await self.chain.submit_extrinsic(extrinsic_data)
        
        # Store transaction records for both users
        await self._store_transaction_record(tx_hash, from_user_id, TransactionType.TRANSFER, -amount_hp)
        await self._store_transaction_record(tx_hash, to_user_id, TransactionType.TRANSFER, amount_hp)
        
        logger.info(f"Transferred {amount_hp} HP from {from_user_id} to {to_user_id}, tx: {tx_hash}")
        return tx_hash
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get status of a blockchain transaction"""
        transaction = await self.chain.get_transaction(tx_hash)
        if not transaction:
            raise ValueError(f"Transaction {tx_hash} not found")
        
        return transaction.to_dict()
    
    async def get_user_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's blockchain transaction history"""
        user_address = await self.get_or_create_user_address(user_id)
        transactions = await self.chain.get_transactions_by_address(user_address.address, limit)
        
        return [tx.to_dict() for tx in transactions]
    
    async def _store_transaction_record(self, tx_hash: str, user_id: str, tx_type: TransactionType, amount_hp: float):
        """Store transaction record in database for fast querying"""
        transactions_collection = await get_collection("blockchain_transactions")
        
        record = {
            "tx_hash": tx_hash,
            "user_id": user_id,
            "transaction_type": tx_type,
            "amount_hp": amount_hp,
            "amount_inr_equiv": abs(amount_hp) * 1000,
            "created_at": datetime.utcnow(),
            "status": TransactionStatus.PENDING
        }
        
        await transactions_collection.insert_one(record)
    
    async def sync_transaction_status(self, tx_hash: str):
        """Sync transaction status from blockchain to database"""
        chain_tx = await self.chain.get_transaction(tx_hash)
        if not chain_tx:
            return
        
        transactions_collection = await get_collection("blockchain_transactions")
        await transactions_collection.update_many(
            {"tx_hash": tx_hash},
            {
                "$set": {
                    "status": chain_tx.status,
                    "block_number": chain_tx.block_number,
                    "block_hash": chain_tx.block_hash,
                    "confirmed_at": chain_tx.timestamp if chain_tx.status == TransactionStatus.CONFIRMED else None
                }
            }
        )
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        chain_info = await self.chain.get_chain_info()
        
        # Count transactions
        total_transactions = len(self.chain.transactions)
        pending_transactions = len(self.chain.pending_transactions)
        
        # Calculate total addresses
        total_addresses = len(self.chain.balances)
        active_addresses = len([addr for addr, balance in self.chain.balances.items() if balance > 0])
        
        return {
            "network": "happy-paisa-mainnet",
            "latest_block": chain_info["currentBlock"],
            "total_supply_hp": chain_info["totalSupply"],
            "total_transactions": total_transactions,
            "pending_transactions": pending_transactions,
            "total_addresses": total_addresses,
            "active_addresses": active_addresses,
            "average_block_time": chain_info["blockTime"],
            "decimals": chain_info["decimals"],
            "symbol": chain_info["symbol"]
        }

# Global instance
blockchain_gateway = HappyPaisaBlockchainGateway()