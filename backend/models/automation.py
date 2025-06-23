from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class AutomationTrigger(BaseModel):
    """Model for automation trigger events"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    event_type: str  # transaction, booking, recharge, order, etc.
    event_data: Dict[str, Any]
    automation_type: str  # messaging, ai_processing, data_sync, backup
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, processing, completed, failed

class WebhookPayload(BaseModel):
    """Model for n8n webhook payloads"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    execution_id: str
    status: str  # success, failed, running
    data: Dict[str, Any]
    timestamp: datetime
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class AutomationResponse(BaseModel):
    """Model for automation execution responses"""
    trigger_id: str
    status: str  # success, failed, pending
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreferences(BaseModel):
    """Model for user notification preferences"""
    user_id: str
    telegram_enabled: bool = True
    telegram_chat_id: Optional[str] = None
    slack_enabled: bool = False
    slack_channel: Optional[str] = None
    email_enabled: bool = True
    sms_enabled: bool = False
    
    # Notification types
    transaction_notifications: bool = True
    booking_confirmations: bool = True
    low_balance_alerts: bool = True
    ai_insights_notifications: bool = True
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AutomationRule(BaseModel):
    """Model for automation rules and conditions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    rule_name: str
    trigger_condition: Dict[str, Any]  # Conditions that trigger the automation
    automation_type: str
    automation_config: Dict[str, Any]  # Configuration for the automation
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AIInsight(BaseModel):
    """Model for AI-generated insights"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str  # spending_analysis, recommendation, trend_analysis
    insights: Dict[str, Any]
    recommendations: List[str] = []
    confidence_score: float = 0.0
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    workflow_id: Optional[str] = None

class BackupRecord(BaseModel):
    """Model for backup operation records"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    backup_type: str  # full, transactions, profile
    destination: str  # google_drive, aws_s3
    backup_size: Optional[int] = None  # Size in bytes
    status: str = "initiated"  # initiated, in_progress, completed, failed
    backup_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class WorkflowTemplate(BaseModel):
    """Model for n8n workflow templates"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str  # messaging, ai_processing, data_sync, backup
    workflow_json: Dict[str, Any]  # n8n workflow definition
    webhook_url: str
    required_config: List[str] = []  # Required configuration parameters
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AutomationMetrics(BaseModel):
    """Model for automation metrics and analytics"""
    user_id: str
    date: datetime
    total_automations: int = 0
    successful_automations: int = 0
    failed_automations: int = 0
    automation_types: Dict[str, int] = {}  # Count by automation type
    notification_channels: Dict[str, int] = {}  # Count by notification channel
    average_response_time: float = 0.0  # Average time in seconds
    updated_at: datetime = Field(default_factory=datetime.utcnow)