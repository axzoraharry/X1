#!/usr/bin/env python3
import requests
import json
import time
import uuid
from datetime import datetime

# Get the backend URL from frontend/.env
BACKEND_URL = "https://abd01438-62a3-49c3-83d1-9130061069a4.preview.emergentagent.com/api"

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

def test_automation_health():
    """Test automation health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/automation/health")
        if response.status_code == 200:
            health_data = response.json()
            log_test("Automation Health Check", True)
            print(f"  Health Status: {health_data.get('status', 'unknown')}")
            print(f"  n8n Connection: {health_data.get('n8n_connection', 'unknown')}")
            return True
        else:
            log_test("Automation Health Check", False, response)
            return False
    except Exception as e:
        log_test("Automation Health Check", False, error=str(e))
        return False

def test_send_notification():
    """Test notification sending endpoint"""
    try:
        # Test different notification channels
        channels = ["telegram", "email", "sms"]
        all_passed = True
        
        for channel in channels:
            test_message = f"Test notification via {channel} at {datetime.now().isoformat()}"
            
            response = requests.post(
                f"{BACKEND_URL}/automation/notifications/send",
                params={
                    "user_id": "demo_user_id",
                    "notification_type": channel,
                    "message": test_message
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                channel_passed = result.get("status") in ["sent", "triggered"]
                log_test(f"Send {channel.title()} Notification", channel_passed, response)
                if not channel_passed:
                    all_passed = False
            else:
                log_test(f"Send {channel.title()} Notification", False, response)
                all_passed = False
        
        return all_passed
    except Exception as e:
        log_test("Send Notification", False, error=str(e))
        return False

def test_ai_process_transaction():
    """Test AI transaction processing endpoint"""
    try:
        # Create sample transaction data
        transaction_data = {
            "id": str(uuid.uuid4()),
            "user_id": "demo_user_id",
            "type": "debit",
            "amount_hp": 1.5,
            "amount_inr": 1500,
            "description": "Shopping - Electronics",
            "category": "Shopping",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{BACKEND_URL}/automation/ai/process-transaction",
            params={
                "user_id": "demo_user_id",
                "analysis_type": "spending_insights"
            },
            json=transaction_data
        )
        
        if response.status_code == 200:
            result = response.json()
            log_test("AI Process Transaction", True)
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Analysis Type: {result.get('analysis_type', 'unknown')}")
            return True
        else:
            log_test("AI Process Transaction", False, response)
            return False
    except Exception as e:
        log_test("AI Process Transaction", False, error=str(e))
        return False

def test_backup_user_data():
    """Test user data backup endpoint"""
    try:
        # Test different backup types
        backup_types = ["full", "transactions", "profile"]
        destinations = ["google_drive", "aws_s3"]
        all_passed = True
        
        for backup_type in backup_types:
            for destination in destinations:
                response = requests.post(
                    f"{BACKEND_URL}/automation/backup/user-data",
                    params={
                        "user_id": "demo_user_id",
                        "backup_type": backup_type,
                        "destination": destination
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    backup_passed = result.get("status") == "backup_initiated"
                    log_test(f"Backup User Data ({backup_type} to {destination})", backup_passed, response)
                    if not backup_passed:
                        all_passed = False
                else:
                    log_test(f"Backup User Data ({backup_type} to {destination})", False, response)
                    all_passed = False
        
        return all_passed
    except Exception as e:
        log_test("Backup User Data", False, error=str(e))
        return False

def test_get_user_automations():
    """Test get user automation history endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/automation/triggers/demo_user_id")
        
        if response.status_code == 200:
            result = response.json()
            log_test("Get User Automation History", True)
            print(f"  User ID: {result.get('user_id', 'unknown')}")
            print(f"  Total Automations: {result.get('total', 0)}")
            return True
        else:
            log_test("Get User Automation History", False, response)
            return False
    except Exception as e:
        log_test("Get User Automation History", False, error=str(e))
        return False

def test_error_handling():
    """Test error handling for invalid inputs"""
    try:
        # Test with invalid user ID
        response = requests.get(f"{BACKEND_URL}/automation/triggers/nonexistent_user")
        invalid_user_handled = response.status_code in [404, 400, 500]
        log_test("Error Handling - Invalid User ID", invalid_user_handled, response)
        
        # Test with invalid notification type
        response = requests.post(
            f"{BACKEND_URL}/automation/notifications/send",
            params={
                "user_id": "demo_user_id",
                "notification_type": "invalid_channel",
                "message": "Test message"
            }
        )
        invalid_channel_handled = response.status_code in [400, 404, 500]
        log_test("Error Handling - Invalid Notification Channel", invalid_channel_handled, response)
        
        # Test with malformed data
        response = requests.post(
            f"{BACKEND_URL}/automation/ai/process-transaction",
            params={
                "user_id": "demo_user_id"
            },
            json={"invalid": "data"}
        )
        malformed_data_handled = response.status_code in [400, 422, 500]
        log_test("Error Handling - Malformed Data", malformed_data_handled, response)
        
        return invalid_user_handled and invalid_channel_handled and malformed_data_handled
    except Exception as e:
        log_test("Error Handling Tests", False, error=str(e))
        return False

def run_all_tests():
    """Run all automation integration tests"""
    print("Starting n8n automation integration tests...")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test health check
    health_ok = test_automation_health()
    if not health_ok:
        print("Automation health check failed, but continuing with other tests...")
    
    # Test notification sending
    notification_ok = test_send_notification()
    if not notification_ok:
        print("Notification sending tests had issues, but continuing...")
    
    # Test AI processing
    ai_ok = test_ai_process_transaction()
    if not ai_ok:
        print("AI processing test had issues, but continuing...")
    
    # Test data backup
    backup_ok = test_backup_user_data()
    if not backup_ok:
        print("Data backup tests had issues, but continuing...")
    
    # Test automation history
    history_ok = test_get_user_automations()
    if not history_ok:
        print("Automation history test had issues, but continuing...")
    
    # Test error handling
    error_handling_ok = test_error_handling()
    if not error_handling_ok:
        print("Error handling tests had issues, but continuing...")
    
    # Print summary
    print("\nTest Summary:")
    print(f"Total tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\nAll automation integration tests passed successfully!")
    else:
        print(f"\n{test_results['failed']} automation integration tests failed.")
        print("Note: Some failures may be expected if n8n is not running.")

if __name__ == "__main__":
    run_all_tests()