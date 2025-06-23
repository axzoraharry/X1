import api from './api';

export const ecommerceService = {
  // Search products
  async searchProducts(searchParams = {}) {
    try {
      const response = await api.get('/api/ecommerce/products/search', {
        params: searchParams
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search products: ${error.message}`);
    }
  },

  // Get all products
  async getAllProducts() {
    try {
      const response = await api.get('/api/ecommerce/products');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get products: ${error.message}`);
    }
  },

  // Get product by ID
  async getProduct(productId) {
    try {
      const response = await api.get(`/api/ecommerce/products/${productId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get product: ${error.message}`);
    }
  },

  // Add to cart
  async addToCart(cartItemData) {
    try {
      const response = await api.post('/api/ecommerce/cart/add', cartItemData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to add to cart: ${error.message}`);
    }
  },

  // Get cart
  async getCart(userId) {
    try {
      const response = await api.get(`/api/ecommerce/cart/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get cart: ${error.message}`);
    }
  },

  // Update cart quantity
  async updateCartQuantity(cartItemId, quantity) {
    try {
      const response = await api.put(`/api/ecommerce/cart/${cartItemId}/quantity`, null, {
        params: { quantity }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update cart: ${error.message}`);
    }
  },

  // Remove from cart
  async removeFromCart(cartItemId) {
    try {
      const response = await api.delete(`/api/ecommerce/cart/${cartItemId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to remove from cart: ${error.message}`);
    }
  },

  // Create order
  async createOrder(orderData) {
    try {
      const response = await api.post('/api/ecommerce/orders', orderData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create order: ${error.message}`);
    }
  },

  // Get user orders
  async getUserOrders(userId) {
    try {
      const response = await api.get(`/api/ecommerce/orders/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get orders: ${error.message}`);
    }
  },

  // Get order details
  async getOrder(orderId) {
    try {
      const response = await api.get(`/api/ecommerce/orders/detail/${orderId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get order: ${error.message}`);
    }
  },

  // Get categories
  async getCategories() {
    try {
      const response = await api.get('/api/ecommerce/categories');
      return response.data.categories;
    } catch (error) {
      throw new Error(`Failed to get categories: ${error.message}`);
    }
  },

  // Get recommendations
  async getRecommendations(userId) {
    try {
      const response = await api.get(`/api/ecommerce/recommendations/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get recommendations: ${error.message}`);
    }
  }
};