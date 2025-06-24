import requests
import unittest
import time
import json
from typing import Dict, Any, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://69f89e24-5de7-4351-a66a-0fabb23e8e21.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

class HappyPaisaAPITest(unittest.TestCase):
    """Test suite for Happy Paisa P2P Marketplace API"""
    
    def setUp(self):
        """Set up test data and create a test user"""
        self.test_user = None
        self.test_product = None
        self.test_transaction = None
        
        # Create a test user
        self.create_test_user()
    
    def create_test_user(self):
        """Create a test user for API testing"""
        username = f"test_user_{int(time.time())}"
        response = requests.post(f"{API_URL}/users", json={
            "username": username,
            "email": f"{username}@example.com"
        })
        
        if response.status_code == 200:
            self.test_user = response.json()
            print(f"✅ Created test user: {username} with ID: {self.test_user['id']}")
        else:
            print(f"❌ Failed to create test user: {response.text}")
    
    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing root endpoint...")
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print(f"✅ Root endpoint returned: {response.json()}")
    
    def test_02_get_user(self):
        """Test retrieving a user by ID"""
        if not self.test_user:
            self.skipTest("No test user available")
        
        print(f"\n🔍 Testing get user endpoint for user ID: {self.test_user['id']}...")
        response = requests.get(f"{API_URL}/users/{self.test_user['id']}")
        self.assertEqual(response.status_code, 200)
        user_data = response.json()
        self.assertEqual(user_data["id"], self.test_user["id"])
        self.assertEqual(user_data["username"], self.test_user["username"])
        self.assertEqual(user_data["email"], self.test_user["email"])
        print(f"✅ User retrieved successfully: {user_data['username']}")
        
        # Verify new users get 10 HP starting balance
        self.assertEqual(user_data["happy_paisa_balance"], 10.0)
        print(f"✅ User has correct starting balance: {user_data['happy_paisa_balance']} HP")
    
    def test_03_create_product(self):
        """Test creating a product listing"""
        if not self.test_user:
            self.skipTest("No test user available")
        
        print(f"\n🔍 Testing product creation...")
        product_data = {
            "title": "Test Smartphone",
            "description": "A brand new test smartphone for API testing",
            "price_hp": 0.5,
            "category": "electronics",
            "image_url": "https://example.com/phone.jpg"
        }
        
        response = requests.post(
            f"{API_URL}/products?seller_id={self.test_user['id']}", 
            json=product_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.test_product = response.json()
        
        # Verify product data
        self.assertEqual(self.test_product["title"], product_data["title"])
        self.assertEqual(self.test_product["description"], product_data["description"])
        self.assertEqual(self.test_product["price_hp"], product_data["price_hp"])
        self.assertEqual(self.test_product["category"], product_data["category"])
        self.assertEqual(self.test_product["seller_id"], self.test_user["id"])
        
        # Verify price conversion (1 HP = 1000 INR)
        self.assertEqual(self.test_product["price_inr"], product_data["price_hp"] * 1000)
        
        print(f"✅ Product created successfully: {self.test_product['title']} (ID: {self.test_product['id']})")
    
    def test_04_get_products(self):
        """Test retrieving product listings"""
        print("\n🔍 Testing product listing retrieval...")
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        products = response.json()
        self.assertIsInstance(products, list)
        print(f"✅ Retrieved {len(products)} products")
        
        # If we created a product, verify it's in the list
        if self.test_product:
            product_ids = [p["id"] for p in products]
            self.assertIn(self.test_product["id"], product_ids)
            print(f"✅ Found our test product in the marketplace")
    
    def test_05_get_product_by_id(self):
        """Test retrieving a specific product by ID"""
        if not self.test_product:
            self.skipTest("No test product available")
        
        print(f"\n🔍 Testing product retrieval by ID: {self.test_product['id']}...")
        response = requests.get(f"{API_URL}/products/{self.test_product['id']}")
        self.assertEqual(response.status_code, 200)
        product = response.json()
        self.assertEqual(product["id"], self.test_product["id"])
        self.assertEqual(product["title"], self.test_product["title"])
        
        # Check if views were incremented
        self.assertGreaterEqual(product["views"], 1)
        print(f"✅ Product retrieved successfully with {product['views']} views")
    
    def test_06_mint_happy_paisa(self):
        """Test minting Happy Paisa (converting INR to HP)"""
        if not self.test_user:
            self.skipTest("No test user available")
        
        print(f"\n🔍 Testing Happy Paisa minting...")
        inr_amount = 5000  # 5000 INR should convert to 5 HP
        
        # Get initial balance
        response = requests.get(f"{API_URL}/users/{self.test_user['id']}")
        initial_balance = response.json()["happy_paisa_balance"]
        
        # Mint Happy Paisa
        response = requests.post(
            f"{API_URL}/happy-paisa/mint/{self.test_user['id']}?amount_inr={inr_amount}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print(f"✅ Minting response: {response.json()['message']}")
        
        # Verify balance increased
        response = requests.get(f"{API_URL}/users/{self.test_user['id']}")
        new_balance = response.json()["happy_paisa_balance"]
        expected_increase = inr_amount / 1000  # Convert INR to HP
        self.assertAlmostEqual(new_balance, initial_balance + expected_increase, places=3)
        print(f"✅ Balance increased from {initial_balance} HP to {new_balance} HP (+{expected_increase} HP)")
    
    def test_07_buy_product(self):
        """Test buying a product with Happy Paisa"""
        if not self.test_user or not self.test_product:
            self.skipTest("No test user or product available")
        
        print(f"\n🔍 Testing product purchase...")
        
        # Get initial balance
        response = requests.get(f"{API_URL}/users/{self.test_user['id']}")
        initial_balance = response.json()["happy_paisa_balance"]
        
        # Make sure we have enough balance
        if initial_balance < self.test_product["price_hp"]:
            print(f"⚠️ Insufficient balance ({initial_balance} HP) to buy product ({self.test_product['price_hp']} HP)")
            self.skipTest("Insufficient balance")
        
        # Buy the product
        response = requests.post(
            f"{API_URL}/transactions?product_id={self.test_product['id']}&buyer_id={self.test_user['id']}"
        )
        self.assertEqual(response.status_code, 200)
        self.test_transaction = response.json()
        
        # Verify transaction data
        self.assertEqual(self.test_transaction["product_id"], self.test_product["id"])
        self.assertEqual(self.test_transaction["buyer_id"], self.test_user["id"])
        self.assertEqual(self.test_transaction["seller_id"], self.test_product["seller_id"])
        self.assertEqual(self.test_transaction["amount_hp"], self.test_product["price_hp"])
        self.assertEqual(self.test_transaction["status"], "escrow")
        
        print(f"✅ Transaction created successfully: {self.test_transaction['id']}")
        
        # Verify balance decreased
        response = requests.get(f"{API_URL}/users/{self.test_user['id']}")
        new_balance = response.json()["happy_paisa_balance"]
        expected_decrease = self.test_product["price_hp"]
        self.assertAlmostEqual(new_balance, initial_balance - expected_decrease, places=3)
        print(f"✅ Balance decreased from {initial_balance} HP to {new_balance} HP (-{expected_decrease} HP)")
        
        # Verify product is no longer available
        response = requests.get(f"{API_URL}/products/{self.test_product['id']}")
        product = response.json()
        self.assertFalse(product["is_available"])
        print(f"✅ Product is now marked as unavailable")
    
    def test_08_complete_transaction(self):
        """Test completing a transaction (moving from escrow to seller)"""
        if not self.test_transaction:
            self.skipTest("No test transaction available")
        
        print(f"\n🔍 Testing transaction completion...")
        
        # Get seller's initial balance
        response = requests.get(f"{API_URL}/users/{self.test_transaction['seller_id']}")
        seller_initial_balance = response.json()["happy_paisa_balance"]
        
        # Complete the transaction
        response = requests.post(f"{API_URL}/transactions/{self.test_transaction['id']}/complete")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print(f"✅ Transaction completion response: {response.json()['message']}")
        
        # Verify seller's balance increased
        response = requests.get(f"{API_URL}/users/{self.test_transaction['seller_id']}")
        seller_new_balance = response.json()["happy_paisa_balance"]
        expected_increase = self.test_transaction["amount_hp"]
        self.assertAlmostEqual(seller_new_balance, seller_initial_balance + expected_increase, places=3)
        print(f"✅ Seller's balance increased from {seller_initial_balance} HP to {seller_new_balance} HP (+{expected_increase} HP)")
        
        # Verify transaction status updated
        response = requests.get(f"{API_URL}/transactions/{self.test_user['id']}")
        transactions = response.json()
        completed_transaction = next((t for t in transactions if t["id"] == self.test_transaction["id"]), None)
        if completed_transaction:
            self.assertEqual(completed_transaction["status"], "completed")
            print(f"✅ Transaction status updated to 'completed'")
        else:
            print(f"⚠️ Could not find completed transaction in user's transaction history")
    
    def test_09_voice_command(self):
        """Test voice command processing"""
        if not self.test_user:
            self.skipTest("No test user available")
        
        print(f"\n🔍 Testing voice command processing...")
        
        # Test different voice commands
        commands = [
            "Check my balance",
            "List my phone for 0.5 HP",
            "Show me electronics",
            "Hello Mr. Happy"
        ]
        
        for command in commands:
            print(f"Testing voice command: '{command}'")
            response = requests.post(f"{API_URL}/voice/command", json={
                "command": command,
                "user_id": self.test_user["id"]
            })
            
            self.assertEqual(response.status_code, 200)
            voice_response = response.json()
            self.assertEqual(voice_response["command"], command)
            self.assertEqual(voice_response["user_id"], self.test_user["id"])
            self.assertIsNotNone(voice_response["response"])
            print(f"✅ Voice response: '{voice_response['response']}'")
    
    def test_10_get_marketplace_stats(self):
        """Test retrieving marketplace statistics"""
        print(f"\n🔍 Testing marketplace statistics...")
        
        response = requests.get(f"{API_URL}/stats")
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        
        # Verify stats structure
        required_fields = [
            "total_users", 
            "total_products", 
            "total_transactions", 
            "total_happy_paisa_circulation",
            "total_inr_equivalent"
        ]
        
        for field in required_fields:
            self.assertIn(field, stats)
            print(f"✅ Stats include {field}: {stats[field]}")
        
        # Verify INR equivalent calculation (1 HP = 1000 INR)
        self.assertEqual(stats["total_inr_equivalent"], stats["total_happy_paisa_circulation"] * 1000)
        print(f"✅ INR equivalent calculation is correct")

if __name__ == "__main__":
    # Run tests in order
    unittest.main(argv=['first-arg-is-ignored'], exit=False)