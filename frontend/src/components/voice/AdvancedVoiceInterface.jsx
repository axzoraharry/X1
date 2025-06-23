import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  MicOff, 
  Send, 
  Sparkles, 
  Volume2, 
  Settings,
  MessageCircle,
  Zap,
  Loader2,
  Bot,
  User
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { useUser } from '../../contexts/UserContext';
import { useApi, useApiMutation } from '../../hooks/useApi';
import { voiceService } from '../../services/voiceService';
import { useToast } from '../../hooks/use-toast';

const AdvancedVoiceInterface = ({ isOpen = true, onClose }) => {
  const { user } = useUser();
  const { toast } = useToast();
  const [message, setMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState([]);
  const messagesEndRef = useRef(null);

  // Fetch voice status
  const { data: voiceStatus } = useApi(
    () => voiceService.getVoiceStatus(),
    []
  );

  // Fetch quick responses
  const { data: quickResponsesData } = useApi(
    () => voiceService.getQuickResponses(),
    []
  );

  // Fetch conversation history
  const { data: historyData, refetch: refetchHistory } = useApi(
    () => user ? voiceService.getConversationHistory(user.id, 20) : Promise.resolve({ conversation_history: [] }),
    [user?.id]
  );

  const { mutate: sendMessage, loading: sendingMessage } = useApiMutation();

  useEffect(() => {
    if (historyData?.conversation_history) {
      const formattedHistory = historyData.conversation_history.map(item => [
        { type: 'user', content: item.user_input, timestamp: item.timestamp },
        { type: 'assistant', content: item.bot_response, timestamp: item.timestamp, intent: item.intent }
      ]).flat();
      setConversation(formattedHistory);
    }
  }, [historyData]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const handleSendMessage = async () => {
    if (!message.trim() || !user) return;

    const userMessage = { type: 'user', content: message, timestamp: new Date().toISOString() };
    setConversation(prev => [...prev, userMessage]);
    
    const currentMessage = message;
    setMessage('');

    try {
      const response = await sendMessage(() => 
        voiceService.chatWithMrHappy(currentMessage, user.id)
      );

      const assistantMessage = {
        type: 'assistant',
        content: response.text_response,
        timestamp: new Date().toISOString(),
        intent: response.intent_data?.intent,
        actions: response.actions || [],
        conversationId: response.conversation_id
      };

      setConversation(prev => [...prev, assistantMessage]);

      // Simulate TTS if available
      if (response.text_response && 'speechSynthesis' in window) {
        speakText(response.text_response);
      }

      // Show actions as toast if available
      if (response.actions && response.actions.length > 0) {
        toast({
          title: "Mr. Happy suggests:",
          description: `Actions available: ${response.actions.join(', ')}`
        });
      }

      // Refresh conversation history
      refetchHistory();

    } catch (error) {
      toast({
        title: "Voice Error",
        description: error.message,
        variant: "destructive"
      });

      const errorMessage = {
        type: 'assistant',
        content: "I'm having trouble processing that right now. Could you please try again?",
        timestamp: new Date().toISOString(),
        isError: true
      };
      setConversation(prev => [...prev, errorMessage]);
    }
  };

  const handleQuickResponse = async (quickResponse) => {
    if (!user) return;

    const userMessage = { 
      type: 'user', 
      content: quickResponse.text, 
      timestamp: new Date().toISOString(),
      isQuick: true 
    };
    setConversation(prev => [...prev, userMessage]);

    try {
      const response = await sendMessage(() =>
        voiceService.processQuickCommand(user.id, quickResponse.action)
      );

      const assistantMessage = {
        type: 'assistant',
        content: response.text_response,
        timestamp: new Date().toISOString(),
        intent: response.intent_data?.intent,
        actions: response.actions || []
      };

      setConversation(prev => [...prev, assistantMessage]);

      if (response.text_response && 'speechSynthesis' in window) {
        speakText(response.text_response);
      }

      refetchHistory();

    } catch (error) {
      toast({
        title: "Quick Command Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      setIsSpeaking(true);
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      speechSynthesis.speak(utterance);
    }
  };

  const startListening = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
        toast({
          title: "Listening...",
          description: "Speak now, I'm listening!"
        });
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
        setIsListening(false);
      };
      
      recognition.onerror = (event) => {
        setIsListening(false);
        toast({
          title: "Speech Recognition Error",
          description: "Could not recognize speech. Please try typing instead.",
          variant: "destructive"
        });
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.start();
    } else {
      toast({
        title: "Speech Not Supported",
        description: "Speech recognition is not supported in your browser.",
        variant: "destructive"
      });
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble = ({ message }) => (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
        <div className={`flex items-start space-x-2 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            message.type === 'user' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
          }`}>
            {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </div>
          <div className={`rounded-lg p-3 ${
            message.type === 'user' 
              ? 'bg-blue-500 text-white' 
              : message.isError
                ? 'bg-red-100 border border-red-200 text-red-800'
                : 'bg-white border border-gray-200 text-gray-800'
          }`}>
            <p className="text-sm">{message.content}</p>
            {message.intent && (
              <Badge variant="secondary" className="mt-2 text-xs">
                {message.intent}
              </Badge>
            )}
            {message.actions && message.actions.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {message.actions.slice(0, 3).map((action, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {action}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
        <p className={`text-xs text-gray-500 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <Card className="fixed bottom-4 right-4 w-96 h-[600px] shadow-2xl border-2 border-gradient-to-r from-blue-500 to-purple-500 z-50">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5" />
            <CardTitle className="text-lg">Mr. Happy 2.0</CardTitle>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-xs">
              {voiceStatus?.status || 'Loading...'}
            </Badge>
            <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white/20">
              ×
            </Button>
          </div>
        </div>
        <CardDescription className="text-blue-100">
          Advanced AI assistant with voice capabilities
        </CardDescription>
      </CardHeader>

      <CardContent className="p-0 flex flex-col h-[500px]">
        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          {conversation.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-600 mb-2">Hello! I'm Mr. Happy 2.0</h3>
              <p className="text-sm text-gray-500 mb-4">
                I'm your advanced AI assistant for the Axzora ecosystem. I can help with your wallet, travel, recharges, shopping, and more!
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {quickResponsesData?.quick_responses?.slice(0, 3).map((response, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickResponse(response)}
                    className="text-xs"
                  >
                    {response.text}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {conversation.map((msg, index) => (
                <MessageBubble key={index} message={msg} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
          
          {sendingMessage && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 rounded-lg p-3 flex items-center space-x-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-gray-600">Mr. Happy is thinking...</span>
              </div>
            </div>
          )}
        </ScrollArea>

        {/* Quick Responses */}
        {quickResponsesData?.quick_responses && conversation.length > 0 && (
          <div className="px-4 py-2 border-t bg-gray-50">
            <p className="text-xs text-gray-600 mb-2">Quick responses:</p>
            <div className="flex flex-wrap gap-1">
              {quickResponsesData.quick_responses.slice(0, 4).map((response, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickResponse(response)}
                  className="text-xs h-6"
                  disabled={sendingMessage}
                >
                  {response.text}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t bg-white">
          <div className="flex items-center space-x-2">
            <div className="flex-1 relative">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message or use voice..."
                disabled={sendingMessage}
                className="pr-12"
              />
            </div>
            <div className="flex items-center space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={isListening ? () => setIsListening(false) : startListening}
                disabled={sendingMessage}
                className={isListening ? 'bg-red-500 text-white animate-pulse' : ''}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </Button>
              
              {isSpeaking && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={stopSpeaking}
                  className="bg-green-500 text-white"
                >
                  <Volume2 className="h-4 w-4" />
                </Button>
              )}
              
              <Button
                onClick={handleSendMessage}
                disabled={!message.trim() || sendingMessage}
                size="sm"
              >
                {sendingMessage ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${voiceStatus?.status === 'online' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span className="text-xs text-gray-500">
                {voiceStatus?.message || 'Connecting...'}
              </span>
            </div>
            <span className="text-xs text-gray-400">
              Press Enter to send
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AdvancedVoiceInterface;