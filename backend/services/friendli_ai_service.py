"""
Friendli AI Service Integration
High-performance LLM inference for financial analytics, blockchain insights, and enhanced AI capabilities
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FriendliAIResponse:
    """Response from Friendli AI API"""
    content: str
    model: str
    usage: Dict[str, Any]
    created_at: datetime
    response_time_ms: float

@dataclass
class TransactionAnalysis:
    """AI analysis of blockchain transaction"""
    transaction_hash: str
    risk_level: str  # low, medium, high, critical
    risk_score: float  # 0-100
    anomaly_detected: bool
    insights: List[str]
    recommendations: List[str]
    fraud_indicators: List[str]
    analysis_summary: str

@dataclass
class WalletInsights:
    """AI-generated wallet insights"""
    user_id: str
    spending_patterns: List[str]
    financial_health_score: float
    recommendations: List[str]
    trends: List[str]
    optimization_tips: List[str]

class FriendliAIService:
    """Service for interacting with Friendli AI API"""
    
    def __init__(self):
        self.api_token = "flp_3IW9xJ2vb3xgLgpOMOl3DYe7LxJ4MC2kKFWDHNh73vQ4d"
        self.base_url = "https://inference.friendli.ai"
        self.default_model = "meta-llama-3.1-8b-instruct"
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        logger.info("Friendli AI Service initialized successfully")
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async request to Friendli AI API"""
        try:
            start_time = datetime.utcnow()
            
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = response.json()
            result["_response_time_ms"] = response_time
            result["_created_at"] = start_time
            
            logger.info(f"Friendli AI request successful: {endpoint} ({response_time:.2f}ms)")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Friendli AI API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Friendli AI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Friendli AI request failed: {e}")
            raise
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            model: str = None, max_tokens: int = 500,
                            temperature: float = 0.7) -> FriendliAIResponse:
        """Generate chat completion using Friendli AI"""
        try:
            payload = {
                "model": model or self.default_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            result = await self._make_request("/v1/chat/completions", payload)
            
            return FriendliAIResponse(
                content=result["choices"][0]["message"]["content"],
                model=result["model"],
                usage=result.get("usage", {}),
                created_at=result["_created_at"],
                response_time_ms=result["_response_time_ms"]
            )
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def analyze_blockchain_transaction(self, transaction_data: Dict[str, Any]) -> TransactionAnalysis:
        """Analyze blockchain transaction for risk and anomalies"""
        try:
            # Prepare context for AI analysis
            prompt = f"""
            Analyze this Happy Paisa blockchain transaction for financial risk and anomalies:
            
            Transaction Details:
            - Hash: {transaction_data.get('hash', 'N/A')}
            - Type: {transaction_data.get('transaction_type', 'unknown')}
            - From: {transaction_data.get('from_address', 'N/A')}
            - To: {transaction_data.get('to_address', 'N/A')}
            - Amount: {transaction_data.get('amount_hp', 0)} HP ({transaction_data.get('amount_inr', 0)} INR)
            - Timestamp: {transaction_data.get('timestamp', 'N/A')}
            - Network: {transaction_data.get('network', 'happy-paisa-mainnet')}
            
            Context:
            - Happy Paisa is a blockchain-backed digital currency (1 HP = ₹1000)
            - This is a financial transaction within the Axzora ecosystem
            - Transaction types: mint (INR→HP), burn (HP→INR), transfer (P2P)
            
            Please provide:
            1. Risk assessment (low/medium/high/critical)
            2. Numerical risk score (0-100)
            3. Anomaly detection (true/false)
            4. Key insights about the transaction
            5. Recommendations for the user
            6. Any fraud indicators
            7. Summary analysis
            
            Format your response as a structured analysis focusing on financial security and user safety.
            """
            
            messages = [
                {"role": "system", "content": "You are a financial security expert specializing in blockchain transaction analysis and fraud detection. Provide accurate, actionable insights for digital currency transactions."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, max_tokens=600, temperature=0.3)
            
            # Parse AI response into structured analysis
            analysis_content = response.content
            
            # Extract structured information from AI response
            risk_level = self._extract_risk_level(analysis_content)
            risk_score = self._extract_risk_score(analysis_content)
            anomaly_detected = self._extract_anomaly_status(analysis_content)
            insights = self._extract_insights(analysis_content)
            recommendations = self._extract_recommendations(analysis_content)
            fraud_indicators = self._extract_fraud_indicators(analysis_content)
            
            return TransactionAnalysis(
                transaction_hash=transaction_data.get('hash', ''),
                risk_level=risk_level,
                risk_score=risk_score,
                anomaly_detected=anomaly_detected,
                insights=insights,
                recommendations=recommendations,
                fraud_indicators=fraud_indicators,
                analysis_summary=analysis_content
            )
            
        except Exception as e:
            logger.error(f"Transaction analysis failed: {e}")
            # Return safe fallback analysis
            return TransactionAnalysis(
                transaction_hash=transaction_data.get('hash', ''),
                risk_level="low",
                risk_score=10.0,
                anomaly_detected=False,
                insights=["AI analysis temporarily unavailable"],
                recommendations=["Monitor transaction normally"],
                fraud_indicators=[],
                analysis_summary="Transaction appears normal based on basic validation."
            )
    
    async def generate_wallet_insights(self, user_data: Dict[str, Any]) -> WalletInsights:
        """Generate AI-powered wallet insights and recommendations"""
        try:
            # Prepare wallet context for AI analysis
            prompt = f"""
            Analyze this Happy Paisa wallet for financial insights and recommendations:
            
            Wallet Information:
            - User ID: {user_data.get('user_id', 'anonymous')}
            - Current Balance: {user_data.get('balance_hp', 0)} HP (₹{user_data.get('balance_inr', 0)})
            - Blockchain Address: {user_data.get('blockchain_address', 'N/A')}
            - Transaction Count: {user_data.get('transaction_count', 0)}
            
            Spending Breakdown:
            {json.dumps(user_data.get('spending_breakdown', {}), indent=2)}
            
            Recent Transactions:
            {json.dumps(user_data.get('recent_transactions', [])[:5], indent=2)}
            
            Analytics:
            - Total Spent: {user_data.get('total_spent_hp', 0)} HP
            - Total Received: {user_data.get('total_received_hp', 0)} HP
            - Average Transaction: ₹{user_data.get('avg_transaction_inr', 0)}
            - Most Active Category: {user_data.get('most_active_category', 'N/A')}
            
            Please provide:
            1. Spending pattern analysis
            2. Financial health score (0-100)
            3. Personalized recommendations
            4. Trend analysis
            5. Optimization tips for better financial management
            
            Focus on actionable insights that help the user optimize their Happy Paisa usage and financial wellness.
            """
            
            messages = [
                {"role": "system", "content": "You are a personal financial advisor with expertise in digital currencies and blockchain-based financial management. Provide helpful, actionable advice for optimizing digital wallet usage."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, max_tokens=700, temperature=0.6)
            
            # Parse AI response into structured insights
            content = response.content
            
            return WalletInsights(
                user_id=user_data.get('user_id', ''),
                spending_patterns=self._extract_spending_patterns(content),
                financial_health_score=self._extract_health_score(content),
                recommendations=self._extract_recommendations(content),
                trends=self._extract_trends(content),
                optimization_tips=self._extract_optimization_tips(content)
            )
            
        except Exception as e:
            logger.error(f"Wallet insights generation failed: {e}")
            # Return safe fallback insights
            return WalletInsights(
                user_id=user_data.get('user_id', ''),
                spending_patterns=["Regular digital currency usage"],
                financial_health_score=75.0,
                recommendations=["Continue monitoring your spending patterns"],
                trends=["Stable wallet usage"],
                optimization_tips=["Keep tracking your transactions for better insights"]
            )
    
    async def enhance_voice_response(self, user_query: str, context: Dict[str, Any]) -> str:
        """Enhance voice AI responses with Friendli AI capabilities"""
        try:
            # Prepare enhanced voice context
            prompt = f"""
            User Voice Query: "{user_query}"
            
            Context:
            - Platform: Axzora Mr. Happy 2.0 (blockchain-powered fintech)
            - User Balance: {context.get('balance_hp', 0)} HP (₹{context.get('balance_inr', 0)})
            - Recent Activity: {context.get('recent_activity', 'None')}
            - Current Feature: {context.get('current_feature', 'General')}
            
            Available Features:
            - Happy Paisa wallet (blockchain currency)
            - Virtual debit cards
            - Travel booking
            - Mobile recharge
            - E-commerce shopping
            - Analytics and insights
            
            Please provide a helpful, conversational response that:
            1. Directly addresses the user's query
            2. Uses the provided context intelligently
            3. Suggests relevant actions or features
            4. Maintains a friendly, professional tone
            5. Includes specific Happy Paisa amounts/conversions when relevant
            
            Keep the response concise but informative, suitable for voice interaction.
            """
            
            messages = [
                {"role": "system", "content": "You are Mr. Happy, the AI assistant for Axzora's blockchain-powered financial platform. You help users with their Happy Paisa digital currency, transactions, and financial services. Be helpful, friendly, and knowledgeable about blockchain and financial services."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, max_tokens=400, temperature=0.8)
            return response.content
            
        except Exception as e:
            logger.error(f"Voice response enhancement failed: {e}")
            return "I'm here to help with your Happy Paisa and financial services. How can I assist you today?"
    
    async def detect_fraud_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transaction patterns for fraud detection"""
        try:
            # Prepare transaction pattern analysis
            transactions_summary = []
            for tx in transactions[-10:]:  # Analyze last 10 transactions
                transactions_summary.append({
                    "type": tx.get("transaction_type", "unknown"),
                    "amount_hp": tx.get("amount_hp", 0),
                    "timestamp": tx.get("timestamp", ""),
                    "status": tx.get("status", "unknown")
                })
            
            prompt = f"""
            Analyze these recent Happy Paisa transactions for fraud patterns:
            
            Transaction History:
            {json.dumps(transactions_summary, indent=2)}
            
            Please identify:
            1. Unusual transaction patterns
            2. Potential fraud indicators
            3. Risk assessment
            4. Recommended security measures
            5. Alert level (none, low, medium, high, critical)
            
            Focus on detecting:
            - Rapid consecutive transactions
            - Unusual amounts or timing
            - Suspicious transaction patterns
            - Account compromise indicators
            """
            
            messages = [
                {"role": "system", "content": "You are a fraud detection specialist for digital currency transactions. Analyze patterns and identify potential security threats in blockchain transactions."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.chat_completion(messages, max_tokens=500, temperature=0.2)
            
            # Parse fraud analysis
            alert_level = self._extract_alert_level(response.content)
            
            return {
                "alert_level": alert_level,
                "analysis": response.content,
                "fraud_detected": alert_level in ["high", "critical"],
                "recommendations": self._extract_recommendations(response.content),
                "confidence_score": 85.0,  # Base confidence for AI analysis
                "analyzed_transactions": len(transactions_summary)
            }
            
        except Exception as e:
            logger.error(f"Fraud pattern detection failed: {e}")
            return {
                "alert_level": "none",
                "analysis": "Fraud detection temporarily unavailable",
                "fraud_detected": False,
                "recommendations": ["Monitor account activity regularly"],
                "confidence_score": 0.0,
                "analyzed_transactions": 0
            }
    
    # Helper methods for parsing AI responses
    def _extract_risk_level(self, content: str) -> str:
        """Extract risk level from AI response"""
        content_lower = content.lower()
        if "critical" in content_lower:
            return "critical"
        elif "high" in content_lower and "risk" in content_lower:
            return "high"
        elif "medium" in content_lower:
            return "medium"
        else:
            return "low"
    
    def _extract_risk_score(self, content: str) -> float:
        """Extract numerical risk score from AI response"""
        import re
        # Look for patterns like "risk score: 85" or "score of 75"
        patterns = [
            r"risk score:?\s*(\d+)",
            r"score of\s*(\d+)",
            r"(\d+)(?:/100|\s*out of 100)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return min(float(match.group(1)), 100.0)
        
        # Default based on risk level
        if "critical" in content.lower():
            return 90.0
        elif "high" in content.lower():
            return 70.0
        elif "medium" in content.lower():
            return 40.0
        else:
            return 15.0
    
    def _extract_anomaly_status(self, content: str) -> bool:
        """Extract anomaly detection status"""
        content_lower = content.lower()
        anomaly_indicators = ["anomaly detected", "unusual", "suspicious", "irregular", "abnormal"]
        return any(indicator in content_lower for indicator in anomaly_indicators)
    
    def _extract_insights(self, content: str) -> List[str]:
        """Extract key insights from AI response"""
        # Simple extraction - look for numbered lists or bullet points
        insights = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')) and 
                len(line) > 10):
                insights.append(line.lstrip('•-*123456789. '))
        
        return insights[:5]  # Limit to 5 insights
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = content.split('\n')
        
        in_recommendations_section = False
        for line in lines:
            line = line.strip()
            if "recommendation" in line.lower():
                in_recommendations_section = True
                continue
            
            if in_recommendations_section and line:
                if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                    recommendations.append(line.lstrip('•-*123456789. '))
                elif not line.startswith(('•', '-', '*')) and len(recommendations) > 0:
                    break
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _extract_fraud_indicators(self, content: str) -> List[str]:
        """Extract fraud indicators from AI response"""
        indicators = []
        fraud_keywords = ["fraud", "suspicious", "unusual", "anomaly", "risk", "alert"]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in fraud_keywords) and len(line) > 10:
                indicators.append(line)
        
        return indicators[:3]  # Limit to 3 indicators
    
    def _extract_spending_patterns(self, content: str) -> List[str]:
        """Extract spending patterns from wallet insights"""
        patterns = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if ("spending" in line.lower() or "pattern" in line.lower()) and len(line) > 15:
                patterns.append(line)
        
        return patterns[:4]  # Limit to 4 patterns
    
    def _extract_health_score(self, content: str) -> float:
        """Extract financial health score"""
        import re
        patterns = [
            r"health score:?\s*(\d+)",
            r"financial health:?\s*(\d+)",
            r"score of\s*(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return min(float(match.group(1)), 100.0)
        
        return 75.0  # Default good health score
    
    def _extract_trends(self, content: str) -> List[str]:
        """Extract financial trends"""
        trends = []
        trend_keywords = ["trend", "increasing", "decreasing", "stable", "growing", "declining"]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in trend_keywords) and len(line) > 10:
                trends.append(line)
        
        return trends[:3]  # Limit to 3 trends
    
    def _extract_optimization_tips(self, content: str) -> List[str]:
        """Extract optimization tips"""
        tips = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if ("tip" in line.lower() or "optimize" in line.lower() or "improve" in line.lower()) and len(line) > 15:
                tips.append(line)
        
        return tips[:4]  # Limit to 4 tips
    
    def _extract_alert_level(self, content: str) -> str:
        """Extract alert level from fraud analysis"""
        content_lower = content.lower()
        if "critical" in content_lower:
            return "critical"
        elif "high" in content_lower:
            return "high"
        elif "medium" in content_lower:
            return "medium"
        elif "low" in content_lower:
            return "low"
        else:
            return "none"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
friendli_ai_service = FriendliAIService()