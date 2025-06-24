import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Filter, 
  Search,
  Receipt,
  MapPin,
  Calendar,
  TrendingUp
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';
import { virtualCardService } from '../../services/virtualCardService';

const CardTransactionHistory = ({ cardId, userId }) => {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  useEffect(() => {
    loadTransactions();
  }, [cardId, userId]);

  useEffect(() => {
    filterTransactions();
  }, [transactions, searchTerm, statusFilter, typeFilter]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await virtualCardService.getCardTransactions(cardId, userId);
      setTransactions(data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterTransactions = () => {
    let filtered = [...transactions];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(txn => 
        txn.merchant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        txn.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        txn.reference_number.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(txn => txn.transaction_status === statusFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(txn => txn.transaction_type === typeFilter);
    }

    setFilteredTransactions(filtered);
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'purchase':
        return <ArrowUpRight className="w-4 h-4 text-red-500" />;
      case 'load':
        return <ArrowDownLeft className="w-4 h-4 text-green-500" />;
      case 'refund':
        return <ArrowDownLeft className="w-4 h-4 text-blue-500" />;
      default:
        return <Receipt className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-IN'),
      time: date.toLocaleTimeString('en-IN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    };
  };

  const getTransactionSummary = () => {
    const totalTransactions = filteredTransactions.length;
    const totalSpent = filteredTransactions
      .filter(txn => txn.transaction_type === 'purchase' && txn.transaction_status === 'approved')
      .reduce((sum, txn) => sum + txn.amount_inr, 0);
    
    const avgTransaction = totalTransactions > 0 ? totalSpent / totalTransactions : 0;

    return { totalTransactions, totalSpent, avgTransaction };
  };

  const summary = getTransactionSummary();

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center space-y-2">
            <Clock className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
            <p className="text-gray-600">Loading transactions...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Transaction Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Receipt className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Transactions</p>
                <p className="text-2xl font-bold">{summary.totalTransactions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Total Spent</p>
                <p className="text-2xl font-bold">₹{summary.totalSpent.toLocaleString()}</p>
                <p className="text-xs text-gray-500">{(summary.totalSpent / 1000).toFixed(3)} HP</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Transaction</p>
                <p className="text-2xl font-bold">₹{Math.round(summary.avgTransaction).toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Transaction History</span>
          </CardTitle>
          <CardDescription>
            View and filter your card transaction history
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="declined">Declined</SelectItem>
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="purchase">Purchase</SelectItem>
                <SelectItem value="load">Load</SelectItem>
                <SelectItem value="refund">Refund</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Transaction List */}
          <div className="space-y-3">
            {filteredTransactions.length === 0 ? (
              <Alert>
                <AlertDescription>
                  No transactions found matching your criteria.
                </AlertDescription>
              </Alert>
            ) : (
              filteredTransactions.map((transaction, index) => {
                const { date, time } = formatDateTime(transaction.created_at);
                
                return (
                  <motion.div
                    key={transaction.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getTransactionIcon(transaction.transaction_type)}
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="font-medium text-gray-900">
                              {transaction.merchant_name}
                            </h4>
                            <span className="text-lg">
                              {virtualCardService.getMerchantCategoryIcon(transaction.merchant_category)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{transaction.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                            <span className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>{date} {time}</span>
                            </span>
                            {transaction.location && (
                              <span className="flex items-center space-x-1">
                                <MapPin className="w-3 h-3" />
                                <span>{transaction.location}</span>
                              </span>
                            )}
                            <span>Ref: {transaction.reference_number}</span>
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <div>
                            <p className={`font-semibold ${
                              transaction.transaction_type === 'purchase' ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {transaction.transaction_type === 'purchase' ? '-' : '+'}
                              ₹{transaction.amount_inr.toLocaleString()}
                            </p>
                            <p className="text-xs text-gray-500">
                              {transaction.amount_hp.toFixed(3)} HP
                            </p>
                          </div>
                          <Badge 
                            className={virtualCardService.getTransactionStatusColor(transaction.transaction_status)}
                            variant="outline"
                          >
                            {transaction.transaction_status}
                          </Badge>
                        </div>
                        {transaction.authorization_code && (
                          <p className="text-xs text-gray-500 mt-1">
                            Auth: {transaction.authorization_code}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })
            )}
          </div>

          {filteredTransactions.length > 0 && (
            <div className="mt-4 text-center">
              <Button variant="outline" onClick={loadTransactions}>
                Refresh Transactions
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CardTransactionHistory;