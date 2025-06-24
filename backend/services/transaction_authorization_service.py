"""
Transaction Authorization Service - Real-time transaction processing
Handles authorization, fraud detection, and real-time balance updates
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..models.virtual_card import (
    VirtualCard, CardTransaction, CardTransactionRequest, 
    TransactionStatus, CardStatus, MerchantCategory
)
from ..services.database import get_collection
from ..services.wallet_service import WalletService
from ..models.wallet import WalletTransaction

logger = logging.getLogger(__name__)

class TransactionAuthorizationService:
    """Service for real-time transaction authorization"""
    
    @staticmethod
    async def authorize_transaction(request: CardTransactionRequest) -> Dict[str, Any]:
        """
        Authorize a card transaction in real-time
        This simulates the authorization flow that would happen via card networks
        """
        try:
            # Get card details
            cards_collection = await get_collection("virtual_cards")
            card_doc = await cards_collection.find_one({"id": request.card_id})
            
            if not card_doc:
                return {
                    "authorized": False,
                    "decline_reason": "CARD_NOT_FOUND",
                    "response_code": "05"
                }
            
            card = VirtualCard(**card_doc)
            
            # Check card status
            if card.card_status != CardStatus.ACTIVE:
                return {
                    "authorized": False,
                    "decline_reason": f"CARD_{card.card_status.upper()}",
                    "response_code": "54"
                }
            
            # Check card expiry
            if datetime.utcnow() > card.expires_at:
                return {
                    "authorized": False,
                    "decline_reason": "CARD_EXPIRED",
                    "response_code": "54"
                }
            
            # Convert amount to Happy Paisa
            amount_hp = request.amount_inr / 1000
            
            # Check daily spending limit
            daily_spent = await TransactionAuthorizationService._get_daily_spending(card.id)
            if daily_spent + request.amount_inr > card.controls.daily_limit_inr:
                return {
                    "authorized": False,
                    "decline_reason": "DAILY_LIMIT_EXCEEDED",
                    "response_code": "61"
                }
            
            # Check monthly spending limit
            monthly_spent = await TransactionAuthorizationService._get_monthly_spending(card.id)
            if monthly_spent + request.amount_inr > card.controls.monthly_limit_inr:
                return {
                    "authorized": False,
                    "decline_reason": "MONTHLY_LIMIT_EXCEEDED",
                    "response_code": "61"
                }
            
            # Check per transaction limit
            if request.amount_inr > card.controls.per_transaction_limit_inr:
                return {
                    "authorized": False,
                    "decline_reason": "TRANSACTION_LIMIT_EXCEEDED",
                    "response_code": "61"
                }
            
            # Check merchant category restrictions
            if request.merchant_category in card.controls.blocked_merchant_categories:
                return {
                    "authorized": False,
                    "decline_reason": "MERCHANT_CATEGORY_BLOCKED",
                    "response_code": "57"
                }
            
            if (card.controls.allowed_merchant_categories and 
                request.merchant_category not in card.controls.allowed_merchant_categories):
                return {
                    "authorized": False,
                    "decline_reason": "MERCHANT_CATEGORY_NOT_ALLOWED",
                    "response_code": "57"
                }
            
            # Check card balance (if using prepaid model)
            if card.current_balance_inr < request.amount_inr:
                # Try to auto-load from Happy Paisa wallet
                user_hp_balance_obj = await WalletService.get_balance(card.user_id)
                user_hp_balance = user_hp_balance_obj.balance_hp
                if user_hp_balance >= amount_hp:
                    # Auto-load from wallet
                    await TransactionAuthorizationService._auto_load_from_wallet(
                        card, amount_hp
                    )
                else:
                    return {
                        "authorized": False,
                        "decline_reason": "INSUFFICIENT_FUNDS",
                        "response_code": "51"
                    }
            
            # Fraud check (simplified)
            fraud_score = await TransactionAuthorizationService._calculate_fraud_score(
                card, request
            )
            if fraud_score > 80:  # High fraud risk
                return {
                    "authorized": False,
                    "decline_reason": "SUSPECTED_FRAUD",
                    "response_code": "59"
                }
            
            # Authorization approved - create transaction record
            authorization_code = f"AXZ{secrets.token_hex(3).upper()}"
            
            transaction = CardTransaction(
                card_id=request.card_id,
                user_id=card.user_id,
                transaction_type="purchase",
                amount_inr=request.amount_inr,
                amount_hp=amount_hp,
                merchant_name=request.merchant_name,
                merchant_category=request.merchant_category,
                description=request.description,
                location=request.location,
                transaction_status=TransactionStatus.APPROVED,
                authorization_code=authorization_code,
                processed_at=datetime.utcnow(),
                metadata=request.metadata or {}
            )
            
            # Save transaction
            transactions_collection = await get_collection("card_transactions")
            await transactions_collection.insert_one(transaction.dict())
            
            # Update card balance and last used time
            await cards_collection.update_one(
                {"id": request.card_id},
                {
                    "$inc": {
                        "current_balance_inr": -request.amount_inr,
                        "current_balance_hp": -amount_hp
                    },
                    "$set": {
                        "last_used_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Create corresponding wallet transaction for tracking
            wallet_transaction = WalletTransaction(
                user_id=card.user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Card purchase - {request.merchant_name}",
                category="Card Transaction",
                reference_id=transaction.id
            )
            await WalletService.add_transaction(wallet_transaction)
            
            logger.info(f"Transaction authorized: {transaction.id} for amount {request.amount_inr} INR")
            
            return {
                "authorized": True,
                "transaction_id": transaction.id,
                "authorization_code": authorization_code,
                "amount_inr": request.amount_inr,
                "amount_hp": amount_hp,
                "response_code": "00",
                "message": "APPROVED"
            }
            
        except Exception as e:
            logger.error(f"Error authorizing transaction: {e}")
            return {
                "authorized": False,
                "decline_reason": "SYSTEM_ERROR",
                "response_code": "96"
            }
    
    @staticmethod
    async def _get_daily_spending(card_id: str) -> float:
        """Get total spending for current day"""
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            transactions_collection = await get_collection("card_transactions")
            pipeline = [
                {
                    "$match": {
                        "card_id": card_id,
                        "transaction_type": "purchase",
                        "transaction_status": "approved",
                        "created_at": {"$gte": today_start, "$lt": today_end}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount_inr"}
                    }
                }
            ]
            
            result = await transactions_collection.aggregate(pipeline).to_list(1)
            return result[0]["total"] if result else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating daily spending: {e}")
            return 0.0
    
    @staticmethod
    async def _get_monthly_spending(card_id: str) -> float:
        """Get total spending for current month"""
        try:
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            transactions_collection = await get_collection("card_transactions")
            pipeline = [
                {
                    "$match": {
                        "card_id": card_id,
                        "transaction_type": "purchase",
                        "transaction_status": "approved",
                        "created_at": {"$gte": month_start}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount_inr"}
                    }
                }
            ]
            
            result = await transactions_collection.aggregate(pipeline).to_list(1)
            return result[0]["total"] if result else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating monthly spending: {e}")
            return 0.0
    
    @staticmethod
    async def _auto_load_from_wallet(card: VirtualCard, amount_hp: float) -> bool:
        """Auto-load card from user's Happy Paisa wallet"""
        try:
            # Deduct from user's wallet
            wallet_transaction = WalletTransaction(
                user_id=card.user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Auto-load to card {card.card_number_masked}",
                category="Card Auto Load",
                reference_id=card.id
            )
            await WalletService.add_transaction(wallet_transaction)
            
            # Add to card balance
            amount_inr = amount_hp * 1000
            cards_collection = await get_collection("virtual_cards")
            await cards_collection.update_one(
                {"id": card.id},
                {
                    "$inc": {
                        "current_balance_hp": amount_hp,
                        "current_balance_inr": amount_inr
                    }
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error auto-loading card: {e}")
            return False
    
    @staticmethod
    async def _calculate_fraud_score(card: VirtualCard, request: CardTransactionRequest) -> int:
        """Calculate fraud risk score (0-100)"""
        try:
            score = 0
            
            # Check for unusual spending patterns
            recent_transactions = await TransactionAuthorizationService._get_recent_transactions(card.id)
            
            # High amount compared to usual spending
            if recent_transactions:
                avg_amount = sum(t.amount_inr for t in recent_transactions) / len(recent_transactions)
                if request.amount_inr > avg_amount * 3:
                    score += 30
            
            # Multiple transactions in short time
            recent_count = len([t for t in recent_transactions 
                              if (datetime.utcnow() - t.created_at).seconds < 300])  # 5 minutes
            if recent_count > 3:
                score += 25
            
            # High-risk merchant categories
            high_risk_categories = [MerchantCategory.ATM_WITHDRAWAL, MerchantCategory.FUEL]
            if request.merchant_category in high_risk_categories:
                score += 15
            
            # Late night transactions
            current_hour = datetime.utcnow().hour
            if current_hour < 6 or current_hour > 23:
                score += 10
            
            return min(score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Error calculating fraud score: {e}")
            return 0
    
    @staticmethod
    async def _get_recent_transactions(card_id: str, hours: int = 24) -> list:
        """Get recent transactions for fraud analysis"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            transactions_collection = await get_collection("card_transactions")
            transactions_cursor = transactions_collection.find({
                "card_id": card_id,
                "transaction_type": "purchase",
                "created_at": {"$gte": cutoff_time}
            }).sort("created_at", -1)
            
            transactions = []
            async for txn_doc in transactions_cursor:
                transactions.append(CardTransaction(**txn_doc))
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []