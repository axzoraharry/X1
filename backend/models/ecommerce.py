from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    price_inr: float
    price_hp: float
    original_price_inr: Optional[float] = None
    rating: float = 0.0
    reviews_count: int = 0
    image: str
    images: List[str] = []
    category: str
    in_stock: bool = True
    stock_quantity: int = 0
    features: List[str] = []
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CartItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    quantity: int = 1
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_number: str = Field(default_factory=lambda: f"ORD{uuid.uuid4().hex[:8].upper()}")
    items: List[dict]  # List of {product_id, quantity, price_hp, price_inr}
    total_amount_hp: float
    total_amount_inr: float
    status: str = "pending"  # "pending", "confirmed", "shipped", "delivered", "cancelled"
    shipping_address: dict
    payment_method: str = "happy_paisa"
    payment_status: str = "pending"  # "pending", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    brand: str
    price_inr: float
    original_price_inr: Optional[float] = None
    image: str
    category: str
    stock_quantity: int = 0
    features: List[str] = []
    description: Optional[str] = None

class CartItemCreate(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1

class OrderCreate(BaseModel):
    user_id: str
    items: List[dict]
    shipping_address: dict
    payment_method: str = "happy_paisa"

class ProductSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "popular"  # "popular", "price_low", "price_high", "rating"