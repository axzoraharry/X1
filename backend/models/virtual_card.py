from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class CardStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class CardType(str, Enum):
    VIRTUAL = "virtual"
    PHYSICAL = "physical"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REVERSED = "reversed"

class MerchantCategory(str, Enum):
    GROCERIES = "groceries"
    FUEL = "fuel"
    RESTAURANTS = "restaurants"
    ONLINE_SHOPPING = "online_shopping"
    ATM_WITHDRAWAL = "atm_withdrawal"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    UTILITIES = "utilities"
    OTHER = "other"

class CardControls(BaseModel):
    daily_limit_inr: float = Field(default=50000, description="Daily spending limit in INR")
    monthly_limit_inr: float = Field(default=200000, description="Monthly spending limit in INR")
    per_transaction_limit_inr: float = Field(default=25000, description="Per transaction limit in INR")
    allowed_merchant_categories: List[MerchantCategory] = Field(default_factory=lambda: list(MerchantCategory))
    blocked_merchant_categories: List[MerchantCategory] = Field(default_factory=list)
    international_transactions_enabled: bool = Field(default=False)
    online_transactions_enabled: bool = Field(default=True)
    atm_withdrawals_enabled: bool = Field(default=True)

class VirtualCard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User ID from users collection")
    card_number_masked: str = Field(..., description="Masked card number (e.g., ****-****-****-1234)")
    card_number_hash: str = Field(..., description="Hashed full card number for internal reference")
    expiry_month: int = Field(..., description="Card expiry month (1-12)")
    expiry_year: int = Field(..., description="Card expiry year (YYYY)")
    cvv_hash: str = Field(..., description="Hashed CVV for internal reference")
    card_holder_name: str = Field(..., description="Cardholder name")
    card_type: CardType = Field(default=CardType.VIRTUAL)
    card_status: CardStatus = Field(default=CardStatus.ACTIVE)
    card_program_id: str = Field(default="axzora_happy_paisa", description="Card program identifier")
    issuer_id: str = Field(default="demo_issuer", description="Partner bank/issuer identifier")
    network: str = Field(default="RuPay", description="Card network (RuPay, Visa, Mastercard)")
    current_balance_inr: float = Field(default=0.0, description="Current loaded balance in INR")
    current_balance_hp: float = Field(default=0.0, description="Current loaded balance in Happy Paisa")
    controls: CardControls = Field(default_factory=CardControls)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    expires_at: datetime = Field(..., description="Card expiration date")
    last_used_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CardCreateRequest(BaseModel):
    user_id: str
    card_holder_name: str
    initial_load_amount_hp: float = Field(default=0.0, description="Initial Happy Paisa amount to load")
    controls: Optional[CardControls] = None
    metadata: Optional[Dict[str, Any]] = None

class CardUpdateRequest(BaseModel):
    card_holder_name: Optional[str] = None
    card_status: Optional[CardStatus] = None
    controls: Optional[CardControls] = None
    metadata: Optional[Dict[str, Any]] = None

class CardDetailsResponse(BaseModel):
    id: str
    user_id: str
    card_number_masked: str
    expiry_month: int
    expiry_year: int
    card_holder_name: str
    card_type: CardType
    card_status: CardStatus
    network: str
    current_balance_inr: float
    current_balance_hp: float
    controls: CardControls
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: datetime

class CardTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_id: str = Field(..., description="Virtual card ID")
    user_id: str = Field(..., description="User ID")
    transaction_type: str = Field(..., description="purchase, load, refund, reversal")
    amount_inr: float = Field(..., description="Transaction amount in INR")
    amount_hp: float = Field(..., description="Equivalent Happy Paisa amount")
    merchant_name: str = Field(..., description="Merchant name")
    merchant_category: MerchantCategory = Field(default=MerchantCategory.OTHER)
    merchant_id: Optional[str] = None
    transaction_status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    authorization_code: Optional[str] = None
    reference_number: str = Field(default_factory=lambda: f"AXZ{uuid.uuid4().hex[:8].upper()}")
    description: str = Field(..., description="Transaction description")
    location: Optional[str] = None
    currency: str = Field(default="INR")
    exchange_rate: float = Field(default=1000.0, description="INR to HP conversion rate")
    fees_inr: float = Field(default=0.0, description="Transaction fees in INR")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CardTransactionRequest(BaseModel):
    card_id: str
    amount_inr: float
    merchant_name: str
    merchant_category: MerchantCategory = MerchantCategory.OTHER
    description: str
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class KYCDocument(BaseModel):
    document_type: str = Field(..., description="aadhar, pan, passport, driving_license")
    document_number: str = Field(..., description="Document number")
    document_url: Optional[str] = None
    verified: bool = Field(default=False)
    verified_at: Optional[datetime] = None

class UserKYC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User ID")
    kyc_status: KYCStatus = Field(default=KYCStatus.NOT_STARTED)
    full_name: str = Field(..., description="Full legal name")
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    phone_verified: bool = Field(default=False)
    email_verified: bool = Field(default=False)
    documents: List[KYCDocument] = Field(default_factory=list)
    risk_score: Optional[int] = Field(default=0, description="Risk score (0-100)")
    approved_for_card_issuance: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[str] = None
    rejection_reason: Optional[str] = None

class KYCRequest(BaseModel):
    user_id: str
    full_name: str
    date_of_birth: str
    address: str
    phone_number: str
    email: str
    documents: List[KYCDocument]