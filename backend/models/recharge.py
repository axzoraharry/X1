from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class RechargePlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operator: str  # "jio", "airtel", "vi", "bsnl"
    amount: float
    amount_hp: float
    validity: str
    data: str
    calls: str
    sms: str
    description: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RechargeRequest(BaseModel):
    user_id: str
    mobile_number: str
    operator: str
    plan_id: str
    payment_method: str = "happy_paisa"

class Recharge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mobile_number: str
    operator: str
    plan_id: str
    amount: float
    amount_hp: float
    status: str = "completed"  # "pending", "completed", "failed"
    transaction_id: Optional[str] = None
    operator_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DTHRecharge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    customer_id: str
    operator: str  # "tata_sky", "dish_tv", "airtel_digital_tv"
    amount: float
    amount_hp: float
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UtilityBill(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    bill_type: str  # "electricity", "gas", "water", "broadband"
    consumer_number: str
    provider: str
    amount: float
    amount_hp: float
    due_date: Optional[datetime] = None
    status: str = "paid"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DTHRequest(BaseModel):
    user_id: str
    customer_id: str
    operator: str
    amount: float

class UtilityBillRequest(BaseModel):
    user_id: str
    bill_type: str
    consumer_number: str
    provider: str
    amount: float