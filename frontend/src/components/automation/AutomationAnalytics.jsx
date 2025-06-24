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
      
      // Simulate analytics data - in real app, this would come from your backend
      const mockAnalytics = {
        overview: {
          total_automations: 347,
          successful_rate: 94.2,
          avg_response_time: 1.3,
          active_rules: 12
        },
        daily_stats: [
          { date: '2024-06-18', automations: 45, success: 42, failed: 3 },
          { date: '2024-06-19', automations: 52, success: 50, failed: 2 },
          { date: '2024-06-20', automations: 38, success: 36, failed: 2 },
          { date: '2024-06-21', automations: 61, success: 58, failed: 3 },
          { date: '2024-06-22', automations: 43, success: 41, failed: 2 },
          { date: '2024-06-23', automations: 56, success: 53, failed: 3 },
          { date: '2024-06-24', automations: 52, success: 47, failed: 5 }
        ],
        automation_types: [
          { name: 'Transaction Notifications', value: 45, color: '#3B82F6' },
          { name: 'AI Insights', value: 20, color: '#8B5CF6' },
          { name: 'Data Backup', value: 15, color: '#10B981' },
          { name: 'Low Balance Alerts', value: 12, color: '#F59E0B' },
          { name: 'Booking Confirmations', value: 8, color: '#EF4444' }
        ],
        performance_metrics: [
          { time: '00:00', response_time: 1.2, success_rate: 95 },
          { time: '04:00', response_time: 0.9, success_rate: 97 },
          { time: '08:00', response_time: 1.8, success_rate: 92 },
          { time: '12:00', response_time: 2.1, success_rate: 89 },
          { time: '16:00', response_time: 1.5, success_rate: 94 },
          { time: '20:00', response_time: 1.3, success_rate: 96 }
        ],
        recent_trends: [
          { week: 'Week 1', notifications: 234, ai_insights: 45, backups: 28 },
          { week: 'Week 2', notifications: 267, ai_insights: 52, backups: 31 },
          { week: 'Week 3', notifications: 298, ai_insights: 61, backups: 35 },
          { week: 'Week 4', notifications: 347, ai_insights: 73, backups: 42 }
        ]
      };
      
      setAnalytics(mockAnalytics);
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
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analytics.daily_stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
                formatter={(value, name) => [value, name === 'success' ? 'Successful' : 'Failed']}
              />
              <Area
                type="monotone"
                dataKey="success"
                stackId="1"
                stroke="#10B981"
                fill="#10B981"
                fillOpacity={0.8}
              />
              <Area
                type="monotone"
                dataKey="failed"
                stackId="1"
                stroke="#EF4444"
                fill="#EF4444"
                fillOpacity={0.8}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Automation Types Pie Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Automation Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analytics.automation_types}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {analytics.automation_types.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Performance Metrics</h3>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span>Response Time (s)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Success Rate (%)</span>
            </div>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analytics.performance_metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="response_time"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: '#3B82F6' }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="success_rate"
              stroke="#10B981"
              strokeWidth={2}
              dot={{ fill: '#10B981' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Recent Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">4-Week Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={analytics.recent_trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="notifications" fill="#3B82F6" name="Notifications" />
            <Bar dataKey="ai_insights" fill="#8B5CF6" name="AI Insights" />
            <Bar dataKey="backups" fill="#10B981" name="Backups" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Insights Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
      >
        <div className="flex items-start gap-3">
          <Activity className="w-6 h-6 text-blue-600 mt-1" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>• Your automation success rate improved by 5.2% this week</p>
              <p>• Transaction notifications are your most active automation (45% of total)</p>
              <p>• Best performance hours: 4:00 AM - 8:00 AM (97% success rate)</p>
              <p>• Recommendation: Enable AI-powered categorization to reduce manual processing</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AutomationAnalytics;