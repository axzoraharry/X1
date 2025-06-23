import api from './api';

export const dashboardService = {
  // Get complete dashboard overview
  async getDashboardOverview(userId) {
    try {
      const response = await api.get(`/api/dashboard/${userId}/overview`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get dashboard overview: ${error.message}`);
    }
  },

  // Get user statistics
  async getUserStats(userId) {
    try {
      const response = await api.get(`/api/dashboard/${userId}/stats`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user stats: ${error.message}`);
    }
  },

  // Get notifications
  async getNotifications(userId, limit = 10) {
    try {
      const response = await api.get(`/api/dashboard/notifications/${userId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get notifications: ${error.message}`);
    }
  },

  // Mark notification as read
  async markNotificationRead(notificationId) {
    try {
      const response = await api.post(`/api/dashboard/notifications/${notificationId}/mark-read`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to mark notification as read: ${error.message}`);
    }
  }
};