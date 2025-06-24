from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class BlockchainWalletBalance(BaseModel):
    """Enhanced wallet balance with blockchain integration"""
    user_id: str
    balance_hp: float = Field(description="Happy Paisa balance")
    balance_inr_equiv: float = Field(description="INR equivalent (1 HP = 1000 INR)")
    blockchain_address: str = Field(description="User's blockchain address")
    network: str = Field(default="happy-paisa-mainnet", description="Blockchain network")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    spending_breakdown: Dict[str, float] = Field(default_factory=dict)
    recent_transactions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Blockchain-specific fields
    balance_planck: Optional[int] = Field(description="Balance in smallest chain unit")
    nonce: Optional[int] = Field(default=0, description="Account nonce")
    is_on_chain: bool = Field(default=True, description="Whether account exists on chain")
    
class BlockchainTransaction(BaseModel):
    """Blockchain transaction model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    blockchain_hash: Optional[str] = Field(description="Blockchain transaction hash")
    block_number: Optional[int] = Field(description="Block number where transaction was included")
    block_hash: Optional[str] = Field(description="Hash of the block")
    transaction_type: str = Field(description="mint, burn, transfer, spend")
    amount_hp: float
    amount_planck: Optional[int] = Field(description="Amount in planck units")
    from_address: Optional[str] = Field(description="Sender blockchain address")
    to_address: Optional[str] = Field(description="Recipient blockchain address")
    status: str = Field(default="pending", description="pending, confirmed, failed, finalized")
    description: str
    category: str = Field(default="Other")
    reference_id: Optional[str] = None
    gas_fee: Optional[float] = Field(default=0.0, description="Transaction fee")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    network: str = Field(default="happy-paisa-mainnet")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BlockchainWalletInfo(BaseModel):
    """Complete wallet information including blockchain details"""
    user_id: str
    balance: BlockchainWalletBalance
    address_info: Dict[str, str]
    network_info: Dict[str, Any]
    recent_transactions: List[BlockchainTransaction]
    analytics: Dict[str, Any]
    
class WalletAnalytics(BaseModel):
    """Wallet analytics with blockchain insights"""
    user_id: str
    period_days: int
    
    # Traditional metrics
    total_spent_hp: float
    total_received_hp: float
    transaction_count: int
    category_spending: Dict[str, float]
    
    # Blockchain metrics
    blockchain_address: str
    network: str
    on_chain_balance: float
    total_gas_paid: float
    blockchain_transaction_count: int
    
    # Network insights
    network_total_supply: float
    user_percentage_of_supply: float
    network_participation_score: float
    
    # Advanced insights
    spending_trend: str = Field(description="increasing, decreasing, stable")
    most_active_category: str
    blockchain_activity_level: str = Field(description="low, medium, high")
    
class P2PTransferRequest(BaseModel):
    """Request model for peer-to-peer transfers"""
    from_user_id: str
    to_user_id: str
    amount_hp: float = Field(gt=0, description="Amount must be positive")
    description: Optional[str] = Field(default="P2P Transfer")
    include_message: Optional[str] = None
    
class PaymentRequest(BaseModel):
    """Request model for payments to merchants/services"""
    user_id: str
    merchant_name: str
    amount_hp: float = Field(gt=0)
    category: str = Field(default="Other")
    description: str
    reference_id: Optional[str] = None
    merchant_address: Optional[str] = Field(description="Merchant's blockchain address")
    
class WalletSyncResponse(BaseModel):
    """Response for wallet synchronization"""
    user_id: str
    sync_status: str = Field(description="success, partial, failed")
    blockchain_balance: float
    local_balance: float
    balance_difference: float
    transactions_synced: int
    sync_timestamp: datetime
    errors: List[str] = Field(default_factory=list)
    
class NetworkStatus(BaseModel):
    """Blockchain network status information"""
    network_name: str
    status: str = Field(description="connected, disconnected, syncing")
    latest_block: int
    block_time_seconds: float
    total_supply_hp: float
    active_addresses: int
    transactions_per_second: float
    network_health_score: float = Field(ge=0, le=100)
    
class AddressInfo(BaseModel):
    """Blockchain address information"""
    address: str
    public_key: str
    network: str
    balance_hp: float
    balance_planck: int
    nonce: int
    is_active: bool
    created_at: datetime
    last_transaction_at: Optional[datetime] = None