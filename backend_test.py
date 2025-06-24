#!/usr/bin/env python3
import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Get the backend URL from frontend/.env
BACKEND_URL = "https://91f0f1ff-fbc5-4d50-a572-45e7123be9d8.preview.emergentagent.com/api"

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

# Blockchain API Tests
def test_blockchain_health():
    """Test blockchain health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            log_test("Blockchain Health Check", True)
            return True
        else:
            log_test("Blockchain Health Check", False, response)
            return False
    except Exception as e:
        log_test("Blockchain Health Check", False, error=str(e))
        return False

def test_blockchain_status():
    """Test blockchain status endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/status")
        if response.status_code == 200 and response.json().get("status") == "operational":
            log_test("Blockchain Status", True)
            return True
        else:
            log_test("Blockchain Status", False, response)
            return False
    except Exception as e:
        log_test("Blockchain Status", False, error=str(e))
        return False

def test_blockchain_network_stats():
    """Test blockchain network statistics endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/network/stats")
        if response.status_code == 200 and "network" in response.json():
            log_test("Blockchain Network Stats", True)
            return True
        else:
            log_test("Blockchain Network Stats", False, response)
            return False
    except Exception as e:
        log_test("Blockchain Network Stats", False, error=str(e))
        return False

def test_user_blockchain_address(user_id):
    """Test user blockchain address endpoint"""
    if not user_id:
        log_test("User Blockchain Address - No User ID", False)
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/user/{user_id}/address")
        if response.status_code == 200 and "address" in response.json():
            log_test("User Blockchain Address", True)
            return response.json()
        else:
            log_test("User Blockchain Address", False, response)
            return False
    except Exception as e:
        log_test("User Blockchain Address", False, error=str(e))
        return False

def test_user_blockchain_balance(user_id):
    """Test user blockchain balance endpoint"""
    if not user_id:
        log_test("User Blockchain Balance - No User ID", False)
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/user/{user_id}/balance")
        if response.status_code == 200 and "balance_hp" in response.json():
            log_test("User Blockchain Balance", True)
            return response.json()
        else:
            log_test("User Blockchain Balance", False, response)
            return False
    except Exception as e:
        log_test("User Blockchain Balance", False, error=str(e))
        return False

def test_mint_happy_paisa(user_id):
    """Test minting Happy Paisa tokens"""
    if not user_id:
        log_test("Mint Happy Paisa - No User ID", False)
        return False
    
    try:
        # Mint a small amount for testing
        amount_hp = 0.5
        response = requests.post(
            f"{BACKEND_URL}/blockchain/user/{user_id}/mint?amount_hp={amount_hp}&reference_id=test_mint_{uuid.uuid4().hex[:8]}"
        )
        
        if response.status_code == 200 and response.json().get("success") == True:
            tx_hash = response.json().get("transaction_hash")
            log_test("Mint Happy Paisa", True)
            return tx_hash
        else:
            log_test("Mint Happy Paisa", False, response)
            return False
    except Exception as e:
        log_test("Mint Happy Paisa", False, error=str(e))
        return False

def test_burn_happy_paisa(user_id):
    """Test burning Happy Paisa tokens"""
    if not user_id:
        log_test("Burn Happy Paisa - No User ID", False)
        return False
    
    try:
        # Burn a small amount for testing
        amount_hp = 0.1
        response = requests.post(
            f"{BACKEND_URL}/blockchain/user/{user_id}/burn?amount_hp={amount_hp}&reference_id=test_burn_{uuid.uuid4().hex[:8]}"
        )
        
        if response.status_code == 200 and response.json().get("success") == True:
            tx_hash = response.json().get("transaction_hash")
            log_test("Burn Happy Paisa", True)
            return tx_hash
        else:
            log_test("Burn Happy Paisa", False, response)
            return False
    except Exception as e:
        log_test("Burn Happy Paisa", False, error=str(e))
        return False

def test_p2p_transfer(from_user_id, to_user_id=None):
    """Test peer-to-peer transfer of Happy Paisa"""
    if not from_user_id:
        log_test("P2P Transfer - No From User ID", False)
        return False
    
    try:
        # If no to_user_id provided, create a test user
        if not to_user_id:
            new_user_email = f"test_recipient_{uuid.uuid4().hex[:8]}@example.com"
            new_user_data = {
                "name": "Test Recipient",
                "email": new_user_email,
                "location": "Test Location",
                "mobile_number": "9876543210"
            }
            
            user_response = requests.post(f"{BACKEND_URL}/users/", json=new_user_data)
            if user_response.status_code == 200:
                to_user_id = user_response.json()["id"]
                print(f"Created recipient user with ID: {to_user_id}")
            else:
                log_test("P2P Transfer - Create Recipient User", False, user_response)
                return False
        
        # Transfer a small amount
        amount_hp = 0.1
        transfer_url = f"{BACKEND_URL}/blockchain/transfer?from_user_id={from_user_id}&to_user_id={to_user_id}&amount_hp={amount_hp}&description=Test P2P Transfer"
        print(f"Making P2P transfer request to: {transfer_url}")
        
        response = requests.post(transfer_url)
        
        print(f"P2P Transfer Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200 and "success" in response.json() and response.json().get("success") == True:
            tx_hash = response.json().get("transaction_hash")
            log_test("P2P Transfer via Blockchain", True)
            
            # Also test the wallet P2P endpoint
            wallet_response = requests.post(
                f"{BACKEND_URL}/wallet/p2p-transfer?from_user_id={from_user_id}&to_user_id={to_user_id}&amount_hp={amount_hp}&description=Test Wallet P2P Transfer"
            )
            
            print(f"Wallet P2P Transfer Response: {wallet_response.status_code} - {wallet_response.text}")
            
            if wallet_response.status_code == 200 and "success" in wallet_response.json() and wallet_response.json().get("success") == True:
                log_test("P2P Transfer via Wallet", True)
            else:
                log_test("P2P Transfer via Wallet", False, wallet_response)
            
            return tx_hash
        else:
            log_test("P2P Transfer via Blockchain", False, response)
            return False
    except Exception as e:
        print(f"P2P Transfer Exception: {str(e)}")
        log_test("P2P Transfer", False, error=str(e))
        return False

def test_transaction_status(tx_hash):
    """Test transaction status endpoint"""
    if not tx_hash:
        log_test("Transaction Status - No Transaction Hash", False)
        return False
    
    try:
        # Wait a moment for transaction to be processed
        time.sleep(2)
        
        response = requests.get(f"{BACKEND_URL}/blockchain/transaction/{tx_hash}")
        if response.status_code == 200 and "status" in response.json():
            log_test("Transaction Status", True)
            return True
        else:
            log_test("Transaction Status", False, response)
            return False
    except Exception as e:
        log_test("Transaction Status", False, error=str(e))
        return False

def test_transaction_sync(tx_hash):
    """Test transaction synchronization endpoint"""
    if not tx_hash:
        log_test("Transaction Sync - No Transaction Hash", False)
        return False
    
    try:
        response = requests.post(f"{BACKEND_URL}/blockchain/sync/transaction/{tx_hash}")
        if response.status_code == 200 and response.json().get("success") == True:
            log_test("Transaction Sync", True)
            return True
        else:
            log_test("Transaction Sync", False, response)
            return False
    except Exception as e:
        log_test("Transaction Sync", False, error=str(e))
        return False

def test_user_transactions(user_id):
    """Test user transactions endpoint"""
    if not user_id:
        log_test("User Transactions - No User ID", False)
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/blockchain/user/{user_id}/transactions")
        if response.status_code == 200 and "transactions" in response.json():
            log_test("User Blockchain Transactions", True)
            return True
        else:
            log_test("User Blockchain Transactions", False, response)
            return False
    except Exception as e:
        log_test("User Blockchain Transactions", False, error=str(e))
        return False

def test_wallet_blockchain_integration(user_id):
    """Test wallet integration with blockchain"""
    if not user_id:
        log_test("Wallet Blockchain Integration - No User ID", False)
        return False
    
    try:
        # Test enhanced wallet balance
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/balance")
        if response.status_code == 200 and "balance_hp" in response.json():
            log_test("Enhanced Wallet Balance", True)
        else:
            log_test("Enhanced Wallet Balance", False, response)
            return False
        
        # Test blockchain address retrieval via wallet
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/blockchain-address")
        if response.status_code == 200 and "address" in response.json():
            log_test("Wallet Blockchain Address", True)
        else:
            log_test("Wallet Blockchain Address", False, response)
            return False
        
        # Test blockchain state sync
        response = requests.post(f"{BACKEND_URL}/wallet/{user_id}/sync-blockchain")
        if response.status_code == 200 and response.json().get("success") == True:
            log_test("Wallet Blockchain Sync", True)
        else:
            log_test("Wallet Blockchain Sync", False, response)
            return False
        
        # Test wallet analytics
        response = requests.get(f"{BACKEND_URL}/wallet/{user_id}/analytics")
        if response.status_code == 200 and "analytics" in response.json():
            log_test("Wallet Analytics with Blockchain", True)
        else:
            log_test("Wallet Analytics with Blockchain", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Wallet Blockchain Integration", False, error=str(e))
        return False

def test_blockchain_explorer():
    """Test blockchain explorer endpoints"""
    try:
        # Test latest blocks
        response = requests.get(f"{BACKEND_URL}/blockchain/explorer/latest-blocks")
        if response.status_code == 200 and "latest_blocks" in response.json():
            log_test("Blockchain Explorer - Latest Blocks", True)
        else:
            log_test("Blockchain Explorer - Latest Blocks", False, response)
            return False
        
        # Test blockchain search with a block number
        response = requests.get(f"{BACKEND_URL}/blockchain/explorer/search/1000000")
        if response.status_code == 200 and "results" in response.json():
            log_test("Blockchain Explorer - Search", True)
        else:
            log_test("Blockchain Explorer - Search", False, response)
            return False
        
        return True
    except Exception as e:
        log_test("Blockchain Explorer", False, error=str(e))
        return False

def test_virtual_cards_blockchain_integration(user_id):
    """Test virtual cards integration with blockchain"""
    if not user_id:
        log_test("Virtual Cards Blockchain Integration - No User ID", False)
        return False
    
    try:
        # First check if user has KYC approved
        kyc_response = requests.get(f"{BACKEND_URL}/virtual-cards/kyc/user/{user_id}")
        
        # If KYC not found or not approved, create demo KYC
        if kyc_response.status_code != 200 or kyc_response.json().get("kyc_status") != "approved":
            demo_kyc_response = requests.post(
                f"{BACKEND_URL}/virtual-cards/demo/create-kyc?user_id={user_id}&full_name=Test User"
            )
            if demo_kyc_response.status_code != 200:
                log_test("Create Demo KYC", False, demo_kyc_response)
                return False
            log_test("Create Demo KYC", True)
        
        # Get user's cards
        cards_response = requests.get(f"{BACKEND_URL}/virtual-cards/user/{user_id}")
        
        # Create a card if user doesn't have one
        if cards_response.status_code != 200 or len(cards_response.json()) == 0:
            card_data = {
                "user_id": user_id,
                "card_holder_name": "Test User",
                "initial_load_amount_hp": 0.0
            }
            create_card_response = requests.post(f"{BACKEND_URL}/virtual-cards/", json=card_data)
            if create_card_response.status_code != 200:
                log_test("Create Virtual Card", False, create_card_response)
                return False
            
            card_id = create_card_response.json()["id"]
            log_test("Create Virtual Card", True)
        else:
            card_id = cards_response.json()[0]["id"]
        
        # Test loading card from blockchain balance
        load_response = requests.post(
            f"{BACKEND_URL}/virtual-cards/{card_id}/load?amount_hp=0.2&user_id={user_id}"
        )
        if load_response.status_code == 200 and load_response.json().get("success") == True:
            log_test("Load Card from Blockchain Balance", True)
        else:
            log_test("Load Card from Blockchain Balance", False, load_response)
            return False
        
        # Test card transactions
        transactions_response = requests.get(
            f"{BACKEND_URL}/virtual-cards/{card_id}/transactions?user_id={user_id}"
        )
        if transactions_response.status_code == 200:
            log_test("Card Transactions with Blockchain", True)
        else:
            log_test("Card Transactions with Blockchain", False, transactions_response)
            return False
        
        # Test simulating a card transaction
        transaction_request = {
            "card_id": card_id,
            "amount_inr": 100.0,  # 0.1 HP
            "merchant_name": "Test Merchant",
            "merchant_category": "retail",
            "description": "Test purchase"
        }
        simulate_response = requests.post(
            f"{BACKEND_URL}/virtual-cards/simulate-transaction", 
            json=transaction_request
        )
        if simulate_response.status_code == 200:
            log_test("Card Transaction with Blockchain", True)
        else:
            log_test("Card Transaction with Blockchain", False, simulate_response)
            return False
        
        return True
    except Exception as e:
        log_test("Virtual Cards Blockchain Integration", False, error=str(e))
        return False

def test_blockchain_api(user_id):
    """Test all blockchain API endpoints"""
    if not user_id:
        log_test("Blockchain API - No User ID", False)
        return False
    
    try:
        # Test blockchain health
        blockchain_health_ok = test_blockchain_health()
        if not blockchain_health_ok:
            return False
        
        # Test blockchain status
        blockchain_status_ok = test_blockchain_status()
        if not blockchain_status_ok:
            return False
        
        # Test blockchain network stats
        network_stats_ok = test_blockchain_network_stats()
        if not network_stats_ok:
            return False
        
        # Test user blockchain address
        user_address = test_user_blockchain_address(user_id)
        if not user_address:
            return False
        
        # Test user blockchain balance
        user_balance = test_user_blockchain_balance(user_id)
        if not user_balance:
            return False
        
        # Test minting Happy Paisa
        mint_tx_hash = test_mint_happy_paisa(user_id)
        if not mint_tx_hash:
            return False
        
        # Test transaction status
        tx_status_ok = test_transaction_status(mint_tx_hash)
        if not tx_status_ok:
            return False
        
        # Test transaction sync
        tx_sync_ok = test_transaction_sync(mint_tx_hash)
        if not tx_sync_ok:
            return False
        
        # Test user transactions
        user_transactions_ok = test_user_transactions(user_id)
        if not user_transactions_ok:
            return False
        
        # Test P2P transfer
        p2p_tx_hash = test_p2p_transfer(user_id)
        if not p2p_tx_hash:
            return False
        
        # Test burning Happy Paisa
        burn_tx_hash = test_burn_happy_paisa(user_id)
        if not burn_tx_hash:
            return False
        
        # Test wallet blockchain integration
        wallet_integration_ok = test_wallet_blockchain_integration(user_id)
        if not wallet_integration_ok:
            return False
        
        # Test blockchain explorer
        explorer_ok = test_blockchain_explorer()
        if not explorer_ok:
            return False
        
        # Test virtual cards blockchain integration
        cards_integration_ok = test_virtual_cards_blockchain_integration(user_id)
        if not cards_integration_ok:
            return False
        
        return True
    
    except Exception as e:
        log_test("Blockchain API", False, error=str(e))
        return False

def run_tests():
    """Run all tests"""
    print("Starting API tests...")
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
    
    # Test blockchain API
    blockchain_ok = test_blockchain_api(user_id)
    if not blockchain_ok:
        print("Blockchain API tests failed.")
    else:
        print("Blockchain API tests passed successfully!")
    
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
    run_tests()
