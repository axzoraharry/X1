import api from './api';

export const userService = {
  // Get user by ID
  async getUser(userId) {
    try {
      const response = await api.get(`/api/users/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user: ${error.message}`);
    }
  },

  // Get user by email
  async getUserByEmail(email) {
    try {
      const response = await api.get(`/api/users/email/${email}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user by email: ${error.message}`);
    }
  },

  // Create new user
  async createUser(userData) {
    try {
      const response = await api.post('/api/users/', userData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create user: ${error.message}`);
    }
  },

  // Update user
  async updateUser(userId, userData) {
    try {
      const response = await api.put(`/api/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update user: ${error.message}`);
    }
  },

  // Get demo user (for testing)
  async getDemoUser() {
    try {
      const response = await api.get('/api/users/email/demo@axzora.com');
      return response.data;
    } catch (error) {
      // If demo user doesn't exist, create it
      const demoUser = {
        name: "Demo User",
        email: "demo@axzora.com",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
        location: "Nagpur, India",
        mobile_number: "9876543210"
      };
      return await this.createUser(demoUser);
    }
  }
};