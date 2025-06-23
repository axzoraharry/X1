"""
Voice interaction API endpoints for Mr. Happy 2.0
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Dict, List, Optional
import logging
from ..services.mycroft_service import (
    mr_happy_voice, 
    process_voice_command, 
    get_voice_conversation_history,
    initialize_voice_service
)
from ..services.wallet_service import WalletService
from ..services.database import get_collection
from pydantic import BaseModel

router = APIRouter(prefix="/api/voice", tags=["voice"])
logger = logging.getLogger(__name__)


class VoiceTextRequest(BaseModel):
    text: str
    user_id: str
    context: Optional[Dict] = None


class VoiceResponse(BaseModel):
    success: bool
    text_response: Optional[str] = None
    audio_response: Optional[str] = None  # Base64 encoded audio
    conversation_id: str
    intent_data: Dict
    context: Dict
    error: Optional[str] = None


@router.on_event("startup")
async def startup_voice_service():
    """Initialize voice service on startup"""
    try:
        success = await initialize_voice_service()
        if success:
            logger.info("Mr. Happy voice service started successfully")
        else:
            logger.warning("Mr. Happy voice service failed to start - will use fallback mode")
    except Exception as e:
        logger.error(f"Error starting voice service: {e}")


@router.get("/status")
async def get_voice_status():
    """Get voice service status"""
    try:
        is_ready = mr_happy_voice.is_ready()
        return {
            "status": "online" if is_ready else "fallback",
            "mycroft_connected": mr_happy_voice.messagebus.connected if hasattr(mr_happy_voice, 'messagebus') else False,
            "skills_loaded": getattr(mr_happy_voice, 'skills_loaded', False),
            "message": "Mr. Happy is ready!" if is_ready else "Mr. Happy is running in fallback mode"
        }
    except Exception as e:
        logger.error(f"Error getting voice status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/chat", response_model=VoiceResponse)
async def chat_with_mr_happy(request: VoiceTextRequest):
    """Chat with Mr. Happy using text input"""
    try:
        # Add user's current context from database
        enhanced_context = request.context or {}
        
        # Get user's wallet info for context
        try:
            wallet_data = await WalletService.get_balance(request.user_id)
            enhanced_context["wallet"] = {
                "balance_hp": wallet_data.balance_hp,
                "balance_inr": wallet_data.balance_inr_equiv,
                "recent_transactions_count": len(wallet_data.recent_transactions)
            }
        except Exception:
            pass  # Continue without wallet context if it fails
        
        # Get user info for context
        try:
            users_collection = await get_collection("users")
            user_data = await users_collection.find_one({"id": request.user_id})
            if user_data:
                enhanced_context["user"] = {
                    "name": user_data.get("name", "User"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email")
                }
        except Exception:
            pass  # Continue without user context if it fails
        
        # Process the voice command
        response = await process_voice_command(
            request.text, 
            request.user_id, 
            enhanced_context
        )
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return VoiceResponse(
            success=response["success"],
            text_response=response["text_response"],
            audio_response=response.get("audio_response"),
            conversation_id=response["conversation_id"],
            intent_data=response["intent_data"],
            context=response["context"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/voice-upload")
async def process_voice_upload(
    user_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """Process uploaded voice audio file"""
    try:
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be audio format")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Process through Mycroft (if available) or fallback
        if mr_happy_voice.is_ready():
            response = await mr_happy_voice.process_voice_input(audio_data, user_id)
        else:
            # Fallback: simulate voice processing
            response = {
                "success": True,
                "text_response": "Voice processing is currently in fallback mode. Please use text chat for now.",
                "conversation_id": "fallback_voice",
                "intent_data": {"fallback": True},
                "context": {"user_id": user_id}
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing voice upload: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")


@router.get("/conversation/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 10):
    """Get conversation history for user"""
    try:
        history = await get_voice_conversation_history(user_id, limit)
        return {
            "user_id": user_id,
            "conversation_history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")


@router.post("/context/{user_id}")
async def set_user_context(user_id: str, context: Dict):
    """Set additional context for user's voice interactions"""
    try:
        await mr_happy_voice.set_user_context(user_id, context)
        return {"message": "Context updated successfully"}
    except Exception as e:
        logger.error(f"Error setting user context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set context: {str(e)}")


@router.post("/quick-commands/{user_id}")
async def process_quick_command(user_id: str, command: str):
    """Process quick voice commands for common actions"""
    try:
        # Map quick commands to actions
        quick_commands = {
            "show_balance": "What's my Happy Paisa balance?",
            "recent_transactions": "Show me my recent transactions",
            "book_travel": "I want to book travel",
            "recharge_mobile": "Help me recharge my mobile",
            "shop_products": "Show me products to buy",
            "weather": "What's the weather like?",
            "help": "What can you help me with?"
        }
        
        if command in quick_commands:
            text_input = quick_commands[command]
            response = await process_voice_command(text_input, user_id)
            return response
        else:
            raise HTTPException(status_code=400, detail="Unknown quick command")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing quick command: {e}")
        raise HTTPException(status_code=500, detail=f"Quick command failed: {str(e)}")


@router.get("/capabilities")
async def get_mr_happy_capabilities():
    """Get Mr. Happy's capabilities and features"""
    return {
        "capabilities": [
            {
                "category": "Wallet Management",
                "features": [
                    "Check Happy Paisa balance",
                    "View transaction history", 
                    "Currency conversion (INR ↔ HP)",
                    "Add money to wallet",
                    "Spending analytics"
                ]
            },
            {
                "category": "Travel Services",
                "features": [
                    "Search flights and hotels",
                    "Book travel with Happy Paisa",
                    "View booking history",
                    "Travel recommendations"
                ]
            },
            {
                "category": "Recharge Services", 
                "features": [
                    "Mobile recharge with operator detection",
                    "DTH and utility bill payments",
                    "Recharge history",
                    "Plan recommendations"
                ]
            },
            {
                "category": "E-commerce",
                "features": [
                    "Product search and recommendations",
                    "Add items to cart",
                    "Order with Happy Paisa",
                    "Order tracking"
                ]
            },
            {
                "category": "AI Assistant",
                "features": [
                    "Natural language conversation",
                    "Voice command processing",
                    "Contextual responses",
                    "Personalized recommendations",
                    "Multi-turn conversations"
                ]
            }
        ],
        "voice_modes": [
            "text_chat",
            "voice_upload", 
            "quick_commands"
        ],
        "languages": ["en-us"],
        "integrations": [
            "mycroft_ai",
            "happy_paisa_wallet",
            "axzora_services"
        ]
    }