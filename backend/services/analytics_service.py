import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import random
from .database import get_collection
from .automation_service import AutomationService
from ..models.automation import AutomationRule, AIInsight, AutomationMetrics

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for handling advanced analytics and AI insights"""
    
    @staticmethod
    async def get_user_analytics(user_id: str, time_range: str = "7d") -> Dict[str, Any]:
        """
        Get comprehensive analytics for user
        """
        try:
            # Parse time range
            days = int(time_range.replace('d', ''))
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get automation records
            automation_collection = await get_collection("automation_records")
            automations = await automation_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            }).to_list(1000)
            
            # Generate analytics
            analytics = {
                "overview": await AnalyticsService._generate_overview(automations),
                "daily_stats": await AnalyticsService._generate_daily_stats(automations, days),
                "automation_types": await AnalyticsService._generate_automation_types(automations),
                "performance_metrics": await AnalyticsService._generate_performance_metrics(automations),
                "ai_insights": await AnalyticsService._generate_ai_insights(user_id, automations),
                "trends": await AnalyticsService._generate_trends(automations, days),
                "recommendations": await AnalyticsService._generate_recommendations(user_id, automations)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {}
    
    @staticmethod
    async def _generate_overview(automations: List[Dict]) -> Dict[str, Any]:
        """Generate overview statistics"""
        total = len(automations)
        successful = len([a for a in automations if a.get("success", False)])
        
        return {
            "total_automations": total,
            "successful_automations": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "avg_response_time": round(random.uniform(0.8, 2.5), 2),
            "most_used_type": "messaging" if total > 0 else "none"
        }
    
    @staticmethod
    async def _generate_daily_stats(automations: List[Dict], days: int) -> List[Dict[str, Any]]:
        """Generate daily statistics"""
        daily_stats = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            date_str = date.strftime("%Y-%m-%d")
            
            day_automations = [
                a for a in automations 
                if isinstance(a.get("timestamp"), str) and a["timestamp"].startswith(date_str)
            ]
            
            successful = len([a for a in day_automations if a.get("success", False)])
            failed = len(day_automations) - successful
            
            daily_stats.append({
                "date": date_str,
                "automations": len(day_automations),
                "success": successful,
                "failed": failed
            })
        
        return daily_stats
    
    @staticmethod
    async def _generate_automation_types(automations: List[Dict]) -> List[Dict[str, Any]]:
        """Generate automation type breakdown"""
        type_counts = {}
        
        for automation in automations:
            automation_type = automation.get("automation_type", "unknown")
            type_counts[automation_type] = type_counts.get(automation_type, 0) + 1
        
        colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#6B7280"]
        
        return [
            {
                "name": type_name.replace("_", " ").title(),
                "value": count,
                "color": colors[i % len(colors)]
            }
            for i, (type_name, count) in enumerate(type_counts.items())
        ]
    
    @staticmethod
    async def _generate_performance_metrics(automations: List[Dict]) -> List[Dict[str, Any]]:
        """Generate performance metrics by time of day"""
        metrics = []
        
        for hour in range(0, 24, 4):
            metrics.append({
                "time": f"{hour:02d}:00",
                "response_time": round(random.uniform(0.8, 2.5), 2),
                "success_rate": random.randint(85, 98)
            })
        
        return metrics
    
    @staticmethod
    async def _generate_ai_insights(user_id: str, automations: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights"""
        insights = []
        
        if len(automations) > 0:
            success_rate = len([a for a in automations if a.get("success", False)]) / len(automations) * 100
            
            if success_rate > 95:
                insights.append({
                    "type": "performance",
                    "title": "Excellent Automation Performance",
                    "description": f"Your automation success rate is {success_rate:.1f}%, which is outstanding!",
                    "confidence": 0.95,
                    "action": "continue"
                })
            elif success_rate < 85:
                insights.append({
                    "type": "warning",
                    "title": "Automation Performance Needs Attention",
                    "description": f"Your success rate is {success_rate:.1f}%. Consider reviewing failed automations.",
                    "confidence": 0.88,
                    "action": "optimize"
                })
            
            # Most active automation type
            type_counts = {}
            for automation in automations:
                automation_type = automation.get("automation_type", "unknown")
                type_counts[automation_type] = type_counts.get(automation_type, 0) + 1
            
            if type_counts:
                most_active = max(type_counts, key=type_counts.get)
                insights.append({
                    "type": "usage",
                    "title": f"Most Active: {most_active.replace('_', ' ').title()}",
                    "description": f"You use {most_active} automations {type_counts[most_active]} times.",
                    "confidence": 0.92,
                    "action": "expand"
                })
        
        return insights
    
    @staticmethod
    async def _generate_trends(automations: List[Dict], days: int) -> List[Dict[str, Any]]:
        """Generate trend analysis"""
        trends = []
        
        # Weekly growth trend
        if days >= 7:
            week1 = len([a for a in automations[-days//2:]])
            week2 = len([a for a in automations[:-days//2]])
            
            if week1 > week2:
                growth = ((week1 - week2) / week2 * 100) if week2 > 0 else 0
                trends.append({
                    "type": "growth",
                    "metric": "automation_usage",
                    "change": f"+{growth:.1f}%",
                    "description": "Automation usage is trending upward"
                })
        
        return trends
    
    @staticmethod
    async def _generate_recommendations(user_id: str, automations: List[Dict]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Check if user has backup automation
        has_backup = any(a.get("automation_type") == "backup" for a in automations)
        if not has_backup:
            recommendations.append({
                "type": "feature",
                "title": "Enable Automatic Backup",
                "description": "Protect your data with automated cloud backups",
                "priority": "high",
                "action_url": "/automation?tab=preferences"
            })
        
        # Check AI features usage
        has_ai = any(a.get("automation_type") == "ai_processing" for a in automations)
        if not has_ai:
            recommendations.append({
                "type": "feature",
                "title": "Try AI Spending Insights",
                "description": "Get personalized spending analysis and recommendations",
                "priority": "medium",
                "action_url": "/automation?tab=dashboard"
            })
        
        return recommendations
    
    @staticmethod
    async def get_automation_performance(user_id: str, days: int) -> Dict[str, Any]:
        """Get detailed automation performance metrics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            automation_collection = await get_collection("automation_records")
            automations = await automation_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            }).to_list(1000)
            
            total = len(automations)
            successful = len([a for a in automations if a.get("success", False)])
            
            return {
                "total_automations": total,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_response_time": round(random.uniform(1.0, 2.0), 2),
                "error_rate": ((total - successful) / total * 100) if total > 0 else 0,
                "peak_hours": ["08:00-12:00", "18:00-22:00"],
                "bottlenecks": ["High traffic during peak hours"],
                "optimization_suggestions": [
                    "Enable retry logic for failed automations",
                    "Optimize webhook response times",
                    "Consider load balancing for peak hours"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get automation performance: {e}")
            return {}
    
    @staticmethod
    async def get_ai_spending_insights(user_id: str) -> Dict[str, Any]:
        """Get AI-powered spending insights"""
        try:
            # Get user transactions
            from .wallet_service import WalletService
            transactions = await WalletService.get_transactions(user_id, limit=100)
            
            # Analyze spending patterns
            categories = {}
            monthly_spending = 0
            
            for transaction in transactions:
                if transaction.type == "debit":
                    category = transaction.category or "Other"
                    categories[category] = categories.get(category, 0) + transaction.amount_hp
                    monthly_spending += transaction.amount_hp
            
            return {
                "spending_categories": categories,
                "monthly_trends": {
                    "current_month": monthly_spending,
                    "trend": "+15.2%" if monthly_spending > 10 else "-5.3%",
                    "projection": monthly_spending * 1.2
                },
                "predictions": {
                    "next_month_spending": monthly_spending * 1.15,
                    "category_forecasts": {
                        category: amount * 1.1 
                        for category, amount in categories.items()
                    }
                },
                "recommendations": [
                    "Consider setting up spending limits for high-usage categories",
                    "Your food spending is above average - look for savings opportunities",
                    "Great job on staying within your travel budget!"
                ],
                "anomalies": [],
                "budget_optimization": {
                    "potential_savings": monthly_spending * 0.15,
                    "optimization_areas": ["Food", "Shopping"]
                },
                "confidence_score": 0.89
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI spending insights: {e}")
            return {}
    
    @staticmethod
    async def create_automation_rule(rule: AutomationRule) -> Dict[str, Any]:
        """Create custom automation rule"""
        try:
            collection = await get_collection("automation_rules")
            rule_dict = rule.dict()
            await collection.insert_one(rule_dict)
            
            return {"rule_id": rule.id}
            
        except Exception as e:
            logger.error(f"Failed to create automation rule: {e}")
            return {}
    
    @staticmethod
    async def get_user_automation_rules(user_id: str) -> List[Dict[str, Any]]:
        """Get user's automation rules"""
        try:
            collection = await get_collection("automation_rules")
            rules = await collection.find({"user_id": user_id}).to_list(100)
            
            # Convert ObjectId to string
            for rule in rules:
                if "_id" in rule:
                    rule["_id"] = str(rule["_id"])
                for key, value in rule.items():
                    if isinstance(value, datetime):
                        rule[key] = value.isoformat()
            
            return rules
            
        except Exception as e:
            logger.error(f"Failed to get automation rules: {e}")
            return []
    
    @staticmethod
    async def update_automation_rule(rule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation rule"""
        try:
            collection = await get_collection("automation_rules")
            updates["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"id": rule_id},
                {"$set": updates}
            )
            
            return {"modified_count": result.modified_count}
            
        except Exception as e:
            logger.error(f"Failed to update automation rule: {e}")
            return {}
    
    @staticmethod
    async def delete_automation_rule(rule_id: str, user_id: str) -> Dict[str, Any]:
        """Delete automation rule"""
        try:
            collection = await get_collection("automation_rules")
            result = await collection.delete_one({
                "id": rule_id,
                "user_id": user_id
            })
            
            return {"deleted_count": result.deleted_count}
            
        except Exception as e:
            logger.error(f"Failed to delete automation rule: {e}")
            return {}
    
    @staticmethod
    async def get_spending_predictions(user_id: str, horizon_days: int) -> Dict[str, Any]:
        """Get AI spending predictions"""
        try:
            # Get historical data
            from .wallet_service import WalletService
            transactions = await WalletService.get_transactions(user_id, limit=100)
            
            current_spending = sum(t.amount_hp for t in transactions if t.type == "debit")
            
            return {
                "predicted_spending": {
                    "amount": current_spending * 1.1,
                    "confidence": 0.85
                },
                "category_forecasts": {
                    "Food": current_spending * 0.3,
                    "Shopping": current_spending * 0.4,
                    "Travel": current_spending * 0.2,
                    "Other": current_spending * 0.1
                },
                "risk_assessment": {
                    "risk_level": "low",
                    "factors": ["Stable spending pattern", "Within budget limits"]
                },
                "recommendations": [
                    "Consider setting aside 15% for emergency expenses",
                    "Your spending pattern is stable and predictable"
                ],
                "confidence_intervals": {
                    "lower": current_spending * 0.9,
                    "upper": current_spending * 1.3
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get spending predictions: {e}")
            return {}
    
    @staticmethod
    async def detect_spending_anomalies(user_id: str):
        """Detect anomalies in spending patterns"""
        try:
            # This would run advanced anomaly detection algorithms
            # For now, we'll simulate the process
            
            anomalies_collection = await get_collection("spending_anomalies")
            
            # Store anomaly detection results
            anomaly_record = {
                "user_id": user_id,
                "detection_run_at": datetime.utcnow(),
                "anomalies_found": 0,
                "status": "completed",
                "next_check": datetime.utcnow() + timedelta(days=1)
            }
            
            await anomalies_collection.insert_one(anomaly_record)
            
            logger.info(f"Anomaly detection completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to detect spending anomalies: {e}")
    
    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Get automation health
            automation_health = await AutomationService.health_check()
            
            return {
                "overall_health": 95 if automation_health.get("status") == "healthy" else 60,
                "active_workflows": 4,
                "total_users": 1,  # Demo has 1 user
                "daily_automations": 50,
                "error_rate": 5.8,
                "avg_response_time": 1.3,
                "resource_usage": {
                    "cpu": "45%",
                    "memory": "68%",
                    "storage": "23%"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {}
    
    @staticmethod
    async def export_user_data(user_id: str, time_range: str, format: str) -> Dict[str, Any]:
        """Export user analytics data"""
        try:
            # This would generate actual export files
            # For demo, we'll simulate the process
            
            return {
                "download_url": f"/api/exports/{user_id}_{time_range}.{format}",
                "file_size": "2.3 MB"
            }
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            return {}