from fastapi import APIRouter, HTTPException
from typing import Dict, List
from ..services.wallet_service import WalletService
from ..services.database import get_collection
from ..models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/{user_id}/overview")
async def get_dashboard_overview(user_id: str):
    """Get complete dashboard overview for user"""
    try:
        # Get user info
        user_collection = await get_collection("users")
        user_data = await user_collection.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = User(**user_data)
        
        # Get wallet balance
        wallet_balance = await WalletService.get_balance(user_id)
        
        # Get recent activity counts
        recent_bookings = await get_recent_activity_count("travel_bookings", user_id)
        recent_recharges = await get_recent_activity_count("recharges", user_id)
        recent_orders = await get_recent_activity_count("orders", user_id)
        
        # Mock weather data (in production, call weather API)
        weather_data = {
            "location": user.location or "Nagpur",
            "temperature": "35°C",
            "condition": "Sunny",
            "humidity": "68%",
            "wind": "12 km/h",
            "forecast": "Tomorrow: 32°C, Chance of rain"
        }
        
        # Mock notifications
        notifications = [
            {
                "id": "notif_1",
                "type": "payment",
                "title": "Payment Successful",
                "message": "Your recent transaction was successful",
                "timestamp": datetime.utcnow().isoformat(),
                "read": False
            },
            {
                "id": "notif_2",
                "type": "travel",
                "title": "Travel Reminder",
                "message": "Don't forget to check-in for your upcoming trip",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "read": False
            }
        ]
        
        # Calculate spending insights
        spending_insights = await calculate_spending_insights(user_id)
        
        return {
            "user": user,
            "wallet": {
                "balance_hp": wallet_balance.balance_hp,
                "balance_inr_equiv": wallet_balance.balance_inr_equiv,
                "recent_transactions": wallet_balance.recent_transactions[:5],
                "spending_breakdown": wallet_balance.spending_breakdown
            },
            "activity_summary": {
                "recent_bookings": recent_bookings,
                "recent_recharges": recent_recharges,
                "recent_orders": recent_orders
            },
            "weather": weather_data,
            "notifications": notifications,
            "spending_insights": spending_insights,
            "quick_actions": [
                {"title": "Book Travel", "icon": "plane", "route": "/travel"},
                {"title": "Mobile Recharge", "icon": "smartphone", "route": "/recharge"},
                {"title": "Shop Now", "icon": "shopping-cart", "route": "/shop"},
                {"title": "Add Money", "icon": "wallet", "route": "/wallet"}
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

async def get_recent_activity_count(collection_name: str, user_id: str, days: int = 7) -> int:
    """Get count of recent activities for a user"""
    try:
        collection = await get_collection(collection_name)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = await collection.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        })
        
        return count
    except Exception:
        return 0

async def calculate_spending_insights(user_id: str) -> Dict:
    """Calculate spending insights for the user"""
    try:
        wallet_balance = await WalletService.get_balance(user_id)
        
        # Calculate total spending this month
        current_month_spending = sum(wallet_balance.spending_breakdown.values())
        
        # Mock comparison data (in production, get from previous months)
        previous_month_spending = current_month_spending * 0.85  # 15% increase
        
        spending_change = ((current_month_spending - previous_month_spending) / previous_month_spending * 100) if previous_month_spending > 0 else 0
        
        # Find top spending category
        top_category = max(wallet_balance.spending_breakdown.items(), key=lambda x: x[1]) if wallet_balance.spending_breakdown else ("N/A", 0)
        
        return {
            "current_month_total": current_month_spending,
            "spending_change_percent": round(spending_change, 1),
            "top_category": {
                "name": top_category[0],
                "amount": top_category[1]
            },
            "savings_tip": get_savings_tip(wallet_balance.spending_breakdown)
        }
        
    except Exception:
        return {
            "current_month_total": 0,
            "spending_change_percent": 0,
            "top_category": {"name": "N/A", "amount": 0},
            "savings_tip": "Start tracking your expenses to get personalized savings tips!"
        }

def get_savings_tip(spending_breakdown: Dict[str, float]) -> str:
    """Generate savings tip based on spending patterns"""
    if not spending_breakdown:
        return "Start using Happy Paisa for all transactions to track your spending!"
    
    top_category = max(spending_breakdown.items(), key=lambda x: x[1])
    
    tips = {
        "Food": "Consider cooking at home more often to save on food expenses.",
        "Travel": "Book flights and hotels in advance for better deals.",
        "Shopping": "Look for Happy Paisa rewards and discounts before shopping.",
        "Recharge": "Consider longer validity plans for better value.",
        "Entertainment": "Look for group discounts and Happy Paisa offers."
    }
    
    return tips.get(top_category[0], "Keep tracking your expenses to identify saving opportunities!")

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    try:
        # Get counts from different collections
        stats = {}
        
        # Travel bookings
        travel_collection = await get_collection("travel_bookings")
        stats["total_bookings"] = await travel_collection.count_documents({"user_id": user_id})
        
        # Recharges
        recharge_collection = await get_collection("recharges")
        stats["total_recharges"] = await recharge_collection.count_documents({"user_id": user_id})
        
        # Orders
        orders_collection = await get_collection("orders")
        stats["total_orders"] = await orders_collection.count_documents({"user_id": user_id})
        
        # Transactions
        transactions_collection = await get_collection("transactions")
        stats["total_transactions"] = await transactions_collection.count_documents({"user_id": user_id})
        
        # Wallet balance
        wallet_balance = await WalletService.get_balance(user_id)
        stats["current_balance_hp"] = wallet_balance.balance_hp
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")

@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str, limit: int = 10):
    """Get user notifications"""
    try:
        # In production, this would fetch from a notifications collection
        # For now, return mock notifications
        notifications = [
            {
                "id": f"notif_{i}",
                "type": "info",
                "title": f"Notification {i}",
                "message": f"This is notification message {i}",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "read": i > 2
            }
            for i in range(1, limit + 1)
        ]
        
        return {"notifications": notifications}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        # In production, this would update the notification in database
        return {"message": "Notification marked as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")