#!/usr/bin/env python3
"""
Fix for n8n Automation Integration Circular Import Issue

This script demonstrates how to fix the circular import issue between
automation_service.py, wallet_service.py, and notification_service.py.

The solution involves:
1. Creating a separate module for shared models and utilities
2. Moving common functionality to this module
3. Refactoring the services to avoid circular dependencies

Example implementation:

1. Create a new file: /app/backend/services/common.py with shared functionality
2. Modify automation_service.py to import WalletService only where needed (lazy import)
3. Modify notification_service.py to import AutomationService only where needed
4. Modify wallet_service.py to import NotificationService only where needed

This approach breaks the circular dependency chain while maintaining functionality.
"""

import os
import sys
import re

# Sample implementation of common.py
COMMON_MODULE = """
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Shared utilities and models that would be used across services
class ServiceResult:
    \"\"\"Common result object for service operations\"\"\"
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }

# Common database operations
async def store_record(collection_name: str, record: Dict[str, Any]) -> bool:
    \"\"\"Store a record in the specified collection\"\"\"
    try:
        from .database import get_collection
        collection = await get_collection(collection_name)
        await collection.insert_one(record)
        return True
    except Exception as e:
        logger.error(f"Failed to store record in {collection_name}: {e}")
        return False

# Environment variables access
def get_env_var(name: str, default: str = "") -> str:
    \"\"\"Get environment variable with default value\"\"\"
    return os.environ.get(name, default)
"""

# Fix for automation_service.py - use lazy imports
AUTOMATION_SERVICE_FIX = """
# Import WalletService only where needed using lazy imports
async def _prepare_backup_data(user_id: str, backup_type: str) -> Dict[str, Any]:
    \"\"\"
    Prepare data for backup based on backup type
    \"\"\"
    backup_data = {"user_id": user_id, "backup_type": backup_type}
    
    if backup_type in ["full", "profile"]:
        # Get user profile
        user_collection = await get_collection("users")
        user_data = await user_collection.find_one({"id": user_id})
        backup_data["user_profile"] = user_data
    
    if backup_type in ["full", "transactions"]:
        # Get transaction history - lazy import WalletService
        from .wallet_service import WalletService
        transactions = await WalletService.get_transactions(user_id, limit=1000)
        backup_data["transactions"] = [tx.dict() for tx in transactions]
    
    if backup_type == "full":
        # Get wallet balance - lazy import WalletService
        from .wallet_service import WalletService
        wallet_balance = await WalletService.get_balance(user_id)
        backup_data["wallet_balance"] = wallet_balance.dict()
    
    return backup_data
"""

# Fix for notification_service.py - use lazy imports
NOTIFICATION_SERVICE_FIX = """
async def send_notification(
    user_id: str,
    notification_type: str,
    message: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> bool:
    \"\"\"
    Send notification through specified channel
    
    Supported notification_type:
    - telegram: Send Telegram message
    - slack: Send Slack notification
    - sms: Send SMS message
    - email: Send email notification
    \"\"\"
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
        
        # Create automation trigger for notification
        from ..models.automation import AutomationTrigger
        automation_trigger = AutomationTrigger(
            user_id=user_id,
            event_type="notification_request",
            event_data=notification_data,
            automation_type="messaging"
        )
        
        # Execute notification - lazy import AutomationService
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
"""

# Fix for wallet_service.py - use lazy imports
WALLET_SERVICE_FIX = """
async def add_transaction(transaction: HappyPaisaTransaction) -> bool:
    \"\"\"
    Add a new transaction to the wallet
    \"\"\"
    try:
        # Validate transaction
        if not transaction.user_id:
            raise ValueError("User ID is required")
        
        if transaction.amount_hp <= 0:
            raise ValueError("Transaction amount must be positive")
        
        # Get current balance
        current_balance = await WalletService.get_balance(transaction.user_id)
        
        # For debit transactions, check if sufficient balance
        if transaction.type == "debit" and current_balance.balance_hp < transaction.amount_hp:
            raise ValueError(f"Insufficient balance: {current_balance.balance_hp} HP")
        
        # Calculate new balance
        if transaction.type == "credit":
            new_balance = current_balance.balance_hp + transaction.amount_hp
        else:  # debit
            new_balance = current_balance.balance_hp - transaction.amount_hp
        
        # Update transaction with INR amount
        transaction.amount_inr = transaction.amount_hp * 1000
        
        # Store transaction
        collection = await get_collection("wallet_transactions")
        await collection.insert_one(transaction.dict())
        
        # Update user balance
        await WalletService._update_user_balance(transaction.user_id, new_balance)
        
        # Send notification if enabled - lazy import NotificationService
        try:
            from .notification_service import NotificationService
            await NotificationService.send_transaction_notification(
                transaction.user_id,
                {
                    "type": transaction.type,
                    "amount_hp": transaction.amount_hp,
                    "amount_inr": transaction.amount_inr,
                    "description": transaction.description
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send transaction notification: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        return False
"""

def main():
    print("This script demonstrates how to fix the circular import issue in the n8n automation integration.")
    print("The solution involves refactoring the services to use lazy imports and creating a common module.")
    print("\nTo implement this fix:")
    print("1. Create a new file: /app/backend/services/common.py")
    print("2. Modify automation_service.py to use lazy imports for WalletService")
    print("3. Modify notification_service.py to use lazy imports for AutomationService")
    print("4. Modify wallet_service.py to use lazy imports for NotificationService")
    
    print("\nExample implementation of common.py:")
    print(COMMON_MODULE)
    
    print("\nExample fix for automation_service.py:")
    print(AUTOMATION_SERVICE_FIX)
    
    print("\nExample fix for notification_service.py:")
    print(NOTIFICATION_SERVICE_FIX)
    
    print("\nExample fix for wallet_service.py:")
    print(WALLET_SERVICE_FIX)
    
    print("\nAfter implementing these changes, restart the backend service:")
    print("sudo supervisorctl restart backend")

if __name__ == "__main__":
    main()