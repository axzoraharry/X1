import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  TrendingUp, 
  Shield, 
  AlertTriangle, 
  CheckCircle,
  Zap,
  RefreshCw,
  Lightbulb
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { friendliAiService } from '../../services/friendliAiService';

const AiInsightsPanel = ({ userId, transactionHash = null }) => {
  const [insights, setInsights] = useState(null);
  const [transactionAnalysis, setTransactionAnalysis] = useState(null);
  const [fraudDetection, setFraudDetection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (userId) {
      loadAllInsights();
    }
  }, [userId, transactionHash]);

  const loadAllInsights = async () => {
    try {
      setLoading(true);
      
      const promises = [
        friendliAiService.getWalletInsights(userId),
        friendliAiService.detectFraud(userId)
      ];

      if (transactionHash) {
        promises.push(friendliAiService.analyzeTransaction(transactionHash));
      }

      const results = await Promise.allSettled(promises);
      
      setInsights(results[0].status === 'fulfilled' ? results[0].value : null);
      setFraudDetection(results[1].status === 'fulfilled' ? results[1].value : null);
      
      if (transactionHash && results[2]) {
        setTransactionAnalysis(results[2].status === 'fulfilled' ? results[2].value : null);
      }

    } catch (error) {
      console.error('Error loading AI insights:', error);
      toast({
        title: "AI Insights Error",
        description: "Failed to load AI insights",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    friendliAiService.clearCache();
    await loadAllInsights();
    setRefreshing(false);
    
    toast({
      title: "Insights Refreshed",
      description: "AI insights have been updated with latest data",
    });
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center space-y-2">
            <Brain className="w-8 h-8 animate-pulse text-blue-600 mx-auto" />
            <p className="text-gray-600">Loading AI insights...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold flex items-center space-x-2">
            <Brain className="w-5 h-5 text-blue-600" />
            <span>AI Insights</span>
            <Badge variant="secondary" className="text-xs">
              Powered by Friendli AI
            </Badge>
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Advanced AI analysis of your financial activity
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
          className="space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Transaction Analysis (if available) */}
      {transactionAnalysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-yellow-600" />
                <span>Transaction Analysis</span>
              </CardTitle>
              <CardDescription>
                AI analysis of transaction: {transactionHash?.slice(0, 16)}...
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Risk Level</span>
                <Badge className={friendliAiService.getRiskLevelColor(transactionAnalysis.analysis.risk_level)}>
                  {transactionAnalysis.analysis.risk_level.toUpperCase()}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Risk Score</span>
                <span className="font-bold text-lg">
                  {Math.round(transactionAnalysis.analysis.risk_score)}/100
                </span>
              </div>

              {transactionAnalysis.analysis.anomaly_detected && (
                <Alert className="border-yellow-200 bg-yellow-50">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <AlertDescription className="text-yellow-800">
                    Anomaly detected in this transaction
                  </AlertDescription>
                </Alert>
              )}

              {transactionAnalysis.analysis.insights.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Key Insights</h4>
                  <ul className="space-y-1">
                    {transactionAnalysis.analysis.insights.slice(0, 3).map((insight, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                        <Lightbulb className="w-3 h-3 mt-1 text-yellow-500" />
                        <span>{friendliAiService.formatAnalysisText(insight)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Fraud Detection */}
      {fraudDetection && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-green-600" />
                <span>Security Analysis</span>
              </CardTitle>
              <CardDescription>
                Fraud detection and security insights
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Security Status</span>
                <div className="flex items-center space-x-2">
                  {fraudDetection.fraud_analysis.fraud_detected ? (
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  ) : (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  )}
                  <Badge className={fraudDetection.fraud_analysis.fraud_detected ? 
                    'text-red-600 bg-red-100' : 'text-green-600 bg-green-100'}>
                    {fraudDetection.fraud_analysis.fraud_detected ? 'Alerts Found' : 'Secure'}
                  </Badge>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Alert Level</span>
                <Badge className={friendliAiService.getRiskLevelColor(fraudDetection.fraud_analysis.alert_level)}>
                  {fraudDetection.fraud_analysis.alert_level.toUpperCase()}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Confidence Score</span>
                <span className="font-bold">
                  {Math.round(fraudDetection.fraud_analysis.confidence_score)}%
                </span>
              </div>

              {fraudDetection.fraud_analysis.recommendations.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Security Recommendations</h4>
                  <ul className="space-y-1">
                    {fraudDetection.fraud_analysis.recommendations.slice(0, 3).map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                        <Shield className="w-3 h-3 mt-1 text-green-500" />
                        <span>{friendliAiService.formatAnalysisText(rec)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Wallet Insights */}
      {insights && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <span>Financial Insights</span>
              </CardTitle>
              <CardDescription>
                AI-powered analysis of your spending patterns
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Financial Health Score</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${friendliAiService.getHealthScoreColor(insights.insights.financial_health_score)}`}
                      style={{ width: `${insights.insights.financial_health_score}%` }}
                    />
                  </div>
                  <span className={`font-bold ${friendliAiService.getHealthScoreColor(insights.insights.financial_health_score)}`}>
                    {Math.round(insights.insights.financial_health_score)}
                  </span>
                </div>
              </div>

              {insights.insights.spending_patterns.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Spending Patterns</h4>
                  <ul className="space-y-1">
                    {insights.insights.spending_patterns.slice(0, 2).map((pattern, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                        <TrendingUp className="w-3 h-3 mt-1 text-purple-500" />
                        <span>{friendliAiService.formatAnalysisText(pattern)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {insights.insights.recommendations.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">AI Recommendations</h4>
                  <ul className="space-y-1">
                    {insights.insights.recommendations.slice(0, 2).map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                        <Lightbulb className="w-3 h-3 mt-1 text-yellow-500" />
                        <span>{friendliAiService.formatAnalysisText(rec)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {insights.insights.optimization_tips.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-2">Optimization Tips</h4>
                  <ul className="space-y-1">
                    {insights.insights.optimization_tips.slice(0, 2).map((tip, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                        <Zap className="w-3 h-3 mt-1 text-blue-500" />
                        <span>{friendliAiService.formatAnalysisText(tip)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* AI Model Info */}
      <div className="text-center text-xs text-gray-500">
        <div className="flex items-center justify-center space-x-2">
          <Brain className="w-3 h-3" />
          <span>Powered by Friendli AI • Meta Llama 3.1 8B Instruct</span>
        </div>
      </div>
    </div>
  );
};

export default AiInsightsPanel;