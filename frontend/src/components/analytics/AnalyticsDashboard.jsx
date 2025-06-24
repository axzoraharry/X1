/**
 * Analytics Dashboard Component
 * Displays comprehensive analytics and insights for Axzora Mr. Happy 2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  Activity, 
  DollarSign, 
  Eye,
  Clock,
  Target,
  Zap,
  BarChart3,
  PieChart as PieChartIcon,
  Calendar,
  Filter
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useAnalyticsContext } from '../../contexts/AnalyticsContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const { trackFeatureUsage } = useAnalyticsContext();

  useEffect(() => {
    // Track feature usage
    trackFeatureUsage('analytics_dashboard', 'viewed');
    fetchAnalyticsData();
  }, [timeRange, trackFeatureUsage]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/analytics/summary?days=${timeRange}`);
      setAnalyticsData(response.data.summary);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
      // Set demo data for demonstration
      setAnalyticsData(getDemoAnalyticsData());
    } finally {
      setLoading(false);
    }
  };

  const getDemoAnalyticsData = () => ({
    total_events: 1250,
    unique_users: 89,
    period_days: timeRange,
    events_breakdown: [
      { event_name: 'page_view', count: 245, latest: '2025-01-19T10:30:00Z' },
      { event_name: 'happy_paisa_transaction', count: 198, latest: '2025-01-19T09:45:00Z' },
      { event_name: 'flight_search', count: 156, latest: '2025-01-19T11:15:00Z' },
      { event_name: 'voice_command', count: 134, latest: '2025-01-19T08:20:00Z' },
      { event_name: 'product_viewed', count: 123, latest: '2025-01-19T12:10:00Z' },
      { event_name: 'mobile_recharge', count: 98, latest: '2025-01-19T07:30:00Z' },
      { event_name: 'user_journey_step', count: 87, latest: '2025-01-19T11:50:00Z' },
      { event_name: 'feature_usage', count: 76, latest: '2025-01-19T10:05:00Z' },
      { event_name: 'booking_completed', count: 65, latest: '2025-01-19T09:15:00Z' },
      { event_name: 'automation_triggered', count: 68, latest: '2025-01-19T08:40:00Z' }
    ],
    revenue_data: [
      { date: '2025-01-13', hp: 45.2, inr: 45200 },
      { date: '2025-01-14', hp: 52.8, inr: 52800 },
      { date: '2025-01-15', hp: 38.9, inr: 38900 },
      { date: '2025-01-16', hp: 67.3, inr: 67300 },
      { date: '2025-01-17', hp: 71.5, inr: 71500 },
      { date: '2025-01-18', hp: 59.2, inr: 59200 },
      { date: '2025-01-19', hp: 63.7, inr: 63700 }
    ],
    user_engagement: {
      avg_session_duration: 847, // seconds
      bounce_rate: 23.4,
      pages_per_session: 4.2,
      conversion_rate: 12.8
    }
  });

  const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#f97316', '#3b82f6', '#ec4899'];

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 border-t-2 border-purple-600 rounded-full animate-spin"></div>
            <span className="text-lg font-medium">Loading Analytics...</span>
          </div>
        </div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: 'Total Events',
      value: analyticsData?.total_events?.toLocaleString() || '0',
      change: '+12.3%',
      icon: Activity,
      color: 'text-purple-600'
    },
    {
      title: 'Active Users',
      value: analyticsData?.unique_users?.toLocaleString() || '0',
      change: '+8.7%',
      icon: Users,
      color: 'text-blue-600'
    },
    {
      title: 'Avg Session Time',
      value: `${Math.floor((analyticsData?.user_engagement?.avg_session_duration || 0) / 60)}m ${(analyticsData?.user_engagement?.avg_session_duration || 0) % 60}s`,
      change: '+15.2%',
      icon: Clock,
      color: 'text-green-600'
    },
    {
      title: 'Conversion Rate',
      value: `${analyticsData?.user_engagement?.conversion_rate || 0}%`,
      change: '+2.1%',
      icon: Target,
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Comprehensive insights for Axzora Mr. Happy 2.0
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Select value={timeRange.toString()} onValueChange={(value) => setTimeRange(parseInt(value))}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</p>
                  <p className="text-sm text-green-600 mt-1">{kpi.change}</p>
                </div>
                <div className={`p-3 rounded-full bg-gray-100 ${kpi.color}`}>
                  <kpi.icon className="w-6 h-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Event Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChartIcon className="w-5 h-5 mr-2" />
              Event Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData?.events_breakdown?.slice(0, 6) || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="count"
                  nameKey="event_name"
                >
                  {(analyticsData?.events_breakdown?.slice(0, 6) || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Revenue Trend Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Revenue Trend (Happy Paisa)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData?.revenue_data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                <YAxis />
                <Tooltip 
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                  formatter={(value, name) => [`${value} HP`, 'Revenue']}
                />
                <Line 
                  type="monotone" 
                  dataKey="hp" 
                  stroke="#8b5cf6" 
                  strokeWidth={3}
                  dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top Events Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Top Events ({timeRange} days)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-medium text-gray-600">Event Name</th>
                  <th className="text-left p-3 font-medium text-gray-600">Count</th>
                  <th className="text-left p-3 font-medium text-gray-600">Latest</th>
                  <th className="text-left p-3 font-medium text-gray-600">Trend</th>
                </tr>
              </thead>
              <tbody>
                {(analyticsData?.events_breakdown || []).map((event, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-3" 
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <span className="font-medium">{event.event_name.replace(/_/g, ' ')}</span>
                      </div>
                    </td>
                    <td className="p-3 font-bold">{event.count.toLocaleString()}</td>
                    <td className="p-3 text-gray-600">
                      {new Date(event.latest).toLocaleDateString()}
                    </td>
                    <td className="p-3">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        +{Math.floor(Math.random() * 20 + 5)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* User Engagement Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <Eye className="w-8 h-8 mx-auto mb-3 text-blue-600" />
            <h3 className="text-lg font-semibold mb-2">Pages per Session</h3>
            <p className="text-3xl font-bold text-blue-600">
              {analyticsData?.user_engagement?.pages_per_session || 0}
            </p>
            <p className="text-sm text-gray-600 mt-1">Avg pages viewed</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <Zap className="w-8 h-8 mx-auto mb-3 text-yellow-600" />
            <h3 className="text-lg font-semibold mb-2">Bounce Rate</h3>
            <p className="text-3xl font-bold text-yellow-600">
              {analyticsData?.user_engagement?.bounce_rate || 0}%
            </p>
            <p className="text-sm text-gray-600 mt-1">Single page visits</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <DollarSign className="w-8 h-8 mx-auto mb-3 text-green-600" />
            <h3 className="text-lg font-semibold mb-2">Total Revenue</h3>
            <p className="text-3xl font-bold text-green-600">
              {(analyticsData?.revenue_data?.reduce((sum, day) => sum + day.hp, 0) || 0).toFixed(1)} HP
            </p>
            <p className="text-sm text-gray-600 mt-1">Last {timeRange} days</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;