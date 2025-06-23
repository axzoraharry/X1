#!/usr/bin/env python3
import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Get the backend URL from frontend/.env
BACKEND_URL = "https://e66826bb-4625-4714-8e1d-45b66c9cd834.preview.emergentagent.com/api"

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, response=None, error=None):
    """Log test result"""
    status = "PASSED" if passed else "FAILED"
    print(f"[{status}] {name}")
    
    if not passed and response:
        print(f"  Response: {response.status_code} - {response.text}")
    if not passed and error:
        print(f"  Error: {error}")
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "timestamp": datetime.now().isoformat()
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            log_test("Health Check", True)
            return True
        else:
            log_test("Health Check", False, response)
            return False
    except Exception as e:
        log_test("Health Check", False, error=str(e))
        return False

def test_user_management():
    """Test user management endpoints"""
    # Get demo user
    try:
        response = requests.get(f"{BACKEND_URL}/users/email/demo@axzora.com")
        if response.status_code == 200:
            demo_user = response.json()
            log_test("Get Demo User", True)
            demo_user_id = demo_user["id"]
        else:
            log_test("Get Demo User", False, response)
            return False
        
        # Create new user
        new_user_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        new_user_data = {
            "name": "Test User",
            "email": new_user_email,
            "location": "Test Location",
            "mobile_number": "9876543210"
        }
        
        response = requests.post(f"{BACKEND_URL}/users/", json=new_user_data)
        if response.status_code == 200:
            new_user = response.json()
            log_test("Create User", True)
            new_user_id = new_user["id"]
        else:
            log_test("Create User", False, response)
            return False
        
        # Update user
        update_data = {
            "name": "Updated Test User",
            "location": "Updated Location"
        }
        
        response = requests.put(f"{BACKEND_URL}/users/{new_user_id}", json=update_data)
        if response.status_code == 200 and response.json()["name"] == "Updated Test User":
            log_test("Update User", True)
        else:
            log_test("Update User", False, response)
            return False
        
        # Get user by ID
        response = requests.get(f"{BACKEND_URL}/users/{new_user_id}")
        if response.status_code == 200 and response.json()["name"] == "Updated Test User":
            log_test("Get User by ID", True)
        else:
            log_test("Get User by ID", False, response)
            return False
        
        # List users
        response = requests.get(f"{BACKEND_URL}/users/")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("List Users", True)
        else:
            log_test("List Users", False, response)
            return False
        
        # Delete user
        response = requests.delete(f"{BACKEND_URL}/users/{new_user_id}")
        if response.status_code == 200:
            log_test("Delete User", True)
        else:
            log_test("Delete User", False, response)
            return False
        
        return demo_user_id
    
    except Exception as e:
        log_test("User Management", False, error=str(e))
        return False

def test_wallet_system(user_id):
    """Test wallet system endpoints"""
    if not user_id:
        log_test("Wallet System - No User ID", False)
        return False
    
    try:
        # Get wallet balance
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/balance")
        if response.status_code == 200:
            wallet_data = response.json()
            log_test("Get Wallet Balance", True)
            initial_balance = wallet_data["balance_hp"]
        else:
            log_test("Get Wallet Balance", False, response)
            return False
        
        # Add credit transaction
        credit_amount = 5.0
        response = requests.post(
            f"{BACKEND_URL}/wallet/{user_id}/credit",
            params={"amount_hp": credit_amount, "description": "Test credit"}
        )
        if response.status_code == 200:
            log_test("Credit Wallet", True)
        else:
            log_test("Credit Wallet", False, response)
            return False
        
        # Verify balance increased
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/balance")
        if response.status_code == 200:
            new_balance = response.json()["balance_hp"]
            if abs(new_balance - (initial_balance + credit_amount)) < 0.001:
                log_test("Verify Credit Balance", True)
            else:
                log_test("Verify Credit Balance", False, response)
                return False
        else:
            log_test("Verify Credit Balance", False, response)
            return False
        
        # Get transactions
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/transactions")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get Transactions", True)
        else:
            log_test("Get Transactions", False, response)
            return False
        
        # Test INR to HP conversion
        inr_amount = 2000
        response = requests.post(
            f"{BACKEND_URL}/wallet/{user_id}/convert/inr-to-hp",
            params={"amount_inr": inr_amount}
        )
        if response.status_code == 200:
            conversion_data = response.json()
            if abs(conversion_data["converted_amount_hp"] - (inr_amount / 1000)) < 0.001:
                log_test("INR to HP Conversion", True)
            else:
                log_test("INR to HP Conversion", False, response)
                return False
        else:
            log_test("INR to HP Conversion", False, response)
            return False
        
        # Test HP to INR conversion
        hp_amount = 1.0
        response = requests.post(
            f"{BACKEND_URL}/wallet/{user_id}/convert/hp-to-inr",
            params={"amount_hp": hp_amount}
        )
        if response.status_code == 200:
            conversion_data = response.json()
            if abs(conversion_data["converted_amount_inr"] - (hp_amount * 1000)) < 0.001:
                log_test("HP to INR Conversion", True)
            else:
                log_test("HP to INR Conversion", False, response)
                return False
        else:
            log_test("HP to INR Conversion", False, response)
            return False
        
        # Debit transaction
        debit_amount = 1.0
        response = requests.post(
            f"{BACKEND_URL}/wallet/{user_id}/debit",
            params={
                "amount_hp": debit_amount, 
                "description": "Test debit",
                "category": "Testing"
            }
        )
        if response.status_code == 200:
            log_test("Debit Wallet", True)
        else:
            log_test("Debit Wallet", False, response)
            return False
        
        return True
    
    except Exception as e:
        log_test("Wallet System", False, error=str(e))
        return False

def test_travel_api(user_id):
    """Test travel API endpoints"""
    if not user_id:
        log_test("Travel API - No User ID", False)
        return False
    
    try:
        # Search flights
        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        flight_search = {
            "origin": "NAG",
            "destination": "GOA",
            "departure_date": str(today),
            "return_date": str(tomorrow),
            "passengers": 1,
            "class_type": "economy"
        }
        
        response = requests.post(f"{BACKEND_URL}/travel/flights/search", json=flight_search)
        if response.status_code == 200 and isinstance(response.json(), list):
            flights = response.json()
            log_test("Search Flights", True)
            if flights:
                flight_id = flights[0]["id"]
            else:
                log_test("No Flights Found", False)
                return False
        else:
            log_test("Search Flights", False, response)
            return False
        
        # Get flight details
        response = requests.get(f"{BACKEND_URL}/travel/flights/{flight_id}")
        if response.status_code == 200:
            log_test("Get Flight Details", True)
        else:
            log_test("Get Flight Details", False, response)
            return False
        
        # Search hotels
        hotel_search = {
            "destination": "Goa",
            "check_in_date": str(today),
            "check_out_date": str(tomorrow),
            "guests": 2
        }
        
        response = requests.post(f"{BACKEND_URL}/travel/hotels/search", json=hotel_search)
        if response.status_code == 200 and isinstance(response.json(), list):
            hotels = response.json()
            log_test("Search Hotels", True)
            if hotels:
                hotel_id = hotels[0]["id"]
            else:
                log_test("No Hotels Found", False)
                return False
        else:
            log_test("Search Hotels", False, response)
            return False
        
        # Get hotel details
        response = requests.get(f"{BACKEND_URL}/travel/hotels/{hotel_id}")
        if response.status_code == 200:
            log_test("Get Hotel Details", True)
        else:
            log_test("Get Hotel Details", False, response)
            return False
        
        # Create flight booking
        booking_data = {
            "user_id": user_id,
            "booking_type": "flight",
            "item_id": flight_id,
            "booking_details": {
                "passengers": [
                    {
                        "name": "Test Passenger",
                        "age": 30,
                        "gender": "Male"
                    }
                ],
                "contact_email": "test@example.com",
                "contact_phone": "9876543210"
            },
            "payment_method": "happy_paisa"
        }
        
        response = requests.post(f"{BACKEND_URL}/travel/bookings", json=booking_data)
        if response.status_code == 200:
            booking = response.json()
            log_test("Create Flight Booking", True)
            booking_id = booking["id"]
        else:
            log_test("Create Flight Booking", False, response)
            return False
        
        # Get user bookings
        response = requests.get(f"{BACKEND_URL}/travel/bookings/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get User Bookings", True)
        else:
            log_test("Get User Bookings", False, response)
            return False
        
        # Get booking details
        response = requests.get(f"{BACKEND_URL}/travel/bookings/detail/{booking_id}")
        if response.status_code == 200:
            log_test("Get Booking Details", True)
        else:
            log_test("Get Booking Details", False, response)
            return False
        
        # Cancel booking
        response = requests.put(f"{BACKEND_URL}/travel/bookings/{booking_id}/cancel")
        if response.status_code == 200:
            log_test("Cancel Booking", True)
        else:
            log_test("Cancel Booking", False, response)
            return False
        
        return True
    
    except Exception as e:
        log_test("Travel API", False, error=str(e))
        return False

def test_recharge_api(user_id):
    """Test recharge API endpoints"""
    if not user_id:
        log_test("Recharge API - No User ID", False)
        return False
    
    try:
        # Get mobile plans
        response = requests.get(f"{BACKEND_URL}/recharge/mobile/plans/jio")
        if response.status_code == 200 and isinstance(response.json(), list):
            plans = response.json()
            log_test("Get Mobile Plans", True)
            if plans:
                plan_id = plans[0]["id"]
            else:
                log_test("No Plans Found", False)
                return False
        else:
            log_test("Get Mobile Plans", False, response)
            return False
        
        # Get all mobile plans
        response = requests.get(f"{BACKEND_URL}/recharge/mobile/plans")
        if response.status_code == 200 and isinstance(response.json(), dict):
            log_test("Get All Mobile Plans", True)
        else:
            log_test("Get All Mobile Plans", False, response)
            return False
        
        # Detect operator
        response = requests.post(
            f"{BACKEND_URL}/recharge/mobile/detect-operator",
            params={"mobile_number": "7012345678"}
        )
        if response.status_code == 200 and "operator" in response.json():
            log_test("Detect Operator", True)
            operator = response.json()["operator"]
        else:
            log_test("Detect Operator", False, response)
            return False
        
        # Mobile recharge
        recharge_data = {
            "user_id": user_id,
            "mobile_number": "7012345678",
            "operator": operator,
            "plan_id": plan_id,
            "payment_method": "happy_paisa"
        }
        
        response = requests.post(f"{BACKEND_URL}/recharge/mobile/recharge", json=recharge_data)
        if response.status_code == 200:
            log_test("Mobile Recharge", True)
        else:
            log_test("Mobile Recharge", False, response)
            return False
        
        # Get recharge history
        response = requests.get(f"{BACKEND_URL}/recharge/mobile/history/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get Recharge History", True)
        else:
            log_test("Get Recharge History", False, response)
            return False
        
        # DTH recharge
        dth_data = {
            "user_id": user_id,
            "customer_id": "12345678",
            "operator": "tata_sky",
            "amount": 299
        }
        
        response = requests.post(f"{BACKEND_URL}/recharge/dth/recharge", json=dth_data)
        if response.status_code == 200:
            log_test("DTH Recharge", True)
        else:
            log_test("DTH Recharge", False, response)
            return False
        
        # Utility bill payment
        bill_data = {
            "user_id": user_id,
            "bill_type": "electricity",
            "consumer_number": "123456789",
            "provider": "MSEB",
            "amount": 500
        }
        
        response = requests.post(f"{BACKEND_URL}/recharge/utility/bill-payment", json=bill_data)
        if response.status_code == 200:
            log_test("Utility Bill Payment", True)
        else:
            log_test("Utility Bill Payment", False, response)
            return False
        
        # Get all recharge history
        response = requests.get(f"{BACKEND_URL}/recharge/history/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), dict):
            log_test("Get All Recharge History", True)
        else:
            log_test("Get All Recharge History", False, response)
            return False
        
        return True
    
    except Exception as e:
        log_test("Recharge API", False, error=str(e))
        return False

def test_ecommerce_api(user_id):
    """Test e-commerce API endpoints"""
    if not user_id:
        log_test("E-commerce API - No User ID", False)
        return False
    
    try:
        # Search products
        response = requests.get(f"{BACKEND_URL}/ecommerce/products/search")
        if response.status_code == 200 and isinstance(response.json(), list):
            products = response.json()
            log_test("Search Products", True)
            if products:
                product_id = products[0]["id"]
            else:
                log_test("No Products Found", False)
                return False
        else:
            log_test("Search Products", False, response)
            return False
        
        # Get product details
        response = requests.get(f"{BACKEND_URL}/ecommerce/products/{product_id}")
        if response.status_code == 200:
            log_test("Get Product Details", True)
        else:
            log_test("Get Product Details", False, response)
            return False
        
        # Get all products
        response = requests.get(f"{BACKEND_URL}/ecommerce/products")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get All Products", True)
        else:
            log_test("Get All Products", False, response)
            return False
        
        # Add to cart
        cart_item = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 2
        }
        
        response = requests.post(f"{BACKEND_URL}/ecommerce/cart/add", json=cart_item)
        if response.status_code == 200:
            cart_item_data = response.json()
            log_test("Add to Cart", True)
            cart_item_id = cart_item_data["id"]
        else:
            log_test("Add to Cart", False, response)
            return False
        
        # Get cart
        response = requests.get(f"{BACKEND_URL}/ecommerce/cart/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get Cart", True)
        else:
            log_test("Get Cart", False, response)
            return False
        
        # Update cart quantity
        response = requests.put(
            f"{BACKEND_URL}/ecommerce/cart/{cart_item_id}/quantity",
            params={"quantity": 3}
        )
        if response.status_code == 200:
            log_test("Update Cart Quantity", True)
        else:
            log_test("Update Cart Quantity", False, response)
            return False
        
        # Create order
        order_data = {
            "user_id": user_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "name": "Test User",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "pincode": "123456",
                "phone": "9876543210"
            },
            "payment_method": "happy_paisa"
        }
        
        response = requests.post(f"{BACKEND_URL}/ecommerce/orders", json=order_data)
        if response.status_code == 200:
            order = response.json()
            log_test("Create Order", True)
            order_id = order["id"]
        else:
            log_test("Create Order", False, response)
            return False
        
        # Get user orders
        response = requests.get(f"{BACKEND_URL}/ecommerce/orders/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get User Orders", True)
        else:
            log_test("Get User Orders", False, response)
            return False
        
        # Get order details
        response = requests.get(f"{BACKEND_URL}/ecommerce/orders/detail/{order_id}")
        if response.status_code == 200:
            log_test("Get Order Details", True)
        else:
            log_test("Get Order Details", False, response)
            return False
        
        # Get categories
        response = requests.get(f"{BACKEND_URL}/ecommerce/categories")
        if response.status_code == 200 and "categories" in response.json():
            log_test("Get Categories", True)
        else:
            log_test("Get Categories", False, response)
            return False
        
        # Get recommendations
        response = requests.get(f"{BACKEND_URL}/ecommerce/recommendations/{user_id}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_test("Get Recommendations", True)
        else:
            log_test("Get Recommendations", False, response)
            return False
        
        return True
    
    except Exception as e:
        log_test("E-commerce API", False, error=str(e))
        return False

def test_dashboard_api(user_id):
    """Test dashboard API endpoints"""
    if not user_id:
        log_test("Dashboard API - No User ID", False)
        return False
    
    try:
        # Get dashboard overview
        response = requests.get(f"{BACKEND_URL}/dashboard/{user_id}/overview")
        if response.status_code == 200:
            overview = response.json()
            if "user" in overview and "wallet" in overview:
                log_test("Get Dashboard Overview", True)
            else:
                log_test("Get Dashboard Overview - Missing Data", False, response)
                return False
        else:
            log_test("Get Dashboard Overview", False, response)
            return False
        
        # Get user stats
        response = requests.get(f"{BACKEND_URL}/dashboard/{user_id}/stats")
        if response.status_code == 200:
            log_test("Get User Stats", True)
        else:
            log_test("Get User Stats", False, response)
            return False
        
        # Get notifications
        response = requests.get(f"{BACKEND_URL}/dashboard/notifications/{user_id}")
        if response.status_code == 200 and "notifications" in response.json():
            log_test("Get Notifications", True)
            notifications = response.json()["notifications"]
            if notifications:
                notification_id = notifications[0]["id"]
            else:
                log_test("No Notifications Found", True)
                return True
        else:
            log_test("Get Notifications", False, response)
            return False
        
        # Mark notification as read
        response = requests.post(f"{BACKEND_URL}/dashboard/notifications/{notification_id}/mark-read")
        if response.status_code == 200:
            log_test("Mark Notification as Read", True)
        else:
            log_test("Mark Notification as Read", False, response)
            return False
        
        return True
    
    except Exception as e:
        log_test("Dashboard API", False, error=str(e))
        return False

def run_all_tests():
    """Run all tests"""
    print("Starting backend API tests...")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test health check
    health_ok = test_health_check()
    if not health_ok:
        print("Health check failed. Aborting tests.")
        return
    
    # Test user management
    user_id = test_user_management()
    if not user_id:
        print("User management tests failed. Aborting tests.")
        return
    
    # Test wallet system
    wallet_ok = test_wallet_system(user_id)
    if not wallet_ok:
        print("Wallet system tests failed. Continuing with other tests.")
    
    # Test travel API
    travel_ok = test_travel_api(user_id)
    if not travel_ok:
        print("Travel API tests failed. Continuing with other tests.")
    
    # Test recharge API
    recharge_ok = test_recharge_api(user_id)
    if not recharge_ok:
        print("Recharge API tests failed. Continuing with other tests.")
    
    # Test e-commerce API
    ecommerce_ok = test_ecommerce_api(user_id)
    if not ecommerce_ok:
        print("E-commerce API tests failed. Continuing with other tests.")
    
    # Test dashboard API
    dashboard_ok = test_dashboard_api(user_id)
    if not dashboard_ok:
        print("Dashboard API tests failed. Continuing with other tests.")
    
    # Print summary
    print("\nTest Summary:")
    print(f"Total tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\nAll tests passed successfully!")
    else:
        print(f"\n{test_results['failed']} tests failed.")

if __name__ == "__main__":
    run_all_tests()