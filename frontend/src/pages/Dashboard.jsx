import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Sparkles } from 'lucide-react';
import DashboardWidgets from '../components/dashboard/DashboardWidgets';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const Dashboard = () => {
  const [isListening, setIsListening] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [aiResponse, setAiResponse] = useState('');

  const handleVoiceToggle = () => {
    setIsListening(!isListening);
    
    if (!isListening) {
      // Simulate voice recognition
      setVoiceText('Listening...');
      setTimeout(() => {
        setVoiceText('Hey Mr. Happy, show me my wallet balance');
        setTimeout(() => {
          setAiResponse('Your Happy Paisa balance is 5.25 HP, equivalent to ₹5,250. Would you like me to show you recent transactions?');
          setIsListening(false);
        }, 2000);
      }, 1000);
    } else {
      setVoiceText('');
      setAiResponse('');
    }
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* AI Voice Interaction Section */}
      <Card className="border-2 border-gradient-to-r from-blue-500 to-purple-500 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <span>AI Voice Assistant</span>
          </CardTitle>
          <CardDescription>
            Click the microphone to start talking with Mr. Happy
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center space-x-4">
            <Button
              size="lg"
              onClick={handleVoiceToggle}
              className={`h-16 w-16 rounded-full transition-all duration-300 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-200' 
                  : 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-200'
              }`}
            >
              {isListening ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
            </Button>
            <div className="flex-1 max-w-md">
              {voiceText && (
                <div className="bg-white p-3 rounded-lg border shadow-sm mb-2">
                  <p className="text-sm text-gray-700">
                    <strong>You:</strong> {voiceText}
                  </p>
                </div>
              )}
              {aiResponse && (
                <div className="bg-gradient-to-r from-blue-100 to-purple-100 p-3 rounded-lg border shadow-sm">
                  <p className="text-sm text-gray-800">
                    <strong>Mr. Happy:</strong> {aiResponse}
                  </p>
                </div>
              )}
              {!voiceText && !aiResponse && (
                <div className="text-center text-muted-foreground">
                  <p className="text-sm">Ready to listen. Click the microphone to start.</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dashboard Widgets */}
      <DashboardWidgets />
    </div>
  );
};

export default Dashboard;