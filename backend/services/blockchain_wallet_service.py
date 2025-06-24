"""
Blockchain-enabled Wallet Service
Integrates traditional wallet operations with Happy Paisa blockchain
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..models.wallet import WalletTransaction, WalletBalance
from ..services.database import get_collection
from ..services.blockchain_gateway_service import blockchain_gateway, TransactionType, TransactionStatus

logger = logging.getLogger(__name__)

class BlockchainWalletService:
    """
    Enhanced wallet service that uses Happy Paisa blockchain as the source of truth
    while maintaining local database for fast queries and analytics
    """
    
    @staticmethod
    async def get_balance(user_id: str) -> WalletBalance:
        """Get user balance from blockchain and sync with local database"""
        try:
            # Get balance from blockchain (source of truth)
            blockchain_balance = await blockchain_gateway.get_user_balance(user_id)
            
            # Get recent transactions for context
            recent_transactions = await BlockchainWalletService.get_recent_transactions(user_id, limit=5)
            
            # Calculate spending breakdown from recent transactions
            spending_breakdown = {"Travel": 0, "Recharge": 0, "Shopping": 0, "Other": 0}
            
            for tx in recent_transactions:
                if tx.get("type") == "debit":
                    category = tx.get("category", "Other")
                    if category in spending_breakdown:
                        spending_breakdown[category] += abs(tx.get("amount_hp", 0))
                    else:
                        spending_breakdown["Other"] += abs(tx.get("amount_hp", 0))
            
            wallet_balance = WalletBalance(
                user_id=user_id,
                balance_hp=blockchain_balance["balance_hp"],
                balance_inr_equiv=blockchain_balance["balance_inr_equiv"],
                blockchain_address=blockchain_balance["address"],
                network="happy-paisa-mainnet",
                last_updated=datetime.utcnow(),
                spending_breakdown=spending_breakdown,
                recent_transactions=recent_transactions
            )
            
            # Update local cache for fast access
            await BlockchainWalletService._update_balance_cache(user_id, wallet_balance)
            
            return wallet_balance
            
        except Exception as e:
            logger.error(f"Error getting blockchain balance for user {user_id}: {e}")
            # Fallback to cached balance if blockchain is unavailable
            return await BlockchainWalletService._get_cached_balance(user_id)
    
    @staticmethod
    async def add_transaction(transaction: WalletTransaction) -> str:
        """Add transaction via blockchain and update local records"""
        try:
            blockchain_tx_hash = None
            
            # Determine blockchain operation type
            if transaction.type == "credit" and transaction.category in ["Bonus", "Refund", "Top-up"]:
                # Mint new Happy Paisa (INR -> HP conversion)
                blockchain_tx_hash = await blockchain_gateway.mint_happy_paisa(
                    transaction.user_id,
                    transaction.amount_hp,
                    transaction.id
                )
                transaction.blockchain_hash = blockchain_tx_hash
                
            elif transaction.type == "debit" and transaction.category == "Withdrawal":
                # Burn Happy Paisa (HP -> INR conversion)
                blockchain_tx_hash = await blockchain_gateway.burn_happy_paisa(
                    transaction.user_id,
                    transaction.amount_hp,
                    transaction.id
                )
                transaction.blockchain_hash = blockchain_tx_hash
                
            else:
                # For internal transactions (spending), we don't need blockchain operations
                # The actual spending happens when services like travel/recharge use the funds
                logger.info(f"Internal transaction recorded: {transaction.id}")
            
            # Store transaction in local database for analytics and history
            transactions_collection = await get_collection("wallet_transactions")
            transaction_dict = transaction.dict()
            transaction_dict["created_at"] = datetime.utcnow()
            transaction_dict["blockchain_network"] = "happy-paisa-mainnet"
            
            await transactions_collection.insert_one(transaction_dict)
            
            logger.info(f"Transaction {transaction.id} processed. Blockchain hash: {blockchain_tx_hash}")
            return transaction.id
            
        except Exception as e:
            logger.error(f"Error adding blockchain transaction: {e}")
            raise
    
    @staticmethod
    async def transfer_to_user(from_user_id: str, to_user_id: str, amount_hp: float, description: str) -> str:
        """Transfer Happy Paisa between users via blockchain"""
        try:
            # Execute blockchain transfer
            blockchain_tx_hash = await blockchain_gateway.transfer_happy_paisa(
                from_user_id, to_user_id, amount_hp, description
            )
            
            # Create local transaction records for both users
            from_transaction = WalletTransaction(
                user_id=from_user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Transfer to user: {description}",
                category="Transfer",
                reference_id=to_user_id,
                blockchain_hash=blockchain_tx_hash
            )
            
            to_transaction = WalletTransaction(
                user_id=to_user_id,
                type="credit", 
                amount_hp=amount_hp,
                description=f"Transfer from user: {description}",
                category="Transfer",
                reference_id=from_user_id,
                blockchain_hash=blockchain_tx_hash
            )
            
            # Store both transactions
            transactions_collection = await get_collection("wallet_transactions")
            
            for tx in [from_transaction, to_transaction]:
                tx_dict = tx.dict()
                tx_dict["created_at"] = datetime.utcnow()
                tx_dict["blockchain_network"] = "happy-paisa-mainnet"
                await transactions_collection.insert_one(tx_dict)
            
            logger.info(f"P2P transfer completed: {amount_hp} HP from {from_user_id} to {to_user_id}")
            return blockchain_tx_hash
            
        except Exception as e:
            logger.error(f"Error processing P2P transfer: {e}")
            raise
    
    @staticmethod
    async def process_payment(user_id: str, amount_hp: float, merchant: str, category: str, reference_id: str = None) -> str:
        """Process payment by transferring Happy Paisa to merchant/service"""
        try:
            # For now, payments are internal debits (actual merchant integration would involve transfers)
            payment_transaction = WalletTransaction(
                user_id=user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Payment to {merchant}",
                category=category,
                reference_id=reference_id
            )
            
            transaction_id = await BlockchainWalletService.add_transaction(payment_transaction)
            
            # In a full implementation, this would transfer HP to merchant's blockchain address
            logger.info(f"Payment processed: {amount_hp} HP to {merchant} for {category}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise
    
    @staticmethod
    async def get_recent_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions from local database (fast access)"""
        try:
            transactions_collection = await get_collection("wallet_transactions")
            
            transactions_cursor = transactions_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            transactions = []
            async for tx_doc in transactions_cursor:
                # Convert ObjectId to string for JSON serialization
                tx_doc["_id"] = str(tx_doc["_id"])
                transactions.append(tx_doc)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
    
    @staticmethod
    async def get_blockchain_transactions(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get full blockchain transaction history"""
        try:
            return await blockchain_gateway.get_user_transactions(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting blockchain transactions: {e}")
            return []
    
    @staticmethod
    async def sync_blockchain_state(user_id: str) -> Dict[str, Any]:
        """Sync local state with blockchain state"""
        try:
            # Get latest blockchain balance
            blockchain_balance = await blockchain_gateway.get_user_balance(user_id)
            
            # Get blockchain transactions
            blockchain_transactions = await blockchain_gateway.get_user_transactions(user_id, 100)
            
            # Update local cache
            cache_collection = await get_collection("wallet_cache")
            await cache_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "blockchain_balance": blockchain_balance,
                        "last_sync": datetime.utcnow(),
                        "network": "happy-paisa-mainnet"
                    }
                },
                upsert=True
            )
            
            return {
                "user_id": user_id,
                "synced_balance": blockchain_balance,
                "synced_transactions": len(blockchain_transactions),
                "sync_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing blockchain state: {e}")
            raise
    
    @staticmethod
    async def get_wallet_analytics(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get wallet analytics including blockchain metrics"""
        try:
            # Get current balance
            balance = await BlockchainWalletService.get_balance(user_id)
            
            # Get recent transactions for analysis
            recent_transactions = await BlockchainWalletService.get_recent_transactions(user_id, 100)
            
            # Calculate analytics
            total_spent = sum(tx.get("amount_hp", 0) for tx in recent_transactions if tx.get("type") == "debit")
            total_received = sum(tx.get("amount_hp", 0) for tx in recent_transactions if tx.get("type") == "credit")
            
            # Category breakdown
            category_spending = {}
            for tx in recent_transactions:
                if tx.get("type") == "debit":
                    category = tx.get("category", "Other")
                    category_spending[category] = category_spending.get(category, 0) + tx.get("amount_hp", 0)
            
            # Get blockchain network stats
            network_stats = await blockchain_gateway.get_network_stats()
            
            return {
                "user_analytics": {
                    "current_balance_hp": balance.balance_hp,
                    "current_balance_inr": balance.balance_inr_equiv,
                    "total_spent_hp": total_spent,
                    "total_received_hp": total_received,
                    "transaction_count": len(recent_transactions),
                    "category_spending": category_spending,
                    "blockchain_address": balance.blockchain_address
                },
                "network_info": {
                    "network": network_stats["network"],
                    "latest_block": network_stats["latest_block"],
                    "total_supply": network_stats["total_supply_hp"],
                    "your_percentage_of_supply": (balance.balance_hp / network_stats["total_supply_hp"] * 100) if network_stats["total_supply_hp"] > 0 else 0
                },
                "blockchain_features": {
                    "decentralized": True,
                    "immutable_transactions": True,
                    "transparent_ledger": True,
                    "cross_chain_compatible": True,
                    "polkadot_parachain_ready": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet analytics: {e}")
            raise
    
    @staticmethod
    async def _update_balance_cache(user_id: str, balance: WalletBalance):
        """Update local balance cache for fast access"""
        try:
            cache_collection = await get_collection("wallet_cache")
            await cache_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "balance_hp": balance.balance_hp,
                        "balance_inr_equiv": balance.balance_inr_equiv,
                        "blockchain_address": balance.blockchain_address,
                        "network": balance.network,
                        "last_updated": balance.last_updated,
                        "spending_breakdown": balance.spending_breakdown
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating balance cache: {e}")
    
    @staticmethod
    async def _get_cached_balance(user_id: str) -> WalletBalance:
        """Get cached balance when blockchain is unavailable"""
        try:
            cache_collection = await get_collection("wallet_cache")
            cached_balance = await cache_collection.find_one({"user_id": user_id})
            
            if cached_balance:
                return WalletBalance(
                    user_id=user_id,
                    balance_hp=cached_balance.get("balance_hp", 0),
                    balance_inr_equiv=cached_balance.get("balance_inr_equiv", 0),
                    blockchain_address=cached_balance.get("blockchain_address", ""),
                    network=cached_balance.get("network", "happy-paisa-mainnet"),
                    last_updated=cached_balance.get("last_updated", datetime.utcnow()),
                    spending_breakdown=cached_balance.get("spending_breakdown", {}),
                    recent_transactions=[]
                )
            else:
                # Return empty balance if no cache
                return WalletBalance(
                    user_id=user_id,
                    balance_hp=0.0,
                    balance_inr_equiv=0.0,
                    blockchain_address="",
                    network="happy-paisa-mainnet",
                    last_updated=datetime.utcnow(),
                    spending_breakdown={},
                    recent_transactions=[]
                )
                
        except Exception as e:
            logger.error(f"Error getting cached balance: {e}")
            # Return minimal balance object
            return WalletBalance(
                user_id=user_id,
                balance_hp=0.0,
                balance_inr_equiv=0.0,
                blockchain_address="",
                network="happy-paisa-mainnet",
                last_updated=datetime.utcnow(),
                spending_breakdown={},
                recent_transactions=[]
            )