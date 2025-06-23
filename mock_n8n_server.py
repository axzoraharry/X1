#!/usr/bin/env python3
"""
Mock n8n Server for Testing Axzora Integration

This simulates n8n webhook endpoints to test our automation integration
before the full n8n installation is complete.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import json
import asyncio
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock n8n Server", version="1.0.0")

# Storage for received webhooks
webhook_history = []

@app.get("/")
async def root():
    return {
        "message": "Mock n8n Server Running",
        "status": "healthy",
        "endpoints": [
            "/webhook/axzora-messaging",
            "/webhook/axzora-ai-processing", 
            "/webhook/axzora-data-sync",
            "/webhook/axzora-backup",
            "/healthz"
        ]
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint that Axzora will ping"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/webhook/axzora-messaging")
async def messaging_webhook(request: Request):
    """Mock messaging workflow webhook"""
    try:
        payload = await request.json()
        logger.info(f"Received messaging webhook: {json.dumps(payload, indent=2)}")
        
        # Simulate processing
        await asyncio.sleep(0.5)
        
        # Store webhook
        webhook_history.append({
            "type": "messaging",
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed"
        })
        
        # Mock successful response
        response = {
            "status": "success",
            "workflow_id": "messaging_workflow_001",
            "execution_id": f"exec_{int(datetime.utcnow().timestamp())}",
            "message": "Telegram notification sent successfully",
            "data": {
                "notification_type": payload.get("event", {}).get("data", {}).get("notification_type", "telegram"),
                "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
                "delivery_status": "delivered",
                "user_id": payload.get("user", {}).get("id", "unknown")
            }
        }
        
        logger.info(f"Sending messaging response: {response}")
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing messaging webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/webhook/axzora-ai-processing")
async def ai_processing_webhook(request: Request):
    """Mock AI processing workflow webhook"""
    try:
        payload = await request.json()
        logger.info(f"Received AI processing webhook: {json.dumps(payload, indent=2)}")
        
        # Simulate AI processing time
        await asyncio.sleep(1.0)
        
        # Store webhook
        webhook_history.append({
            "type": "ai_processing",
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed"
        })
        
        # Mock AI analysis results
        transaction_data = payload.get("transaction_data", {})
        amount_hp = transaction_data.get("amount_hp", 0)
        
        # Generate mock AI insights
        insights = {
            "spending_category": "Food & Beverages" if amount_hp < 1.0 else "Shopping",
            "monthly_trend": "+15.2%",
            "compared_to_average": "Above average" if amount_hp > 2.0 else "Below average",
            "budget_impact": f"{(amount_hp / 10) * 100:.1f}% of monthly budget",
            "recommendation_score": 8.5
        }
        
        recommendations = [
            "Consider setting up automatic savings for small purchases",
            "This category is trending higher this month",
            "Great choice! This aligns with your spending goals"
        ]
        
        response = {
            "status": "success",
            "workflow_id": "ai_processing_workflow_002",
            "execution_id": f"exec_{int(datetime.utcnow().timestamp())}",
            "data": {
                "user_id": payload.get("user_id"),
                "insights": insights,
                "recommendations": recommendations,
                "analysis_type": payload.get("analysis_type", "spending_insights"),
                "confidence_score": 0.92,
                "processed_at": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Sending AI processing response: {response}")
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing AI webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/webhook/axzora-data-sync")
async def data_sync_webhook(request: Request):
    """Mock data sync workflow webhook"""
    try:
        payload = await request.json()
        logger.info(f"Received data sync webhook: {json.dumps(payload, indent=2)}")
        
        # Simulate sync processing
        await asyncio.sleep(0.3)
        
        # Store webhook
        webhook_history.append({
            "type": "data_sync",
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed"
        })
        
        response = {
            "status": "success",
            "workflow_id": "data_sync_workflow_003",
            "execution_id": f"exec_{int(datetime.utcnow().timestamp())}",
            "data": {
                "sync_type": payload.get("sync_type", "incremental"),
                "records_processed": 157,
                "sync_duration": "2.3s",
                "destination": payload.get("destination", "postgresql"),
                "last_sync": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Sending data sync response: {response}")
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing data sync webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/webhook/axzora-backup")
async def backup_webhook(request: Request):
    """Mock backup workflow webhook"""
    try:
        payload = await request.json()
        logger.info(f"Received backup webhook: {json.dumps(payload, indent=2)}")
        
        # Simulate backup processing
        await asyncio.sleep(2.0)
        
        # Store webhook
        webhook_history.append({
            "type": "backup",
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processed"
        })
        
        backup_size = 1024 * 1024 * 12  # 12MB mock size
        
        response = {
            "status": "success", 
            "workflow_id": "backup_workflow_004",
            "execution_id": f"exec_{int(datetime.utcnow().timestamp())}",
            "data": {
                "backup_type": payload.get("backup_type", "full"),
                "destination": payload.get("destination", "google_drive"),
                "backup_size": backup_size,
                "backup_url": f"https://drive.google.com/file/backup_{int(datetime.utcnow().timestamp())}/view",
                "file_count": 245,
                "completion_time": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Sending backup response: {response}")
        return JSONResponse(content=response, status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing backup webhook: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/webhook/history")
async def get_webhook_history():
    """Get history of received webhooks for debugging"""
    return {
        "total_webhooks": len(webhook_history),
        "webhooks": webhook_history[-10:],  # Last 10 webhooks
        "summary": {
            "messaging": len([w for w in webhook_history if w["type"] == "messaging"]),
            "ai_processing": len([w for w in webhook_history if w["type"] == "ai_processing"]),
            "data_sync": len([w for w in webhook_history if w["type"] == "data_sync"]),
            "backup": len([w for w in webhook_history if w["type"] == "backup"])
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Mock n8n Server for Axzora Integration Testing...")
    print("📡 This simulates n8n webhook endpoints")
    print("🔗 Axzora app will connect to: http://localhost:5678")
    print("📊 Webhook history available at: http://localhost:5678/webhook/history")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=5678, log_level="info")