"""
Mycroft AI Integration Service for Mr. Happy 2.0
Provides advanced voice interaction capabilities
"""

import asyncio
import json
import logging
import websocket
import threading
import time
from typing import Dict, List, Optional, Callable
import requests
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class MycroftMessageBus:
    """
    WebSocket client for Mycroft messagebus communication
    """
    
    def __init__(self, host="localhost", port=8181):
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}/core"
        self.ws = None
        self.connected = False
        self.message_handlers = {}
        self.response_queue = {}
        
    def connect(self):
        """Connect to Mycroft messagebus"""
        try:
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait for connection
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
                
            return self.connected
        except Exception as e:
            logger.error(f"Failed to connect to Mycroft messagebus: {e}")
            return False
    
    def _on_open(self, ws):
        """Handle WebSocket connection open"""
        self.connected = True
        logger.info("Connected to Mycroft messagebus")
        
    def _on_message(self, ws, message):
        """Handle incoming messages from Mycroft"""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "")
            
            # Handle specific message types
            if msg_type in self.message_handlers:
                self.message_handlers[msg_type](data)
                
            # Handle response queue for synchronous requests
            if "context" in data and "request_id" in data["context"]:
                request_id = data["context"]["request_id"]
                if request_id in self.response_queue:
                    self.response_queue[request_id] = data
                    
        except Exception as e:
            logger.error(f"Error handling Mycroft message: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"Mycroft messagebus error: {error}")
        
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        self.connected = False
        logger.info("Disconnected from Mycroft messagebus")
    
    def send_message(self, msg_type: str, data: Dict = None, context: Dict = None):
        """Send message to Mycroft"""
        if not self.connected:
            return False
            
        message = {
            "type": msg_type,
            "data": data or {},
            "context": context or {}
        }
        
        try:
            self.ws.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to Mycroft: {e}")
            return False
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register handler for specific message type"""
        self.message_handlers[msg_type] = handler
    
    def wait_for_response(self, request_id: str, timeout: float = 5.0) -> Optional[Dict]:
        """Wait for response to a specific request"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if request_id in self.response_queue:
                response = self.response_queue.pop(request_id)
                return response
            time.sleep(0.1)
        return None


class MrHappyVoiceService:
    """
    Advanced voice service integrating Mycroft AI with Mr. Happy context
    """
    
    def __init__(self):
        self.messagebus = MycroftMessageBus()
        self.is_initialized = False
        self.user_context = {}
        self.conversation_history = []
        self.skills_loaded = False
        
    async def initialize(self):
        """Initialize Mycroft integration"""
        try:
            # Connect to messagebus
            if not self.messagebus.connect():
                logger.error("Failed to connect to Mycroft messagebus")
                return False
            
            # Register message handlers
            self.messagebus.register_handler("mycroft.ready", self._on_mycroft_ready)
            self.messagebus.register_handler("speak", self._on_speak)
            self.messagebus.register_handler("recognizer_loop:utterance", self._on_utterance)
            self.messagebus.register_handler("intent_service:intent.service", self._on_intent)
            
            # Load custom Mr. Happy skills
            await self._load_custom_skills()
            
            self.is_initialized = True
            logger.info("Mr. Happy voice service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize voice service: {e}")
            return False
    
    def _on_mycroft_ready(self, message):
        """Handle Mycroft ready signal"""
        logger.info("Mycroft core is ready")
        self.skills_loaded = True
    
    def _on_speak(self, message):
        """Handle TTS output from Mycroft"""
        utterance = message.get("data", {}).get("utterance", "")
        logger.info(f"Mr. Happy speaking: {utterance}")
        
        # Store in conversation history
        self.conversation_history.append({
            "type": "assistant",
            "content": utterance,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _on_utterance(self, message):
        """Handle STT input to Mycroft"""
        utterances = message.get("data", {}).get("utterances", [])
        if utterances:
            user_input = utterances[0]
            logger.info(f"User said: {user_input}")
            
            # Store in conversation history
            self.conversation_history.append({
                "type": "user",
                "content": user_input,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def _on_intent(self, message):
        """Handle intent recognition"""
        intent_data = message.get("data", {})
        logger.info(f"Intent recognized: {intent_data}")
    
    async def _load_custom_skills(self):
        """Load custom Mr. Happy skills"""
        try:
            # Send custom skill configurations
            self.messagebus.send_message("mycroft.skills.loaded", {
                "skills": ["axzora.happy_wallet", "axzora.travel_booking", "axzora.recharge_service"]
            })
            
            logger.info("Custom Mr. Happy skills loaded")
        except Exception as e:
            logger.error(f"Failed to load custom skills: {e}")
    
    async def process_voice_input(self, audio_data: bytes, user_id: str) -> Dict:
        """Process voice input and return Mr. Happy's response"""
        if not self.is_initialized:
            return {"error": "Voice service not initialized"}
        
        try:
            request_id = str(uuid.uuid4())
            
            # Set user context
            self.user_context[user_id] = {
                "user_id": user_id,
                "session_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send audio for processing
            self.messagebus.send_message("recognizer_loop:audio", {
                "audio_data": audio_data.hex(),  # Convert bytes to hex string
                "user_id": user_id
            }, context={"request_id": request_id})
            
            # Wait for response
            response = self.messagebus.wait_for_response(request_id, timeout=10.0)
            
            if response:
                return {
                    "success": True,
                    "response": response.get("data", {}),
                    "conversation_id": request_id
                }
            else:
                return {"error": "Timeout waiting for response"}
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {"error": str(e)}
    
    async def process_text_input(self, text: str, user_id: str, context: Dict = None) -> Dict:
        """Process text input and return Mr. Happy's response"""
        if not self.is_initialized:
            return {"error": "Voice service not initialized"}
        
        try:
            request_id = str(uuid.uuid4())
            
            # Add user context and Axzora-specific information
            enhanced_context = {
                "user_id": user_id,
                "session_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "axzora_mr_happy",
                "capabilities": [
                    "wallet_management",
                    "travel_booking", 
                    "recharge_services",
                    "ecommerce_assistance",
                    "financial_insights"
                ]
            }
            
            if context:
                enhanced_context.update(context)
            
            # Send text for intent processing
            self.messagebus.send_message("recognizer_loop:utterance", {
                "utterances": [text],
                "lang": "en-us",
                "user_id": user_id
            }, context={"request_id": request_id, **enhanced_context})
            
            # Wait for response (TTS)
            response = self.messagebus.wait_for_response(request_id, timeout=8.0)
            
            if response:
                # Extract the spoken response
                spoken_text = response.get("data", {}).get("utterance", "")
                
                return {
                    "success": True,
                    "text_response": spoken_text,
                    "audio_response": None,  # Will be generated by TTS
                    "conversation_id": request_id,
                    "intent_data": response.get("data", {}),
                    "context": enhanced_context
                }
            else:
                # Fallback response if Mycroft doesn't respond
                return await self._generate_fallback_response(text, user_id, enhanced_context)
                
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return {"error": str(e)}
    
    async def _generate_fallback_response(self, text: str, user_id: str, context: Dict) -> Dict:
        """Generate fallback response when Mycroft is unavailable"""
        
        # Simple intent detection for key Axzora services
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["wallet", "balance", "money", "paisa"]):
            response = f"I can help you with your Happy Paisa wallet. Your current balance and recent transactions are available in the wallet section. Would you like me to show you your balance?"
            
        elif any(word in text_lower for word in ["travel", "flight", "hotel", "book"]):
            response = f"I can assist you with travel bookings! I can help you find flights, hotels, and book them using your Happy Paisa. What destination are you interested in?"
            
        elif any(word in text_lower for word in ["recharge", "mobile", "phone", "dth"]):
            response = f"I can help you recharge your mobile, DTH, or pay utility bills using Happy Paisa. What service would you like to recharge?"
            
        elif any(word in text_lower for word in ["shop", "buy", "product", "order"]):
            response = f"I can help you shop for products in our e-commerce store. All purchases can be made with Happy Paisa rewards. What are you looking for?"
            
        else:
            response = f"Hello! I'm Mr. Happy, your AI assistant for the Axzora ecosystem. I can help you with wallet management, travel booking, recharges, shopping, and more. What would you like to do today?"
        
        return {
            "success": True,
            "text_response": response,
            "audio_response": None,
            "conversation_id": str(uuid.uuid4()),
            "intent_data": {"fallback": True},
            "context": context
        }
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for user"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    async def set_user_context(self, user_id: str, context: Dict):
        """Set additional context for user sessions"""
        if user_id not in self.user_context:
            self.user_context[user_id] = {}
        self.user_context[user_id].update(context)
    
    def is_ready(self) -> bool:
        """Check if voice service is ready"""
        return self.is_initialized and self.messagebus.connected


# Global instance
mr_happy_voice = MrHappyVoiceService()


async def initialize_voice_service():
    """Initialize the voice service"""
    return await mr_happy_voice.initialize()


async def process_voice_command(text: str, user_id: str, context: Dict = None) -> Dict:
    """Process voice command through Mr. Happy"""
    return await mr_happy_voice.process_text_input(text, user_id, context)


async def get_voice_conversation_history(user_id: str, limit: int = 10) -> List[Dict]:
    """Get conversation history"""
    return await mr_happy_voice.get_conversation_history(user_id, limit)