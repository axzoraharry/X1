// Automation Service for n8n workflow integration
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class AutomationService {
  
  /**
   * Trigger automation workflow
   */
  static async triggerAutomation(automationType, triggerData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/trigger/${automationType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(triggerData)
      });

      if (!response.ok) {
        throw new Error(`Failed to trigger automation: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Automation trigger error:', error);
      throw error;
    }
  }

  /**
   * Send notification through automation system
   */
  static async sendNotification(userId, notificationType, message, additionalData = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/notifications/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          notification_type: notificationType,
          message: message,
          additional_data: additionalData
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to send notification: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Notification send error:', error);
      throw error;
    }
  }

  /**
   * Process transaction with AI
   */
  static async processTransactionWithAI(userId, transactionData, analysisType = 'spending_insights') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/ai/process-transaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          transaction_data: transactionData,
          analysis_type: analysisType
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to process with AI: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI processing error:', error);
      throw error;
    }
  }

  /**
   * Backup user data
   */
  static async backupUserData(userId, backupType = 'full', destination = 'google_drive') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/backup/user-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          backup_type: backupType,
          destination: destination
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to backup data: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Backup error:', error);
      throw error;
    }
  }

  /**
   * Get user automation history
   */
  static async getUserAutomations(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/triggers/${userId}`);

      if (!response.ok) {
        throw new Error(`Failed to get automations: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get automations error:', error);
      throw error;
    }
  }

  /**
   * Check automation service health
   */
  static async getHealthStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/automation/health`);

      if (!response.ok) {
        throw new Error(`Failed to get health status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Trigger messaging automation for booking confirmations
   */
  static async sendBookingConfirmation(userId, bookingData) {
    const triggerData = {
      user_id: userId,
      event_type: 'booking_confirmation',
      event_data: bookingData,
      automation_type: 'messaging'
    };

    return await this.triggerAutomation('messaging', triggerData);
  }

  /**
   * Trigger AI analysis for spending insights
   */
  static async analyzeSpendingPatterns(userId, transactionHistory) {
    const triggerData = {
      user_id: userId,
      event_type: 'spending_analysis',
      event_data: {
        analysis_type: 'spending_patterns',
        transaction_history: transactionHistory
      },
      automation_type: 'ai_processing'
    };

    return await this.triggerAutomation('ai_processing', triggerData);
  }

  /**
   * Trigger data synchronization
   */
  static async syncUserData(userId, syncType = 'incremental') {
    const triggerData = {
      user_id: userId,
      event_type: 'data_sync',
      event_data: {
        sync_type: syncType,
        destination: 'database'
      },
      automation_type: 'data_sync'
    };

    return await this.triggerAutomation('data_sync', triggerData);
  }

  /**
   * Trigger recharge confirmation notification
   */
  static async sendRechargeConfirmation(userId, rechargeData) {
    const triggerData = {
      user_id: userId,
      event_type: 'recharge_confirmation',
      event_data: rechargeData,
      automation_type: 'messaging'
    };

    return await this.triggerAutomation('messaging', triggerData);
  }

  /**
   * Send custom notification
   */
  static async sendCustomNotification(userId, title, message, channels = ['telegram']) {
    const promises = channels.map(channel => 
      this.sendNotification(userId, channel, `${title}\n\n${message}`)
    );

    try {
      const results = await Promise.allSettled(promises);
      return {
        success: results.filter(r => r.status === 'fulfilled').length,
        failed: results.filter(r => r.status === 'rejected').length,
        results: results
      };
    } catch (error) {
      console.error('Custom notification error:', error);
      throw error;
    }
  }
}

export default AutomationService;