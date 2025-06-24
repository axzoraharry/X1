import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Zap,
  CheckCircle,
  XCircle,
  BarChart3,
  PieChart as PieChartIcon,
  Activity
} from 'lucide-react';
import AutomationService from '../../services/automationService';

const AutomationAnalytics = ({ userId }) => {
  const [analytics, setAnalytics] = useState({
    overview: {
      total_automations: 0,
      successful_rate: 0,
      avg_response_time: 0,
      active_rules: 0
    },
    daily_stats: [],
    automation_types: [],
    performance_metrics: [],
    recent_trends: []
  });
  
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [userId, timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      // Get real analytics data from the backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/dashboard/${userId}?time_range=${timeRange}`);
      const analyticsData = await response.json();
      
      // Transform the data for display
      const transformedAnalytics = {
        overview: {
          total_automations: analyticsData.overview?.total_automations || 0,
          successful_rate: analyticsData.overview?.success_rate || 0,
          avg_response_time: analyticsData.overview?.avg_response_time || 0,
          active_rules: 4 // Mock value
        },
        daily_stats: analyticsData.daily_stats || [],
        automation_types: analyticsData.automation_types || [],
        performance_metrics: analyticsData.performance_metrics || [],
        recent_trends: analyticsData.trends || []
      };
      
      setAnalytics(transformedAnalytics);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'blue' }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600 mt-1`}>{value}</p>
          {change && (
            <p className={`text-sm mt-1 flex items-center gap-1 ${
              change > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {change > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {Math.abs(change)}% from last period
            </p>
          )}
        </div>
        <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
          <div className="h-80 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            Automation Analytics
          </h1>
          <p className="text-gray-600 mt-1">
            Deep insights into your automation performance and usage patterns
          </p>
        </div>
        
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total Automations"
          value={analytics.overview.total_automations.toLocaleString()}
          change={8.2}
          icon={Zap}
          color="blue"
        />
        <StatCard
          title="Success Rate"
          value={`${analytics.overview.successful_rate}%`}
          change={2.1}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Avg Response Time"
          value={`${analytics.overview.avg_response_time}s`}
          change={-15.3}
          icon={Clock}
          color="purple"
        />
        <StatCard
          title="Active Rules"
          value={analytics.overview.active_rules}
          change={12.5}
          icon={Target}
          color="orange"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Activity Chart */}
        <SimpleChart 
          data={analytics.daily_stats} 
          title="Daily Activity" 
          type="bar"
        />

        {/* Automation Types Chart */}
        <SimpleChart 
          data={analytics.automation_types} 
          title="Automation Types" 
          type="pie"
        />
      </div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          {analytics.performance_metrics.map((metric, index) => (
            <div key={index} className="text-center">
              <p className="text-sm text-gray-600">{metric.time}</p>
              <p className="text-lg font-semibold text-blue-600">{metric.response_time}s</p>
              <p className="text-xs text-green-600">{metric.success_rate}%</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* AI Insights Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
      >
        <div className="flex items-start gap-3">
          <Activity className="w-6 h-6 text-blue-600 mt-1" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Real-Time AI Insights</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>• Your automation success rate is {analytics.overview.successful_rate.toFixed(1)}%</p>
              <p>• Total automations executed: {analytics.overview.total_automations}</p>
              <p>• Most active automation type: {analytics.automation_types[0]?.name || 'Messaging'}</p>
              <p>• Average response time: {analytics.overview.avg_response_time}s</p>
              <p>• Recommendation: {analytics.overview.successful_rate > 80 ? 'Excellent performance! Keep it up.' : 'Consider optimizing failed automations for better performance.'}</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AutomationAnalytics;