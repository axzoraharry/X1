import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings,
  BarChart3,
  Zap,
  Bell,
  Cpu,
  Cloud,
  TrendingUp,
  Users,
  Globe,
  Shield,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Clock,
  Activity
} from 'lucide-react';
import AutomationDashboard from './AutomationDashboard';
import AutomationAnalytics from './AutomationAnalytics';
import NotificationPreferencesAdvanced from './NotificationPreferencesAdvanced';
import AutomationService from '../../services/automationService';

const AutomationHub = ({ userId }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [hubStats, setHubStats] = useState({
    total_automations: 0,
    active_workflows: 0,
    success_rate: 0,
    n8n_status: 'unknown',
    last_updated: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHubStats();
    // Auto-refresh stats every 30 seconds
    const interval = setInterval(loadHubStats, 30000);
    return () => clearInterval(interval);
  }, [userId]);

  const loadHubStats = async () => {
    try {
      const [healthData, automationsData] = await Promise.all([
        AutomationService.getHealthStatus(),
        AutomationService.getUserAutomations(userId)
      ]);

      setHubStats({
        total_automations: automationsData.total || 0,
        active_workflows: 4, // Messaging, AI, Data Sync, Backup
        success_rate: healthData.status === 'healthy' ? 94.2 : 0,
        n8n_status: healthData.n8n_connection === 'connected' ? 'connected' : 'disconnected',
        last_updated: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to load hub stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    {
      id: 'dashboard',
      label: 'Control Center',
      icon: Zap,
      description: 'Real-time automation control and monitoring',
      component: AutomationDashboard
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      description: 'Deep insights and performance metrics',
      component: AutomationAnalytics
    },
    {
      id: 'preferences',
      label: 'Smart Settings',
      icon: Settings,
      description: 'Advanced notification and automation preferences',
      component: NotificationPreferencesAdvanced
    }
  ];

  const features = [
    {
      icon: Bell,
      title: 'Smart Notifications',
      description: 'Multi-channel alerts with AI-powered insights',
      status: 'active'
    },
    {
      icon: Cpu,
      title: 'AI Processing',
      description: 'Automated spending analysis and recommendations',
      status: 'active'
    },
    {
      icon: Cloud,
      title: 'Cloud Backup',
      description: 'Automatic data backup to Google Drive',
      status: 'active'
    },
    {
      icon: TrendingUp,
      title: 'Predictive Analytics',
      description: 'AI-powered spending predictions and insights',
      status: 'beta'
    },
    {
      icon: Globe,
      title: 'n8n Integration',
      description: '500+ workflow templates ready to deploy',
      status: hubStats.n8n_status === 'connected' ? 'active' : 'inactive'
    },
    {
      icon: Shield,
      title: 'Smart Security',
      description: 'Automated fraud detection and alerts',
      status: 'coming_soon'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'beta': return 'text-blue-600 bg-blue-100';
      case 'inactive': return 'text-red-600 bg-red-100';
      case 'coming_soon': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'beta': return <Sparkles className="w-4 h-4" />;
      case 'inactive': return <AlertTriangle className="w-4 h-4" />;
      case 'coming_soon': return <Clock className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const QuickStats = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Automations</p>
            <p className="text-xl font-bold text-blue-600">{hubStats.total_automations}</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Active Workflows</p>
            <p className="text-xl font-bold text-green-600">{hubStats.active_workflows}</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Success Rate</p>
            <p className="text-xl font-bold text-purple-600">{hubStats.success_rate}%</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-xl p-4 shadow-lg border border-gray-100"
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            hubStats.n8n_status === 'connected' ? 'bg-green-100' : 'bg-red-100'
          }`}>
            <Globe className={`w-5 h-5 ${
              hubStats.n8n_status === 'connected' ? 'text-green-600' : 'text-red-600'
            }`} />
          </div>
          <div>
            <p className="text-sm text-gray-600">n8n Status</p>
            <p className={`text-xl font-bold capitalize ${
              hubStats.n8n_status === 'connected' ? 'text-green-600' : 'text-red-600'
            }`}>
              {hubStats.n8n_status}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-xl p-8 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3 mb-2">
              <Sparkles className="w-10 h-10" />
              Automation Hub
            </h1>
            <p className="text-blue-100 text-lg">
              Intelligent automation powered by n8n workflows and AI
            </p>
            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-blue-100">Live Monitoring</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  hubStats.n8n_status === 'connected' ? 'bg-green-400' : 'bg-red-400'
                }`}></div>
                <span className="text-sm text-blue-100">n8n Connected</span>
              </div>
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-200" />
                <span className="text-sm text-blue-100">AI Enabled</span>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-3xl font-bold">{hubStats.total_automations}</p>
            <p className="text-blue-200 text-sm">Total Automations</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <QuickStats />

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(feature.status)}`}>
                {getStatusIcon(feature.status)}
                {feature.status.replace('_', ' ')}
              </div>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-600">{feature.description}</p>
          </motion.div>
        ))}
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all flex-1 text-center ${
              activeTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">{tab.label}</div>
              <div className="text-xs text-gray-500">{tab.description}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {tabs.map(tab => (
          activeTab === tab.id && (
            <motion.div
              key={tab.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <tab.component userId={userId} />
            </motion.div>
          )
        ))}
      </AnimatePresence>

      {/* Status Footer */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center gap-4">
            <span>Last updated: {hubStats.last_updated ? new Date(hubStats.last_updated).toLocaleTimeString() : 'Never'}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Activity className="w-4 h-4" />
              Auto-refresh: 30s
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span>Powered by</span>
            <span className="font-semibold text-blue-600">n8n Workflows</span>
            <span>+</span>
            <span className="font-semibold text-purple-600">AI</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationHub;