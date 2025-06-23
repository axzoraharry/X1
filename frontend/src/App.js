import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import { UserProvider } from "./contexts/UserContext";
import Header from "./components/layout/Header";
import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./pages/Dashboard";
import Travel from "./pages/Travel";
import Recharge from "./pages/Recharge";
import ShopUpdated from "./pages/ShopUpdated";
import WalletUpdated from "./pages/WalletUpdated";

const App = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isVoiceListening, setIsVoiceListening] = useState(false);

  const handleVoiceToggle = () => {
    setIsVoiceListening(!isVoiceListening);
  };

  return (
    <div className="App">
      <UserProvider>
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
                  <Route path="/git" element={<div className="p-6"><h1 className="text-2xl font-bold">Git Activity Coming Soon</h1></div>} />
                  <Route path="/weather" element={<div className="p-6"><h1 className="text-2xl font-bold">Weather Details Coming Soon</h1></div>} />
                  <Route path="/analytics" element={<div className="p-6"><h1 className="text-2xl font-bold">Analytics Dashboard Coming Soon</h1></div>} />
                  <Route path="/payments" element={<div className="p-6"><h1 className="text-2xl font-bold">Payment History Coming Soon</h1></div>} />
                  <Route path="/settings" element={<div className="p-6"><h1 className="text-2xl font-bold">Settings Panel Coming Soon</h1></div>} />
                </Routes>
              </main>
            </div>
          </div>
          
          {/* Toast Notifications */}
          <Toaster />
        </BrowserRouter>
      </UserProvider>
    </div>
  );
};

export default App;