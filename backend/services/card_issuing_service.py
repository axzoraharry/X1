"""
Card Issuing Service - Manages virtual debit card lifecycle
Handles card creation, management, and integration with external partners
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..models.virtual_card import (
    VirtualCard, CardCreateRequest, CardUpdateRequest, CardDetailsResponse,
    CardTransaction, CardTransactionRequest, CardStatus, TransactionStatus,
    UserKYC, KYCStatus, KYCRequest, CardControls
)
from ..services.database import get_collection
from ..services.wallet_service import WalletService
from ..models.wallet import WalletTransaction

logger = logging.getLogger(__name__)

class CardIssuingService:
    """Service for managing virtual debit card operations"""
    
    @staticmethod
    def _generate_card_number() -> str:
        """Generate a mock card number for demo purposes"""
        # Using a test BIN range (starting with 4000 for Visa test cards)
        # In production, this would come from the bank/issuer partner
        prefix = "4000"  # Test card prefix
        middle = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
        
        # Generate check digit using Luhn algorithm
        digits = prefix + middle
        check_digit = CardIssuingService._luhn_checksum(digits)
        
        return digits + str(check_digit)
    
    @staticmethod
    def _luhn_checksum(card_num: str) -> int:
        """Calculate Luhn checksum for card number validation"""
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return (10 - (checksum % 10)) % 10
    
    @staticmethod
    def _mask_card_number(card_number: str) -> str:
        """Mask card number for display (show only last 4 digits)"""
        if len(card_number) < 8:
            return "*" * len(card_number)
        return f"****-****-****-{card_number[-4:]}"
    
    @staticmethod
    def _hash_sensitive_data(data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def _generate_cvv() -> str:
        """Generate a 3-digit CVV"""
        return f"{secrets.randbelow(1000):03d}"
    
    @staticmethod
    def _generate_expiry_date() -> tuple:
        """Generate expiry date (3 years from now)"""
        expiry = datetime.utcnow() + timedelta(days=365*3)
        return expiry.month, expiry.year, expiry
    
    @staticmethod
    async def check_user_kyc_status(user_id: str) -> KYCStatus:
        """Check if user has completed KYC for card issuance"""
        try:
            kyc_collection = await get_collection("user_kyc")
            kyc_record = await kyc_collection.find_one({"user_id": user_id})
            
            if not kyc_record:
                return KYCStatus.NOT_STARTED
            
            kyc_data = UserKYC(**kyc_record)
            return kyc_data.kyc_status
        except Exception as e:
            logger.error(f"Error checking KYC status for user {user_id}: {e}")
            return KYCStatus.NOT_STARTED
    
    @staticmethod
    async def create_virtual_card(request: CardCreateRequest) -> VirtualCard:
        """Create a new virtual debit card for a user"""
        try:
            # Check KYC status
            kyc_status = await CardIssuingService.check_user_kyc_status(request.user_id)
            if kyc_status != KYCStatus.APPROVED:
                raise ValueError(f"User KYC not approved. Current status: {kyc_status}")
            
            # Check if user already has an active card
            cards_collection = await get_collection("virtual_cards")
            existing_card = await cards_collection.find_one({
                "user_id": request.user_id,
                "card_status": {"$in": ["active", "frozen"]}
            })
            
            if existing_card:
                raise ValueError("User already has an active virtual card")
            
            # Generate card details
            card_number = CardIssuingService._generate_card_number()
            cvv = CardIssuingService._generate_cvv()
            expiry_month, expiry_year, expires_at = CardIssuingService._generate_expiry_date()
            
            # Create card object
            card = VirtualCard(
                user_id=request.user_id,
                card_number_masked=CardIssuingService._mask_card_number(card_number),
                card_number_hash=CardIssuingService._hash_sensitive_data(card_number),
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                cvv_hash=CardIssuingService._hash_sensitive_data(cvv),
                card_holder_name=request.card_holder_name,
                expires_at=expires_at,
                controls=request.controls or CardControls(),
                metadata=request.metadata or {}
            )
            
            # Store card in database
            await cards_collection.insert_one(card.dict())
            
            # Load initial amount if specified
            if request.initial_load_amount_hp > 0:
                await CardIssuingService.load_card_funds(
                    card.id, 
                    request.initial_load_amount_hp
                )
            
            logger.info(f"Virtual card created successfully for user {request.user_id}: {card.id}")
            return card
            
        except Exception as e:
            logger.error(f"Error creating virtual card: {e}")
            raise
    
    @staticmethod
    async def get_card_details(card_id: str, user_id: str) -> Optional[CardDetailsResponse]:
        """Get card details for display"""
        try:
            cards_collection = await get_collection("virtual_cards")
            card_doc = await cards_collection.find_one({
                "id": card_id,
                "user_id": user_id
            })
            
            if not card_doc:
                return None
            
            card = VirtualCard(**card_doc)
            return CardDetailsResponse(
                id=card.id,
                user_id=card.user_id,
                card_number_masked=card.card_number_masked,
                expiry_month=card.expiry_month,
                expiry_year=card.expiry_year,
                card_holder_name=card.card_holder_name,
                card_type=card.card_type,
                card_status=card.card_status,
                network=card.network,
                current_balance_inr=card.current_balance_inr,
                current_balance_hp=card.current_balance_hp,
                controls=card.controls,
                created_at=card.created_at,
                last_used_at=card.last_used_at,
                expires_at=card.expires_at
            )
        except Exception as e:
            logger.error(f"Error getting card details: {e}")
            return None
    
    @staticmethod
    async def get_user_cards(user_id: str) -> List[CardDetailsResponse]:
        """Get all cards for a user"""
        try:
            cards_collection = await get_collection("virtual_cards")
            cards_cursor = cards_collection.find({"user_id": user_id})
            cards = []
            
            async for card_doc in cards_cursor:
                card = VirtualCard(**card_doc)
                cards.append(CardDetailsResponse(
                    id=card.id,
                    user_id=card.user_id,
                    card_number_masked=card.card_number_masked,
                    expiry_month=card.expiry_month,
                    expiry_year=card.expiry_year,
                    card_holder_name=card.card_holder_name,
                    card_type=card.card_type,
                    card_status=card.card_status,
                    network=card.network,
                    current_balance_inr=card.current_balance_inr,
                    current_balance_hp=card.current_balance_hp,
                    controls=card.controls,
                    created_at=card.created_at,
                    last_used_at=card.last_used_at,
                    expires_at=card.expires_at
                ))
            
            return cards
        except Exception as e:
            logger.error(f"Error getting user cards: {e}")
            return []
    
    @staticmethod
    async def update_card_status(card_id: str, user_id: str, status: CardStatus) -> bool:
        """Update card status (freeze/unfreeze/block)"""
        try:
            cards_collection = await get_collection("virtual_cards")
            result = await cards_collection.update_one(
                {"id": card_id, "user_id": user_id},
                {
                    "$set": {
                        "card_status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating card status: {e}")
            return False
    
    @staticmethod
    async def update_card_controls(card_id: str, user_id: str, controls: CardControls) -> bool:
        """Update card spending controls and limits"""
        try:
            cards_collection = await get_collection("virtual_cards")
            result = await cards_collection.update_one(
                {"id": card_id, "user_id": user_id},
                {
                    "$set": {
                        "controls": controls.dict(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating card controls: {e}")
            return False
    
    @staticmethod
    async def load_card_funds(card_id: str, amount_hp: float) -> bool:
        """Load Happy Paisa funds onto the card from user's wallet"""
        try:
            cards_collection = await get_collection("virtual_cards")
            card_doc = await cards_collection.find_one({"id": card_id})
            
            if not card_doc:
                raise ValueError("Card not found")
            
            card = VirtualCard(**card_doc)
            
            # Check user's Happy Paisa balance
            user_balance = await WalletService.get_balance(card.user_id)
            if user_balance < amount_hp:
                raise ValueError("Insufficient Happy Paisa balance")
            
            # Deduct from user's wallet
            wallet_transaction = WalletTransaction(
                user_id=card.user_id,
                type="debit",
                amount_hp=amount_hp,
                description=f"Card load - {card.card_number_masked}",
                category="Card Load",
                reference_id=card.id
            )
            await WalletService.add_transaction(wallet_transaction)
            
            # Add to card balance
            amount_inr = amount_hp * 1000  # Convert HP to INR
            await cards_collection.update_one(
                {"id": card_id},
                {
                    "$inc": {
                        "current_balance_hp": amount_hp,
                        "current_balance_inr": amount_inr
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Create card transaction record
            card_transaction = CardTransaction(
                card_id=card.id,
                user_id=card.user_id,
                transaction_type="load",
                amount_inr=amount_inr,
                amount_hp=amount_hp,
                merchant_name="Axzora Card Load",
                description=f"Card load from Happy Paisa wallet",
                transaction_status=TransactionStatus.APPROVED,
                authorization_code=f"AXZ{secrets.token_hex(4).upper()}"
            )
            
            transactions_collection = await get_collection("card_transactions")
            await transactions_collection.insert_one(card_transaction.dict())
            
            logger.info(f"Card {card_id} loaded with {amount_hp} HP")
            return True
            
        except Exception as e:
            logger.error(f"Error loading card funds: {e}")
            raise
    
    @staticmethod
    async def get_card_transactions(card_id: str, user_id: str, limit: int = 50) -> List[CardTransaction]:
        """Get transaction history for a card"""
        try:
            transactions_collection = await get_collection("card_transactions")
            transactions_cursor = transactions_collection.find(
                {"card_id": card_id, "user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            transactions = []
            async for txn_doc in transactions_cursor:
                transactions.append(CardTransaction(**txn_doc))
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting card transactions: {e}")
            return []