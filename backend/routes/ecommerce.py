from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.ecommerce import Product, CartItem, Order, ProductCreate, CartItemCreate, OrderCreate, ProductSearch
from ..services.database import get_collection
from ..services.wallet_service import WalletService
from ..models.wallet import WalletTransaction

router = APIRouter(prefix="/api/ecommerce", tags=["ecommerce"])

# Mock products data
MOCK_PRODUCTS = [
    {
        "id": "prod_1",
        "name": "Wireless Earbuds Pro",
        "brand": "TechSound",
        "price_inr": 4999,
        "price_hp": 4.999,
        "original_price_inr": 6999,
        "rating": 4.5,
        "reviews_count": 234,
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300&h=300&fit=crop",
        "category": "Electronics",
        "in_stock": True,
        "stock_quantity": 50,
        "features": ["Noise Cancellation", "20hr Battery", "Quick Charge", "Water Resistant"],
        "description": "Premium wireless earbuds with advanced noise cancellation technology."
    },
    {
        "id": "prod_2",
        "name": "Smart Watch X",
        "brand": "FitTech",
        "price_inr": 8999,
        "price_hp": 8.999,
        "original_price_inr": 12999,
        "rating": 4.3,
        "reviews_count": 156,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
        "category": "Wearables",
        "in_stock": True,
        "stock_quantity": 25,
        "features": ["Heart Rate Monitor", "GPS", "Water Proof", "7-day Battery"],
        "description": "Advanced smart watch with comprehensive health tracking features."
    },
    {
        "id": "prod_3",
        "name": "Premium Coffee Beans",
        "brand": "Roast Masters",
        "price_inr": 899,
        "price_hp": 0.899,
        "original_price_inr": 1299,
        "rating": 4.7,
        "reviews_count": 89,
        "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300&h=300&fit=crop",
        "category": "Food & Beverage",
        "in_stock": True,
        "stock_quantity": 100,
        "features": ["Arabica Beans", "Medium Roast", "Single Origin", "500g Pack"],
        "description": "Premium single-origin arabica coffee beans, perfectly roasted."
    },
    {
        "id": "prod_4",
        "name": "Bluetooth Speaker",
        "brand": "SoundWave",
        "price_inr": 2999,
        "price_hp": 2.999,
        "original_price_inr": 4499,
        "rating": 4.2,
        "reviews_count": 312,
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=300&h=300&fit=crop",
        "category": "Electronics",
        "in_stock": True,
        "stock_quantity": 75,
        "features": ["360° Sound", "12hr Battery", "Water Resistant", "Wireless"],
        "description": "Portable bluetooth speaker with 360-degree sound technology."
    }
]

@router.get("/products/search", response_model=List[Product])
async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "popular"
):
    """Search products with filters"""
    try:
        filtered_products = MOCK_PRODUCTS.copy()
        
        # Apply filters
        if query:
            filtered_products = [
                p for p in filtered_products 
                if query.lower() in p["name"].lower() or query.lower() in p["brand"].lower()
            ]
        
        if category and category != "all":
            filtered_products = [
                p for p in filtered_products 
                if p["category"].lower() == category.lower()
            ]
        
        if min_price is not None:
            filtered_products = [
                p for p in filtered_products 
                if p["price_inr"] >= min_price
            ]
        
        if max_price is not None:
            filtered_products = [
                p for p in filtered_products 
                if p["price_inr"] <= max_price
            ]
        
        # Apply sorting
        if sort_by == "price_low":
            filtered_products.sort(key=lambda x: x["price_inr"])
        elif sort_by == "price_high":
            filtered_products.sort(key=lambda x: x["price_inr"], reverse=True)
        elif sort_by == "rating":
            filtered_products.sort(key=lambda x: x["rating"], reverse=True)
        # Default is popular (current order)
        
        return [Product(**product) for product in filtered_products]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product search failed: {str(e)}")

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by ID"""
    try:
        for product_data in MOCK_PRODUCTS:
            if product_data["id"] == product_id:
                return Product(**product_data)
        
        raise HTTPException(status_code=404, detail="Product not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product: {str(e)}")

@router.get("/products", response_model=List[Product])
async def get_all_products():
    """Get all products"""
    try:
        return [Product(**product) for product in MOCK_PRODUCTS]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get products: {str(e)}")

@router.post("/cart/add", response_model=CartItem)
async def add_to_cart(cart_item: CartItemCreate):
    """Add item to cart"""
    try:
        collection = await get_collection("cart_items")
        
        # Check if product exists
        product_exists = any(p["id"] == cart_item.product_id for p in MOCK_PRODUCTS)
        if not product_exists:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already in cart
        existing_item = await collection.find_one({
            "user_id": cart_item.user_id,
            "product_id": cart_item.product_id
        })
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item["quantity"] + cart_item.quantity
            await collection.update_one(
                {"id": existing_item["id"]},
                {"$set": {"quantity": new_quantity}}
            )
            existing_item["quantity"] = new_quantity
            return CartItem(**existing_item)
        else:
            # Create new cart item
            new_cart_item = CartItem(**cart_item.dict())
            await collection.insert_one(new_cart_item.dict())
            return new_cart_item
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to cart: {str(e)}")

@router.get("/cart/{user_id}", response_model=List[dict])
async def get_cart(user_id: str):
    """Get user's cart with product details"""
    try:
        collection = await get_collection("cart_items")
        
        cart_items = await collection.find({"user_id": user_id}).to_list(100)
        
        # Enrich with product details
        enriched_cart = []
        for item in cart_items:
            # Find product details
            product_data = None
            for product in MOCK_PRODUCTS:
                if product["id"] == item["product_id"]:
                    product_data = product
                    break
            
            if product_data:
                enriched_item = {
                    "cart_item": CartItem(**item),
                    "product": Product(**product_data),
                    "total_price_hp": product_data["price_hp"] * item["quantity"],
                    "total_price_inr": product_data["price_inr"] * item["quantity"]
                }
                enriched_cart.append(enriched_item)
        
        return enriched_cart
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cart: {str(e)}")

@router.put("/cart/{cart_item_id}/quantity")
async def update_cart_quantity(cart_item_id: str, quantity: int):
    """Update cart item quantity"""
    try:
        collection = await get_collection("cart_items")
        
        if quantity <= 0:
            # Remove item
            result = await collection.delete_one({"id": cart_item_id})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Cart item not found")
            return {"message": "Item removed from cart"}
        else:
            # Update quantity
            result = await collection.update_one(
                {"id": cart_item_id},
                {"$set": {"quantity": quantity}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Cart item not found")
            return {"message": "Quantity updated"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update cart: {str(e)}")

@router.delete("/cart/{cart_item_id}")
async def remove_from_cart(cart_item_id: str):
    """Remove item from cart"""
    try:
        collection = await get_collection("cart_items")
        
        result = await collection.delete_one({"id": cart_item_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Item removed from cart"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from cart: {str(e)}")

@router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    """Create order from cart"""
    try:
        collection = await get_collection("orders")
        
        # Calculate total
        total_hp = 0
        total_inr = 0
        
        for item in order.items:
            product_data = None
            for product in MOCK_PRODUCTS:
                if product["id"] == item["product_id"]:
                    product_data = product
                    break
            
            if not product_data:
                raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
            
            item_total_hp = product_data["price_hp"] * item["quantity"]
            item_total_inr = product_data["price_inr"] * item["quantity"]
            
            total_hp += item_total_hp
            total_inr += item_total_inr
            
            # Add pricing info to item
            item["price_hp"] = product_data["price_hp"]
            item["price_inr"] = product_data["price_inr"]
        
        # Check balance if paying with Happy Paisa
        if order.payment_method == "happy_paisa":
            balance = await WalletService.get_balance(order.user_id)
            if balance.balance_hp < total_hp:
                raise HTTPException(status_code=400, detail="Insufficient Happy Paisa balance")
        
        # Create order
        new_order = Order(
            user_id=order.user_id,
            items=order.items,
            total_amount_hp=total_hp,
            total_amount_inr=total_inr,
            shipping_address=order.shipping_address,
            payment_method=order.payment_method
        )
        
        # Save order
        await collection.insert_one(new_order.dict())
        
        # Process payment if Happy Paisa
        if order.payment_method == "happy_paisa":
            transaction = WalletTransaction(
                user_id=order.user_id,
                type="debit",
                amount_hp=total_hp,
                description=f"E-commerce order - {new_order.order_number}",
                category="Shopping",
                reference_id=new_order.id
            )
            await WalletService.add_transaction(transaction)
            
            # Update order payment status
            await collection.update_one(
                {"id": new_order.id},
                {"$set": {"payment_status": "completed", "status": "confirmed"}}
            )
            new_order.payment_status = "completed"
            new_order.status = "confirmed"
        
        # Clear cart
        cart_collection = await get_collection("cart_items")
        await cart_collection.delete_many({"user_id": order.user_id})
        
        return new_order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

@router.get("/orders/{user_id}", response_model=List[Order])
async def get_user_orders(user_id: str):
    """Get user's orders"""
    try:
        collection = await get_collection("orders")
        
        orders = await collection.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        return [Order(**order) for order in orders]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@router.get("/orders/detail/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get order details"""
    try:
        collection = await get_collection("orders")
        
        order = await collection.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return Order(**order)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order: {str(e)}")

@router.get("/categories")
async def get_categories():
    """Get product categories"""
    try:
        categories = list(set(product["category"] for product in MOCK_PRODUCTS))
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/recommendations/{user_id}", response_model=List[Product])
async def get_recommendations(user_id: str):
    """Get personalized product recommendations"""
    try:
        # Simple recommendation: return highest rated products
        # In production, this would use ML algorithms
        sorted_products = sorted(MOCK_PRODUCTS, key=lambda x: x["rating"], reverse=True)
        recommendations = sorted_products[:3]
        
        return [Product(**product) for product in recommendations]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")