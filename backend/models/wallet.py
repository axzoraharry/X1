from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

class HappyPaisaTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # "credit" or "debit"
    amount_hp: float
    amount_inr: float = Field(default=0.0)  # Calculated as amount_hp * 1000
    description: str
    category: str  # "Food", "Travel", "Recharge", "Shopping", etc.
    status: str = "completed"  # "pending", "completed", "failed"
    reference_id: Optional[str] = None  # For linking to other transactions
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HappyPaisaWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    balance_hp: float = 0.0
    balance_inr_equiv: float = 0.0  # Always balance_hp * 1000
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WalletTransaction(BaseModel):
    user_id: str
    type: str
    amount_hp: float
    description: str
    category: str
    reference_id: Optional[str] = None

class WalletBalance(BaseModel):
    user_id: str
    balance_hp: float = Field(description="Happy Paisa balance")
    balance_inr_equiv: float = Field(description="INR equivalent (1 HP = 1000 INR)")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    spending_breakdown: Dict[str, float] = Field(default_factory=dict)
    recent_transactions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Blockchain-specific fields
    blockchain_address: Optional[str] = Field(default="", description="User's blockchain address")
    network: Optional[str] = Field(default="happy-paisa-mainnet", description="Blockchain network")

class TransactionCreate(BaseModel):
    user_id: str
    type: str
    amount_hp: float
    description: str
    category: str
    reference_id: Optional[str] = None