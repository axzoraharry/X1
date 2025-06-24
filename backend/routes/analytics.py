"""
Analytics API Routes for Axzora Mr. Happy 2.0
Provides endpoints for tracking events and retrieving analytics data
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Request Models
class EventTrackingRequest(BaseModel):
    event_name: str = Field(..., description="Name of the event to track")
    user_id: Optional[str] = Field(None, description="User identifier")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Event parameters")

class UserJourneyRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    journey_step: str = Field(..., description="Current step in user journey")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class BusinessMetricRequest(BaseModel):
    metric_name: str = Field(..., description="Name of the business metric")
    value: float = Field(..., description="Metric value")
    currency: str = Field("HP", description="Currency code")
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ErrorTrackingRequest(BaseModel):
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    user_id: Optional[str] = Field(None, description="User identifier")
    endpoint: Optional[str] = Field(None, description="API endpoint where error occurred")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

class PerformanceMetricRequest(BaseModel):
    operation_name: str = Field(..., description="Name of the operation")
    duration_ms: float = Field(..., description="Operation duration in milliseconds")
    success: bool = Field(..., description="Whether operation was successful")
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional performance data")

# Axzora-specific request models
class HappyPaisaTransactionRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    transaction_type: str = Field(..., description="Type of transaction (credit/debit)")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency (HP/INR)")
    transaction_id: str = Field(..., description="Unique transaction identifier")

class BookingEventRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    booking_type: str = Field(..., description="Type of booking (flight/hotel/recharge)")
    booking_id: str = Field(..., description="Unique booking identifier")
    amount: float = Field(..., description="Booking amount")
    status: str = Field(..., description="Booking status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional booking data")

class VoiceCommandRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    command_type: str = Field(..., description="Type of voice command")
    success: bool = Field(..., description="Whether command was successful")
    duration_ms: float = Field(..., description="Command processing duration")
    confidence_score: Optional[float] = Field(None, description="Voice recognition confidence")

# Analytics API Endpoints

@router.post("/track-event")
async def track_event(request: EventTrackingRequest, http_request: Request):
    """Track a custom analytics event"""
    try:
        client_id = http_request.client.host if http_request.client else "unknown"
        
        success = await analytics_service.track_event(
            event_name=request.event_name,
            user_id=request.user_id,
            client_id=client_id,
            parameters=request.parameters
        )
        
        if success:
            return {
                "status": "success",
                "message": "Event tracked successfully",
                "event_name": request.event_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to track event")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-user-journey")
async def track_user_journey(request: UserJourneyRequest):
    """Track user journey step for funnel analysis"""
    try:
        await analytics_service.track_user_journey(
            user_id=request.user_id,
            journey_step=request.journey_step,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": "User journey step tracked",
            "user_id": request.user_id,
            "journey_step": request.journey_step
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-business-metric")
async def track_business_metric(request: BusinessMetricRequest):
    """Track business metrics like revenue, transactions"""
    try:
        await analytics_service.track_business_metric(
            metric_name=request.metric_name,
            value=request.value,
            currency=request.currency,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": "Business metric tracked",
            "metric_name": request.metric_name,
            "value": request.value,
            "currency": request.currency
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-error")
async def track_error(request: ErrorTrackingRequest):
    """Track application errors for monitoring"""
    try:
        await analytics_service.track_error(
            error_type=request.error_type,
            error_message=request.error_message,
            user_id=request.user_id,
            endpoint=request.endpoint,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": "Error tracked for monitoring",
            "error_type": request.error_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-performance")
async def track_performance(request: PerformanceMetricRequest):
    """Track performance metrics for optimization"""
    try:
        await analytics_service.track_performance_metric(
            operation_name=request.operation_name,
            duration_ms=request.duration_ms,
            success=request.success,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": "Performance metric tracked",
            "operation_name": request.operation_name,
            "duration_ms": request.duration_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Axzora-specific tracking endpoints

@router.post("/track-happy-paisa-transaction")
async def track_happy_paisa_transaction(request: HappyPaisaTransactionRequest):
    """Track Happy Paisa wallet transactions"""
    try:
        await analytics_service.track_happy_paisa_transaction(
            user_id=request.user_id,
            transaction_type=request.transaction_type,
            amount=request.amount,
            currency=request.currency,
            transaction_id=request.transaction_id
        )
        
        return {
            "status": "success",
            "message": "Happy Paisa transaction tracked",
            "transaction_id": request.transaction_id,
            "amount": request.amount,
            "currency": request.currency
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-booking")
async def track_booking(request: BookingEventRequest):
    """Track travel and service bookings"""
    try:
        await analytics_service.track_booking_event(
            user_id=request.user_id,
            booking_type=request.booking_type,
            booking_id=request.booking_id,
            amount=request.amount,
            status=request.status,
            metadata=request.metadata
        )
        
        return {
            "status": "success",
            "message": f"{request.booking_type} booking tracked",
            "booking_id": request.booking_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-voice-command")
async def track_voice_command(request: VoiceCommandRequest):
    """Track Mr. Happy voice assistant usage"""
    try:
        await analytics_service.track_voice_command(
            user_id=request.user_id,
            command_type=request.command_type,
            success=request.success,
            duration_ms=request.duration_ms,
            confidence_score=request.confidence_score
        )
        
        return {
            "status": "success",
            "message": "Voice command tracked",
            "command_type": request.command_type,
            "success": request.success
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Data Retrieval Endpoints

@router.get("/summary/{user_id}")
async def get_user_analytics_summary(user_id: str, days: int = 30):
    """Get analytics summary for a specific user"""
    try:
        summary = await analytics_service.get_analytics_summary(
            user_id=user_id,
            days=days
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_global_analytics_summary(days: int = 30):
    """Get global analytics summary for all users"""
    try:
        summary = await analytics_service.get_analytics_summary(days=days)
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health_check():
    """Check analytics service health"""
    try:
        # Test database connection
        db_status = "connected" if analytics_service.analytics_collection is not None else "disconnected"
        
        # Test GA4 connection
        ga4_status = "configured" if analytics_service.ga4_client is not None else "demo_mode"
        
        # Test Firebase connection
        firebase_status = "connected" if analytics_service.firebase_app is not None else "demo_mode"
        
        return {
            "status": "healthy",
            "services": {
                "database": db_status,
                "ga4": ga4_status,
                "firebase": firebase_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }