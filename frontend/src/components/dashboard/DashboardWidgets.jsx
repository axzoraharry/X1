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
  MapPin
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { 
  mockHappyPaisaWallet, 
  mockFlights, 
  mockProducts, 
  mockGitActivity, 
  mockWeather,
  mockNotifications,
  mockUser 
} from '../../data/mockData';

const DashboardWidgets = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const WalletWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Happy Paisa Wallet</CardTitle>
        <Wallet className="h-4 w-4 text-yellow-600" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-yellow-600">
          {mockHappyPaisaWallet.balance_hp} HP
        </div>
        <p className="text-xs text-muted-foreground">
          Equivalent to ₹{mockHappyPaisaWallet.balance_inr_equiv.toLocaleString()}
        </p>
        <div className="mt-4 space-y-2">
          {Object.entries(mockHappyPaisaWallet.spending_breakdown).slice(0, 3).map(([category, amount]) => (
            <div key={category} className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">{category}</span>
              <span className="text-xs font-medium">{amount} HP</span>
            </div>
          ))}
        </div>
        <Button className="w-full mt-3" size="sm">
          Manage Wallet
        </Button>
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
        <div className="space-y-3">
          {mockHappyPaisaWallet.recent_transactions.slice(0, 3).map((transaction) => (
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
        <div className="text-2xl font-bold">{mockWeather.temperature}</div>
        <div className="flex items-center space-x-2">
          <MapPin className="h-3 w-3 text-muted-foreground" />
          <p className="text-xs text-muted-foreground">{mockWeather.location}</p>
        </div>
        <p className="text-sm text-foreground mt-1">{mockWeather.condition}</p>
        <div className="mt-3 space-y-1">
          <div className="flex justify-between text-xs">
            <span>Humidity</span>
            <span>{mockWeather.humidity}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span>Wind</span>
            <span>{mockWeather.wind}</span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2">{mockWeather.forecast}</p>
      </CardContent>
    </Card>
  );

  const GitActivityWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center">
          <GitBranch className="h-4 w-4 mr-2" />
          Git Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {mockGitActivity.slice(0, 2).map((activity) => (
            <div key={activity.id} className="space-y-1">
              <div className="flex items-center justify-between">
                <Badge variant="secondary" className="text-xs">
                  {activity.type}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {new Date(activity.timestamp).toLocaleDateString()}
                </span>
              </div>
              <p className="text-xs">
                {activity.message || activity.title}
              </p>
            </div>
          ))}
        </div>
        <Button variant="outline" size="sm" className="w-full mt-3">
          View All Activity
        </Button>
      </CardContent>
    </Card>
  );

  const RecommendationsWidget = () => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Mr. Happy's Recommendations</CardTitle>
        <CardDescription>Personalized suggestions for you</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
            <div className="flex items-start space-x-2">
              <Plane className="h-4 w-4 text-blue-600 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-blue-800">Flight Deal Alert</p>
                <p className="text-xs text-blue-600">Mumbai flights 30% off this weekend</p>
              </div>
            </div>
          </div>
          <div className="p-3 bg-green-50 rounded-lg border border-green-100">
            <div className="flex items-start space-x-2">
              <Smartphone className="h-4 w-4 text-green-600 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-green-800">Recharge Reminder</p>
                <p className="text-xs text-green-600">Your plan expires in 3 days</p>
              </div>
            </div>
          </div>
        </div>
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
              <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
              <AvatarFallback>{mockUser.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-lg">Good {
                currentTime.getHours() < 12 ? 'Morning' : 
                currentTime.getHours() < 17 ? 'Afternoon' : 'Evening'
              }, {mockUser.name.split(' ')[0]}!</CardTitle>
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
            Welcome to your AI-powered digital ecosystem. Ask me anything or use the quick actions below to get started.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button size="sm" onClick={() => alert("Mr. Happy: How can I help you today?")}>
              Talk to Mr. Happy
            </Button>
            <Button variant="outline" size="sm">
              View Today's Schedule
            </Button>
          </div>
        </CardContent>
      </Card>

      <WalletWidget />
      <QuickActionsWidget />
      <RecentActivityWidget />
      <WeatherWidget />
      <GitActivityWidget />
      <RecommendationsWidget />
    </div>
  );
};

export default DashboardWidgets;