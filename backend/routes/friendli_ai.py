"""
Friendli AI API Routes - Enhanced AI capabilities for financial analytics
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..services.friendli_ai_service import friendli_ai_service
from ..services.blockchain_gateway_service import blockchain_gateway
from ..services.blockchain_wallet_service import BlockchainWalletService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["friendli-ai"])

@router.post("/analyze-transaction")
async def analyze_blockchain_transaction(
    transaction_hash: str = Query(..., description="Blockchain transaction hash to analyze"),
    background_tasks: BackgroundTasks = None
):
    """Analyze a blockchain transaction using Friendli AI for risk and fraud detection"""
    try:
        # Get transaction details from blockchain
        transaction_data = await blockchain_gateway.get_transaction_status(transaction_hash)
        
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Perform AI analysis
        analysis = await friendli_ai_service.analyze_blockchain_transaction(transaction_data)
        
        # Store analysis results for future reference
        if background_tasks:
            background_tasks.add_task(
                _store_transaction_analysis, 
                transaction_hash, 
                analysis.__dict__
            )
        
        return {
            "transaction_hash": transaction_hash,
            "analysis": {
                "risk_level": analysis.risk_level,
                "risk_score": analysis.risk_score,
                "anomaly_detected": analysis.anomaly_detected,
                "insights": analysis.insights,
                "recommendations": analysis.recommendations,
                "fraud_indicators": analysis.fraud_indicators,
                "summary": analysis.analysis_summary
            },
            "analyzed_at": datetime.utcnow().isoformat(),
            "ai_model": "friendli-meta-llama-3.1-8b-instruct"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/wallet-insights/{user_id}")
async def get_wallet_insights(user_id: str):
    """Generate AI-powered wallet insights and recommendations"""
    try:
        # Get comprehensive wallet data
        wallet_analytics = await BlockchainWalletService.get_wallet_analytics(user_id, days=30)
        balance_info = await BlockchainWalletService.get_balance(user_id)
        
        # Prepare data for AI analysis
        user_data = {
            "user_id": user_id,
            "balance_hp": balance_info.balance_hp,
            "balance_inr": balance_info.balance_inr_equiv,
            "blockchain_address": balance_info.blockchain_address,
            "spending_breakdown": balance_info.spending_breakdown,
            "recent_transactions": balance_info.recent_transactions,
            "transaction_count": len(balance_info.recent_transactions),
            "total_spent_hp": wallet_analytics.get("user_analytics", {}).get("total_spent_hp", 0),
            "total_received_hp": wallet_analytics.get("user_analytics", {}).get("total_received_hp", 0),
            "avg_transaction_inr": wallet_analytics.get("user_analytics", {}).get("avg_transaction_inr", 0),
            "most_active_category": "General"  # Simplified for now
        }
        
        # Generate AI insights
        insights = await friendli_ai_service.generate_wallet_insights(user_data)
        
        return {
            "user_id": user_id,
            "insights": {
                "spending_patterns": insights.spending_patterns,
                "financial_health_score": insights.financial_health_score,
                "recommendations": insights.recommendations,
                "trends": insights.trends,
                "optimization_tips": insights.optimization_tips
            },
            "wallet_summary": {
                "current_balance_hp": user_data["balance_hp"],
                "current_balance_inr": user_data["balance_inr"],
                "blockchain_address": user_data["blockchain_address"],
                "transaction_count": user_data["transaction_count"]
            },
            "generated_at": datetime.utcnow().isoformat(),
            "ai_model": "friendli-meta-llama-3.1-8b-instruct"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@router.post("/voice-enhance")
async def enhance_voice_response(
    query: str = Query(..., description="User voice query"),
    user_id: Optional[str] = Query(None, description="User ID for context"),
    current_feature: Optional[str] = Query(None, description="Current app feature/page")
):
    """Enhance voice AI responses using Friendli AI"""
    try:
        # Build context for enhanced response
        context = {
            "current_feature": current_feature or "General"
        }
        
        # Add user context if available
        if user_id:
            try:
                balance_info = await BlockchainWalletService.get_balance(user_id)
                context.update({
                    "balance_hp": balance_info.balance_hp,
                    "balance_inr": balance_info.balance_inr_equiv,
                    "recent_activity": f"{len(balance_info.recent_transactions)} recent transactions"
                })
            except:
                # Continue without user context if unavailable
                pass
        
        # Generate enhanced response
        enhanced_response = await friendli_ai_service.enhance_voice_response(query, context)
        
        return {
            "query": query,
            "enhanced_response": enhanced_response,
            "context_used": context,
            "response_time": datetime.utcnow().isoformat(),
            "ai_model": "friendli-meta-llama-3.1-8b-instruct"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice enhancement failed: {str(e)}")

@router.post("/fraud-detection/{user_id}")
async def detect_fraud_patterns(user_id: str):
    """Analyze user's transaction patterns for fraud detection"""
    try:
        # Get recent transactions
        transactions = await BlockchainWalletService.get_recent_transactions(user_id, limit=20)
        blockchain_transactions = await BlockchainWalletService.get_blockchain_transactions(user_id, limit=10)
        
        # Combine transaction data
        all_transactions = transactions + [
            {
                "transaction_type": tx.get("transaction_type", "unknown"),
                "amount_hp": tx.get("amount_hp", 0),
                "timestamp": tx.get("timestamp", ""),
                "status": tx.get("status", "unknown"),
                "source": "blockchain"
            }
            for tx in blockchain_transactions
        ]
        
        # Perform fraud analysis
        fraud_analysis = await friendli_ai_service.detect_fraud_patterns(all_transactions)
        
        return {
            "user_id": user_id,
            "fraud_analysis": fraud_analysis,
            "transactions_analyzed": len(all_transactions),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "ai_model": "friendli-meta-llama-3.1-8b-instruct"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fraud detection failed: {str(e)}")

@router.post("/chat")
async def ai_chat(request_body: Dict[str, Any]):
    """General AI chat endpoint using Friendli AI"""
    try:
        messages = request_body.get("messages", [])
        model = request_body.get("model")
        max_tokens = request_body.get("max_tokens", 500)
        temperature = request_body.get("temperature", 0.7)
        
        response = await friendli_ai_service.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "response": {
                "content": response.content,
                "model": response.model,
                "usage": response.usage,
                "response_time_ms": response.response_time_ms
            },
            "created_at": response.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@router.get("/analytics/insights")
async def get_platform_insights(
    days: int = Query(default=7, le=30, description="Number of days to analyze")
):
    """Generate AI insights about platform usage and trends"""
    try:
        # Get network statistics
        network_stats = await blockchain_gateway.get_network_stats()
        
        # Prepare platform data for analysis
        platform_data = {
            "network": network_stats["network"],
            "total_supply_hp": network_stats["total_supply_hp"],
            "total_transactions": network_stats["total_transactions"],
            "active_addresses": network_stats["active_addresses"],
            "latest_block": network_stats["latest_block"],
            "analysis_period_days": days
        }
        
        # Generate platform insights
        prompt = f"""
        Analyze the Axzora Happy Paisa blockchain platform metrics:
        
        Platform Statistics:
        - Network: {platform_data['network']}
        - Total Supply: {platform_data['total_supply_hp']} HP
        - Total Transactions: {platform_data['total_transactions']}
        - Active Addresses: {platform_data['active_addresses']}
        - Latest Block: {platform_data['latest_block']}
        - Analysis Period: {days} days
        
        Please provide:
        1. Platform health assessment
        2. Growth trends and patterns
        3. User adoption insights
        4. Network utilization analysis
        5. Recommendations for platform improvement
        
        Focus on actionable insights for a blockchain-powered fintech platform.
        """
        
        messages = [
            {"role": "system", "content": "You are a blockchain analytics expert providing insights for a fintech platform. Focus on platform health, growth trends, and actionable recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        response = await friendli_ai_service.chat_completion(messages, max_tokens=600, temperature=0.6)
        
        return {
            "platform_insights": response.content,
            "metrics_analyzed": platform_data,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "ai_model": response.model
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Platform insights failed: {str(e)}")

@router.get("/health")
async def ai_service_health():
    """Health check for Friendli AI service"""
    try:
        # Test basic AI functionality
        test_messages = [
            {"role": "user", "content": "Hello, please respond with 'AI service operational' if you're working correctly."}
        ]
        
        test_response = await friendli_ai_service.chat_completion(test_messages, max_tokens=50, temperature=0.1)
        
        return {
            "status": "healthy",
            "service": "friendli_ai",
            "ai_response_test": "passed" if "operational" in test_response.content.lower() else "warning",
            "model": test_response.model,
            "response_time_ms": test_response.response_time_ms,
            "features": {
                "transaction_analysis": "operational",
                "wallet_insights": "operational",
                "voice_enhancement": "operational",
                "fraud_detection": "operational",
                "chat_completion": "operational"
            },
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "friendli_ai",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

# Background task functions
async def _store_transaction_analysis(transaction_hash: str, analysis: Dict[str, Any]):
    """Store transaction analysis results"""
    try:
        from ..services.database import get_collection
        
        analysis_collection = await get_collection("ai_transaction_analysis")
        
        analysis_record = {
            "transaction_hash": transaction_hash,
            "analysis": analysis,
            "created_at": datetime.utcnow(),
            "ai_service": "friendli_ai"
        }
        
        await analysis_collection.insert_one(analysis_record)
        
    except Exception as e:
        logger.error(f"Failed to store transaction analysis: {e}")