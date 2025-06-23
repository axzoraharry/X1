from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import route modules
from .routes import users, wallet, travel, recharge, ecommerce, dashboard

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'axzora_mrhappy')]

# Create the main app without a prefix
app = FastAPI(title="Axzora Mr. Happy 2.0 API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Axzora Mr. Happy 2.0 API is running!", "status": "online"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Include all route modules
app.include_router(users.router)
app.include_router(wallet.router)
app.include_router(travel.router)
app.include_router(recharge.router)
app.include_router(ecommerce.router)
app.include_router(dashboard.router)

# Include the main API router
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

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Axzora Mr. Happy 2.0 API starting up...")
    
    # Initialize sample data if needed
    await initialize_sample_data()
    
    logger.info("Startup complete!")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connections on shutdown"""
    logger.info("Shutting down Axzora Mr. Happy 2.0 API...")
    client.close()

async def initialize_sample_data():
    """Initialize sample data for demo purposes"""
    try:
        # Create sample user if not exists
        users_collection = db["users"]
        sample_user = await users_collection.find_one({"email": "demo@axzora.com"})
        
        if not sample_user:
            from .models.user import User
            demo_user = User(
                name="Demo User",
                email="demo@axzora.com",
                avatar="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
                location="Nagpur, India",
                mobile_number="9876543210"
            )
            await users_collection.insert_one(demo_user.dict())
            
            # Create demo wallet with some balance
            from .services.wallet_service import WalletService
            from .models.wallet import WalletTransaction
            
            # Add initial balance
            initial_transaction = WalletTransaction(
                user_id=demo_user.id,
                type="credit",
                amount_hp=10.0,
                description="Welcome bonus",
                category="Bonus"
            )
            await WalletService.add_transaction(initial_transaction)
            
            logger.info("Sample data initialized")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)