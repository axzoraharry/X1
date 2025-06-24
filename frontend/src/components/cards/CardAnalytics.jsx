import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  AlertTriangle,
  Store,
  Calendar,
  DollarSign,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { virtualCardService } from '../../services/virtualCardService';

const CardAnalytics = ({ cardId, userId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [merchantInsights, setMerchantInsights] = useState(null);
  const [fraudAlerts, setFraudAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30');

  useEffect(() => {
    loadAnalytics();
  }, [cardId, userId, period]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [analyticsData, merchantData, alertsData] = await Promise.all([
        virtualCardService.getSpendingAnalytics(userId, cardId, parseInt(period)),
        virtualCardService.getMerchantInsights(userId, parseInt(period)),
        virtualCardService.getFraudAlerts(userId, 7)
      ]);
      
      setAnalytics(analyticsData);
      setMerchantInsights(merchantData);
      setFraudAlerts(alertsData);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getSpendingTrend = () => {
    if (!analytics?.daily_spending || analytics.daily_spending.length < 2) {
      return 'neutral';
    }
    
    const recent = analytics.daily_spending.slice(-7);
    const firstHalf = recent.slice(0, Math.ceil(recent.length / 2));
    const secondHalf = recent.slice(Math.ceil(recent.length / 2));
    
    const firstAvg = firstHalf.reduce((sum, day) => sum + day.total_amount_inr, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, day) => sum + day.total_amount_inr, 0) / secondHalf.length;
    
    if (secondAvg > firstAvg * 1.1) return 'increasing';
    if (secondAvg < firstAvg * 0.9) return 'decreasing';
    return 'stable';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center space-y-2">
            <BarChart3 className="w-8 h-8 animate-pulse text-blue-600 mx-auto" />
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const spendingTrend = getSpendingTrend();

  return (
    <div className="space-y-6">
      {/* Header with Period Selector */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Card Analytics</h3>
          <p className="text-sm text-gray-600">Insights into your spending patterns</p>
        </div>
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">7 Days</SelectItem>
            <SelectItem value="30">30 Days</SelectItem>
            <SelectItem value="90">90 Days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Fraud Alerts */}
      {fraudAlerts?.alerts_count > 0 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <div className="flex justify-between items-center">
              <div>
                <strong>Security Alert!</strong>
                <p className="text-sm mt-1">
                  {fraudAlerts.alerts_count} suspicious activities detected in the last 7 days
                </p>
              </div>
              <Badge variant="destructive">
                {fraudAlerts.summary.high_severity + fraudAlerts.summary.medium_severity} alerts
              </Badge>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Spent</p>
                <p className="text-xl font-bold">
                  {formatCurrency(analytics?.total_statistics?.total_spent_inr || 0)}
                </p>
                <p className="text-xs text-gray-500">
                  {(analytics?.total_statistics?.total_spent_hp || 0).toFixed(3)} HP
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Transactions</p>
                <p className="text-xl font-bold">
                  {analytics?.total_statistics?.total_transactions || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Average</p>
                <p className="text-xl font-bold">
                  {formatCurrency(analytics?.total_statistics?.avg_transaction_inr || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className={`w-5 h-5 ${
                spendingTrend === 'increasing' ? 'text-red-600' : 
                spendingTrend === 'decreasing' ? 'text-green-600' : 'text-gray-600'
              }`} />
              <div>
                <p className="text-sm font-medium text-gray-600">Trend</p>
                <p className={`text-lg font-semibold ${
                  spendingTrend === 'increasing' ? 'text-red-600' : 
                  spendingTrend === 'decreasing' ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {spendingTrend === 'increasing' ? '↗ Rising' :
                   spendingTrend === 'decreasing' ? '↘ Falling' : '→ Stable'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Spending by Category */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <PieChart className="w-5 h-5 text-blue-600" />
            <span>Spending by Category</span>
          </CardTitle>
          <CardDescription>
            Where your money goes in the last {period} days
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analytics?.spending_by_category?.length > 0 ? (
            <div className="space-y-3">
              {analytics.spending_by_category.map((category, index) => {
                const percentage = (category.total_amount_inr / analytics.total_statistics.total_spent_inr) * 100;
                return (
                  <motion.div
                    key={category._id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">
                        {virtualCardService.getMerchantCategoryIcon(category._id)}
                      </span>
                      <div>
                        <p className="font-medium capitalize">
                          {category._id.replace('_', ' ')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {category.transaction_count} transactions
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        {formatCurrency(category.total_amount_inr)}
                      </p>
                      <p className="text-sm text-gray-600">
                        {percentage.toFixed(1)}%
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No spending data available for the selected period
            </p>
          )}
        </CardContent>
      </Card>

      {/* Top Merchants */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Store className="w-5 h-5 text-green-600" />
            <span>Top Merchants</span>
          </CardTitle>
          <CardDescription>
            Your most frequent spending destinations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {merchantInsights?.top_merchants?.length > 0 ? (
            <div className="space-y-3">
              {merchantInsights.top_merchants.slice(0, 5).map((merchant, index) => (
                <motion.div
                  key={merchant._id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-bold">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{merchant._id}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>{merchant.transaction_count} transactions</span>
                        <span>Avg: {formatCurrency(merchant.avg_transaction_inr)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">
                      {formatCurrency(merchant.total_spent_inr)}
                    </p>
                    <p className="text-sm text-gray-600">
                      Last: {new Date(merchant.last_transaction).toLocaleDateString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No merchant data available
            </p>
          )}
        </CardContent>
      </Card>

      {/* Daily Spending Pattern */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-purple-600" />
            <span>Daily Spending Pattern</span>
          </CardTitle>
          <CardDescription>
            Your spending activity over the last {period} days
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analytics?.daily_spending?.length > 0 ? (
            <div className="space-y-2">
              {analytics.daily_spending.slice(-10).map((day, index) => {
                const maxAmount = Math.max(...analytics.daily_spending.map(d => d.total_amount_inr));
                const barWidth = maxAmount > 0 ? (day.total_amount_inr / maxAmount) * 100 : 0;
                
                return (
                  <motion.div
                    key={day._id.date}
                    initial={{ opacity: 0, scaleX: 0 }}
                    animate={{ opacity: 1, scaleX: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 p-2"
                  >
                    <div className="w-20 text-sm text-gray-600">
                      {new Date(day._id.date).toLocaleDateString('en-IN', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                    <div className="flex-1 relative">
                      <div className="h-6 bg-gray-200 rounded">
                        <div 
                          className="h-full bg-blue-500 rounded transition-all duration-300"
                          style={{ width: `${Math.max(barWidth, 2)}%` }}
                        />
                      </div>
                    </div>
                    <div className="w-24 text-right text-sm font-medium">
                      {formatCurrency(day.total_amount_inr)}
                    </div>
                    <div className="w-16 text-right text-xs text-gray-500">
                      {day.transaction_count} txns
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No daily spending data available
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CardAnalytics;