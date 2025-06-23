"""
Advanced Voice API endpoints for Mr. Happy 2.0
Enhanced voice interaction with intelligent responses
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Dict, List, Optional
import logging
from pydantic import BaseModel

from ..services.advanced_voice_service import (
    process_advanced_voice_command,
    get_advanced_conversation_history,
    get_quick_responses
)

router = APIRouter(prefix="/api/voice", tags=["voice"])
logger = logging.getLogger(__name__)


class VoiceRequest(BaseModel):
    text: str
    user_id: str
    context: Optional[Dict] = None


class VoiceResponse(BaseModel):
    success: bool
    text_response: str
    audio_response: Optional[str] = None
    conversation_id: str
    intent_data: Dict
    context: Dict
    actions: List[str] = []
    error: Optional[str] = None


@router.get("/status")
async def get_voice_status():
    """Get Mr. Happy voice service status"""
    return {
        "status": "online",
        "service": "advanced_mr_happy",
        "version": "2.0",
        "capabilities": [
            "intelligent_conversation",
            "context_awareness", 
            "multi_service_integration",
            "personalized_responses",
            "action_recommendations"
        ],
        "message": "Mr. Happy 2.0 is ready with advanced AI capabilities!"
    }


@router.post("/chat", response_model=VoiceResponse)
async def chat_with_mr_happy(request: VoiceRequest):
    """Advanced chat with Mr. Happy using enhanced AI"""
    try:
        logger.info(f"Processing voice request from user {request.user_id}: {request.text}")
        
        # Process through advanced voice service
        response = await process_advanced_voice_command(
            request.text,
            request.user_id,
            request.context
        )
        
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Processing failed"))
        
        return VoiceResponse(
            success=response["success"],
            text_response=response["text_response"],
            audio_response=response.get("audio_response"),
            conversation_id=response["conversation_id"],
            intent_data=response["intent_data"],
            context=response["context"],
            actions=response.get("actions", []),
            error=response.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in advanced chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/conversation/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 10):
    """Get conversation history with Mr. Happy"""
    try:
        history = get_advanced_conversation_history(user_id, limit)
        return {
            "user_id": user_id,
            "conversation_history": history,
            "total_messages": len(history),
            "service": "advanced_mr_happy"
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")


@router.get("/quick-responses")
async def get_quick_response_options():
    """Get predefined quick response options"""
    try:
        responses = get_quick_responses()
        return {
            "quick_responses": responses,
            "message": "Choose a quick response or type your own message"
        }
    except Exception as e:
        logger.error(f"Error getting quick responses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get quick responses: {str(e)}")


@router.post("/quick-command/{user_id}")
async def process_quick_command(user_id: str, command: str):
    """Process predefined quick commands"""
    try:
        # Map quick commands to natural language
        command_map = {
            "wallet_balance": "What's my Happy Paisa balance?",
            "recent_transactions": "Show me my recent transactions",
            "add_money": "I want to add money to my wallet",
            "travel_search": "Help me search for travel options",
            "book_flight": "I want to book a flight",
            "recharge_mobile": "Help me recharge my mobile",
            "recharge_dth": "I want to recharge my DTH",
            "pay_utility": "Help me pay utility bills",
            "shop_products": "Show me products to buy",
            "view_cart": "Show me my shopping cart",
            "weather": "What's the weather like?",
            "help": "What can you help me with?",
            "greeting": "Hello Mr. Happy"
        }
        
        if command not in command_map:
            raise HTTPException(status_code=400, detail="Unknown quick command")
        
        text_input = command_map[command]
        response = await process_advanced_voice_command(text_input, user_id)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing quick command: {e}")
        raise HTTPException(status_code=500, detail=f"Quick command failed: {str(e)}")


@router.get("/capabilities")
async def get_mr_happy_capabilities():
    """Get comprehensive Mr. Happy capabilities"""
    return {
        "service_name": "Mr. Happy 2.0 - Advanced AI Assistant",
        "version": "2.0.0",
        "capabilities": {
            "wallet_services": {
                "description": "Complete Happy Paisa wallet management",
                "features": [
                    "Check balance and transaction history",
                    "Add money with currency conversion (INR ↔ HP)", 
                    "Real-time spending analytics",
                    "Intelligent financial insights",
                    "Budget tracking and recommendations"
                ]
            },
            "travel_services": {
                "description": "Comprehensive travel booking assistance",
                "features": [
                    "Flight search across multiple airlines",
                    "Hotel booking with amenity filters",
                    "Price comparisons and recommendations",
                    "Happy Paisa payment integration",
                    "Booking history and management"
                ]
            },
            "recharge_services": {
                "description": "All-in-one recharge and bill payment",
                "features": [
                    "Mobile recharge with automatic operator detection",
                    "DTH and cable TV recharge",
                    "Utility bill payments (electricity, water, gas)",
                    "Broadband and landline bill payments",
                    "Plan recommendations based on usage"
                ]
            },
            "ecommerce_services": {
                "description": "Intelligent shopping assistance",
                "features": [
                    "Product search and recommendations",
                    "Cart management and optimization",
                    "Order tracking and history",
                    "Happy Paisa rewards program",
                    "Personalized product suggestions"
                ]
            },
            "ai_features": {
                "description": "Advanced AI conversation capabilities",
                "features": [
                    "Natural language understanding",
                    "Context-aware responses",
                    "Multi-turn conversations",
                    "Personalized recommendations",
                    "Intelligent action suggestions",
                    "Learning from user preferences"
                ]
            }
        },
        "integration_features": [
            "Real-time data from all Axzora services",
            "Cross-service recommendations",
            "Unified user experience",
            "Intelligent automation",
            "Proactive assistance"
        ],
        "supported_intents": [
            "wallet_balance", "wallet_add_money", "wallet_transactions",
            "travel_search", "travel_book", "recharge_mobile", "recharge_dth",
            "recharge_utility", "shopping_search", "shopping_cart", 
            "weather", "help", "greeting", "goodbye"
        ],
        "languages": ["en-us"],
        "response_modes": ["text", "actions", "quick_responses"]
    }


@router.post("/simulate-voice")
async def simulate_voice_interaction(request: VoiceRequest):
    """Simulate voice interaction for testing (without actual audio processing)"""
    try:
        # Add simulation context
        enhanced_context = request.context or {}
        enhanced_context["simulation"] = True
        enhanced_context["audio_processed"] = False
        
        # Process as text-based voice simulation
        response = await process_advanced_voice_command(
            request.text,
            request.user_id,
            enhanced_context
        )
        
        # Add simulation indicators
        if response["success"]:
            response["simulation_note"] = "This is a simulated voice interaction. In production, this would include TTS audio output."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in voice simulation: {e}")
        raise HTTPException(status_code=500, detail=f"Voice simulation failed: {str(e)}")


@router.get("/personality")
async def get_mr_happy_personality():
    """Get Mr. Happy's personality and communication style"""
    return {
        "name": "Mr. Happy",
        "personality": {
            "tone": "Friendly and enthusiastic",
            "style": "Helpful and informative",
            "characteristics": [
                "Always positive and encouraging",
                "Knowledgeable about all Axzora services",
                "Proactive in offering assistance",
                "Clear and concise in communication",
                "Focused on user success and satisfaction"
            ]
        },
        "expertise_areas": [
            "Financial management with Happy Paisa",
            "Travel planning and booking",
            "Digital service management",
            "E-commerce and shopping assistance",
            "Technology and digital literacy"
        ],
        "communication_principles": [
            "User-centric approach",
            "Context-aware responses",
            "Action-oriented suggestions",
            "Educational and informative",
            "Respectful of user privacy"
        ],
        "sample_phrases": [
            "I'd be happy to help you with that!",
            "Let me check your account details...",
            "Here's what I found for you:",
            "Would you like me to proceed with this action?",
            "I can help you save money on this transaction!"
        ]
    }