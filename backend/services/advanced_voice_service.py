"""
Advanced Voice Service for Mr. Happy 2.0
Provides intelligent voice responses with context awareness
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import re

from .wallet_service import WalletService
from .database import get_collection

logger = logging.getLogger(__name__)


class AdvancedMrHappyVoice:
    """
    Advanced AI voice assistant for Axzora's Mr. Happy 2.0
    Provides contextual, intelligent responses across all services
    """
    
    def __init__(self):
        self.conversation_history = {}
        self.user_contexts = {}
        self.intent_patterns = self._load_intent_patterns()
        self.personality = {
            "name": "Mr. Happy",
            "tone": "friendly",
            "style": "helpful",
            "expertise": ["finance", "travel", "shopping", "digital_services"]
        }
    
    def _load_intent_patterns(self) -> Dict:
        """Load intent recognition patterns"""
        return {
            "wallet_balance": [
                r"balance", r"money", r"paisa", r"wallet", r"funds",
                r"how much.*have", r"what.*balance", r"check.*wallet"
            ],
            "wallet_add_money": [
                r"add money", r"top up", r"recharge wallet", r"put money",
                r"deposit", r"fund.*wallet", r"credit.*wallet"
            ],
            "wallet_transactions": [
                r"transactions", r"history", r"payments", r"recent.*activity",
                r"what.*spent", r"transaction.*history", r"spending"
            ],
            "travel_search": [
                r"flight", r"hotel", r"travel", r"book.*trip", r"vacation",
                r"fly.*to", r"visit.*place", r"tour", r"holiday"
            ],
            "travel_book": [
                r"book.*flight", r"book.*hotel", r"make.*reservation",
                r"confirm.*booking", r"purchase.*ticket"
            ],
            "recharge_mobile": [
                r"recharge", r"mobile", r"phone", r"prepaid", r"topup",
                r"data.*pack", r"talk.*time", r"cellular"
            ],
            "recharge_dth": [
                r"dth", r"dish", r"satellite", r"tv", r"television",
                r"cable", r"set.*top.*box"
            ],
            "recharge_utility": [
                r"electricity", r"water", r"gas", r"utility", r"bill",
                r"electric.*bill", r"water.*bill", r"gas.*bill"
            ],
            "shopping_search": [
                r"shop", r"buy", r"purchase", r"product", r"item",
                r"shopping", r"order", r"online.*store"
            ],
            "shopping_cart": [
                r"cart", r"add.*cart", r"remove.*cart", r"checkout",
                r"basket", r"shopping.*bag"
            ],
            "help": [
                r"help", r"assist", r"what.*can.*do", r"features",
                r"capabilities", r"how.*work", r"guide"
            ],
            "greeting": [
                r"hello", r"hi", r"hey", r"good.*morning", r"good.*afternoon",
                r"good.*evening", r"greetings", r"howdy"
            ],
            "weather": [
                r"weather", r"temperature", r"forecast", r"raining",
                r"sunny", r"cloudy", r"climate"
            ],
            "goodbye": [
                r"bye", r"goodbye", r"see.*you", r"thanks", r"thank.*you",
                r"exit", r"quit", r"stop"
            ]
        }
    
    def _detect_intent(self, text: str) -> str:
        """Detect user intent from text"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return "general_inquiry"
    
    async def _get_user_context(self, user_id: str) -> Dict:
        """Get comprehensive user context"""
        context = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Get user info
            users_collection = await get_collection("users")
            user_data = await users_collection.find_one({"id": user_id})
            if user_data:
                context["user"] = {
                    "name": user_data.get("name", "User"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email")
                }
            
            # Get wallet info
            wallet_data = await WalletService.get_balance(user_id)
            context["wallet"] = {
                "balance_hp": wallet_data.balance_hp,
                "balance_inr": wallet_data.balance_inr_equiv,
                "recent_transactions": len(wallet_data.recent_transactions),
                "spending_categories": list(wallet_data.spending_breakdown.keys())
            }
            
            # Get recent activity counts
            travel_collection = await get_collection("travel_bookings")
            travel_count = await travel_collection.count_documents({"user_id": user_id})
            context["activity"] = {
                "travel_bookings": travel_count
            }
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
        
        return context
    
    async def process_voice_input(self, text: str, user_id: str, additional_context: Dict = None) -> Dict:
        """Process voice input and generate intelligent response"""
        try:
            # Get user context
            context = await self._get_user_context(user_id)
            if additional_context:
                context.update(additional_context)
            
            # Detect intent
            intent = self._detect_intent(text)
            
            # Generate response based on intent
            response = await self._generate_response(intent, text, context)
            
            # Store conversation
            conversation_id = str(uuid.uuid4())
            self._store_conversation(user_id, text, response["text"], intent, conversation_id)
            
            return {
                "success": True,
                "text_response": response["text"],
                "audio_response": None,  # Can be enhanced with TTS
                "conversation_id": conversation_id,
                "intent_data": {
                    "intent": intent,
                    "confidence": response.get("confidence", 0.8),
                    "entities": response.get("entities", [])
                },
                "context": context,
                "actions": response.get("actions", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {
                "success": False,
                "error": str(e),
                "text_response": "I'm having trouble processing that right now. Could you please try again?",
                "conversation_id": str(uuid.uuid4()),
                "intent_data": {"intent": "error"},
                "context": {}
            }
    
    async def _generate_response(self, intent: str, text: str, context: Dict) -> Dict:
        """Generate contextual response based on intent"""
        user_name = context.get("user", {}).get("name", "there")
        wallet_balance = context.get("wallet", {}).get("balance_hp", 0)
        
        responses = {
            "greeting": {
                "text": f"Hello {user_name}! I'm Mr. Happy, your AI assistant for the Axzora ecosystem. I can help you with your wallet, travel bookings, recharges, shopping, and more. What would you like to do today?",
                "actions": ["show_dashboard"]
            },
            
            "wallet_balance": {
                "text": f"Your current Happy Paisa balance is {wallet_balance:.3f} HP, which equals ₹{wallet_balance * 1000:,.0f}. Your wallet is ready for transactions across all Axzora services!",
                "actions": ["show_wallet", "show_recent_transactions"]
            },
            
            "wallet_add_money": {
                "text": f"I can help you add money to your Happy Paisa wallet! You can convert INR to Happy Paisa at the rate of ₹1,000 = 1 HP. Would you like me to guide you through the top-up process?",
                "actions": ["show_add_money_form"]
            },
            
            "wallet_transactions": {
                "text": f"Let me show you your recent transaction history. You have {context.get('wallet', {}).get('recent_transactions', 0)} recent transactions. I can help you analyze your spending patterns too.",
                "actions": ["show_transaction_history", "show_spending_analytics"]
            },
            
            "travel_search": {
                "text": f"I'd love to help you plan your travel! I can search for flights and hotels, and you can book them using your Happy Paisa. Where would you like to go? Popular destinations include Goa, Mumbai, Delhi, and Bangalore.",
                "actions": ["show_travel_search", "show_popular_destinations"]
            },
            
            "travel_book": {
                "text": f"Great! I can help you book your travel. With your current balance of {wallet_balance:.3f} HP, you can book flights and hotels. Let me show you the available options and help you complete the booking.",
                "actions": ["show_booking_form", "show_payment_options"]
            },
            
            "recharge_mobile": {
                "text": f"I can help you recharge your mobile instantly! I support all major operators like Jio, Airtel, Vi, and BSNL. Just tell me your mobile number and I'll show you the best recharge plans available.",
                "actions": ["show_recharge_form", "detect_operator"]
            },
            
            "recharge_dth": {
                "text": f"I can help you recharge your DTH or pay TV bills! I support Tata Sky, Dish TV, Airtel Digital TV, and more. Your Happy Paisa balance of {wallet_balance:.3f} HP is ready for the transaction.",
                "actions": ["show_dth_options"]
            },
            
            "recharge_utility": {
                "text": f"I can help you pay your utility bills quickly! Whether it's electricity, water, gas, or broadband bills, I can process them using your Happy Paisa. Which utility bill would you like to pay?",
                "actions": ["show_utility_options"]
            },
            
            "shopping_search": {
                "text": f"Welcome to the Axzora shop! I can help you find products across electronics, fashion, home goods, and more. All purchases earn Happy Paisa rewards. What are you looking for today?",
                "actions": ["show_product_catalog", "show_categories"]
            },
            
            "shopping_cart": {
                "text": f"I can help you manage your shopping cart! You can add items, review your selections, and checkout using your Happy Paisa balance of {wallet_balance:.3f} HP. Would you like to see your current cart?",
                "actions": ["show_cart", "show_checkout"]
            },
            
            "weather": {
                "text": f"The weather in {context.get('user', {}).get('location', 'your area')} is sunny at 35°C. Perfect weather for planning outdoor activities! Would you like me to help you plan any travel based on the weather?",
                "actions": ["show_weather_details", "suggest_travel"]
            },
            
            "help": {
                "text": f"I'm Mr. Happy, your comprehensive AI assistant! I can help you with:\n• Wallet management and Happy Paisa transactions\n• Travel booking (flights, hotels, buses)\n• Mobile and DTH recharges\n• Utility bill payments\n• E-commerce shopping\n• Weather and recommendations\n\nWhat would you like to explore?",
                "actions": ["show_capabilities", "show_quick_actions"]
            },
            
            "goodbye": {
                "text": f"Thank you for using Axzora's Mr. Happy! I'm always here to help you with your digital services. Have a wonderful day, {user_name}!",
                "actions": ["minimize_chat"]
            },
            
            "general_inquiry": {
                "text": f"I understand you're asking about something, {user_name}. I'm here to help with your Happy Paisa wallet, travel bookings, recharges, shopping, and more. Could you be more specific about what you'd like to do?",
                "actions": ["show_suggestions"]
            }
        }
        
        response = responses.get(intent, responses["general_inquiry"])
        
        # Add context-specific enhancements
        if wallet_balance < 1.0 and intent in ["travel_book", "shopping_cart", "recharge_mobile"]:
            response["text"] += f"\n\nNote: Your current balance is low ({wallet_balance:.3f} HP). You might want to add money to your wallet first."
            response["actions"].append("suggest_add_money")
        
        return response
    
    def _store_conversation(self, user_id: str, user_input: str, bot_response: str, intent: str, conversation_id: str):
        """Store conversation in memory"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "conversation_id": conversation_id,
            "user_input": user_input,
            "bot_response": bot_response,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 50 conversations per user
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for user"""
        if user_id not in self.conversation_history:
            return []
        
        return self.conversation_history[user_id][-limit:]
    
    def get_quick_responses(self) -> List[Dict]:
        """Get predefined quick response options"""
        return [
            {"text": "Show my wallet balance", "action": "wallet_balance"},
            {"text": "Find flights to Goa", "action": "travel_search"},
            {"text": "Recharge my mobile", "action": "recharge_mobile"},
            {"text": "Show me products", "action": "shopping_search"},
            {"text": "What can you help with?", "action": "help"}
        ]


# Global instance
advanced_mr_happy = AdvancedMrHappyVoice()


async def process_advanced_voice_command(text: str, user_id: str, context: Dict = None) -> Dict:
    """Process voice command through advanced Mr. Happy"""
    return await advanced_mr_happy.process_voice_input(text, user_id, context)


def get_advanced_conversation_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history"""
    return advanced_mr_happy.get_conversation_history(user_id, limit)


def get_quick_responses() -> List[Dict]:
    """Get quick response options"""
    return advanced_mr_happy.get_quick_responses()