import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BellIcon,
  DevicePhoneMobileIcon,
  EnvelopeIcon,
  ChatBubbleLeftEllipsisIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const NotificationPreferences = ({ userId }) => {
  const [preferences, setPreferences] = useState({
    transaction_notifications: {
      telegram: true,
      email: false,
      sms: false
    },
    booking_confirmations: {
      telegram: true,
      email: true,
      sms: false
    },
    low_balance_alerts: {
      telegram: true,
      sms: true,
      email: false
    },
    ai_insights: {
      telegram: true,
      email: false,
      sms: false
    }
  });

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  const notificationTypes = [
    {
      key: 'transaction_notifications',
      title: 'Transaction Notifications',
      description: 'Get notified about wallet transactions',
      icon: <BellIcon className="w-5 h-5" />
    },
    {
      key: 'booking_confirmations',
      title: 'Booking Confirmations',
      description: 'Receive confirmations for travel and service bookings',
      icon: <CogIcon className="w-5 h-5" />
    },
    {
      key: 'low_balance_alerts',
      title: 'Low Balance Alerts',
      description: 'Get alerted when your Happy Paisa balance is low',
      icon: <DevicePhoneMobileIcon className="w-5 h-5" />
    },
    {
      key: 'ai_insights',
      title: 'AI Insights',
      description: 'Receive AI-powered spending insights and recommendations',
      icon: <ChatBubbleLeftEllipsisIcon className="w-5 h-5" />
    }
  ];

  const channels = [
    {
      key: 'telegram',
      title: 'Telegram',
      icon: <ChatBubbleLeftEllipsisIcon className="w-4 h-4" />,
      color: 'blue'
    },
    {
      key: 'email',
      title: 'Email',
      icon: <EnvelopeIcon className="w-4 h-4" />,
      color: 'green'
    },
    {
      key: 'sms',
      title: 'SMS',
      icon: <DevicePhoneMobileIcon className="w-4 h-4" />,
      color: 'orange'
    }
  ];

  const handlePreferenceChange = (notificationType, channel, enabled) => {
    setPreferences(prev => ({
      ...prev,
      [notificationType]: {
        ...prev[notificationType],
        [channel]: enabled
      }
    }));
  };

  const savePreferences = async () => {
    setLoading(true);
    try {
      // Here you would call your API to save preferences
      // await AutomationService.saveNotificationPreferences(userId, preferences);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
      alert('Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <BellIcon className="w-8 h-8" />
          Notification Preferences
        </h2>
        <p className="text-indigo-100 mt-1">
          Customize how you receive notifications from n8n workflows
        </p>
      </div>

      {/* Preferences Grid */}
      <div className="space-y-4">
        {notificationTypes.map((notificationType) => (
          <motion.div
            key={notificationType.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-lg border border-gray-100 p-6"
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                {notificationType.icon}
              </div>
              
              <div className="flex-grow">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {notificationType.title}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {notificationType.description}
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {channels.map((channel) => (
                    <label
                      key={channel.key}
                      className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                        preferences[notificationType.key]?.[channel.key]
                          ? `border-${channel.color}-500 bg-${channel.color}-50`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={preferences[notificationType.key]?.[channel.key] || false}
                        onChange={(e) => handlePreferenceChange(
                          notificationType.key, 
                          channel.key, 
                          e.target.checked
                        )}
                        className={`w-4 h-4 text-${channel.color}-600 focus:ring-${channel.color}-500 border-gray-300 rounded`}
                      />
                      <div className={`flex items-center gap-2 text-${channel.color}-600`}>
                        {channel.icon}
                        <span className="font-medium">{channel.title}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={savePreferences}
          disabled={loading}
          className={`px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all ${
            saved
              ? 'bg-green-500 text-white'
              : loading
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Saving...
            </>
          ) : saved ? (
            <>
              ✓ Saved
            </>
          ) : (
            <>
              Save Preferences
            </>
          )}
        </motion.button>
      </div>

      {/* Information Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex gap-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <BellIcon className="w-4 h-4 text-blue-600" />
            </div>
          </div>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">About n8n Notifications</h4>
            <p className="text-blue-700 text-sm">
              These preferences control how our n8n automation workflows send you notifications. 
              Telegram provides the fastest delivery, while email is great for detailed information. 
              SMS is reserved for critical alerts only.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationPreferences;