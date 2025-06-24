import api from './api';

export const virtualCardService = {
  // Card Management
  async getUserCards(userId) {
    try {
      const response = await api.get(`/api/virtual-cards/user/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user cards: ${error.message}`);
    }
  },

  async getCardDetails(cardId, userId) {
    try {
      const response = await api.get(`/api/virtual-cards/${cardId}?user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get card details: ${error.message}`);
    }
  },

  async createVirtualCard(cardData) {
    try {
      const response = await api.post('/api/virtual-cards/', cardData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create virtual card: ${error.message}`);
    }
  },

  async updateCardStatus(cardId, userId, status) {
    try {
      const response = await api.patch(`/api/virtual-cards/${cardId}/status?user_id=${userId}`, null, {
        params: { status }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update card status: ${error.message}`);
    }
  },

  async updateCardControls(cardId, userId, controls) {
    try {
      const response = await api.patch(`/api/virtual-cards/${cardId}/controls?user_id=${userId}`, controls);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update card controls: ${error.message}`);
    }
  },

  async loadCardFunds(cardId, userId, amountHp) {
    try {
      const response = await api.post(`/api/virtual-cards/${cardId}/load?amount_hp=${amountHp}&user_id=${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to load card funds: ${error.message}`);
    }
  },

  // Transactions
  async getCardTransactions(cardId, userId, limit = 50) {
    try {
      const response = await api.get(`/api/virtual-cards/${cardId}/transactions?user_id=${userId}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get card transactions: ${error.message}`);
    }
  },

  async simulateTransaction(transactionData) {
    try {
      const response = await api.post('/api/virtual-cards/simulate-transaction', transactionData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to simulate transaction: ${error.message}`);
    }
  },

  // KYC Management
  async getKycStatus(userId) {
    try {
      const response = await api.get(`/api/virtual-cards/kyc/user/${userId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return null; // KYC not found
      }
      throw new Error(`Failed to get KYC status: ${error.message}`);
    }
  },

  async initiateKyc(kycData) {
    try {
      const response = await api.post('/api/virtual-cards/kyc/initiate', kycData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to initiate KYC: ${error.message}`);
    }
  },

  async getKycRequirements() {
    try {
      const response = await api.get('/api/virtual-cards/kyc/requirements');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get KYC requirements: ${error.message}`);
    }
  },

  async verifyDocument(documentType, documentNumber) {
    try {
      const response = await api.post('/api/virtual-cards/kyc/verify-document', null, {
        params: { document_type: documentType, document_number: documentNumber }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to verify document: ${error.message}`);
    }
  },

  async createDemoKyc(userId, fullName) {
    try {
      const response = await api.post('/api/virtual-cards/demo/create-kyc', null, {
        params: { user_id: userId, full_name: fullName }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create demo KYC: ${error.message}`);
    }
  },

  // Analytics
  async getSpendingAnalytics(userId, cardId = null, days = 30) {
    try {
      const params = { user_id: userId, days };
      if (cardId) params.card_id = cardId;
      
      const response = await api.get('/api/card-management/analytics/spending', { params });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get spending analytics: ${error.message}`);
    }
  },

  async getMerchantInsights(userId, days = 30) {
    try {
      const response = await api.get('/api/card-management/analytics/merchant-insights', {
        params: { user_id: userId, days }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get merchant insights: ${error.message}`);
    }
  },

  async getFraudAlerts(userId, days = 7) {
    try {
      const response = await api.get(`/api/card-management/fraud-alerts/${userId}`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get fraud alerts: ${error.message}`);
    }
  },

  // Utility Functions
  async getCardNetworks() {
    try {
      const response = await api.get('/api/virtual-cards/demo/card-networks');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get card networks: ${error.message}`);
    }
  },

  async getControlTemplates() {
    try {
      const response = await api.get('/api/card-management/controls/templates');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get control templates: ${error.message}`);
    }
  },

  async getComplianceLimits() {
    try {
      const response = await api.get('/api/card-management/compliance/transaction-limits');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get compliance limits: ${error.message}`);
    }
  },

  // Helper Functions
  formatCardNumber(maskedNumber) {
    return maskedNumber || '****-****-****-****';
  },

  formatExpiryDate(month, year) {
    const monthStr = month.toString().padStart(2, '0');
    const yearStr = year.toString().slice(-2);
    return `${monthStr}/${yearStr}`;
  },

  getCardStatusColor(status) {
    const colors = {
      'active': 'text-green-600 bg-green-100',
      'frozen': 'text-yellow-600 bg-yellow-100', 
      'blocked': 'text-red-600 bg-red-100',
      'expired': 'text-gray-600 bg-gray-100',
      'cancelled': 'text-red-600 bg-red-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  },

  getTransactionStatusColor(status) {
    const colors = {
      'approved': 'text-green-600',
      'pending': 'text-yellow-600',
      'declined': 'text-red-600', 
      'reversed': 'text-gray-600'
    };
    return colors[status] || 'text-gray-600';
  },

  getMerchantCategoryIcon(category) {
    const icons = {
      'groceries': '🛒',
      'fuel': '⛽',
      'restaurants': '🍽️',
      'online_shopping': '🛍️',
      'atm_withdrawal': '🏧',
      'travel': '✈️',
      'entertainment': '🎬',
      'healthcare': '🏥',
      'education': '📚',
      'utilities': '⚡',
      'other': '💳'
    };
    return icons[category] || '💳';
  },

  // Validation Functions
  validateCardholderName(name) {
    if (!name || name.trim().length < 2) {
      return 'Cardholder name must be at least 2 characters';
    }
    if (name.length > 50) {
      return 'Cardholder name must not exceed 50 characters';
    }
    if (!/^[a-zA-Z\s]+$/.test(name)) {
      return 'Cardholder name can only contain letters and spaces';
    }
    return null;
  },

  validateLoadAmount(amount, maxBalance = 100) {
    if (!amount || amount <= 0) {
      return 'Amount must be greater than 0';
    }
    if (amount > maxBalance) {
      return `Amount cannot exceed ${maxBalance} HP`;
    }
    return null;
  },

  validateDailyLimit(limit) {
    if (!limit || limit <= 0) {
      return 'Daily limit must be greater than 0';
    }
    if (limit > 200000) {
      return 'Daily limit cannot exceed ₹2,00,000 as per RBI guidelines';
    }
    return null;
  }
};