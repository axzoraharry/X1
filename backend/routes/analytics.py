from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
from ..services.analytics_service import AnalyticsService
from ..services.automation_service import AutomationService
from ..models.automation import AutomationRule, AIInsight, AutomationMetrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

class AnalyticsRequest(BaseModel):
    user_id: str
    time_range: str = "7d"  # 7d, 30d, 90d
    metrics: List[str] = ["automation_performance", "usage_patterns", "ai_insights"]

class CustomRuleRequest(BaseModel):
    user_id: str
    rule_name: str
    trigger_conditions: Dict[str, Any]
    automation_config: Dict[str, Any]
    is_active: bool = True

@router.get("/dashboard/{user_id}")
async def get_analytics_dashboard(user_id: str, time_range: str = "7d"):
    """
    Get comprehensive analytics dashboard for user
    """
    try:
        analytics_data = await AnalyticsService.get_user_analytics(user_id, time_range)
        
        return {
            "user_id": user_id,
            "time_range": time_range,
            "overview": analytics_data.get("overview", {}),
            "daily_stats": analytics_data.get("daily_stats", []),
            "automation_types": analytics_data.get("automation_types", []),
            "performance_metrics": analytics_data.get("performance_metrics", []),
            "ai_insights": analytics_data.get("ai_insights", []),
            "trends": analytics_data.get("trends", []),
            "recommendations": analytics_data.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@router.get("/automation-performance/{user_id}")
async def get_automation_performance(user_id: str, days: int = 7):
    """
    Get detailed automation performance metrics
    """
    try:
        performance_data = await AnalyticsService.get_automation_performance(user_id, days)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_automations": performance_data.get("total_automations", 0),
            "success_rate": performance_data.get("success_rate", 0),
            "avg_response_time": performance_data.get("avg_response_time", 0),
            "error_rate": performance_data.get("error_rate", 0),
            "peak_hours": performance_data.get("peak_hours", []),
            "bottlenecks": performance_data.get("bottlenecks", []),
            "optimization_suggestions": performance_data.get("optimization_suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to get automation performance: {e}")
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")

@router.get("/spending-insights/{user_id}")
async def get_ai_spending_insights(user_id: str):
    """
    Get AI-powered spending insights and predictions
    """
    try:
        insights = await AnalyticsService.get_ai_spending_insights(user_id)
        
        return {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "spending_categories": insights.get("spending_categories", {}),
            "monthly_trends": insights.get("monthly_trends", {}),
            "predictions": insights.get("predictions", {}),
            "recommendations": insights.get("recommendations", []),
            "anomalies": insights.get("anomalies", []),
            "budget_optimization": insights.get("budget_optimization", {}),
            "confidence_score": insights.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Failed to get spending insights: {e}")
        raise HTTPException(status_code=500, detail=f"AI insights failed: {str(e)}")

@router.post("/custom-rules/{user_id}")
async def create_custom_automation_rule(user_id: str, rule_request: CustomRuleRequest):
    """
    Create custom automation rule for user
    """
    try:
        rule = AutomationRule(
            user_id=user_id,
            rule_name=rule_request.rule_name,
            trigger_condition=rule_request.trigger_conditions,
            automation_config=rule_request.automation_config,
            is_active=rule_request.is_active
        )
        
        result = await AnalyticsService.create_automation_rule(rule)
        
        return {
            "status": "created",
            "rule_id": result.get("rule_id"),
            "rule_name": rule_request.rule_name,
            "is_active": rule_request.is_active,
            "message": "Custom automation rule created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create custom rule: {e}")
        raise HTTPException(status_code=500, detail=f"Rule creation failed: {str(e)}")

@router.get("/custom-rules/{user_id}")
async def get_user_automation_rules(user_id: str):
    """
    Get user's custom automation rules
    """
    try:
        rules = await AnalyticsService.get_user_automation_rules(user_id)
        
        return {
            "user_id": user_id,
            "rules": rules,
            "total_rules": len(rules),
            "active_rules": len([r for r in rules if r.get("is_active", False)])
        }
        
    except Exception as e:
        logger.error(f"Failed to get automation rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get rules: {str(e)}")

@router.put("/custom-rules/{rule_id}")
async def update_automation_rule(rule_id: str, rule_request: CustomRuleRequest):
    """
    Update existing automation rule
    """
    try:
        result = await AnalyticsService.update_automation_rule(rule_id, rule_request.dict())
        
        return {
            "status": "updated",
            "rule_id": rule_id,
            "message": "Automation rule updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update automation rule: {e}")
        raise HTTPException(status_code=500, detail=f"Rule update failed: {str(e)}")

@router.delete("/custom-rules/{rule_id}")
async def delete_automation_rule(rule_id: str, user_id: str):
    """
    Delete automation rule
    """
    try:
        result = await AnalyticsService.delete_automation_rule(rule_id, user_id)
        
        return {
            "status": "deleted",
            "rule_id": rule_id,
            "message": "Automation rule deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete automation rule: {e}")
        raise HTTPException(status_code=500, detail=f"Rule deletion failed: {str(e)}")

@router.get("/predictions/{user_id}")
async def get_spending_predictions(user_id: str, horizon_days: int = 30):
    """
    Get AI-powered spending predictions
    """
    try:
        predictions = await AnalyticsService.get_spending_predictions(user_id, horizon_days)
        
        return {
            "user_id": user_id,
            "prediction_horizon_days": horizon_days,
            "predicted_spending": predictions.get("predicted_spending", {}),
            "category_forecasts": predictions.get("category_forecasts", {}),
            "risk_assessment": predictions.get("risk_assessment", {}),
            "recommendations": predictions.get("recommendations", []),
            "confidence_intervals": predictions.get("confidence_intervals", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get spending predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Predictions failed: {str(e)}")

@router.post("/anomaly-detection/{user_id}")
async def detect_spending_anomalies(user_id: str, background_tasks: BackgroundTasks):
    """
    Detect anomalies in spending patterns
    """
    try:
        # Run anomaly detection in background
        background_tasks.add_task(
            AnalyticsService.detect_spending_anomalies,
            user_id
        )
        
        return {
            "status": "detection_started",
            "user_id": user_id,
            "message": "Anomaly detection initiated. Results will be available shortly."
        }
        
    except Exception as e:
        logger.error(f"Failed to start anomaly detection: {e}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.get("/automation-health")
async def get_automation_health():
    """
    Get overall automation system health
    """
    try:
        health_metrics = await AnalyticsService.get_system_health()
        
        return {
            "status": "healthy" if health_metrics.get("overall_health", 0) > 80 else "degraded",
            "overall_health_score": health_metrics.get("overall_health", 0),
            "active_workflows": health_metrics.get("active_workflows", 0),
            "total_users": health_metrics.get("total_users", 0),
            "daily_automations": health_metrics.get("daily_automations", 0),
            "error_rate": health_metrics.get("error_rate", 0),
            "avg_response_time": health_metrics.get("avg_response_time", 0),
            "resource_usage": health_metrics.get("resource_usage", {}),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get automation health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/export/{user_id}")
async def export_analytics_data(user_id: str, format: str = "json", time_range: str = "30d"):
    """
    Export user analytics data in various formats
    """
    try:
        if format not in ["json", "csv", "xlsx"]:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        export_data = await AnalyticsService.export_user_data(user_id, time_range, format)
        
        return {
            "status": "export_ready",
            "user_id": user_id,
            "format": format,
            "time_range": time_range,
            "download_url": export_data.get("download_url"),
            "file_size": export_data.get("file_size"),
            "generated_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to export analytics data: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")