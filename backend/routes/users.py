from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.user import User, UserCreate, UserUpdate
from ..services.database import get_collection
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    collection = await get_collection("users")
    
    # Check if user already exists
    existing_user = await collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(**user.dict())
    await collection.insert_one(new_user.dict())
    
    return new_user

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    collection = await get_collection("users")
    
    user = await collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

@router.get("/email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """Get user by email"""
    collection = await get_collection("users")
    
    user = await collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    collection = await get_collection("users")
    
    # Check if user exists
    existing_user = await collection.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await collection.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    # Return updated user
    updated_user = await collection.find_one({"id": user_id})
    return User(**updated_user)

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    collection = await get_collection("users")
    
    result = await collection.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.get("/", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100):
    """List all users"""
    collection = await get_collection("users")
    
    users = await collection.find().skip(skip).limit(limit).to_list(limit)
    return [User(**user) for user in users]