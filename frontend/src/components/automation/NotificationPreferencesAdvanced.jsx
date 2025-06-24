import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell,
  Settings,
  Save,
  AlertTriangle,
  CheckCircle,
  Smartphone,
  Mail,
  MessageSquare,
  Volume2,
  VolumeX,
  CreditCard,
  Plane,
  ShoppingCart,
  TrendingUp
} from 'lucide-react';

const NotificationPreferencesAdvanced = ({ userId }) => {
  const [preferences, setPreferences] = useState({
    transaction_alerts: { enabled: true, channels: ['telegram'], threshold: 0, sound: true },
    spending_insights: { enabled: true, channels: ['telegram'], frequency: 'weekly', ai_powered: true },
    low_balance: { enabled: true, channels: ['telegram', 'sms'], threshold: 1.0, urgent: true },
    booking_confirmations: { enabled: true, channels: ['email', 'telegram'], include_details: true },
    auto_backup: { enabled: true, frequency: 'daily', destination: 'google_drive' },
    smart_categorization: { enabled: true, ai_learning: true },
    ai_features: {
      personalized_insights: true,
      spending_predictions: true,
      recommendation_engine: true,
      voice_commands: false,
      smart_notifications: true
    }
  });

  const [activeTab, setActiveTab] = useState('notifications');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const updatePreference = (category, field, value) => {
    setPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: value
      }
    }));
  };

  const toggleChannel = (category, channel) => {
    const currentChannels = preferences[category].channels || [];
    const newChannels = currentChannels.includes(channel)
      ? currentChannels.filter(c => c !== channel)
      : [...currentChannels, channel];
    
    updatePreference(category, 'channels', newChannels);
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'automation', label: 'Automation', icon: Settings },
    { id: 'ai', label: 'AI Features', icon: TrendingUp }
  ];

  const channels = [
    { id: 'telegram', label: 'Telegram', icon: MessageSquare, color: 'blue' },
    { id: 'email', label: 'Email', icon: Mail, color: 'green' },
    { id: 'sms', label: 'SMS', icon: Smartphone, color: 'orange' }
  ];

  const PreferenceCard = ({ title, description, icon: Icon, config, category, children }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={config.enabled}
            onChange={(e) => updatePreference(category, 'enabled', e.target.checked)}
            className="sr-only"
          />
          <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            config.enabled ? 'bg-blue-600' : 'bg-gray-200'
          }`}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              config.enabled ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </div>
        </label>
      </div>

      {config.enabled && children && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="space-y-3"
        >
          {children}
        </motion.div>
      )}
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Settings className="w-8 h-8" />
          Smart Preferences
        </h1>
        <p className="text-blue-100 mt-2">
          Configure your intelligent automation and notification preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              activeTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'notifications' && (
          <motion.div
            key="notifications"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            <PreferenceCard
              title="Transaction Alerts"
              description="Get notified about all wallet activities"
              icon={CreditCard}
              config={preferences.transaction_alerts}
              category="transaction_alerts"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Channels</label>
                <div className="grid grid-cols-3 gap-2">
                  {channels.map(channel => {
                    const isSelected = preferences.transaction_alerts.channels?.includes(channel.id);
                    return (
                      <button
                        key={channel.id}
                        onClick={() => toggleChannel('transaction_alerts', channel.id)}
                        className={`flex items-center gap-2 p-2 rounded-lg border-2 transition-all ${
                          isSelected
                            ? `border-${channel.color}-500 bg-${channel.color}-50`
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <channel.icon className="w-4 h-4" />
                        <span className="text-sm">{channel.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </PreferenceCard>

            <PreferenceCard
              title="AI Spending Insights"
              description="Receive personalized spending analysis"
              icon={TrendingUp}
              config={preferences.spending_insights}
              category="spending_insights"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                <select
                  value={preferences.spending_insights.frequency}
                  onChange={(e) => updatePreference('spending_insights', 'frequency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </PreferenceCard>

            <PreferenceCard
              title="Low Balance Alerts"
              description="Never run out of Happy Paisa unexpectedly"
              icon={AlertTriangle}
              config={preferences.low_balance}
              category="low_balance"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Threshold (HP)</label>
                <input
                  type="number"
                  step="0.1"
                  value={preferences.low_balance.threshold}
                  onChange={(e) => updatePreference('low_balance', 'threshold', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                />
              </div>
            </PreferenceCard>
          </motion.div>
        )}

        {activeTab === 'automation' && (
          <motion.div
            key="automation"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            <PreferenceCard
              title="Auto Backup"
              description="Automatically backup your data to cloud storage"
              icon={Save}
              config={preferences.auto_backup}
              category="auto_backup"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                <select
                  value={preferences.auto_backup.frequency}
                  onChange={(e) => updatePreference('auto_backup', 'frequency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </PreferenceCard>

            <PreferenceCard
              title="Smart Categorization"
              description="AI-powered transaction categorization"
              icon={TrendingUp}
              config={preferences.smart_categorization}
              category="smart_categorization"
            >
              <div className="space-y-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={preferences.smart_categorization.ai_learning}
                    onChange={(e) => updatePreference('smart_categorization', 'ai_learning', e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <span className="text-sm text-gray-700">Enable AI learning</span>
                </label>
              </div>
            </PreferenceCard>
          </motion.div>
        )}

        {activeTab === 'ai' && (
          <motion.div
            key="ai"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Features</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(preferences.ai_features).map(([key, value]) => (
                  <label key={key} className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => setPreferences(prev => ({
                        ...prev,
                        ai_features: {
                          ...prev.ai_features,
                          [key]: e.target.checked
                        }
                      }))}
                      className="w-4 h-4 text-purple-600 rounded"
                    />
                    <span className="text-sm text-gray-700 capitalize">
                      {key.replace('_', ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Save Button */}
      <motion.div 
        className="flex justify-end"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <button
          onClick={savePreferences}
          disabled={saving}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
            saved
              ? 'bg-green-500 text-white'
              : saving
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
          }`}
        >
          {saving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Saving...
            </>
          ) : saved ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Preferences
            </>
          )}
        </button>
      </motion.div>
    </div>
  );
};

export default NotificationPreferencesAdvanced;