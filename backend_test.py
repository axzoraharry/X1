#!/usr/bin/env python3
import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Get the backend URL from frontend/.env
BACKEND_URL = "https://83d0d702-1cb4-4aa6-aecf-c0ffe0eead99.preview.emergentagent.com/api"

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

def test_analytics_health():
    """Test analytics health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            log_test("Analytics Health Check", True)
            return True
        else:
            log_test("Analytics Health Check", False, response)
            return False
    except Exception as e:
        log_test("Analytics Health Check", False, error=str(e))
        return False

def test_analytics_summary():
    """Test analytics summary endpoint"""
    try:
        # Test global analytics summary
        response = requests.get(f"{BACKEND_URL}/analytics/summary")
        if response.status_code == 200 and "summary" in response.json():
            log_test("Global Analytics Summary", True)
        else:
            log_test("Global Analytics Summary", False, response)
            return False
        
        # Test user-specific analytics summary
        # First get a valid user ID
        user_response = requests.get(f"{BACKEND_URL}/users/email/demo@axzora.com")
        if user_response.status_code == 200:
            user_id = user_response.json()["id"]
            
            response = requests.get(f"{BACKEND_URL}/analytics/summary/{user_id}")
            if response.status_code == 200 and "summary" in response.json():
                log_test("User Analytics Summary", True)
            else:
                log_test("User Analytics Summary", False, response)
                return False
        else:
            log_test("Get User for Analytics Summary", False, user_response)
            return False
        
        return True
    except Exception as e:
        log_test("Analytics Summary", False, error=str(e))
        return False

def test_event_tracking(user_id):
    """Test event tracking endpoint"""
    if not user_id:
        log_test("Event Tracking - No User ID", False)
        return False
    
    try:
        # Track a custom event
        event_data = {
            "event_name": "test_event",
            "user_id": user_id,
            "parameters": {
                "test_param": "test_value",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/analytics/track-event", json=event_data)
        if response.status_code == 200 and response.json().get("status") == "success":
            log_test("Track Custom Event", True)
        else:
            log_test("Track Custom Event", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Event Tracking", False, error=str(e))
        return False

def test_user_journey_tracking(user_id):
    """Test user journey tracking endpoint"""
    if not user_id:
        log_test("User Journey Tracking - No User ID", False)
        return False
    
    try:
        # Track user journey step
        journey_data = {
            "user_id": user_id,
            "journey_step": "test_step",
            "metadata": {
                "source": "test",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/analytics/track-user-journey", json=journey_data)
        if response.status_code == 200 and response.json().get("status") == "success":
            log_test("Track User Journey", True)
        else:
            log_test("Track User Journey", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("User Journey Tracking", False, error=str(e))
        return False

def test_happy_paisa_transaction_tracking(user_id):
    """Test Happy Paisa transaction tracking endpoint"""
    if not user_id:
        log_test("Happy Paisa Transaction Tracking - No User ID", False)
        return False
    
    try:
        # Track Happy Paisa transaction
        transaction_data = {
            "user_id": user_id,
            "transaction_type": "credit",
            "amount": 1.5,
            "currency": "HP",
            "transaction_id": f"test_tx_{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(f"{BACKEND_URL}/analytics/track-happy-paisa-transaction", json=transaction_data)
        if response.status_code == 200 and response.json().get("status") == "success":
            log_test("Track Happy Paisa Transaction", True)
        else:
            log_test("Track Happy Paisa Transaction", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Happy Paisa Transaction Tracking", False, error=str(e))
        return False

def test_booking_tracking(user_id):
    """Test booking tracking endpoint"""
    if not user_id:
        log_test("Booking Tracking - No User ID", False)
        return False
    
    try:
        # Track booking event
        booking_data = {
            "user_id": user_id,
            "booking_type": "flight",
            "booking_id": f"test_booking_{uuid.uuid4().hex[:8]}",
            "amount": 2.5,
            "status": "confirmed",
            "metadata": {
                "destination": "Goa",
                "passengers": 1,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        response = requests.post(f"{BACKEND_URL}/analytics/track-booking", json=booking_data)
        if response.status_code == 200 and response.json().get("status") == "success":
            log_test("Track Booking Event", True)
        else:
            log_test("Track Booking Event", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Booking Tracking", False, error=str(e))
        return False

def test_voice_command_tracking(user_id):
    """Test voice command tracking endpoint"""
    if not user_id:
        log_test("Voice Command Tracking - No User ID", False)
        return False
    
    try:
        # Track voice command
        voice_data = {
            "user_id": user_id,
            "command_type": "booking_inquiry",
            "success": True,
            "duration_ms": 1250.5,
            "confidence_score": 0.92
        }
        
        response = requests.post(f"{BACKEND_URL}/analytics/track-voice-command", json=voice_data)
        if response.status_code == 200 and response.json().get("status") == "success":
            log_test("Track Voice Command", True)
        else:
            log_test("Track Voice Command", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Voice Command Tracking", False, error=str(e))
        return False

def test_analytics_api(user_id):
    """Test all analytics API endpoints"""
    if not user_id:
        log_test("Analytics API - No User ID", False)
        return False
    
    try:
        # Test analytics health
        analytics_health_ok = test_analytics_health()
        if not analytics_health_ok:
            return False
        
        # Test analytics summary
        analytics_summary_ok = test_analytics_summary()
        if not analytics_summary_ok:
            return False
        
        # Test event tracking
        event_tracking_ok = test_event_tracking(user_id)
        if not event_tracking_ok:
            return False
        
        # Test user journey tracking
        user_journey_ok = test_user_journey_tracking(user_id)
        if not user_journey_ok:
            return False
        
        # Test Happy Paisa transaction tracking
        hp_transaction_ok = test_happy_paisa_transaction_tracking(user_id)
        if not hp_transaction_ok:
            return False
        
        # Test booking tracking
        booking_tracking_ok = test_booking_tracking(user_id)
        if not booking_tracking_ok:
            return False
        
        # Test voice command tracking
        voice_command_ok = test_voice_command_tracking(user_id)
        if not voice_command_ok:
            return False
        
        return True
    
    except Exception as e:
        log_test("Analytics API", False, error=str(e))
        return False

def run_analytics_tests():
    """Run only analytics tests"""
    print("Starting analytics API tests...")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test health check
    health_ok = test_health_check()
    if not health_ok:
        print("Health check failed. Aborting tests.")
        return
    
    # Test user management to get user ID
    user_id = test_user_management()
    if not user_id:
        print("User management tests failed. Aborting tests.")
        return
    
    # Test analytics API
    analytics_ok = test_analytics_api(user_id)
    if not analytics_ok:
        print("Analytics API tests failed.")
    else:
        print("Analytics API tests passed successfully!")
    
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
    run_analytics_tests()
