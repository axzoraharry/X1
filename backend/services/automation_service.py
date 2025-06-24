import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from ..models.automation import AutomationTrigger, WebhookPayload, AutomationResponse
from ..models.user import User
from ..models.wallet import HappyPaisaTransaction
from .database import get_collection
from .wallet_service import WalletService
from bson import ObjectId

logger = logging.getLogger(__name__)

def json_serializer(obj):
    """Custom JSON serializer for datetime and ObjectId objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class AutomationService:
    """Service for handling n8n workflow automation integrations"""
    
    N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY", "")
    
    @staticmethod
    async def execute_automation(trigger: AutomationTrigger) -> AutomationResponse:
        """
        Execute automation based on trigger type
        """
        try:
            if trigger.automation_type == "messaging":
                return await AutomationService._execute_messaging(trigger)
            elif trigger.automation_type == "ai_processing":
                return await AutomationService._execute_ai_processing(trigger)
            elif trigger.automation_type == "data_sync":
                return await AutomationService._execute_data_sync(trigger)
            elif trigger.automation_type == "backup":
                return await AutomationService._execute_backup(trigger)
            else:
                raise ValueError(f"Unknown automation type: {trigger.automation_type}")
                
        except Exception as e:
            logger.error(f"Automation execution failed: {e}")
            return AutomationResponse(
                trigger_id=trigger.id,
                status="failed",
                error=str(e)
            )
    
    @staticmethod
    async def _execute_messaging(trigger: AutomationTrigger) -> AutomationResponse:
        """
        Execute messaging workflows (Telegram, Slack notifications)
        """
        try:
            # Determine message type based on event
            message_template = await AutomationService._get_message_template(
                trigger.event_type, 
                trigger.event_data
            )
            
            # Get user info for personalization
            user_collection = await get_collection("users")
            user_data = await user_collection.find_one({"id": trigger.user_id})
            
            if not user_data:
                raise ValueError(f"User not found: {trigger.user_id}")
            
            user = User(**user_data)
            
            # Prepare webhook payload for n8n
            webhook_payload = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile_number
                },
                "event": {
                    "type": trigger.event_type,
                    "data": trigger.event_data,
                    "timestamp": trigger.timestamp.isoformat()
                },
                "message": message_template,
                "automation_id": trigger.id
            }
            
            # Trigger n8n workflow
            success = await AutomationService._trigger_n8n_workflow(
                "messaging", 
                webhook_payload
            )
            
            # Store automation record
            await AutomationService._store_automation_record(trigger, "messaging", success)
            
            return AutomationResponse(
                trigger_id=trigger.id,
                status="success" if success else "failed",
                result={"message_sent": success}
            )
            
        except Exception as e:
            logger.error(f"Messaging automation failed: {e}")
            return AutomationResponse(
                trigger_id=trigger.id,
                status="failed",
                error=str(e)
            )
    
    @staticmethod
    async def _execute_ai_processing(trigger: AutomationTrigger) -> AutomationResponse:
        """
        Execute AI processing workflows (OpenAI data processing)
        """
        try:
            # Get user's transaction history for context using lazy import
            from .wallet_service import WalletService
            transactions = await WalletService.get_transactions(trigger.user_id, limit=20)
            
            # Prepare data for AI analysis
            ai_payload = {
                "user_id": trigger.user_id,
                "analysis_type": trigger.event_data.get("analysis_type", "spending_insights"),
                "transaction_data": trigger.event_data.get("transaction_data", {}),
                "transaction_history": [tx.dict() for tx in transactions],
                "timestamp": trigger.timestamp.isoformat(),
                "automation_id": trigger.id
            }
            
            # Trigger n8n AI workflow
            success = await AutomationService._trigger_n8n_workflow(
                "ai_processing", 
                ai_payload
            )
            
            # Store automation record
            await AutomationService._store_automation_record(trigger, "ai_processing", success)
            
            return AutomationResponse(
                trigger_id=trigger.id,
                status="success" if success else "failed",
                result={"ai_processing_triggered": success}
            )
            
        except Exception as e:
            logger.error(f"AI processing automation failed: {e}")
            return AutomationResponse(
                trigger_id=trigger.id,
                status="failed",
                error=str(e)
            )
    
    @staticmethod
    async def _execute_data_sync(trigger: AutomationTrigger) -> AutomationResponse:
        """
        Execute data synchronization workflows
        """
        try:
            # Get user data for sync
            user_collection = await get_collection("users")
            user_data = await user_collection.find_one({"id": trigger.user_id})
            
            # Get wallet data using lazy import
            from .wallet_service import WalletService
            wallet_balance = await WalletService.get_balance(trigger.user_id)
            
            sync_payload = {
                "user_data": user_data,
                "wallet_data": wallet_balance.dict(),
                "sync_type": trigger.event_data.get("sync_type", "full"),
                "destination": trigger.event_data.get("destination", "database"),
                "timestamp": trigger.timestamp.isoformat(),
                "automation_id": trigger.id
            }
            
            # Trigger n8n data sync workflow
            success = await AutomationService._trigger_n8n_workflow(
                "data_sync", 
                sync_payload
            )
            
            # Store automation record
            await AutomationService._store_automation_record(trigger, "data_sync", success)
            
            return AutomationResponse(
                trigger_id=trigger.id,
                status="success" if success else "failed",
                result={"data_sync_triggered": success}
            )
            
        except Exception as e:
            logger.error(f"Data sync automation failed: {e}")
            return AutomationResponse(
                trigger_id=trigger.id,
                status="failed",
                error=str(e)
            )
    
    @staticmethod
    async def _execute_backup(trigger: AutomationTrigger) -> AutomationResponse:
        """
        Execute backup workflows (Google Drive, AWS S3)
        """
        try:
            # Prepare backup data
            backup_data = await AutomationService._prepare_backup_data(
                trigger.user_id,
                trigger.event_data.get("backup_type", "full")
            )
            
            backup_payload = {
                "user_id": trigger.user_id,
                "backup_type": trigger.event_data.get("backup_type", "full"),
                "destination": trigger.event_data.get("destination", "google_drive"),
                "backup_data": backup_data,
                "timestamp": trigger.timestamp.isoformat(),
                "automation_id": trigger.id
            }
            
            # Trigger n8n backup workflow
            success = await AutomationService._trigger_n8n_workflow(
                "backup", 
                backup_payload
            )
            
            # Store automation record
            await AutomationService._store_automation_record(trigger, "backup", success)
            
            return AutomationResponse(
                trigger_id=trigger.id,
                status="success" if success else "failed",
                result={
                    "backup_triggered": success,
                    "backup_id": f"backup_{trigger.user_id}_{int(trigger.timestamp.timestamp())}"
                }
            )
            
        except Exception as e:
            logger.error(f"Backup automation failed: {e}")
            return AutomationResponse(
                trigger_id=trigger.id,
                status="failed",
                error=str(e)
            )
    
    @staticmethod
    async def _trigger_n8n_workflow(workflow_type: str, payload: Dict[str, Any]) -> bool:
        """
        Trigger n8n workflow via webhook
        """
        try:
            # Map workflow types to webhook URLs
            webhook_urls = {
                "messaging": f"{AutomationService.N8N_BASE_URL}/webhook/axzora-messaging",
                "ai_processing": f"{AutomationService.N8N_BASE_URL}/webhook/axzora-ai-processing",
                "data_sync": f"{AutomationService.N8N_BASE_URL}/webhook/axzora-data-sync",
                "backup": f"{AutomationService.N8N_BASE_URL}/webhook/axzora-backup"
            }
            
            webhook_url = webhook_urls.get(workflow_type)
            if not webhook_url:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if AutomationService.N8N_API_KEY:
                headers["Authorization"] = f"Bearer {AutomationService.N8N_API_KEY}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    data=json.dumps(payload, default=json_serializer),
                    headers=headers,
                    timeout=30
                ) as response:
                    success = response.status == 200
                    if not success:
                        logger.error(f"n8n webhook failed: {response.status} - {await response.text()}")
                    else:
                        logger.info(f"n8n webhook success: {workflow_type}")
                    return success
                    
        except Exception as e:
            logger.error(f"Failed to trigger n8n workflow: {e}")
            return False
    
    @staticmethod
    async def _get_message_template(event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Generate message templates based on event type
        """
        templates = {
            "transaction_credit": "💰 Your Happy Paisa wallet has been credited with {amount} HP (₹{inr_amount}). Current balance: {balance} HP",
            "transaction_debit": "💳 Payment of {amount} HP (₹{inr_amount}) processed successfully for {description}. Remaining balance: {balance} HP",
            "travel_booking": "✈️ Your travel booking is confirmed! {description}. Amount: {amount} HP. Booking ID: {reference_id}",
            "recharge_success": "📱 Recharge successful! {description}. Amount: {amount} HP. Your service is now active.",
            "order_placed": "🛒 Order placed successfully! {description}. Amount: {amount} HP. Order ID: {reference_id}",
            "low_balance": "⚠️ Low balance alert! Your Happy Paisa balance is {balance} HP. Consider adding funds to continue using services.",
            "ai_insights": "🤖 AI Insights: {insights}. Recommendations: {recommendations}"
        }
        
        return templates.get(event_type, "📢 Update: {description}")
    
    @staticmethod
    async def _prepare_backup_data(user_id: str, backup_type: str) -> Dict[str, Any]:
        """
        Prepare data for backup based on backup type
        """
        backup_data = {"user_id": user_id, "backup_type": backup_type}
        
        if backup_type in ["full", "profile"]:
            # Get user profile
            user_collection = await get_collection("users")
            user_data = await user_collection.find_one({"id": user_id})
            backup_data["user_profile"] = user_data
        
        if backup_type in ["full", "transactions"]:
            # Get transaction history using lazy import
            from .wallet_service import WalletService
            transactions = await WalletService.get_transactions(user_id, limit=1000)
            backup_data["transactions"] = [tx.dict() for tx in transactions]
        
        if backup_type == "full":
            # Get wallet balance using lazy import
            from .wallet_service import WalletService
            wallet_balance = await WalletService.get_balance(user_id)
            backup_data["wallet_balance"] = wallet_balance.dict()
        
        return backup_data
    
    @staticmethod
    async def _store_automation_record(trigger: AutomationTrigger, automation_type: str, success: bool):
        """
        Store automation execution record
        """
        try:
            collection = await get_collection("automation_records")
            record = {
                "trigger_id": trigger.id,
                "user_id": trigger.user_id,
                "automation_type": automation_type,
                "event_type": trigger.event_type,
                "success": success,
                "timestamp": datetime.utcnow(),
                "event_data": trigger.event_data
            }
            await collection.insert_one(record)
        except Exception as e:
            logger.error(f"Failed to store automation record: {e}")
    
    @staticmethod
    async def handle_webhook(payload: WebhookPayload) -> Dict[str, Any]:
        """
        Handle incoming webhook from n8n workflows
        """
        try:
            # Store webhook result
            collection = await get_collection("webhook_results")
            await collection.insert_one(payload.dict())
            
            # Process webhook based on workflow type
            if "messaging" in payload.workflow_id:
                return await AutomationService._handle_messaging_webhook(payload)
            elif "ai_processing" in payload.workflow_id:
                return await AutomationService._handle_ai_webhook(payload)
            elif "backup" in payload.workflow_id:
                return await AutomationService._handle_backup_webhook(payload)
            else:
                return {"status": "received", "message": "Webhook processed"}
                
        except Exception as e:
            logger.error(f"Webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def _handle_messaging_webhook(payload: WebhookPayload) -> Dict[str, Any]:
        """
        Handle messaging workflow webhook results
        """
        return {
            "status": "message_delivered" if payload.status == "success" else "message_failed",
            "delivery_info": payload.data.get("delivery_info", {})
        }
    
    @staticmethod
    async def _handle_ai_webhook(payload: WebhookPayload) -> Dict[str, Any]:
        """
        Handle AI processing workflow webhook results
        """
        try:
            # Extract AI insights and store them
            insights = payload.data.get("insights", {})
            recommendations = payload.data.get("recommendations", [])
            
            # Store AI results for user
            collection = await get_collection("ai_insights")
            ai_record = {
                "user_id": payload.data.get("user_id"),
                "insights": insights,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow(),
                "workflow_id": payload.workflow_id
            }
            await collection.insert_one(ai_record)
            
            return {
                "status": "ai_processing_complete",
                "insights": insights,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"AI webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def _handle_backup_webhook(payload: WebhookPayload) -> Dict[str, Any]:
        """
        Handle backup workflow webhook results
        """
        return {
            "status": "backup_complete" if payload.status == "success" else "backup_failed",
            "backup_info": payload.data.get("backup_info", {})
        }
    
    @staticmethod
    async def get_user_automations(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's automation history
        """
        try:
            collection = await get_collection("automation_records")
            records = await collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(50).to_list(50)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get user automations: {e}")
            return []
    
    @staticmethod
    async def health_check() -> Dict[str, Any]:
        """
        Check automation service health
        """
        try:
            # Test n8n connectivity
            n8n_healthy = await AutomationService._test_n8n_connection()
            
            return {
                "status": "healthy" if n8n_healthy else "degraded",
                "n8n_connection": "connected" if n8n_healthy else "disconnected",
                "services": {
                    "messaging": "operational",
                    "ai_processing": "operational",
                    "data_sync": "operational",
                    "backup": "operational"
                },
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    @staticmethod
    async def _test_n8n_connection() -> bool:
        """
        Test connection to n8n instance
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{AutomationService.N8N_BASE_URL}/healthz",
                    timeout=10
                ) as response:
                    return response.status == 200
                    
        except Exception:
            return False
    
    @staticmethod
    async def execute_ai_processing(trigger: AutomationTrigger) -> Dict[str, Any]:
        """
        Execute AI processing and return results
        """
        response = await AutomationService._execute_ai_processing(trigger)
        return response.result or {}
    
    @staticmethod
    async def execute_backup(trigger: AutomationTrigger) -> Dict[str, Any]:
        """
        Execute backup and return results
        """
        response = await AutomationService._execute_backup(trigger)
        return response.result or {}