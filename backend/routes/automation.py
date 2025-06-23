from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import json
from ..services.automation_service import AutomationService
from ..services.notification_service import NotificationService
from ..models.automation import WebhookPayload, AutomationTrigger, AutomationResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/automation", tags=["automation"])

class TriggerRequest(BaseModel):
    user_id: str
    event_type: str  # transaction, booking, recharge, order, etc.
    event_data: Dict[str, Any]
    automation_type: str  # notification, ai_processing, data_sync, etc.

class WebhookRequest(BaseModel):
    workflow_id: str
    execution_id: str
    status: str
    data: Dict[str, Any]
    timestamp: datetime

@router.post("/trigger/{automation_type}")
async def trigger_automation(
    automation_type: str, 
    trigger_request: TriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger n8n workflows based on app events
    
    Supported automation_type:
    - messaging: Send notifications (Telegram, Slack, SMS)
    - ai_processing: Process data with OpenAI
    - data_sync: Sync data to external systems
    - backup: Backup user data to cloud storage
    """
    try:
        # Validate automation type
        if automation_type not in ['messaging', 'ai_processing', 'data_sync', 'backup']:
            raise HTTPException(status_code=400, detail="Invalid automation type")
        
        # Create automation trigger
        automation_trigger = AutomationTrigger(
            user_id=trigger_request.user_id,
            event_type=trigger_request.event_type,
            event_data=trigger_request.event_data,
            automation_type=automation_type
        )
        
        # Execute automation in background
        background_tasks.add_task(
            AutomationService.execute_automation,
            automation_trigger
        )
        
        return {
            "status": "triggered",
            "automation_type": automation_type,
            "trigger_id": automation_trigger.id,
            "message": f"Automation {automation_type} triggered successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger automation: {e}")
        raise HTTPException(status_code=500, detail=f"Automation trigger failed: {str(e)}")

@router.post("/webhook/n8n")
async def n8n_webhook(webhook_request: WebhookRequest):
    """
    Receive webhook callbacks from n8n workflows
    """
    try:
        # Process webhook payload
        webhook_payload = WebhookPayload(
            workflow_id=webhook_request.workflow_id,
            execution_id=webhook_request.execution_id,
            status=webhook_request.status,
            data=webhook_request.data,
            timestamp=webhook_request.timestamp
        )
        
        # Handle webhook based on workflow type
        result = await AutomationService.handle_webhook(webhook_payload)
        
        return {
            "status": "processed",
            "webhook_id": webhook_payload.id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/notifications/send")
async def send_notification(
    user_id: str,
    notification_type: str,  # telegram, slack, sms, email
    message: str,
    additional_data: Optional[Dict[str, Any]] = None
):
    """
    Send notifications through n8n workflows
    """
    try:
        result = await NotificationService.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            additional_data=additional_data or {}
        )
        
        return {
            "status": "sent" if result else "failed",
            "notification_type": notification_type,
            "message": "Notification sent successfully" if result else "Failed to send notification"
        }
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")

@router.get("/triggers/{user_id}")
async def get_user_automations(user_id: str):
    """
    Get user's automation triggers and their status
    """
    try:
        automations = await AutomationService.get_user_automations(user_id)
        return {
            "user_id": user_id,
            "automations": automations,
            "total": len(automations)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user automations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get automations: {str(e)}")

@router.post("/ai/process-transaction")
async def process_transaction_with_ai(
    user_id: str,
    transaction_data: Dict[str, Any],
    analysis_type: str = "spending_insights"
):
    """
    Process transaction data with AI (OpenAI workflow)
    """
    try:
        # Trigger AI processing workflow
        automation_trigger = AutomationTrigger(
            user_id=user_id,
            event_type="ai_analysis",
            event_data={
                "transaction_data": transaction_data,
                "analysis_type": analysis_type
            },
            automation_type="ai_processing"
        )
        
        result = await AutomationService.execute_ai_processing(automation_trigger)
        
        return {
            "status": "processed",
            "analysis_type": analysis_type,
            "insights": result.get("insights", {}),
            "recommendations": result.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@router.post("/backup/user-data")
async def backup_user_data(
    user_id: str,
    backup_type: str = "full",  # full, transactions, profile
    destination: str = "google_drive"  # google_drive, aws_s3
):
    """
    Backup user data using n8n workflows
    """
    try:
        automation_trigger = AutomationTrigger(
            user_id=user_id,
            event_type="data_backup",
            event_data={
                "backup_type": backup_type,
                "destination": destination
            },
            automation_type="backup"
        )
        
        result = await AutomationService.execute_backup(automation_trigger)
        
        return {
            "status": "backup_initiated",
            "backup_type": backup_type,
            "destination": destination,
            "backup_id": result.get("backup_id")
        }
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@router.get("/health")
async def automation_health_check():
    """
    Check automation service health and n8n connectivity
    """
    try:
        health_status = await AutomationService.health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }