import api from './api';

export const friendliAiService = {
  // Transaction Analysis
  async analyzeTransaction(transactionHash) {
    try {
      const response = await api.post(`/api/ai/analyze-transaction?transaction_hash=${transactionHash}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to analyze transaction: ${error.message}`);
    }
  },

  // Wallet Insights
  async getWalletInsights(userId) {
    try {
      const response = await api.get(`/api/ai/wallet-insights/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get wallet insights: ${error.message}`);
    }
  },

  // Voice Enhancement
  async enhanceVoiceResponse(query, userId = null, currentFeature = null) {
    try {
      const params = new URLSearchParams({ query });
      if (userId) params.append('user_id', userId);
      if (currentFeature) params.append('current_feature', currentFeature);

      const response = await api.post(`/api/ai/voice-enhance?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to enhance voice response: ${error.message}`);
    }
  },

  // Fraud Detection
  async detectFraud(userId) {
    try {
      const response = await api.post(`/api/ai/fraud-detection/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to detect fraud: ${error.message}`);
    }
  },

  // General AI Chat
  async chatCompletion(messages, options = {}) {
    try {
      const payload = {
        messages,
        model: options.model,
        max_tokens: options.maxTokens || 500,
        temperature: options.temperature || 0.7
      };

      const response = await api.post('/api/ai/chat', payload);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to complete chat: ${error.message}`);
    }
  },

  // Platform Insights
  async getPlatformInsights(days = 7) {
    try {
      const response = await api.get(`/api/ai/analytics/insights?days=${days}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get platform insights: ${error.message}`);
    }
  },

  // AI Service Health
  async checkHealth() {
    try {
      const response = await api.get('/api/ai/health');
      return response.data;
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  },

  // Utility Functions
  getRiskLevelColor(riskLevel) {
    const colors = {
      'low': 'text-green-600 bg-green-100',
      'medium': 'text-yellow-600 bg-yellow-100',
      'high': 'text-orange-600 bg-orange-100',
      'critical': 'text-red-600 bg-red-100'
    };
    return colors[riskLevel] || 'text-gray-600 bg-gray-100';
  },

  getHealthScoreColor(score) {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  },

  formatAnalysisText(text) {
    // Clean up AI response formatting
    return text
      .replace(/\*\*/g, '') // Remove markdown bold
      .replace(/###/g, '') // Remove markdown headers
      .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
      .trim();
  },

  extractKeyPoints(text) {
    // Extract numbered lists or bullet points
    const lines = text.split('\n');
    const keyPoints = [];
    
    for (const line of lines) {
      const cleanLine = line.trim();
      if (cleanLine.match(/^(\d+\.|•|-|\*)\s+.+/) && cleanLine.length > 10) {
        keyPoints.push(cleanLine.replace(/^(\d+\.|•|-|\*)\s+/, ''));
      }
    }
    
    return keyPoints.slice(0, 5); // Limit to 5 key points
  },

  // AI Response Caching
  _cache: new Map(),
  
  async getCachedResponse(key, fetchFunction, ttlMs = 300000) { // 5 minute TTL
    const cached = this._cache.get(key);
    
    if (cached && (Date.now() - cached.timestamp) < ttlMs) {
      return cached.data;
    }
    
    const data = await fetchFunction();
    this._cache.set(key, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  },

  clearCache() {
    this._cache.clear();
  }
};