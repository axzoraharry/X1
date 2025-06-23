import api from './api';

export const voiceService = {
  // Get voice service status
  async getVoiceStatus() {
    try {
      const response = await api.get('/api/voice/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get voice status: ${error.message}`);
    }
  },

  // Chat with Mr. Happy
  async chatWithMrHappy(text, userId, context = null) {
    try {
      const response = await api.post('/api/voice/chat', {
        text,
        user_id: userId,
        context
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to chat with Mr. Happy: ${error.message}`);
    }
  },

  // Get conversation history
  async getConversationHistory(userId, limit = 10) {
    try {
      const response = await api.get(`/api/voice/conversation/${userId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get conversation history: ${error.message}`);
    }
  },

  // Get quick response options
  async getQuickResponses() {
    try {
      const response = await api.get('/api/voice/quick-responses');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get quick responses: ${error.message}`);
    }
  },

  // Process quick command
  async processQuickCommand(userId, command) {
    try {
      const response = await api.post(`/api/voice/quick-command/${userId}`, null, {
        params: { command }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to process quick command: ${error.message}`);
    }
  },

  // Get Mr. Happy capabilities
  async getCapabilities() {
    try {
      const response = await api.get('/api/voice/capabilities');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get capabilities: ${error.message}`);
    }
  },

  // Simulate voice interaction
  async simulateVoiceInteraction(text, userId, context = null) {
    try {
      const response = await api.post('/api/voice/simulate-voice', {
        text,
        user_id: userId,
        context
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to simulate voice interaction: ${error.message}`);
    }
  },

  // Get Mr. Happy personality info
  async getPersonality() {
    try {
      const response = await api.get('/api/voice/personality');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get personality info: ${error.message}`);
    }
  }
};