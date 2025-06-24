"""
Card Management API Routes - Additional card management and administrative functions
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ..models.virtual_card import (
    CardStatus, TransactionStatus, MerchantCategory, CardControls
)
from ..services.database import get_collection

router = APIRouter(prefix="/api/card-management", tags=["card-management"])

@router.get("/analytics/spending")
async def get_spending_analytics(
    user_id: str = Query(...),
    card_id: Optional[str] = Query(None),
    days: int = Query(default=30, le=365)
):
    """Get spending analytics for cards"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {
            "user_id": user_id,
            "transaction_type": "purchase",
            "transaction_status": "approved",
            "created_at": {"$gte": cutoff_date}
        }
        
        if card_id:
            query["card_id"] = card_id
        
        transactions_collection = await get_collection("card_transactions")
        
        # Spending by category
        category_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$merchant_category",
                    "total_amount_inr": {"$sum": "$amount_inr"},
                    "total_amount_hp": {"$sum": "$amount_hp"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_amount_inr": -1}}
        ]
        
        category_spending = await transactions_collection.aggregate(category_pipeline).to_list(None)
        
        # Daily spending
        daily_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
                    },
                    "total_amount_inr": {"$sum": "$amount_inr"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.date": 1}}
        ]
        
        daily_spending = await transactions_collection.aggregate(daily_pipeline).to_list(None)
        
        # Total statistics
        total_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_spent_inr": {"$sum": "$amount_inr"},
                    "total_spent_hp": {"$sum": "$amount_hp"},
                    "total_transactions": {"$sum": 1},
                    "avg_transaction_inr": {"$avg": "$amount_inr"}
                }
            }
        ]
        
        total_stats = await transactions_collection.aggregate(total_pipeline).to_list(1)
        total_stats = total_stats[0] if total_stats else {
            "total_spent_inr": 0,
            "total_spent_hp": 0,
            "total_transactions": 0,
            "avg_transaction_inr": 0
        }
        
        return {
            "period_days": days,
            "total_statistics": total_stats,
            "spending_by_category": category_spending,
            "daily_spending": daily_spending,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get spending analytics")

@router.get("/analytics/merchant-insights")
async def get_merchant_insights(
    user_id: str = Query(...),
    days: int = Query(default=30, le=365)
):
    """Get merchant spending insights"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        transactions_collection = await get_collection("card_transactions")
        
        # Top merchants
        merchant_pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "transaction_type": "purchase",
                    "transaction_status": "approved",
                    "created_at": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": "$merchant_name",
                    "total_spent_inr": {"$sum": "$amount_inr"},
                    "transaction_count": {"$sum": 1},
                    "avg_transaction_inr": {"$avg": "$amount_inr"},
                    "last_transaction": {"$max": "$created_at"},
                    "categories": {"$addToSet": "$merchant_category"}
                }
            },
            {"$sort": {"total_spent_inr": -1}},
            {"$limit": 20}
        ]
        
        top_merchants = await transactions_collection.aggregate(merchant_pipeline).to_list(None)
        
        return {
            "period_days": days,
            "top_merchants": top_merchants,
            "insights": {
                "total_unique_merchants": len(top_merchants),
                "most_frequent_merchant": top_merchants[0]["_id"] if top_merchants else None,
                "highest_spending_merchant": top_merchants[0]["_id"] if top_merchants else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get merchant insights")

@router.get("/controls/templates")
async def get_control_templates():
    """Get predefined card control templates"""
    templates = {
        "conservative": CardControls(
            daily_limit_inr=10000,
            monthly_limit_inr=50000,
            per_transaction_limit_inr=5000,
            allowed_merchant_categories=[
                MerchantCategory.GROCERIES,
                MerchantCategory.UTILITIES,
                MerchantCategory.HEALTHCARE
            ],
            international_transactions_enabled=False,
            online_transactions_enabled=True,
            atm_withdrawals_enabled=True
        ),
        "standard": CardControls(
            daily_limit_inr=25000,
            monthly_limit_inr=100000,
            per_transaction_limit_inr=15000,
            blocked_merchant_categories=[
                MerchantCategory.ATM_WITHDRAWAL
            ],
            international_transactions_enabled=False,
            online_transactions_enabled=True,
            atm_withdrawals_enabled=True
        ),
        "premium": CardControls(
            daily_limit_inr=50000,
            monthly_limit_inr=200000,
            per_transaction_limit_inr=25000,
            allowed_merchant_categories=list(MerchantCategory),
            international_transactions_enabled=True,
            online_transactions_enabled=True,
            atm_withdrawals_enabled=True
        ),
        "travel": CardControls(
            daily_limit_inr=30000,
            monthly_limit_inr=150000,
            per_transaction_limit_inr=20000,
            allowed_merchant_categories=[
                MerchantCategory.TRAVEL,
                MerchantCategory.RESTAURANTS,
                MerchantCategory.ENTERTAINMENT,
                MerchantCategory.FUEL,
                MerchantCategory.GROCERIES
            ],
            international_transactions_enabled=True,
            online_transactions_enabled=True,
            atm_withdrawals_enabled=True
        )
    }
    
    return {
        "templates": templates,
        "recommendations": {
            "new_users": "conservative",
            "regular_users": "standard",
            "high_volume_users": "premium",
            "frequent_travelers": "travel"
        }
    }

@router.get("/fraud-alerts/{user_id}")
async def get_fraud_alerts(user_id: str, days: int = Query(default=7, le=30)):
    """Get fraud alerts and suspicious activities"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        transactions_collection = await get_collection("card_transactions")
        
        # Find suspicious patterns
        alerts = []
        
        # High amount transactions
        high_amount_transactions = await transactions_collection.find({
            "user_id": user_id,
            "amount_inr": {"$gte": 20000},
            "created_at": {"$gte": cutoff_date}
        }).to_list(None)
        
        for txn in high_amount_transactions:
            alerts.append({
                "type": "high_amount",
                "severity": "medium",
                "transaction_id": txn["id"],
                "amount_inr": txn["amount_inr"],
                "merchant": txn["merchant_name"],
                "timestamp": txn["created_at"],
                "message": f"High amount transaction: ₹{txn['amount_inr']:,.2f}"
            })
        
        # Multiple transactions in short time
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "transaction_type": "purchase",
                    "created_at": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "hour": {"$dateToString": {"format": "%Y-%m-%d %H", "date": "$created_at"}}
                    },
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$amount_inr"},
                    "transactions": {"$push": "$$ROOT"}
                }
            },
            {
                "$match": {"count": {"$gte": 5}}
            }
        ]
        
        frequent_transactions = await transactions_collection.aggregate(pipeline).to_list(None)
        
        for group in frequent_transactions:
            alerts.append({
                "type": "frequent_transactions",
                "severity": "high",
                "count": group["count"],
                "hour": group["_id"]["hour"],
                "total_amount_inr": group["total_amount"],
                "message": f"Multiple transactions ({group['count']}) in same hour"
            })
        
        return {
            "period_days": days,
            "alerts_count": len(alerts),
            "alerts": sorted(alerts, key=lambda x: x.get("timestamp", datetime.min), reverse=True),
            "summary": {
                "high_severity": len([a for a in alerts if a.get("severity") == "high"]),
                "medium_severity": len([a for a in alerts if a.get("severity") == "medium"]),
                "low_severity": len([a for a in alerts if a.get("severity") == "low"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get fraud alerts")

@router.get("/compliance/transaction-limits")
async def get_compliance_limits():
    """Get regulatory compliance limits and requirements"""
    return {
        "rbi_ppi_limits": {
            "minimum_kyc": {
                "daily_limit_inr": 10000,
                "monthly_limit_inr": 10000,
                "annual_limit_inr": 120000,
                "description": "Limits for minimum KYC PPI as per RBI Master Direction"
            },
            "full_kyc": {
                "daily_limit_inr": 200000,
                "monthly_limit_inr": 200000,
                "annual_limit_inr": 2400000,
                "description": "Limits for full KYC PPI as per RBI Master Direction"
            }
        },
        "recommended_limits": {
            "conservative": {
                "daily_limit_inr": 25000,
                "monthly_limit_inr": 100000,
                "per_transaction_limit_inr": 15000
            },
            "standard": {
                "daily_limit_inr": 50000,
                "monthly_limit_inr": 200000,
                "per_transaction_limit_inr": 25000
            }
        },
        "compliance_notes": [
            "All limits subject to RBI PPI Master Direction",
            "KYC requirements must be met for higher limits",
            "International transaction limits may be different",
            "Merchant category restrictions may apply"
        ]
    }

@router.get("/statistics/system")
async def get_system_statistics():
    """Get system-wide card statistics (admin endpoint)"""
    try:
        cards_collection = await get_collection("virtual_cards")
        transactions_collection = await get_collection("card_transactions")
        kyc_collection = await get_collection("user_kyc")
        
        # Card statistics
        total_cards = await cards_collection.count_documents({})
        active_cards = await cards_collection.count_documents({"card_status": "active"})
        frozen_cards = await cards_collection.count_documents({"card_status": "frozen"})
        
        # Transaction statistics
        total_transactions = await transactions_collection.count_documents({})
        approved_transactions = await transactions_collection.count_documents({"transaction_status": "approved"})
        declined_transactions = await transactions_collection.count_documents({"transaction_status": "declined"})
        
        # Volume statistics
        volume_pipeline = [
            {
                "$match": {
                    "transaction_type": "purchase",
                    "transaction_status": "approved"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_volume_inr": {"$sum": "$amount_inr"},
                    "total_volume_hp": {"$sum": "$amount_hp"},
                    "avg_transaction_inr": {"$avg": "$amount_inr"}
                }
            }
        ]
        
        volume_stats = await transactions_collection.aggregate(volume_pipeline).to_list(1)
        volume_stats = volume_stats[0] if volume_stats else {
            "total_volume_inr": 0,
            "total_volume_hp": 0,
            "avg_transaction_inr": 0
        }
        
        # KYC statistics
        total_kyc = await kyc_collection.count_documents({})
        approved_kyc = await kyc_collection.count_documents({"kyc_status": "approved"})
        pending_kyc = await kyc_collection.count_documents({"kyc_status": {"$in": ["in_progress", "under_review"]}})
        
        return {
            "cards": {
                "total": total_cards,
                "active": active_cards,
                "frozen": frozen_cards,
                "utilization_rate": round((active_cards / total_cards * 100) if total_cards > 0 else 0, 2)
            },
            "transactions": {
                "total": total_transactions,
                "approved": approved_transactions,
                "declined": declined_transactions,
                "approval_rate": round((approved_transactions / total_transactions * 100) if total_transactions > 0 else 0, 2)
            },
            "volume": volume_stats,
            "kyc": {
                "total": total_kyc,
                "approved": approved_kyc,
                "pending": pending_kyc,
                "approval_rate": round((approved_kyc / total_kyc * 100) if total_kyc > 0 else 0, 2)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get system statistics")