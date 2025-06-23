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
  Calendar
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockHappyPaisaWallet } from '../data/mockData';

const WalletPage = () => {
  const [amount, setAmount] = useState('');
  const [conversionType, setConversionType] = useState('inr-to-hp');

  const handleConversion = () => {
    if (!amount) return;
    
    const amountNum = parseFloat(amount);
    if (conversionType === 'inr-to-hp') {
      const hpAmount = amountNum / 1000;
      alert(`₹${amountNum} = ${hpAmount} Happy Paisa`);
    } else {
      const inrAmount = amountNum * 1000;
      alert(`${amountNum} Happy Paisa = ₹${inrAmount}`);
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

  const SpendingCategoryCard = ({ category, amount, budget }) => {
    const percentage = budget ? (amount / budget.limit) * 100 : 0;
    const isOverBudget = percentage > 100;
    
    return (
      <Card className="hover:shadow-md transition-all duration-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">{category}</h3>
            <Badge variant={isOverBudget ? 'destructive' : 'secondary'} className="text-xs">
              {budget?.status || 'no-limit'}
            </Badge>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{amount} HP spent</span>
              {budget && <span>{budget.limit} HP limit</span>}
            </div>
            {budget && (
              <Progress 
                value={Math.min(percentage, 100)} 
                className={`h-2 ${isOverBudget ? 'bg-red-100' : 'bg-green-100'}`}
              />
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Happy Paisa Wallet</h1>
          <p className="text-muted-foreground">Your digital currency ecosystem</p>
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
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-4xl font-bold text-yellow-800">
                  {mockHappyPaisaWallet.balance_hp} HP
                </p>
                <p className="text-lg text-yellow-600">
                  ≈ ₹{mockHappyPaisaWallet.balance_inr_equiv.toLocaleString()}
                </p>
              </div>
              <div className="flex space-x-3">
                <Button className="flex-1 bg-yellow-600 hover:bg-yellow-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Money
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
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">This Month</span>
              <div className="text-right">
                <p className="font-semibold text-green-600">+2.5 HP</p>
                <p className="text-xs text-muted-foreground">Income</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Spent</span>
              <div className="text-right">
                <p className="font-semibold text-red-600">-1.8 HP</p>
                <p className="text-xs text-muted-foreground">Expenses</p>
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t">
              <span className="text-sm font-medium">Net Change</span>
              <div className="text-right">
                <p className="font-bold text-green-600">+0.7 HP</p>
                <p className="text-xs text-muted-foreground">This month</p>
              </div>
            </div>
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
              <CardDescription>Your latest Happy Paisa activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockHappyPaisaWallet.recent_transactions.map((transaction) => (
                  <TransactionItem key={transaction.id} transaction={transaction} />
                ))}
              </div>
              <Button variant="outline" className="w-full mt-4">
                View All Transactions
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(mockHappyPaisaWallet.spending_breakdown).map(([category, amount]) => (
              <SpendingCategoryCard 
                key={category}
                category={category}
                amount={amount}
                budget={mockHappyPaisaWallet.budget_status[category]}
              />
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <PieChart className="h-5 w-5" />
                <span>Spending Overview</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <PieChart className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Detailed Analytics Coming Soon</h3>
                <p className="text-muted-foreground">
                  Advanced spending analytics and insights will be available soon.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="convert" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5" />
                <span>Currency Conversion</span>
              </CardTitle>
              <CardDescription>Convert between INR and Happy Paisa</CardDescription>
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
                  />
                </div>
                <div className="flex items-end">
                  <Button onClick={handleConversion} className="w-full">
                    Convert
                  </Button>
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2">Conversion Rate</h4>
                <p className="text-sm text-blue-600">
                  1 Happy Paisa (HP) = ₹1,000 (Fixed Rate)
                </p>
                <p className="text-xs text-blue-500 mt-1">
                  This is a stable, fixed conversion rate for all transactions.
                </p>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium">Payment Methods</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <Card className="p-3 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <CreditCard className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="font-medium text-sm">Credit/Debit Card</p>
                        <p className="text-xs text-muted-foreground">Instant conversion</p>
                      </div>
                    </div>
                  </Card>
                  <Card className="p-3 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <Banknote className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium text-sm">Bank Transfer</p>
                        <p className="text-xs text-muted-foreground">UPI & Net Banking</p>
                      </div>
                    </div>
                  </Card>
                </div>
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
                  Wallet settings and preferences will be available here.
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