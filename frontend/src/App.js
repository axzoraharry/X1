import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import { UserProvider } from "./contexts/UserContext";
import { AnalyticsProvider } from "./contexts/AnalyticsContext";
import Header from "./components/layout/Header";
import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard";
import Travel from "./pages/Travel";
import Recharge from "./pages/Recharge";
import ShopUpdated from "./pages/ShopUpdated";
import WalletUpdated from "./pages/WalletUpdated";
import VirtualCards from "./pages/VirtualCards";
import AutomationHub from "./components/automation/AutomationHub";
import AnalyticsDashboard from "./components/analytics/AnalyticsDashboard";

const App = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isVoiceListening, setIsVoiceListening] = useState(false);

  const handleVoiceToggle = () => {
    setIsVoiceListening(!isVoiceListening);
  };

  return (
    <div className="App">
      <UserProvider>
        <AnalyticsProvider>
          <BrowserRouter>
            <div className="flex h-screen bg-background">
              {/* Sidebar */}
              <Sidebar collapsed={sidebarCollapsed} />
              
              {/* Main Content */}
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <Header 
                  onVoiceToggle={handleVoiceToggle}
                  isListening={isVoiceListening}
                />
                
                {/* Page Content */}
                <main className="flex-1 overflow-y-auto bg-gray-50/30">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/travel" element={<Travel />} />
                    <Route path="/recharge" element={<Recharge />} />
                    <Route path="/shop" element={<ShopUpdated />} />
                    <Route path="/wallet" element={<WalletUpdated />} />
                    <Route path="/virtual-cards" element={<VirtualCards />} />
                    <Route path="/automation" element={<AutomationHub userId="43f08807-ea8e-4f96-ab9b-4b529b4b7475" />} />
                    <Route path="/git" element={<div className="p-6"><h1 className="text-2xl font-bold">Git Activity Coming Soon</h1></div>} />
                    <Route path="/weather" element={<div className="p-6"><h1 className="text-2xl font-bold">Weather Details Coming Soon</h1></div>} />
                    <Route path="/analytics" element={<AnalyticsDashboard />} />
                  <Route path="/payments" element={<div className="p-6"><h1 className="text-2xl font-bold">Payment History Coming Soon</h1></div>} />
                  <Route path="/settings" element={<div className="p-6"><h1 className="text-2xl font-bold">Settings Panel Coming Soon</h1></div>} />
                </Routes>
              </main>
            </div>
          </div>
          
          {/* Toast Notifications */}
          <Toaster />
        </BrowserRouter>
        </AnalyticsProvider>
      </UserProvider>
    </div>
  );
};

export default App;