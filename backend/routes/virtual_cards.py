"""
Virtual Cards API Routes - Handles all virtual debit card operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..models.virtual_card import (
    VirtualCard, CardCreateRequest, CardUpdateRequest, CardDetailsResponse,
    CardTransaction, CardTransactionRequest, CardStatus, CardControls,
    UserKYC, KYCRequest, KYCStatus
)
from ..services.card_issuing_service import CardIssuingService
from ..services.transaction_authorization_service import TransactionAuthorizationService
from ..services.kyc_service import KYCService

router = APIRouter(prefix="/api/virtual-cards", tags=["virtual-cards"])

# Card Management Endpoints

@router.post("/", response_model=CardDetailsResponse)
async def create_virtual_card(request: CardCreateRequest):
    """Create a new virtual debit card"""
    try:
        card = await CardIssuingService.create_virtual_card(request)
        return await CardIssuingService.get_card_details(card.id, card.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create virtual card")

@router.get("/user/{user_id}", response_model=List[CardDetailsResponse])
async def get_user_cards(user_id: str):
    """Get all virtual cards for a user"""
    try:
        cards = await CardIssuingService.get_user_cards(user_id)
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user cards")

@router.get("/{card_id}", response_model=CardDetailsResponse)
async def get_card_details(card_id: str, user_id: str = Query(...)):
    """Get details of a specific virtual card"""
    try:
        card = await CardIssuingService.get_card_details(card_id, user_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        return card
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get card details")

@router.patch("/{card_id}/status")
async def update_card_status(
    card_id: str, 
    status: CardStatus,
    user_id: str = Query(...)
):
    """Update card status (freeze/unfreeze/block)"""
    try:
        success = await CardIssuingService.update_card_status(card_id, user_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Card not found or update failed")
        
        return {
            "success": True,
            "message": f"Card status updated to {status}",
            "card_id": card_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update card status")

@router.patch("/{card_id}/controls")
async def update_card_controls(
    card_id: str,
    controls: CardControls,
    user_id: str = Query(...)
):
    """Update card spending controls and limits"""
    try:
        success = await CardIssuingService.update_card_controls(card_id, user_id, controls)
        if not success:
            raise HTTPException(status_code=404, detail="Card not found or update failed")
        
        return {
            "success": True,
            "message": "Card controls updated successfully",
            "card_id": card_id,
            "controls": controls
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update card controls")

@router.post("/{card_id}/load")
async def load_card_funds(
    card_id: str,
    amount_hp: float = Query(..., description="Amount in Happy Paisa to load"),
    user_id: str = Query(...)
):
    """Load Happy Paisa funds onto the card"""
    try:
        if amount_hp <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        success = await CardIssuingService.load_card_funds(card_id, amount_hp)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to load funds")
        
        return {
            "success": True,
            "message": f"Loaded {amount_hp} HP onto card",
            "card_id": card_id,
            "amount_hp": amount_hp,
            "amount_inr": amount_hp * 1000
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load card funds")

# Transaction Endpoints

@router.get("/{card_id}/transactions", response_model=List[CardTransaction])
async def get_card_transactions(
    card_id: str,
    user_id: str = Query(...),
    limit: int = Query(default=50, le=100)
):
    """Get transaction history for a card"""
    try:
        transactions = await CardIssuingService.get_card_transactions(card_id, user_id, limit)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get card transactions")

@router.post("/{card_id}/authorize", response_model=dict)
async def authorize_transaction(card_id: str, request: CardTransactionRequest):
    """Authorize a card transaction (simulates real-time authorization)"""
    try:
        # Ensure card_id matches
        request.card_id = card_id
        
        authorization_result = await TransactionAuthorizationService.authorize_transaction(request)
        return authorization_result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to authorize transaction")

@router.post("/simulate-transaction")
async def simulate_card_transaction(request: CardTransactionRequest):
    """Simulate a card transaction for testing purposes"""
    try:
        authorization_result = await TransactionAuthorizationService.authorize_transaction(request)
        
        if authorization_result["authorized"]:
            return {
                "success": True,
                "message": "Transaction approved",
                "transaction_id": authorization_result["transaction_id"],
                "authorization_code": authorization_result["authorization_code"],
                "amount_inr": authorization_result["amount_inr"],
                "amount_hp": authorization_result["amount_hp"]
            }
        else:
            return {
                "success": False,
                "message": "Transaction declined",
                "decline_reason": authorization_result["decline_reason"],
                "response_code": authorization_result["response_code"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to simulate transaction")

# KYC Endpoints

@router.post("/kyc/initiate", response_model=UserKYC)
async def initiate_kyc(request: KYCRequest):
    """Initiate KYC process for card issuance"""
    try:
        kyc_record = await KYCService.initiate_kyc(request)
        return kyc_record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initiate KYC")

@router.get("/kyc/user/{user_id}", response_model=UserKYC)
async def get_kyc_status(user_id: str):
    """Get KYC status for a user"""
    try:
        kyc_record = await KYCService.get_kyc_status(user_id)
        if not kyc_record:
            raise HTTPException(status_code=404, detail="KYC record not found")
        return kyc_record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get KYC status")

@router.get("/kyc/requirements")
async def get_kyc_requirements():
    """Get KYC requirements and document types"""
    try:
        requirements = await KYCService.get_kyc_requirements()
        return requirements
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get KYC requirements")

@router.post("/kyc/verify-document")
async def verify_document(document_type: str, document_number: str):
    """Verify a document with external APIs (simulation)"""
    try:
        verification_result = await KYCService.simulate_document_verification(
            document_type, document_number
        )
        return verification_result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to verify document")

@router.patch("/kyc/{kyc_id}/status")
async def update_kyc_status(
    kyc_id: str,
    status: KYCStatus,
    reviewer_id: str = Query(default="admin"),
    rejection_reason: Optional[str] = Query(default=None)
):
    """Update KYC status (approve/reject) - Admin endpoint"""
    try:
        success = await KYCService.update_kyc_status(
            kyc_id, status, reviewer_id, rejection_reason
        )
        if not success:
            raise HTTPException(status_code=404, detail="KYC record not found")
        
        return {
            "success": True,
            "message": f"KYC status updated to {status}",
            "kyc_id": kyc_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update KYC status")

# Demo/Testing Endpoints

@router.post("/demo/create-kyc")
async def create_demo_kyc(user_id: str, full_name: str):
    """Create demo KYC for testing (auto-approved)"""
    try:
        kyc_record = await KYCService.create_demo_kyc_for_user(user_id, full_name)
        return {
            "success": True,
            "message": "Demo KYC created and approved",
            "kyc_id": kyc_record.id,
            "user_id": user_id,
            "status": kyc_record.kyc_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create demo KYC")

@router.get("/demo/card-networks")
async def get_supported_card_networks():
    """Get supported card networks and their features"""
    return {
        "networks": [
            {
                "name": "RuPay",
                "description": "India's domestic card payment network",
                "features": ["Lower transaction costs", "Government backing", "Wide acceptance"],
                "supported": True
            },
            {
                "name": "Visa",
                "description": "Global payment network",
                "features": ["International acceptance", "Premium features", "Advanced security"],
                "supported": True
            },
            {
                "name": "Mastercard", 
                "description": "Global payment network",
                "features": ["International acceptance", "Wide merchant network", "Digital wallet support"],
                "supported": True
            }
        ],
        "default_network": "RuPay",
        "recommendation": "RuPay for domestic transactions, Visa/Mastercard for international"
    }

@router.get("/health")
async def card_service_health():
    """Health check for virtual cards service"""
    return {
        "status": "healthy",
        "service": "virtual_cards",
        "features": {
            "card_issuance": "operational",
            "transaction_authorization": "operational", 
            "kyc_verification": "operational",
            "fraud_detection": "operational"
        },
        "supported_operations": [
            "create_virtual_card",
            "freeze_unfreeze_card",
            "set_spending_limits",
            "real_time_authorization",
            "transaction_history",
            "kyc_verification"
        ]
    }