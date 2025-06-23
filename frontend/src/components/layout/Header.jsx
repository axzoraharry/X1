import React, { useState } from 'react';
import { Bell, Search, Mic, MicOff, User, Wallet, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger 
} from '../ui/dropdown-menu';
import { useUser } from '../../contexts/UserContext';
import { useApi } from '../../hooks/useApi';
import { walletService } from '../../services/walletService';
import { dashboardService } from '../../services/dashboardService';

const Header = ({ onVoiceToggle, isListening = false }) => {
  const { user, loading: userLoading } = useUser();
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch wallet balance for header display
  const { data: walletData } = useApi(
    () => user ? walletService.getWalletBalance(user.id) : Promise.resolve(null),
    [user?.id]
  );

  // Fetch notifications
  const { data: notificationsData } = useApi(
    () => user ? dashboardService.getNotifications(user.id, 5) : Promise.resolve({ notifications: [] }),
    [user?.id]
  );

  const notifications = notificationsData?.notifications || [];
  const unreadCount = notifications.filter(n => !n.read).length;

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      console.log('Searching for:', searchQuery);
      // Simulate voice interaction with real user data
      setTimeout(() => {
        alert(`Mr. Happy: I found some results for "${searchQuery}". ${user ? `${user.name}, h` : 'H'}ow can I help you with that?`);
      }, 500);
    }
  };

  if (userLoading) {
    return (
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-center px-4">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Loading Axzora...</span>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Axzora
              </h1>
              <p className="text-xs text-muted-foreground -mt-1">Mr. Happy 2.0</p>
            </div>
          </div>
        </div>

        {/* Search Bar with Voice */}
        <div className="flex-1 max-w-lg mx-4">
          <form onSubmit={handleSearch} className="relative">
            <Input
              type="text"
              placeholder={user ? `Ask Mr. Happy anything, ${user.name}...` : "Ask Mr. Happy anything..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pr-20 pl-10 h-10 rounded-full border-2 border-muted hover:border-blue-300 focus:border-blue-500 transition-all duration-300"
            />
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
              <Button
                type="button"
                size="sm"
                variant={isListening ? "destructive" : "secondary"}
                onClick={onVoiceToggle}
                className={`h-6 w-6 p-0 rounded-full transition-all duration-300 ${
                  isListening ? 'animate-pulse bg-red-500 hover:bg-red-600' : 'hover:bg-blue-100'
                }`}
              >
                {isListening ? <MicOff className="h-3 w-3" /> : <Mic className="h-3 w-3" />}
              </Button>
              <Button type="submit" size="sm" variant="ghost" className="h-6 w-6 p-0 rounded-full">
                <Search className="h-3 w-3" />
              </Button>
            </div>
          </form>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-3">
          {/* Happy Paisa Balance */}
          <div className="hidden md:flex items-center space-x-2 bg-gradient-to-r from-yellow-50 to-yellow-100 px-3 py-1.5 rounded-full border border-yellow-200">
            <Wallet className="h-4 w-4 text-yellow-600" />
            {walletData ? (
              <>
                <span className="text-sm font-semibold text-yellow-800">
                  {walletData.balance_hp} HP
                </span>
                <span className="text-xs text-yellow-600">
                  (₹{walletData.balance_inr_equiv?.toLocaleString()})
                </span>
              </>
            ) : (
              <span className="text-sm text-yellow-600">Loading...</span>
            )}
          </div>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="relative h-9 w-9 rounded-full">
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center animate-pulse"
                  >
                    {unreadCount}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {notifications.slice(0, 3).map((notif) => (
                <DropdownMenuItem key={notif.id} className="flex flex-col items-start p-3">
                  <div className="flex items-center justify-between w-full">
                    <span className="font-medium text-sm">{notif.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(notif.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{notif.message}</p>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-center">
                <span className="text-sm text-blue-600">View all notifications</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                  <Avatar className="h-9 w-9">
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback>{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                    <p className="text-xs leading-none text-green-600">✓ Live Connected</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Wallet className="mr-2 h-4 w-4" />
                  <span>Happy Paisa Wallet</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <span>Sign out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;