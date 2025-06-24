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
    balance_hp: float
    balance_inr_equiv: float
    recent_transactions: List[HappyPaisaTransaction]
    spending_breakdown: Dict[str, float]

class TransactionCreate(BaseModel):
    user_id: str
    type: str
    amount_hp: float
    description: str
    category: str
    reference_id: Optional[str] = None