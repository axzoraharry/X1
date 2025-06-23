from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    if db.database is None:
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'axzora_mrhappy')
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client[db_name]
    return db.database

async def close_database():
    if db.client:
        db.client.close()

# Collection helpers
async def get_collection(collection_name: str):
    database = await get_database()
    return database[collection_name]