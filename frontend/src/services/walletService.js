import api from './api';

export const walletService = {
  // Wallet Management
  async getWalletBalance(userId) {
    try {
      const response = await api.get(`/api/wallet/${userId}/balance`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get wallet balance: ${error.message}`);
    }
  },

  async getTransactions(userId, limit = 20) {
    try {
      const response = await api.get(`/api/wallet/${userId}/transactions?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get transactions: ${error.message}`);
    }
  },

  async creditWallet(userId, amountHp, description = 'Manual credit') {
    try {
      const response = await api.post(`/api/wallet/${userId}/credit`, {
        amount_hp: amountHp,
        description
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to credit wallet: ${error.message}`);
    }
  },

  async debitWallet(userId, amountHp, description = 'Manual debit') {
    try {
      const response = await api.post(`/api/wallet/${userId}/debit`, {
        amount_hp: amountHp,
        description
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to debit wallet: ${error.message}`);
    }
  },

  async convertInrToHp(userId, amountInr) {
    try {
      const response = await api.post(`/api/wallet/${userId}/convert-inr-to-hp`, {
        amount_inr: amountInr
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert INR to HP: ${error.message}`);
    }
  },

  async convertHpToInr(userId, amountHp) {
    try {
      const response = await api.post(`/api/wallet/${userId}/convert-hp-to-inr`, {
        amount_hp: amountHp
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to convert HP to INR: ${error.message}`);
    }
  }
};

export const blockchainService = {
  // Network Status
  async getNetworkStatus() {
    try {
      const response = await api.get('/api/blockchain/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get network status: ${error.message}`);
    }
  },

  async getNetworkStats() {
    try {
      const response = await api.get('/api/blockchain/network/stats');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get network stats: ${error.message}`);
    }
  },

  // User Blockchain Operations
  async getUserAddress(userId) {
    try {
      const response = await api.get(`/api/blockchain/user/${userId}/address`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user address: ${error.message}`);
    }
  },

  async getUserBlockchainBalance(userId) {
    try {
      const response = await api.get(`/api/blockchain/user/${userId}/balance`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get blockchain balance: ${error.message}`);
    }
  },

  async getUserBlockchainTransactions(userId, limit = 50) {
    try {
      const response = await api.get(`/api/blockchain/user/${userId}/transactions?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get blockchain transactions: ${error.message}`);
    }
  },

  // Mint and Burn Operations
  async mintHappyPaisa(userId, amountHp, referenceId = null) {
    try {
      const response = await api.post(`/api/blockchain/user/${userId}/mint?amount_hp=${amountHp}${referenceId ? `&reference_id=${referenceId}` : ''}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to mint Happy Paisa: ${error.message}`);
    }
  },

  async burnHappyPaisa(userId, amountHp, referenceId = null) {
    try {
      const response = await api.post(`/api/blockchain/user/${userId}/burn?amount_hp=${amountHp}${referenceId ? `&reference_id=${referenceId}` : ''}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to burn Happy Paisa: ${error.message}`);
    }
  },

  // P2P Transfers
  async transferHappyPaisa(fromUserId, toUserId, amountHp, description = 'P2P Transfer') {
    try {
      const response = await api.post(`/api/blockchain/transfer?from_user_id=${fromUserId}&to_user_id=${toUserId}&amount_hp=${amountHp}&description=${encodeURIComponent(description)}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to transfer Happy Paisa: ${error.message}`);
    }
  },

  // Transaction Status
  async getTransactionStatus(txHash) {
    try {
      const response = await api.get(`/api/blockchain/transaction/${txHash}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get transaction status: ${error.message}`);
    }
  },

  async syncTransactionStatus(txHash) {
    try {
      const response = await api.post(`/api/blockchain/sync/transaction/${txHash}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to sync transaction: ${error.message}`);
    }
  },

  // Explorer Functions
  async getLatestBlocks(limit = 10) {
    try {
      const response = await api.get(`/api/blockchain/explorer/latest-blocks?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get latest blocks: ${error.message}`);
    }
  },

  async searchBlockchain(query) {
    try {
      const response = await api.get(`/api/blockchain/explorer/search/${query}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search blockchain: ${error.message}`);
    }
  },

  // Enhanced Wallet Operations
  async getEnhancedBalance(userId) {
    try {
      const response = await api.get(`/api/wallet/${userId}/balance`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get enhanced balance: ${error.message}`);
    }
  },

  async p2pTransfer(fromUserId, toUserId, amountHp, description = 'P2P Transfer') {
    try {
      const response = await api.post(`/api/wallet/p2p-transfer?from_user_id=${fromUserId}&to_user_id=${toUserId}&amount_hp=${amountHp}&description=${encodeURIComponent(description)}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to complete P2P transfer: ${error.message}`);
    }
  },

  async syncBlockchainState(userId) {
    try {
      const response = await api.post(`/api/wallet/${userId}/sync-blockchain`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to sync blockchain state: ${error.message}`);
    }
  },

  async getWalletAnalytics(userId, days = 30) {
    try {
      const response = await api.get(`/api/wallet/${userId}/analytics?days=${days}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get wallet analytics: ${error.message}`);
    }
  },

  // Utility Functions
  formatAddress(address) {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-6)}`;
  },

  formatTransactionHash(hash) {
    if (!hash) return '';
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  },

  getTransactionStatusColor(status) {
    const colors = {
      'pending': 'text-yellow-600 bg-yellow-100',
      'confirmed': 'text-green-600 bg-green-100',
      'failed': 'text-red-600 bg-red-100',
      'finalized': 'text-blue-600 bg-blue-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  },

  getTransactionTypeIcon(type) {
    const icons = {
      'mint': '🪙',
      'burn': '🔥',
      'transfer': '📤',
      'receive': '📥'
    };
    return icons[type] || '💸';
  },

  convertHpToInr(amountHp) {
    return amountHp * 1000;
  },

  convertInrToHp(amountInr) {
    return amountInr / 1000;
  },

  convertHpToPlanck(amountHp) {
    return Math.floor(amountHp * Math.pow(10, 12));
  },

  convertPlanckToHp(amountPlanck) {
    return amountPlanck / Math.pow(10, 12);
  },

  validateHpAmount(amount, maxAmount = null) {
    if (!amount || amount <= 0) {
      return 'Amount must be greater than 0';
    }
    if (maxAmount && amount > maxAmount) {
      return `Amount cannot exceed ${maxAmount} HP`;
    }
    return null;
  },

  // Network Health Check
  async checkNetworkHealth() {
    try {
      const response = await api.get('/api/blockchain/health');
      return response.data;
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }
};