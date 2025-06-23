import api from './api';

export const rechargeService = {
  // Get mobile plans for operator
  async getMobilePlans(operator) {
    try {
      const response = await api.get(`/api/recharge/mobile/plans/${operator}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get mobile plans: ${error.message}`);
    }
  },

  // Get all mobile plans
  async getAllMobilePlans() {
    try {
      const response = await api.get('/api/recharge/mobile/plans');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get all mobile plans: ${error.message}`);
    }
  },

  // Detect operator from mobile number
  async detectOperator(mobileNumber) {
    try {
      const response = await api.post('/api/recharge/mobile/detect-operator', null, {
        params: { mobile_number: mobileNumber }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to detect operator: ${error.message}`);
    }
  },

  // Process mobile recharge
  async mobileRecharge(rechargeData) {
    try {
      const response = await api.post('/api/recharge/mobile/recharge', rechargeData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to process recharge: ${error.message}`);
    }
  },

  // Get recharge history
  async getRechargeHistory(userId, limit = 50) {
    try {
      const response = await api.get(`/api/recharge/mobile/history/${userId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get recharge history: ${error.message}`);
    }
  },

  // DTH recharge
  async dthRecharge(dthData) {
    try {
      const response = await api.post('/api/recharge/dth/recharge', dthData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to process DTH recharge: ${error.message}`);
    }
  },

  // Pay utility bill
  async payUtilityBill(billData) {
    try {
      const response = await api.post('/api/recharge/utility/bill-payment', billData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to pay utility bill: ${error.message}`);
    }
  },

  // Get complete recharge history
  async getAllRechargeHistory(userId) {
    try {
      const response = await api.get(`/api/recharge/history/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get complete recharge history: ${error.message}`);
    }
  }
};