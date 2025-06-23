from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import uuid

class FlightSearch(BaseModel):
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = 1
    class_type: str = "economy"

class Flight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    airline: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    price_inr: float
    price_hp: float
    stops: int = 0
    aircraft: Optional[str] = None
    available_seats: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HotelSearch(BaseModel):
    destination: str
    check_in_date: date
    check_out_date: date
    guests: int = 1

class Hotel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    rating: float
    price_per_night_inr: float
    price_per_night_hp: float
    images: List[str]
    amenities: List[str]
    reviews_count: int
    available_rooms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TravelBooking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    booking_type: str  # "flight", "hotel", "bus"
    booking_reference: str
    item_id: str  # flight_id, hotel_id, etc.
    total_amount_hp: float
    total_amount_inr: float
    status: str = "confirmed"  # "pending", "confirmed", "cancelled"
    booking_details: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookingCreate(BaseModel):
    user_id: str
    booking_type: str
    item_id: str
    booking_details: dict
    payment_method: str = "happy_paisa"