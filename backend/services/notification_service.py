import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
from .database import get_collection
from .automation_service import AutomationService
from ..models.automation import AutomationTrigger

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling various notification channels through n8n workflows"""
    
    @staticmethod
    async def send_notification(
        user_id: str,
        notification_type: str,
        message: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification through specified channel
        
        Supported notification_type:
        - telegram: Send Telegram message
        - slack: Send Slack notification
        - sms: Send SMS message
        - email: Send email notification
        """
        try:
            # Get user information
            user_collection = await get_collection("users")
            user_data = await user_collection.find_one({"id": user_id})
            
            if not user_data:
                logger.error(f"User not found: {user_id}")
                return False
            
            # Prepare notification data
            notification_data = {
                "notification_type": notification_type,
                "message": message,
                "user_info": {
                    "id": user_data.get("id"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "mobile": user_data.get("mobile_number")
                },
                "additional_data": additional_data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create automation trigger for notification using lazy import
            from ..models.automation import AutomationTrigger
            
            automation_trigger = AutomationTrigger(
                user_id=user_id,
                event_type="notification_request",
                event_data=notification_data,
                automation_type="messaging"
            )
            
            # Execute notification using lazy import
            from .automation_service import AutomationService
            response = await AutomationService.execute_automation(automation_trigger)
            
            # Store notification record
            await NotificationService._store_notification_record(
                user_id, notification_type, message, response.status == "success"
            )
            
            return response.status == "success"
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return False
    
    @staticmethod
    async def send_transaction_notification(
        user_id: str,
        transaction_data: Dict[str, Any],
        notification_channels: list = ["telegram"]
    ) -> Dict[str, bool]:
        """
        Send transaction notifications across multiple channels
        """
        results = {}
        
        # Prepare transaction message
        transaction_type = transaction_data.get("type", "unknown")
        amount_hp = transaction_data.get("amount_hp", 0)
        amount_inr = transaction_data.get("amount_inr", 0)
        description = transaction_data.get("description", "Transaction")
        
        if transaction_type == "credit":
            message = f"💰 Wallet Credited: {amount_hp} HP (₹{amount_inr:,.2f}) - {description}"
        elif transaction_type == "debit":
            message = f"💳 Payment Processed: {amount_hp} HP (₹{amount_inr:,.2f}) - {description}"
        else:
            message = f"📊 Transaction: {amount_hp} HP (₹{amount_inr:,.2f}) - {description}"
        
        # Send to each channel
        for channel in notification_channels:
            try:
                success = await NotificationService.send_notification(
                    user_id=user_id,
                    notification_type=channel,
                    message=message,
                    additional_data=transaction_data
                )
                results[channel] = success
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results[channel] = False
        
        return results
    
    @staticmethod
    async def send_booking_confirmation(
        user_id: str,
        booking_data: Dict[str, Any],
        notification_channels: list = ["telegram", "email"]
    ) -> Dict[str, bool]:
        """
        Send booking confirmation notifications
        """
        results = {}
        
        # Prepare booking message
        booking_type = booking_data.get("type", "booking")
        description = booking_data.get("description", "Service booked")
        amount_hp = booking_data.get("amount_hp", 0)
        booking_id = booking_data.get("reference_id", "N/A")
        
        message = f"✅ {booking_type.title()} Confirmed!\n"
        message += f"📋 {description}\n"
        message += f"💰 Amount: {amount_hp} HP\n"
        message += f"🆔 Booking ID: {booking_id}"
        
        # Send to each channel
        for channel in notification_channels:
            try:
                success = await NotificationService.send_notification(
                    user_id=user_id,
                    notification_type=channel,
                    message=message,
                    additional_data=booking_data
                )
                results[channel] = success
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results[channel] = False
        
        return results
    
    @staticmethod
    async def send_low_balance_alert(
        user_id: str,
        current_balance: float,
        notification_channels: list = ["telegram", "sms"]
    ) -> Dict[str, bool]:
        """
        Send low balance alert notifications
        """
        results = {}
        
        message = f"⚠️ Low Balance Alert!\n"
        message += f"💰 Current Balance: {current_balance} HP (₹{current_balance * 1000:,.2f})\n"
        message += f"💡 Consider adding funds to continue using Axzora services."
        
        # Send to each channel
        for channel in notification_channels:
            try:
                success = await NotificationService.send_notification(
                    user_id=user_id,
                    notification_type=channel,
                    message=message,
                    additional_data={"balance": current_balance, "alert_type": "low_balance"}
                )
                results[channel] = success
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results[channel] = False
        
        return results
    
    @staticmethod
    async def send_ai_insights_notification(
        user_id: str,
        insights: Dict[str, Any],
        notification_channels: list = ["telegram"]
    ) -> Dict[str, bool]:
        """
        Send AI-generated insights notifications
        """
        results = {}
        
        # Prepare insights message
        message = "🤖 Your AI-Powered Spending Insights\n\n"
        
        if "top_category" in insights:
            message += f"📊 Top Spending: {insights['top_category']}\n"
        
        if "monthly_trend" in insights:
            trend = insights['monthly_trend']
            trend_emoji = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
            message += f"{trend_emoji} Monthly Trend: {trend:+.1f}%\n"
        
        if "recommendations" in insights:
            message += f"\n💡 Recommendations:\n"
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                message += f"{i}. {rec}\n"
        
        # Send to each channel
        for channel in notification_channels:
            try:
                success = await NotificationService.send_notification(
                    user_id=user_id,
                    notification_type=channel,
                    message=message,
                    additional_data=insights
                )
                results[channel] = success
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results[channel] = False
        
        return results
    
    @staticmethod
    async def _store_notification_record(
        user_id: str,
        notification_type: str,
        message: str,
        success: bool
    ):
        """
        Store notification record in database
        """
        try:
            collection = await get_collection("notification_records")
            record = {
                "user_id": user_id,
                "notification_type": notification_type,
                "message": message,
                "success": success,
                "timestamp": datetime.utcnow()
            }
            await collection.insert_one(record)
        except Exception as e:
            logger.error(f"Failed to store notification record: {e}")
    
    @staticmethod
    async def get_user_notifications(user_id: str, limit: int = 50) -> list:
        """
        Get user's notification history
        """
        try:
            collection = await get_collection("notification_records")
            records = await collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    @staticmethod
    async def configure_user_preferences(
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Configure user notification preferences
        """
        try:
            collection = await get_collection("notification_preferences")
            
            preference_record = {
                "user_id": user_id,
                "preferences": preferences,
                "updated_at": datetime.utcnow()
            }
            
            await collection.update_one(
                {"user_id": user_id},
                {"$set": preference_record},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure user preferences: {e}")
            return False
    
    @staticmethod
    async def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """
        Get user notification preferences
        """
        try:
            collection = await get_collection("notification_preferences")
            preferences = await collection.find_one({"user_id": user_id})
            
            if preferences:
                return preferences.get("preferences", {})
            
            # Return default preferences
            return {
                "transaction_notifications": {
                    "telegram": True,
                    "email": False,
                    "sms": False
                },
                "booking_confirmations": {
                    "telegram": True,
                    "email": True,
                    "sms": False
                },
                "low_balance_alerts": {
                    "telegram": True,
                    "sms": True,
                    "email": False
                },
                "ai_insights": {
                    "telegram": True,
                    "email": False,
                    "sms": False
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return {}