import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { 
  Home, 
  Plane, 
  Smartphone, 
  ShoppingCart, 
  Wallet, 
  Settings,
  GitBranch,
  Cloud,
  Activity,
  CreditCard,
  Cog8ToothIcon
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: Home,
    description: 'AI-powered overview'
  },
  {
    title: 'Travel',
    href: '/travel',
    icon: Plane,
    description: 'Flights, Hotels, Buses',
    badge: 'Hot'
  },
  {
    title: 'Recharge',
    href: '/recharge',
    icon: Smartphone,
    description: 'Mobile, DTH, Utilities'
  },
  {
    title: 'E-commerce',
    href: '/shop',
    icon: ShoppingCart,
    description: 'Curated products',
    badge: 'New'
  },
  {
    title: 'Happy Paisa',
    href: '/wallet',
    icon: Wallet,
    description: 'Digital currency wallet'
  },
  {
    title: 'Automation',
    href: '/automation',
    icon: Settings,
    description: 'n8n workflows & AI',
    badge: 'Smart'
  },
  {
    title: 'Git Activity',
    href: '/git',
    icon: GitBranch,
    description: 'Development tracking'
  }
];

const secondaryItems = [
  {
    title: 'Weather',
    href: '/weather',
    icon: Cloud,
    description: 'Local forecasts'
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: Activity,
    description: 'Usage insights'
  },
  {
    title: 'Payments',
    href: '/payments',
    icon: CreditCard,
    description: 'Transaction history'
  },
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'App preferences'
  }
];

const Sidebar = ({ collapsed = false }) => {
  const location = useLocation();

  const NavItem = ({ item, isActive }) => (
    <Link to={item.href} className="block">
      <Button
        variant={isActive ? "secondary" : "ghost"}
        className={cn(
          "w-full justify-start h-12 mb-1 transition-all duration-200 hover:bg-secondary/80",
          isActive && "bg-secondary shadow-sm border-l-4 border-l-blue-500",
          collapsed && "justify-center px-2"
        )}
      >
        <item.icon className={cn("h-5 w-5", !collapsed && "mr-3")} />
        {!collapsed && (
          <div className="flex-1 text-left">
            <div className="flex items-center justify-between">
              <span className="font-medium">{item.title}</span>
              {item.badge && (
                <Badge variant="secondary" className="text-xs">
                  {item.badge}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {item.description}
            </p>
          </div>
        )}
      </Button>
    </Link>
  );

  return (
    <div className={cn(
      "flex flex-col h-full bg-background border-r transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Main Navigation */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-1">
          {!collapsed && (
            <h2 className="text-lg font-semibold text-foreground mb-4 px-2">
              Services
            </h2>
          )}
          {navigationItems.map((item) => (
            <NavItem
              key={item.href}
              item={item}
              isActive={location.pathname === item.href}
            />
          ))}
        </div>

        {/* Secondary Navigation */}
        <div className="mt-8 space-y-1">
          {!collapsed && (
            <h3 className="text-sm font-medium text-muted-foreground mb-3 px-2">
              Tools & Insights
            </h3>
          )}
          {secondaryItems.map((item) => (
            <NavItem
              key={item.href}
              item={item}
              isActive={location.pathname === item.href}
            />
          ))}
        </div>
      </div>

      {/* Mr. Happy Voice Assistant Status */}
      {!collapsed && (
        <div className="p-3 border-t">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-lg border border-blue-100">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-foreground">Mr. Happy</span>
            </div>
            <p className="text-xs text-muted-foreground">
              AI Assistant is online and ready to help
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full mt-2 text-xs"
              onClick={() => alert("Voice customization coming soon!")}
            >
              Customize Voice
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;