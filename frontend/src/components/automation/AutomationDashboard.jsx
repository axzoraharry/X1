import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Cog8ToothIcon,
  BellIcon,
  CloudArrowUpIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import AutomationService from '../../services/automationService';

const AutomationDashboard = ({ userId }) => {
  const [automations, setAutomations] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testNotification, setTestNotification] = useState('');

  useEffect(() => {
    loadAutomationData();
  }, [userId]);

  const loadAutomationData = async () => {
    try {
      setLoading(true);
      const [automationsData, healthData] = await Promise.all([
        AutomationService.getUserAutomations(userId),
        AutomationService.getHealthStatus()
      ]);
      
      setAutomations(automationsData.automations || []);
      setHealthStatus(healthData);
    } catch (error) {
      console.error('Failed to load automation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendTestNotification = async () => {
    try {
      await AutomationService.sendNotification(
        userId,
        'telegram',
        testNotification || 'Test notification from Axzora Mr. Happy 2.0!',
        { test: true, timestamp: new Date().toISOString() }
      );
      alert('Test notification sent successfully!');
      setTestNotification('');
    } catch (error) {
      alert('Failed to send test notification: ' + error.message);
    }
  };

  const triggerAIAnalysis = async () => {
    try {
      await AutomationService.analyzeSpendingPatterns(userId, []);
      alert('AI analysis triggered successfully!');
      loadAutomationData();
    } catch (error) {
      alert('Failed to trigger AI analysis: ' + error.message);
    }
  };

  const triggerBackup = async () => {
    try {
      await AutomationService.backupUserData(userId, 'full', 'google_drive');
      alert('Data backup initiated successfully!');
      loadAutomationData();
    } catch (error) {
      alert('Failed to initiate backup: ' + error.message);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getAutomationIcon = (type) => {
    switch (type) {
      case 'messaging':
        return <BellIcon className="w-5 h-5 text-blue-500" />;
      case 'ai_processing':
        return <CpuChipIcon className="w-5 h-5 text-purple-500" />;
      case 'data_sync':
        return <ChartBarIcon className="w-5 h-5 text-green-500" />;
      case 'backup':
        return <CloudArrowUpIcon className="w-5 h-5 text-orange-500" />;
      default:
        return <Cog8ToothIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Cog8ToothIcon className="w-8 h-8" />
              Automation Dashboard
            </h2>
            <p className="text-blue-100 mt-1">
              n8n Workflow Integration & Smart Notifications
            </p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
              healthStatus?.status === 'healthy' 
                ? 'bg-green-500 bg-opacity-20 text-green-100' 
                : 'bg-red-500 bg-opacity-20 text-red-100'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                healthStatus?.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'
              }`}></div>
              {healthStatus?.status || 'Unknown'}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
        >
          <div className="flex items-center gap-3 mb-3">
            <BellIcon className="w-6 h-6 text-blue-500" />
            <h3 className="font-semibold">Test Notification</h3>
          </div>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Enter test message..."
              value={testNotification}
              onChange={(e) => setTestNotification(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={sendTestNotification}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Send Test
            </button>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
        >
          <div className="flex items-center gap-3 mb-3">
            <CpuChipIcon className="w-6 h-6 text-purple-500" />
            <h3 className="font-semibold">AI Analysis</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            Generate spending insights with AI
          </p>
          <button
            onClick={triggerAIAnalysis}
            className="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition-colors"
          >
            Analyze Now
          </button>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
        >
          <div className="flex items-center gap-3 mb-3">
            <CloudArrowUpIcon className="w-6 h-6 text-orange-500" />
            <h3 className="font-semibold">Data Backup</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            Backup data to Google Drive
          </p>
          <button
            onClick={triggerBackup}
            className="w-full bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Backup Now
          </button>
        </motion.div>
      </div>

      {/* Automation History */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Recent Automations</h3>
          <p className="text-gray-600 text-sm">Last {automations.length} automation executions</p>
        </div>
        
        <div className="divide-y divide-gray-100">
          {automations.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <Cog8ToothIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No automations triggered yet</p>
              <p className="text-sm">Automations will appear here once triggered</p>
            </div>
          ) : (
            automations.slice(0, 10).map((automation, index) => (
              <motion.div
                key={automation.trigger_id || index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getAutomationIcon(automation.automation_type)}
                    <div>
                      <p className="font-medium text-gray-900">
                        {automation.automation_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      <p className="text-sm text-gray-600">
                        {automation.event_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(automation.success ? 'success' : 'failed')}
                    <span className="text-xs text-gray-500">
                      {new Date(automation.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Health Status Details */}
      {healthStatus && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {healthStatus.services && Object.entries(healthStatus.services).map(([service, status]) => (
              <div key={service} className="text-center">
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full mb-2 ${
                  status === 'operational' ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {getAutomationIcon(service)}
                </div>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {service.replace('_', ' ')}
                </p>
                <p className={`text-xs ${
                  status === 'operational' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {status}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AutomationDashboard;