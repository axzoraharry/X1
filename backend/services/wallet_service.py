from typing import List, Dict
from datetime import datetime, timedelta
from ..models.wallet import HappyPaisaWallet, HappyPaisaTransaction, WalletTransaction, WalletBalance
from .database import get_collection
from .notification_service import NotificationService
from ..models.automation import AutomationTrigger
from .automation_service import AutomationService
import logging

logger = logging.getLogger(__name__)

class WalletService:
    
    @staticmethod
    async def get_or_create_wallet(user_id: str) -> HappyPaisaWallet:
        """Get or create a wallet for a user"""
        collection = await get_collection("wallets")
        
        wallet_data = await collection.find_one({"user_id": user_id})
        if wallet_data:
            return HappyPaisaWallet(**wallet_data)
        
        # Create new wallet
        new_wallet = HappyPaisaWallet(user_id=user_id)
        await collection.insert_one(new_wallet.dict())
        return new_wallet
    
    @staticmethod
    async def get_balance(user_id: str) -> WalletBalance:
        """Get wallet balance with recent transactions and spending breakdown"""
        # Get wallet
        wallet = await WalletService.get_or_create_wallet(user_id)
        
        # Get recent transactions
        transactions_collection = await get_collection("transactions")
        recent_transactions = await transactions_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        transaction_objects = [HappyPaisaTransaction(**tx) for tx in recent_transactions]
        
        # Calculate spending breakdown by category
        spending_breakdown = {}
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        spending_cursor = transactions_collection.find({
            "user_id": user_id,
            "type": "debit",
            "timestamp": {"$gte": thirty_days_ago}
        })
        
        async for transaction in spending_cursor:
            category = transaction.get("category", "Other")
            amount = transaction.get("amount_hp", 0)
            spending_breakdown[category] = spending_breakdown.get(category, 0) + amount
        
        return WalletBalance(
            balance_hp=wallet.balance_hp,
            balance_inr_equiv=wallet.balance_inr_equiv,
            recent_transactions=transaction_objects,
            spending_breakdown=spending_breakdown
        )
    
    @staticmethod
    async def add_transaction(transaction: WalletTransaction) -> HappyPaisaTransaction:
        """Add a new transaction and update wallet balance"""
        # Calculate INR equivalent
        amount_inr = transaction.amount_hp * 1000
        
        # Create transaction record
        new_transaction = HappyPaisaTransaction(
            user_id=transaction.user_id,
            type=transaction.type,
            amount_hp=transaction.amount_hp,
            amount_inr=amount_inr,
            description=transaction.description,
            category=transaction.category,
            reference_id=transaction.reference_id
        )
        
        # Insert transaction
        transactions_collection = await get_collection("transactions")
        await transactions_collection.insert_one(new_transaction.dict())
        
        # Update wallet balance
        await WalletService.update_balance(
            transaction.user_id, 
            transaction.amount_hp, 
            transaction.type
        )
        
        # Trigger automation workflows using lazy imports
        try:
            # Lazy import to avoid circular dependency
            from .notification_service import NotificationService
            
            # Send transaction notification
            await NotificationService.send_transaction_notification(
                user_id=transaction.user_id,
                transaction_data=new_transaction.dict(),
                notification_channels=["telegram"]
            )
            
            # Check for low balance alert
            if transaction.type == "debit":
                balance = await WalletService.get_balance(transaction.user_id)
                if balance.balance_hp < 1.0:  # Low balance threshold: 1 HP
                    await NotificationService.send_low_balance_alert(
                        user_id=transaction.user_id,
                        current_balance=balance.balance_hp,
                        notification_channels=["telegram", "sms"]
                    )
            
            # Trigger AI analysis for spending insights (weekly)
            if transaction.type == "debit" and transaction.amount_hp > 0.5:
                # Lazy import to avoid circular dependency
                from ..models.automation import AutomationTrigger
                from .automation_service import AutomationService
                
                automation_trigger = AutomationTrigger(
                    user_id=transaction.user_id,
                    event_type="transaction_analysis",
                    event_data=new_transaction.dict(),
                    automation_type="ai_processing"
                )
                await AutomationService.execute_automation(automation_trigger)
            
        except Exception as e:
            logger.error(f"Failed to trigger transaction automations: {e}")
            # Don't fail the transaction if automation fails
        
        return new_transaction
    
    @staticmethod
    async def update_balance(user_id: str, amount_hp: float, transaction_type: str):
        """Update wallet balance based on transaction"""
        collection = await get_collection("wallets")
        
        # Calculate change
        balance_change = amount_hp if transaction_type == "credit" else -amount_hp
        inr_change = balance_change * 1000
        
        # Update wallet
        await collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "balance_hp": balance_change,
                    "balance_inr_equiv": inr_change
                },
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
    
    @staticmethod
    async def transfer_hp(from_user_id: str, to_user_id: str, amount_hp: float, description: str) -> bool:
        """Transfer Happy Paisa between users"""
        try:
            # Check sender balance
            sender_wallet = await WalletService.get_or_create_wallet(from_user_id)
            if sender_wallet.balance_hp < amount_hp:
                return False
            
            # Create debit transaction for sender
            await WalletService.add_transaction(WalletTransaction(
                user_id=from_user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Transfer to user: {description}",
                category="Transfer"
            ))
            
            # Create credit transaction for receiver
            await WalletService.add_transaction(WalletTransaction(
                user_id=to_user_id,
                type="credit",
                amount_hp=amount_hp,
                description=f"Transfer from user: {description}",
                category="Transfer"
            ))
            
            return True
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return False
    
    @staticmethod
    async def get_transactions(user_id: str, limit: int = 50, offset: int = 0) -> List[HappyPaisaTransaction]:
        """Get user transactions with pagination"""
        collection = await get_collection("transactions")
        
        transactions = await collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).skip(offset).limit(limit).to_list(limit)
        
        return [HappyPaisaTransaction(**tx) for tx in transactions]