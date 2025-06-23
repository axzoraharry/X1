from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..models.recharge import RechargePlan, Recharge, RechargeRequest, DTHRecharge, DTHRequest, UtilityBill, UtilityBillRequest
from ..services.database import get_collection
from ..services.wallet_service import WalletService
from ..models.wallet import WalletTransaction
from datetime import datetime

router = APIRouter(prefix="/api/recharge", tags=["recharge"])

# Mock recharge plans
MOCK_PLANS = {
    "jio": [
        {
            "id": "jio_1",
            "operator": "jio",
            "amount": 299,
            "amount_hp": 0.299,
            "validity": "28 days",
            "data": "2GB/day",
            "calls": "Unlimited",
            "sms": "100/day",
            "description": "Popular Plan"
        },
        {
            "id": "jio_2", 
            "operator": "jio",
            "amount": 599,
            "amount_hp": 0.599,
            "validity": "84 days",
            "data": "2GB/day",
            "calls": "Unlimited",
            "sms": "100/day",
            "description": "Long Validity"
        },
        {
            "id": "jio_3",
            "operator": "jio",
            "amount": 149,
            "amount_hp": 0.149,
            "validity": "20 days",
            "data": "1GB/day",
            "calls": "Unlimited",
            "sms": "100/day",
            "description": "Budget Plan"
        }
    ],
    "airtel": [
        {
            "id": "airtel_1",
            "operator": "airtel",
            "amount": 319,
            "amount_hp": 0.319,
            "validity": "30 days",
            "data": "2.5GB/day",
            "calls": "Unlimited",
            "sms": "100/day",
            "description": "Popular Plan"
        },
        {
            "id": "airtel_2",
            "operator": "airtel",
            "amount": 549,
            "amount_hp": 0.549,
            "validity": "56 days",
            "data": "2GB/day",
            "calls": "Unlimited",
            "sms": "100/day",
            "description": "Best Value"
        }
    ]
}

@router.get("/mobile/plans/{operator}", response_model=List[RechargePlan])
async def get_mobile_plans(operator: str):
    """Get mobile recharge plans for an operator"""
    try:
        operator_lower = operator.lower()
        if operator_lower not in MOCK_PLANS:
            raise HTTPException(status_code=404, detail="Operator not found")
        
        plans = [RechargePlan(**plan) for plan in MOCK_PLANS[operator_lower]]
        return plans
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plans: {str(e)}")

@router.get("/mobile/plans", response_model=Dict[str, List[RechargePlan]])
async def get_all_mobile_plans():
    """Get all mobile recharge plans"""
    try:
        all_plans = {}
        for operator, plans in MOCK_PLANS.items():
            all_plans[operator] = [RechargePlan(**plan) for plan in plans]
        return all_plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plans: {str(e)}")

@router.post("/mobile/detect-operator")
async def detect_operator(mobile_number: str):
    """Detect mobile operator from number"""
    try:
        # Simple operator detection based on first few digits
        # In production, this would use a real operator detection service
        
        if mobile_number.startswith(('70', '71', '72', '73', '74', '75', '76', '77', '78', '79')):
            return {"operator": "jio", "circle": "All India"}
        elif mobile_number.startswith(('99', '98', '97', '96', '95', '94', '93', '92', '91', '90')):
            return {"operator": "airtel", "circle": "All India"}
        elif mobile_number.startswith(('89', '88', '87', '86', '85', '84', '83', '82', '81', '80')):
            return {"operator": "vi", "circle": "All India"}
        else:
            return {"operator": "bsnl", "circle": "All India"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operator detection failed: {str(e)}")

@router.post("/mobile/recharge", response_model=Recharge)
async def mobile_recharge(recharge_request: RechargeRequest):
    """Process mobile recharge"""
    try:
        collection = await get_collection("recharges")
        
        # Find the plan
        plan = None
        for operator_plans in MOCK_PLANS.values():
            for p in operator_plans:
                if p["id"] == recharge_request.plan_id:
                    plan = p
                    break
            if plan:
                break
        
        if not plan:
            raise HTTPException(status_code=404, detail="Recharge plan not found")
        
        # Check balance if paying with Happy Paisa
        if recharge_request.payment_method == "happy_paisa":
            balance = await WalletService.get_balance(recharge_request.user_id)
            if balance.balance_hp < plan["amount_hp"]:
                raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
        
        # Create recharge record
        new_recharge = Recharge(
            user_id=recharge_request.user_id,
            mobile_number=recharge_request.mobile_number,
            operator=recharge_request.operator,
            plan_id=recharge_request.plan_id,
            amount=plan["amount"],
            amount_hp=plan["amount_hp"],
            operator_reference=f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Save recharge
        await collection.insert_one(new_recharge.dict())
        
        # Process payment if Happy Paisa
        if recharge_request.payment_method == "happy_paisa":
            transaction = WalletTransaction(
                user_id=recharge_request.user_id,
                type="debit",
                amount_hp=plan["amount_hp"],
                description=f"Mobile recharge - {recharge_request.mobile_number}",
                category="Recharge",
                reference_id=new_recharge.id
            )
            await WalletService.add_transaction(transaction)
        
        return new_recharge
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recharge failed: {str(e)}")

@router.get("/mobile/history/{user_id}", response_model=List[Recharge])
async def get_recharge_history(user_id: str, limit: int = 50):
    """Get user's recharge history"""
    try:
        collection = await get_collection("recharges")
        
        recharges = await collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return [Recharge(**recharge) for recharge in recharges]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recharge history: {str(e)}")

@router.post("/dth/recharge", response_model=DTHRecharge)
async def dth_recharge(dth_request: DTHRequest):
    """Process DTH recharge"""
    try:
        collection = await get_collection("dth_recharges")
        
        # Check balance
        balance = await WalletService.get_balance(dth_request.user_id)
        amount_hp = dth_request.amount / 1000
        
        if balance.balance_hp < amount_hp:
            raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
        
        # Create DTH recharge record
        new_dth_recharge = DTHRecharge(
            user_id=dth_request.user_id,
            customer_id=dth_request.customer_id,
            operator=dth_request.operator,
            amount=dth_request.amount,
            amount_hp=amount_hp
        )
        
        # Save recharge
        await collection.insert_one(new_dth_recharge.dict())
        
        # Process payment
        transaction = WalletTransaction(
            user_id=dth_request.user_id,
            type="debit",
            amount_hp=amount_hp,
            description=f"DTH recharge - {dth_request.operator}",
            category="Recharge",
            reference_id=new_dth_recharge.id
        )
        await WalletService.add_transaction(transaction)
        
        return new_dth_recharge
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DTH recharge failed: {str(e)}")

@router.post("/utility/bill-payment", response_model=UtilityBill)
async def pay_utility_bill(bill_request: UtilityBillRequest):
    """Pay utility bill"""
    try:
        collection = await get_collection("utility_bills")
        
        # Check balance
        balance = await WalletService.get_balance(bill_request.user_id)
        amount_hp = bill_request.amount / 1000
        
        if balance.balance_hp < amount_hp:
            raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
        
        # Create bill payment record
        new_bill_payment = UtilityBill(
            user_id=bill_request.user_id,
            bill_type=bill_request.bill_type,
            consumer_number=bill_request.consumer_number,
            provider=bill_request.provider,
            amount=bill_request.amount,
            amount_hp=amount_hp
        )
        
        # Save bill payment
        await collection.insert_one(new_bill_payment.dict())
        
        # Process payment
        transaction = WalletTransaction(
            user_id=bill_request.user_id,
            type="debit",
            amount_hp=amount_hp,
            description=f"{bill_request.bill_type.title()} bill - {bill_request.provider}",
            category="Utilities",
            reference_id=new_bill_payment.id
        )
        await WalletService.add_transaction(transaction)
        
        return new_bill_payment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bill payment failed: {str(e)}")

@router.get("/history/{user_id}")
async def get_all_recharge_history(user_id: str):
    """Get complete recharge and bill payment history"""
    try:
        # Get mobile recharges
        recharge_collection = await get_collection("recharges")
        recharges = await recharge_collection.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        
        # Get DTH recharges
        dth_collection = await get_collection("dth_recharges")
        dth_recharges = await dth_collection.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        
        # Get utility bills
        utility_collection = await get_collection("utility_bills")
        utility_bills = await utility_collection.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        
        return {
            "mobile_recharges": [Recharge(**r) for r in recharges],
            "dth_recharges": [DTHRecharge(**r) for r in dth_recharges],
            "utility_bills": [UtilityBill(**r) for r in utility_bills]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")