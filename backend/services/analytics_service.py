"""
Analytics Service for Axzora Mr. Happy 2.0
Handles Firebase Analytics and GA4 server-side event tracking
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
# Removed pyga4 import as it's not compatible
import firebase_admin
from firebase_admin import credentials, analytics
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import requests

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Comprehensive analytics service for tracking user behavior,
    business metrics, and system performance
    """
    
    def __init__(self):
        self.ga4_client = None
        self.firebase_app = None
        self.mongo_client = None
        self.analytics_collection = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Firebase Admin SDK and GA4 client"""
        try:
            # GA4 Configuration (replace with actual credentials)
            measurement_id = os.getenv('GA_MEASUREMENT_ID', 'G-DEMO123456')
            api_secret = os.getenv('GA_API_SECRET', 'demo-api-secret')
            
            if measurement_id != 'G-DEMO123456' and api_secret != 'demo-api-secret':
                # Using direct API calls instead of pyga4 library
                self.ga4_client = {
                    "measurement_id": measurement_id,
                    "api_secret": api_secret
                }
                logger.info("GA4 client initialized successfully")
            else:
                logger.warning("Using demo GA4 credentials - replace with actual keys")
            
            # Firebase Admin SDK initialization
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                self.firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.warning("Firebase service account not found - using demo mode")
            
            # MongoDB for analytics storage
            mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            db = self.mongo_client[os.getenv('DB_NAME', 'test_database')]
            self.analytics_collection = db['analytics_events']
            
        except Exception as e:
            logger.error(f"Analytics service initialization error: {e}")
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track analytics event to both GA4 and MongoDB
        """
        try:
            event_data = {
                'event_name': event_name,
                'user_id': user_id,
                'client_id': client_id or f"user_{user_id}" if user_id else "anonymous",
                'parameters': parameters or {},
                'timestamp': datetime.utcnow(),
                'source': 'backend'
            }
            
            # Store in MongoDB for custom analytics
            if self.analytics_collection:
                await self.analytics_collection.insert_one(event_data)
            
            # Send to GA4 if client is available
            if self.ga4_client:
                try:
                    # Using direct GA4 Measurement Protocol API
                    ga4_endpoint = f"https://www.google-analytics.com/mp/collect?measurement_id={self.ga4_client['measurement_id']}&api_secret={self.ga4_client['api_secret']}"
                    
                    ga4_payload = {
                        "client_id": event_data['client_id'],
                        "events": [{
                            "name": event_name,
                            "params": {
                                "timestamp_micros": int(datetime.utcnow().timestamp() * 1000000),
                                **(parameters or {})
                            }
                        }]
                    }
                    
                    # Non-blocking request using asyncio
                    asyncio.create_task(self._send_ga4_event(ga4_endpoint, ga4_payload))
                except Exception as e:
                    logger.error(f"GA4 event sending failed: {e}")
                    # Continue execution even if GA4 fails
            
            logger.debug(f"Event tracked: {event_name}")
            return True
            
        except Exception as e:
            logger.error(f"Event tracking failed: {e}")
            return False
    
    async def _send_ga4_event(self, endpoint: str, payload: Dict):
        """Helper method to send events to GA4 asynchronously"""
        try:
            # Using requests in a non-blocking way
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: requests.post(endpoint, json=payload, timeout=5)
            )
        except Exception as e:
            logger.error(f"GA4 API request failed: {e}")
            logger.error(f"Event tracking failed: {e}")
            return False
    
    async def track_user_journey(
        self,
        user_id: str,
        journey_step: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track user journey steps for funnel analysis"""
        await self.track_event(
            event_name='user_journey_step',
            user_id=user_id,
            parameters={
                'journey_step': journey_step,
                'step_timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
    
    async def track_business_metric(
        self,
        metric_name: str,
        value: float,
        currency: str = 'HP',
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track business-critical metrics like revenue, transactions"""
        await self.track_event(
            event_name='business_metric',
            user_id=user_id,
            parameters={
                'metric_name': metric_name,
                'value': value,
                'currency': currency,
                'metric_timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
    
    async def track_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track application errors for monitoring"""
        await self.track_event(
            event_name='application_error',
            user_id=user_id,
            parameters={
                'error_type': error_type,
                'error_message': error_message,
                'endpoint': endpoint,
                'error_timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
    
    async def track_performance_metric(
        self,
        operation_name: str,
        duration_ms: float,
        success: bool,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track performance metrics for optimization"""
        await self.track_event(
            event_name='performance_metric',
            user_id=user_id,
            parameters={
                'operation_name': operation_name,
                'duration_ms': duration_ms,
                'success': success,
                'performance_timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
    
    # Axzora-specific tracking methods
    async def track_happy_paisa_transaction(
        self,
        user_id: str,
        transaction_type: str,
        amount: float,
        currency: str,
        transaction_id: str
    ):
        """Track Happy Paisa wallet transactions"""
        await self.track_event(
            event_name='happy_paisa_transaction',
            user_id=user_id,
            parameters={
                'transaction_type': transaction_type,
                'amount': amount,
                'currency': currency,
                'transaction_id': transaction_id,
                'conversion_rate': 1000 if currency == 'HP' else 0.001
            }
        )
    
    async def track_booking_event(
        self,
        user_id: str,
        booking_type: str,
        booking_id: str,
        amount: float,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track travel and service bookings"""
        await self.track_event(
            event_name=f'{booking_type}_booking',
            user_id=user_id,
            parameters={
                'booking_type': booking_type,
                'booking_id': booking_id,
                'amount': amount,
                'status': status,
                'booking_timestamp': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
    
    async def track_voice_command(
        self,
        user_id: str,
        command_type: str,
        success: bool,
        duration_ms: float,
        confidence_score: Optional[float] = None
    ):
        """Track Mr. Happy voice assistant usage"""
        await self.track_event(
            event_name='voice_command',
            user_id=user_id,
            parameters={
                'command_type': command_type,
                'success': success,
                'duration_ms': duration_ms,
                'confidence_score': confidence_score,
                'voice_timestamp': datetime.utcnow().isoformat()
            }
        )
    
    async def get_analytics_summary(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics summary for dashboard"""
        try:
            if not self.analytics_collection:
                return {"error": "Analytics storage not available"}
            
            # Calculate date range
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query
            query = {"timestamp": {"$gte": start_date}}
            if user_id:
                query["user_id"] = user_id
            
            # Aggregate analytics data
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$event_name",
                        "count": {"$sum": 1},
                        "latest": {"$max": "$timestamp"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            events_summary = []
            async for result in self.analytics_collection.aggregate(pipeline):
                events_summary.append({
                    "event_name": result["_id"],
                    "count": result["count"],
                    "latest": result["latest"].isoformat()
                })
            
            # Get total unique users
            total_users = await self.analytics_collection.distinct(
                "user_id", 
                query
            )
            
            return {
                "period_days": days,
                "total_events": sum(event["count"] for event in events_summary),
                "unique_users": len(total_users),
                "events_breakdown": events_summary[:10],  # Top 10 events
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics summary generation failed: {e}")
            return {"error": str(e)}

# Global analytics service instance
analytics_service = AnalyticsService()