import React, { useState, useEffect } from 'react';
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  Plane, 
  Smartphone, 
  ShoppingCart,
  GitBranch,
  Cloud,
  Bell,
  Activity,
  Calendar,
  MapPin,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { useUser } from '../../contexts/UserContext';
import { useApi } from '../../hooks/useApi';
import { dashboardService } from '../../services/dashboardService';
import { walletService } from '../../services/walletService';

const DashboardWidgets = () => {
  const { user } = useUser();
  const [currentTime, setCurrentTime] = useState(new Date());

  // Fetch dashboard data
  const { 
    data: dashboardData, 
    loading: dashboardLoading, 
    error: dashboardError 
  } = useApi(
    () => user ? dashboardService.getDashboardOverview(user.id) : Promise.resolve(null),
    [user?.id]
  );

  // Fetch wallet data
  const { 
    data: walletData, 
    loading: walletLoading, 
    refetch: refetchWallet 
  } = useApi(
    () => user ? walletService.getWalletBalance(user.id) : Promise.resolve(null),
    [user?.id]
  );

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading user data...</span>
      </div>
    );
  }

  const WalletWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Happy Paisa Wallet</CardTitle>
        <Wallet className="h-4 w-4 text-yellow-600" />
      </CardHeader>
      <CardContent>
        {walletLoading ? (
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading wallet...</span>
          </div>
        ) : walletData ? (
          <>
            <div className="text-2xl font-bold text-yellow-600">
              {walletData.balance_hp} HP
            </div>
            <p className="text-xs text-muted-foreground">
              Equivalent to ₹{walletData.balance_inr_equiv?.toLocaleString()}
            </p>
            <div className="mt-4 space-y-2">
              {Object.entries(walletData.spending_breakdown || {}).slice(0, 3).map(([category, amount]) => (
                <div key={category} className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{category}</span>
                  <span className="text-xs font-medium">{amount} HP</span>
                </div>
              ))}
            </div>
            <Button className="w-full mt-3" size="sm" onClick={refetchWallet}>
              Refresh Wallet
            </Button>
          </>
        ) : (
          <div className="text-sm text-muted-foreground">Failed to load wallet data</div>
        )}
      </CardContent>
    </Card>
  );

  const RecentActivityWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center">
          <Activity className="h-4 w-4 mr-2" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        {walletLoading ? (
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading activity...</span>
          </div>
        ) : walletData?.recent_transactions ? (
          <div className="space-y-3">
            {walletData.recent_transactions.slice(0, 3).map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    transaction.type === 'credit' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="text-xs font-medium">{transaction.description}</p>
                    <p className="text-xs text-muted-foreground">{transaction.category}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-xs font-medium ${
                    transaction.type === 'credit' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.type === 'credit' ? '+' : '-'}{transaction.amount_hp} HP
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(transaction.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">No recent activity</div>
        )}
      </CardContent>
    </Card>
  );

  const QuickActionsWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
        <CardDescription>What would you like to do today?</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
            <Plane className="h-4 w-4" />
            <span className="text-xs">Book Travel</span>
          </Button>
          <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
            <Smartphone className="h-4 w-4" />
            <span className="text-xs">Recharge</span>
          </Button>
          <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
            <ShoppingCart className="h-4 w-4" />
            <span className="text-xs">Shop</span>
          </Button>
          <Button variant="outline" size="sm" className="h-12 flex flex-col space-y-1">
            <Wallet className="h-4 w-4" />
            <span className="text-xs">Add Money</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const WeatherWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Weather</CardTitle>
        <Cloud className="h-4 w-4 text-blue-500" />
      </CardHeader>
      <CardContent>
        {dashboardData?.weather ? (
          <>
            <div className="text-2xl font-bold">{dashboardData.weather.temperature}</div>
            <div className="flex items-center space-x-2">
              <MapPin className="h-3 w-3 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">{dashboardData.weather.location}</p>
            </div>
            <p className="text-sm text-foreground mt-1">{dashboardData.weather.condition}</p>
            <div className="mt-3 space-y-1">
              <div className="flex justify-between text-xs">
                <span>Humidity</span>
                <span>{dashboardData.weather.humidity}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span>Wind</span>
                <span>{dashboardData.weather.wind}</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">{dashboardData.weather.forecast}</p>
          </>
        ) : (
          <div className="text-sm text-muted-foreground">Weather data unavailable</div>
        )}
      </CardContent>
    </Card>
  );

  const StatsWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center">
          <GitBranch className="h-4 w-4 mr-2" />
          Your Stats
        </CardTitle>
      </CardHeader>
      <CardContent>
        {dashboardData?.activity_summary ? (
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Bookings</span>
              <span className="text-xs font-medium">{dashboardData.activity_summary.recent_bookings}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Recharges</span>
              <span className="text-xs font-medium">{dashboardData.activity_summary.recent_recharges}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-muted-foreground">Orders</span>
              <span className="text-xs font-medium">{dashboardData.activity_summary.recent_orders}</span>
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">Loading stats...</div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {/* User Welcome Card */}
      <Card className="md:col-span-2 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={user.avatar} alt={user.name} />
              <AvatarFallback>{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-lg">Good {
                currentTime.getHours() < 12 ? 'Morning' : 
                currentTime.getHours() < 17 ? 'Afternoon' : 'Evening'
              }, {user.name.split(' ')[0]}!</CardTitle>
              <CardDescription>
                {currentTime.toLocaleDateString()} • {currentTime.toLocaleTimeString()}
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-600">Mr. Happy is online</span>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Welcome to your AI-powered digital ecosystem. Your data is now live and connected to real services!
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button size="sm" onClick={() => alert("Mr. Happy: How can I help you today? All your data is now real and connected!")}>
              Talk to Mr. Happy
            </Button>
            <Button variant="outline" size="sm">
              View Today's Activity
            </Button>
          </div>
        </CardContent>
      </Card>

      <WalletWidget />
      <QuickActionsWidget />
      <RecentActivityWidget />
      <WeatherWidget />
      <StatsWidget />
    </div>
  );
};

export default DashboardWidgets;