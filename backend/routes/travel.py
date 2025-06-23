from fastapi import APIRouter, HTTPException
from typing import List
from ..models.travel import Flight, Hotel, FlightSearch, HotelSearch, TravelBooking, BookingCreate
from ..services.database import get_collection
from ..services.wallet_service import WalletService
from ..models.wallet import WalletTransaction
from datetime import datetime

router = APIRouter(prefix="/api/travel", tags=["travel"])

# Mock data for demonstration
MOCK_FLIGHTS = [
    {
        "id": "flight_1",
        "airline": "IndiGo",
        "flight_number": "6E-123",
        "origin": "NAG",
        "destination": "GOA",
        "departure_time": "08:30",
        "arrival_time": "10:15",
        "duration": "1h 45m",
        "price_inr": 4999,
        "price_hp": 4.999,
        "stops": 0,
        "aircraft": "A320",
        "available_seats": 23
    },
    {
        "id": "flight_2",
        "airline": "Air India",
        "flight_number": "AI-456",
        "origin": "NAG",
        "destination": "GOA",
        "departure_time": "14:20",
        "arrival_time": "16:30",
        "duration": "2h 10m",
        "price_inr": 5499,
        "price_hp": 5.499,
        "stops": 0,
        "aircraft": "A321",
        "available_seats": 15
    },
    {
        "id": "flight_3",
        "airline": "SpiceJet",
        "flight_number": "SG-789",
        "origin": "NAG",
        "destination": "GOA",
        "departure_time": "19:45",
        "arrival_time": "21:35",
        "duration": "1h 50m",
        "price_inr": 3999,
        "price_hp": 3.999,
        "stops": 0,
        "aircraft": "B737",
        "available_seats": 31
    }
]

MOCK_HOTELS = [
    {
        "id": "hotel_1",
        "name": "Taj Exotica Resort & Spa",
        "location": "Benaulim, South Goa",
        "rating": 4.8,
        "price_per_night_inr": 12000,
        "price_per_night_hp": 12.0,
        "images": ["https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=400&h=300&fit=crop"],
        "amenities": ["Pool", "Spa", "Beach Access", "Wi-Fi", "Restaurant"],
        "reviews_count": 1247,
        "available_rooms": 3
    },
    {
        "id": "hotel_2", 
        "name": "The Leela Goa",
        "location": "Cavelossim Beach, South Goa",
        "rating": 4.7,
        "price_per_night_inr": 8500,
        "price_per_night_hp": 8.5,
        "images": ["https://images.unsplash.com/photo-1578774204375-826dc5d996ed?w=400&h=300&fit=crop"],
        "amenities": ["Pool", "Beach Access", "Wi-Fi", "Gym", "Restaurant"],
        "reviews_count": 892,
        "available_rooms": 7
    }
]

@router.post("/flights/search", response_model=List[Flight])
async def search_flights(search: FlightSearch):
    """Search for flights"""
    try:
        # For now, return mock data. In production, this would call external APIs
        filtered_flights = []
        for flight_data in MOCK_FLIGHTS:
            if (flight_data["origin"].upper() == search.origin.upper() and 
                flight_data["destination"].upper() == search.destination.upper()):
                flight = Flight(**flight_data)
                filtered_flights.append(flight)
        
        return filtered_flights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")

@router.get("/flights/{flight_id}", response_model=Flight)
async def get_flight(flight_id: str):
    """Get flight details by ID"""
    try:
        for flight_data in MOCK_FLIGHTS:
            if flight_data["id"] == flight_id:
                return Flight(**flight_data)
        
        raise HTTPException(status_code=404, detail="Flight not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flight: {str(e)}")

@router.post("/hotels/search", response_model=List[Hotel])
async def search_hotels(search: HotelSearch):
    """Search for hotels"""
    try:
        # For now, return mock data
        filtered_hotels = []
        for hotel_data in MOCK_HOTELS:
            # Simple destination matching
            if search.destination.lower() in hotel_data["location"].lower():
                hotel = Hotel(**hotel_data)
                filtered_hotels.append(hotel)
        
        return filtered_hotels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")

@router.get("/hotels/{hotel_id}", response_model=Hotel)
async def get_hotel(hotel_id: str):
    """Get hotel details by ID"""
    try:
        for hotel_data in MOCK_HOTELS:
            if hotel_data["id"] == hotel_id:
                return Hotel(**hotel_data)
        
        raise HTTPException(status_code=404, detail="Hotel not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hotel: {str(e)}")

@router.post("/bookings", response_model=TravelBooking)
async def create_booking(booking: BookingCreate):
    """Create a travel booking"""
    try:
        collection = await get_collection("travel_bookings")
        
        # Get item details based on booking type
        item_price_hp = 0
        item_price_inr = 0
        
        if booking.booking_type == "flight":
            for flight_data in MOCK_FLIGHTS:
                if flight_data["id"] == booking.item_id:
                    item_price_hp = flight_data["price_hp"]
                    item_price_inr = flight_data["price_inr"]
                    break
        elif booking.booking_type == "hotel":
            for hotel_data in MOCK_HOTELS:
                if hotel_data["id"] == booking.item_id:
                    item_price_hp = hotel_data["price_per_night_hp"]
                    item_price_inr = hotel_data["price_per_night_inr"]
                    break
        
        if item_price_hp == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Check user balance if paying with Happy Paisa
        if booking.payment_method == "happy_paisa":
            balance = await WalletService.get_balance(booking.user_id)
            if balance.balance_hp < item_price_hp:
                raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
        
        # Create booking
        new_booking = TravelBooking(
            user_id=booking.user_id,
            booking_type=booking.booking_type,
            booking_reference=f"AXZ{datetime.now().strftime('%Y%m%d%H%M%S')}",
            item_id=booking.item_id,
            total_amount_hp=item_price_hp,
            total_amount_inr=item_price_inr,
            booking_details=booking.booking_details
        )
        
        # Save booking
        await collection.insert_one(new_booking.dict())
        
        # Process payment if Happy Paisa
        if booking.payment_method == "happy_paisa":
            transaction = WalletTransaction(
                user_id=booking.user_id,
                type="debit",
                amount_hp=item_price_hp,
                description=f"{booking.booking_type.title()} booking - {new_booking.booking_reference}",
                category="Travel",
                reference_id=new_booking.id
            )
            await WalletService.add_transaction(transaction)
        
        return new_booking
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

@router.get("/bookings/{user_id}", response_model=List[TravelBooking])
async def get_user_bookings(user_id: str):
    """Get user's travel bookings"""
    try:
        collection = await get_collection("travel_bookings")
        
        bookings = await collection.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        return [TravelBooking(**booking) for booking in bookings]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bookings: {str(e)}")

@router.get("/bookings/detail/{booking_id}", response_model=TravelBooking)
async def get_booking(booking_id: str):
    """Get booking details by ID"""
    try:
        collection = await get_collection("travel_bookings")
        
        booking = await collection.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return TravelBooking(**booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get booking: {str(e)}")

@router.put("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str):
    """Cancel a booking"""
    try:
        collection = await get_collection("travel_bookings")
        
        # Get booking
        booking = await collection.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Update status
        await collection.update_one(
            {"id": booking_id},
            {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
        )
        
        # Refund if paid with Happy Paisa
        booking_obj = TravelBooking(**booking)
        if booking_obj.total_amount_hp > 0:
            refund_transaction = WalletTransaction(
                user_id=booking_obj.user_id,
                type="credit",
                amount_hp=booking_obj.total_amount_hp,
                description=f"Refund for cancelled booking - {booking_obj.booking_reference}",
                category="Refund",
                reference_id=booking_id
            )
            await WalletService.add_transaction(refund_transaction)
        
        return {"message": "Booking cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel booking: {str(e)}")