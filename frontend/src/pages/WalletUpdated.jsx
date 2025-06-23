import React, { useState } from 'react';
import { 
  Wallet as WalletIcon, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  Minus, 
  ArrowUpRight, 
  ArrowDownLeft,
  CreditCard,
  Banknote,
  PieChart,
  Calendar,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useUser } from '../contexts/UserContext';
import { useApi, useApiMutation } from '../hooks/useApi';
import { walletService } from '../services/walletService';
import { useToast } from '../hooks/use-toast';

const WalletPage = () => {
  const { user } = useUser();
  const { toast } = useToast();
  const [amount, setAmount] = useState('');
  const [conversionType, setConversionType] = useState('inr-to-hp');

  // Fetch wallet data
  const { 
    data: walletData, 
    loading: walletLoading, 
    error: walletError,
    refetch: refetchWallet 
  } = useApi(
    () => user ? walletService.getWalletBalance(user.id) : Promise.resolve(null),
    [user?.id]
  );

  // Fetch transactions
  const { 
    data: transactions, 
    loading: transactionsLoading,
    refetch: refetchTransactions 
  } = useApi(
    () => user ? walletService.getTransactions(user.id, 20) : Promise.resolve([]),
    [user?.id]
  );

  const { mutate: performMutation, loading: mutationLoading } = useApiMutation();

  const handleConversion = async () => {
    if (!amount || !user) {
      toast({
        title: "Error",
        description: "Please enter a valid amount",
        variant: "destructive"
      });
      return;
    }
    
    try {
      const amountNum = parseFloat(amount);
      if (conversionType === 'inr-to-hp') {
        await performMutation(() => walletService.convertInrToHp(user.id, amountNum));
        toast({
          title: "Conversion Successful",
          description: `₹${amountNum} converted to ${amountNum / 1000} Happy Paisa`,
        });
      } else {
        await performMutation(() => walletService.convertHpToInr(user.id, amountNum));
        toast({
          title: "Conversion Successful", 
          description: `${amountNum} Happy Paisa converted to ₹${amountNum * 1000}`,
        });
      }
      
      // Refresh wallet data
      refetchWallet();
      refetchTransactions();
      setAmount('');
    } catch (error) {
      toast({
        title: "Conversion Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleAddMoney = async () => {
    if (!user) return;
    
    try {
      await performMutation(() => walletService.creditWallet(user.id, 5.0, "Quick top-up"));
      toast({
        title: "Money Added",
        description: "5 HP added to your wallet",
      });
      refetchWallet();
      refetchTransactions();
    } catch (error) {
      toast({
        title: "Add Money Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const TransactionItem = ({ transaction }) => (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
      <div className="flex items-center space-x-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          transaction.type === 'credit' 
            ? 'bg-green-100 text-green-600' 
            : 'bg-red-100 text-red-600'
        }`}>
          {transaction.type === 'credit' ? <ArrowDownLeft className="h-5 w-5" /> : <ArrowUpRight className="h-5 w-5" />}
        </div>
        <div>
          <p className="font-medium text-sm">{transaction.description}</p>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">{transaction.category}</Badge>
            <span className="text-xs text-muted-foreground">
              {new Date(transaction.timestamp).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
      <div className="text-right">
        <p className={`font-semibold ${
          transaction.type === 'credit' ? 'text-green-600' : 'text-red-600'
        }`}>
          {transaction.type === 'credit' ? '+' : '-'}{transaction.amount_hp} HP
        </p>
        <p className="text-xs text-muted-foreground">
          {transaction.type === 'credit' ? '+' : '-'}₹{(transaction.amount_hp * 1000).toLocaleString()}
        </p>
        <Badge variant={transaction.status === 'completed' ? 'default' : 'secondary'} className="text-xs mt-1">
          {transaction.status}
        </Badge>
      </div>
    </div>
  );

  const SpendingCategoryCard = ({ category, amount }) => {
    return (
      <Card className="hover:shadow-md transition-all duration-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">{category}</h3>
            <Badge variant="secondary" className="text-xs">Active</Badge>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{amount} HP spent</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (!user) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <h2 className="text-lg font-semibold">Loading Wallet...</h2>
        </div>
      </div>
    );
  }

  if (walletError) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-red-600">Error Loading Wallet</h2>
          <p className="text-muted-foreground">{walletError}</p>
          <Button onClick={refetchWallet} className="mt-4">Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Happy Paisa Wallet</h1>
          <p className="text-muted-foreground">Your digital currency ecosystem - Live Data</p>
        </div>
        <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-50 to-yellow-100 px-4 py-2 rounded-lg">
          <WalletIcon className="h-5 w-5 text-yellow-600" />
          <span className="text-sm font-medium">1 HP = ₹1,000</span>
        </div>
      </div>

      {/* Balance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <WalletIcon className="h-6 w-6 text-yellow-600" />
              <span>Current Balance</span>
              {walletLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                {walletLoading ? (
                  <div className="animate-pulse">
                    <div className="h-10 bg-yellow-200 rounded w-32 mb-2"></div>
                    <div className="h-6 bg-yellow-200 rounded w-24"></div>
                  </div>
                ) : walletData ? (
                  <>
                    <p className="text-4xl font-bold text-yellow-800">
                      {walletData.balance_hp.toFixed(3)} HP
                    </p>
                    <p className="text-lg text-yellow-600">
                      ≈ ₹{walletData.balance_inr_equiv?.toLocaleString()}
                    </p>
                  </>
                ) : (
                  <p className="text-lg text-yellow-600">Failed to load balance</p>
                )}
              </div>
              <div className="flex space-x-3">
                <Button 
                  className="flex-1 bg-yellow-600 hover:bg-yellow-700"
                  onClick={handleAddMoney}
                  disabled={mutationLoading}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {mutationLoading ? 'Adding...' : 'Add Money'}
                </Button>
                <Button variant="outline" className="flex-1 border-yellow-300 text-yellow-700 hover:bg-yellow-50">
                  <Minus className="h-4 w-4 mr-2" />
                  Withdraw
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Quick Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {walletLoading ? (
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded"></div>
              </div>
            ) : walletData ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Total Transactions</span>
                  <div className="text-right">
                    <p className="font-semibold">{walletData.recent_transactions?.length || 0}</p>
                    <p className="text-xs text-muted-foreground">This period</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Last Activity</span>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">
                      {walletData.recent_transactions?.[0] ? 
                        new Date(walletData.recent_transactions[0].timestamp).toLocaleDateString() : 
                        'No activity'
                      }
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Unable to load stats</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="transactions" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="convert">Convert</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="transactions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Your latest Happy Paisa activity - Live Data</CardDescription>
            </CardHeader>
            <CardContent>
              {transactionsLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="animate-pulse flex space-x-4 p-3 border rounded-lg">
                      <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : transactions && transactions.length > 0 ? (
                <div className="space-y-3">
                  {transactions.map((transaction) => (
                    <TransactionItem key={transaction.id} transaction={transaction} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No transactions yet</p>
                </div>
              )}
              <Button variant="outline" className="w-full mt-4" onClick={refetchTransactions}>
                Refresh Transactions
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {walletData?.spending_breakdown ? 
              Object.entries(walletData.spending_breakdown).map(([category, amount]) => (
                <SpendingCategoryCard 
                  key={category}
                  category={category}
                  amount={amount}
                />
              )) : 
              <div className="col-span-full text-center py-8">
                <p className="text-muted-foreground">No spending data available yet</p>
              </div>
            }
          </div>
        </TabsContent>

        <TabsContent value="convert" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5" />
                <span>Currency Conversion</span>
              </CardTitle>
              <CardDescription>Convert between INR and Happy Paisa - Live Processing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Conversion Type</label>
                  <Select value={conversionType} onValueChange={setConversionType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inr-to-hp">INR → Happy Paisa</SelectItem>
                      <SelectItem value="hp-to-inr">Happy Paisa → INR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">
                    Amount ({conversionType === 'inr-to-hp' ? 'INR' : 'HP'})
                  </label>
                  <Input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder={conversionType === 'inr-to-hp' ? '1000' : '1'}
                    disabled={mutationLoading}
                  />
                </div>
                <div className="flex items-end">
                  <Button 
                    onClick={handleConversion} 
                    className="w-full"
                    disabled={mutationLoading || !amount}
                  >
                    {mutationLoading ? 'Converting...' : 'Convert Now'}
                  </Button>
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2">Live Conversion Rate</h4>
                <p className="text-sm text-blue-600">
                  1 Happy Paisa (HP) = ₹1,000 (Fixed Rate)
                </p>
                <p className="text-xs text-blue-500 mt-1">
                  Instant conversion with real-time balance updates.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Wallet Settings</CardTitle>
              <CardDescription>Manage your Happy Paisa preferences</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <h3 className="text-lg font-semibold mb-2">Settings Panel</h3>
                <p className="text-muted-foreground">
                  Advanced wallet settings coming soon.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WalletPage;