from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCROW = "escrow"

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME = "home"
    BOOKS = "books"
    SPORTS = "sports"
    SERVICES = "services"
    DIGITAL = "digital"
    OTHER = "other"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    happy_paisa_balance: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rating: float = 5.0
    total_transactions: int = 0

class UserCreate(BaseModel):
    username: str
    email: str

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price_hp: float  # Price in Happy Paisa
    price_inr: float  # Price in INR (price_hp * 1000)
    category: ProductCategory
    seller_id: str
    seller_username: str
    image_url: Optional[str] = None
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0

class ProductCreate(BaseModel):
    title: str
    description: str
    price_hp: float
    category: ProductCategory
    image_url: Optional[str] = None

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    seller_id: str
    buyer_id: str
    amount_hp: float
    amount_inr: float
    status: TransactionStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class VoiceCommand(BaseModel):
    command: str
    user_id: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VoiceCommandRequest(BaseModel):
    command: str
    user_id: str

class HappyPaisaTransfer(BaseModel):
    from_user_id: str
    to_user_id: str
    amount_hp: float
    description: str

# Helper functions
def hp_to_inr(hp_amount: float) -> float:
    return hp_amount * 1000

def inr_to_hp(inr_amount: float) -> float:
    return inr_amount / 1000

async def get_user_by_id(user_id: str) -> Optional[User]:
    user_doc = await db.users.find_one({"id": user_id})
    return User(**user_doc) if user_doc else None

async def update_user_balance(user_id: str, amount_change: float):
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"happy_paisa_balance": amount_change}}
    )

# Voice command processor
def process_voice_command(command: str, user_id: str) -> str:
    command_lower = command.lower()
    
    if "balance" in command_lower or "wallet" in command_lower:
        return f"I'll check your Happy Paisa balance for you."
    elif "list" in command_lower and ("product" in command_lower or "item" in command_lower):
        return f"I'll help you create a new product listing. What would you like to sell?"
    elif "buy" in command_lower or "purchase" in command_lower:
        return f"I'll help you find products to buy. What are you looking for?"
    elif "send" in command_lower and "happy paisa" in command_lower:
        return f"I'll help you send Happy Paisa to someone. Who would you like to send it to?"
    elif "marketplace" in command_lower or "browse" in command_lower:
        return f"Let me show you the latest products in the marketplace."
    elif "hello" in command_lower or "hi" in command_lower:
        return f"Hello! I'm Mr. Happy, your voice assistant. How can I help you with the marketplace today?"
    else:
        return f"I understand you want to '{command}'. Let me help you with that in the marketplace."

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to Happy Paisa P2P Marketplace"}

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    user = User(**user_data.dict())
    user.happy_paisa_balance = 10.0  # Give new users 10 HP to start
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/users", response_model=List[User])
async def get_all_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, seller_id: str):
    seller = await get_user_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    product = Product(
        **product_data.dict(),
        seller_id=seller_id,
        seller_username=seller.username,
        price_inr=hp_to_inr(product_data.price_hp)
    )
    await db.products.insert_one(product.dict())
    return product

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[ProductCategory] = None):
    query = {"is_available": True}
    if category:
        query["category"] = category
    
    products = await db.products.find(query).sort("created_at", -1).to_list(1000)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product_doc = await db.products.find_one({"id": product_id})
    if not product_doc:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Increment views
    await db.products.update_one(
        {"id": product_id},
        {"$inc": {"views": 1}}
    )
    
    return Product(**product_doc)

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(product_id: str, buyer_id: str):
    # Get product and buyer
    product_doc = await db.products.find_one({"id": product_id})
    if not product_doc:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = Product(**product_doc)
    if not product.is_available:
        raise HTTPException(status_code=400, detail="Product not available")
    
    buyer = await get_user_by_id(buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    if buyer.happy_paisa_balance < product.price_hp:
        raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
    
    # Create transaction in escrow
    transaction = Transaction(
        product_id=product_id,
        seller_id=product.seller_id,
        buyer_id=buyer_id,
        amount_hp=product.price_hp,
        amount_inr=product.price_inr,
        status=TransactionStatus.ESCROW
    )
    
    # Deduct from buyer (put in escrow)
    await update_user_balance(buyer_id, -product.price_hp)
    
    # Mark product as unavailable
    await db.products.update_one(
        {"id": product_id},
        {"$set": {"is_available": False}}
    )
    
    await db.transactions.insert_one(transaction.dict())
    return transaction

@api_router.post("/transactions/{transaction_id}/complete")
async def complete_transaction(transaction_id: str):
    transaction_doc = await db.transactions.find_one({"id": transaction_id})
    if not transaction_doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction = Transaction(**transaction_doc)
    if transaction.status != TransactionStatus.ESCROW:
        raise HTTPException(status_code=400, detail="Transaction not in escrow")
    
    # Transfer Happy Paisa to seller
    await update_user_balance(transaction.seller_id, transaction.amount_hp)
    
    # Update transaction status
    await db.transactions.update_one(
        {"id": transaction_id},
        {
            "$set": {
                "status": TransactionStatus.COMPLETED,
                "completed_at": datetime.utcnow()
            }
        }
    )
    
    # Update user transaction counts
    await db.users.update_one(
        {"id": transaction.seller_id},
        {"$inc": {"total_transactions": 1}}
    )
    await db.users.update_one(
        {"id": transaction.buyer_id},
        {"$inc": {"total_transactions": 1}}
    )
    
    return {"message": "Transaction completed successfully"}

@api_router.get("/transactions/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str):
    transactions = await db.transactions.find({
        "$or": [{"seller_id": user_id}, {"buyer_id": user_id}]
    }).sort("created_at", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.post("/happy-paisa/transfer")
async def transfer_happy_paisa(transfer_data: HappyPaisaTransfer):
    # Verify users exist
    from_user = await get_user_by_id(transfer_data.from_user_id)
    to_user = await get_user_by_id(transfer_data.to_user_id)
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if from_user.happy_paisa_balance < transfer_data.amount_hp:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Perform transfer
    await update_user_balance(transfer_data.from_user_id, -transfer_data.amount_hp)
    await update_user_balance(transfer_data.to_user_id, transfer_data.amount_hp)
    
    return {"message": "Transfer completed successfully"}

@api_router.post("/happy-paisa/mint/{user_id}")
async def mint_happy_paisa(user_id: str, amount_inr: float):
    """Simulate minting Happy Paisa when user adds INR"""
    amount_hp = inr_to_hp(amount_inr)
    await update_user_balance(user_id, amount_hp)
    return {"message": f"Minted {amount_hp} HP from {amount_inr} INR"}

@api_router.post("/voice/command", response_model=VoiceCommand)
async def process_voice(command_data: VoiceCommandRequest):
    response = process_voice_command(command_data.command, command_data.user_id)
    
    voice_command = VoiceCommand(
        command=command_data.command,
        user_id=command_data.user_id,
        response=response
    )
    
    await db.voice_commands.insert_one(voice_command.dict())
    return voice_command

@api_router.get("/voice/history/{user_id}", response_model=List[VoiceCommand])
async def get_voice_history(user_id: str):
    commands = await db.voice_commands.find({"user_id": user_id}).sort("timestamp", -1).limit(50).to_list(50)
    return [VoiceCommand(**cmd) for cmd in commands]

@api_router.get("/stats")
async def get_marketplace_stats():
    total_users = await db.users.count_documents({})
    total_products = await db.products.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    
    # Calculate total Happy Paisa in circulation
    users = await db.users.find({}).to_list(1000)
    total_hp_circulation = sum(user.get("happy_paisa_balance", 0) for user in users)
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_transactions": total_transactions,
        "total_happy_paisa_circulation": total_hp_circulation,
        "total_inr_equivalent": hp_to_inr(total_hp_circulation)
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()