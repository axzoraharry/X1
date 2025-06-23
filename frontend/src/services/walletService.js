import api from './api';

export const walletService = {
  // Get wallet balance and overview
  async getWalletBalance(userId) {
    try {
      const response = await api.get(`/api/wallet/${userId}/balance`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get wallet balance: ${error.message}`);
    }
  },

  // Get transaction history
  async getTransactions(userId, limit = 50, offset = 0) {
    try {
      const response = await api.get(`/api/wallet/${userId}/transactions`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get transactions: ${error.message}`);
    }
  },

  // Add transaction
  async addTransaction(userId, transactionData) {
    try {
      const response = await api.post(`/api/wallet/${userId}/transactions`, transactionData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to add transaction: ${error.message}`);
    }
  },

  // Credit wallet
  async creditWallet(userId, amountHp, description = "Wallet top-up") {
    try {
      const response = await api.post(`/api/wallet/${userId}/credit`, null, {
        params: { amount_hp: amountHp, description }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to credit wallet: ${error.message}`);
    }
  },

  // Debit wallet
  async debitWallet(userId, amountHp, description, category = "Payment") {
    try {
      const response = await api.post(`/api/wallet/${userId}/debit`, null, {
        params: { amount_hp: amountHp, description, category }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to debit wallet: ${error.message}`);
    }
  },

  // Transfer Happy Paisa
  async transferHp(fromUserId, toUserId, amountHp, description = "Transfer") {
    try {
      const response = await api.post('/api/wallet/transfer', null, {
        params: { from_user_id: fromUserId, to_user_id: toUserId, amount_hp: amountHp, description }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to transfer HP: ${error.message}`);
    }
  },

  // Convert INR to HP
  async convertInrToHp(userId, amountInr) {
    try {
      const response = await api.post(`/api/wallet/${userId}/convert/inr-to-hp`, null, {
        params: { amount_inr: amountInr }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert INR to HP: ${error.message}`);
    }
  },

  // Convert HP to INR
  async convertHpToInr(userId, amountHp) {
    try {
      const response = await api.post(`/api/wallet/${userId}/convert/hp-to-inr`, null, {
        params: { amount_hp: amountHp }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert HP to INR: ${error.message}`);
    }
  }
};