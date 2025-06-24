import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Eye, 
  EyeOff, 
  Copy, 
  Snowflake, 
  Play, 
  CreditCard,
  Shield,
  Wifi,
  Clock
} from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { virtualCardService } from '../../services/virtualCardService';

const VirtualCardDisplay = ({ 
  card, 
  showSensitiveData = false, 
  onStatusUpdate,
  className = "" 
}) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const { toast } = useToast();

  // Mock sensitive data for demo (in production, this would require re-authentication)
  const getSensitiveCardData = () => ({
    fullNumber: "4000 1234 5678 3672",
    cvv: "123"
  });

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied!",
        description: `${label} copied to clipboard`,
        duration: 2000,
      });
    } catch (err) {
      toast({
        title: "Copy failed",
        description: "Unable to copy to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleStatusToggle = async () => {
    setIsUpdating(true);
    try {
      const newStatus = card.card_status === 'active' ? 'frozen' : 'active';
      await virtualCardService.updateCardStatus(card.id, card.user_id, newStatus);
      
      if (onStatusUpdate) {
        onStatusUpdate(card.id, newStatus);
      }

      toast({
        title: "Card Updated",
        description: `Card ${newStatus === 'active' ? 'activated' : 'frozen'} successfully`,
      });
    } catch (error) {
      toast({
        title: "Update Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const cardGradients = {
    'RuPay': 'from-blue-600 via-blue-700 to-blue-800',
    'Visa': 'from-indigo-600 via-purple-600 to-purple-700',
    'Mastercard': 'from-red-500 via-red-600 to-red-700'
  };

  const gradient = cardGradients[card.network] || cardGradients['RuPay'];

  return (
    <div className={`relative w-full max-w-sm mx-auto ${className}`}>
      <motion.div
        className="relative w-full h-56 cursor-pointer"
        style={{ perspective: 1000 }}
        onClick={() => setIsFlipped(!isFlipped)}
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      >
        <motion.div
          className="absolute inset-0 w-full h-full"
          style={{ transformStyle: 'preserve-3d' }}
          animate={{ rotateY: isFlipped ? 180 : 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Front of Card */}
          <Card className={`absolute inset-0 w-full h-full bg-gradient-to-br ${gradient} text-white border-0 shadow-2xl`}>
            <CardContent className="p-6 h-full flex flex-col justify-between">
              {/* Card Header */}
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <Badge 
                    variant="secondary" 
                    className={`${virtualCardService.getCardStatusColor(card.card_status)} border-0 text-xs`}
                  >
                    {card.card_status.toUpperCase()}
                  </Badge>
                  <div className="flex items-center space-x-2">
                    <Wifi className="w-4 h-4 opacity-80" />
                    <Shield className="w-4 h-4 opacity-80" />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs opacity-80">AXZORA</div>
                  <div className="text-lg font-bold">{card.network}</div>
                </div>
              </div>

              {/* Card Number */}
              <div className="space-y-4">
                <div>
                  <div className="text-2xl font-mono tracking-wider">
                    {showSensitiveData && showDetails 
                      ? getSensitiveCardData().fullNumber 
                      : card.card_number_masked
                    }
                  </div>
                </div>

                {/* Cardholder and Expiry */}
                <div className="flex justify-between items-end">
                  <div>
                    <div className="text-xs opacity-80">CARDHOLDER</div>
                    <div className="font-semibold text-sm uppercase tracking-wide">
                      {card.card_holder_name}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs opacity-80">EXPIRES</div>
                    <div className="font-mono text-sm">
                      {virtualCardService.formatExpiryDate(card.expiry_month, card.expiry_year)}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Back of Card */}
          <Card className={`absolute inset-0 w-full h-full bg-gradient-to-br ${gradient} text-white border-0 shadow-2xl`}
                style={{ transform: 'rotateY(180deg)' }}>
            <CardContent className="p-6 h-full flex flex-col">
              {/* Magnetic Stripe */}
              <div className="bg-black h-12 w-full -mx-6 mt-4 mb-6"></div>

              {/* CVV Section */}
              <div className="bg-white bg-opacity-20 p-4 rounded space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs opacity-80">CVV</span>
                  <div className="font-mono text-lg tracking-wider">
                    {showSensitiveData && showDetails ? getSensitiveCardData().cvv : "***"}
                  </div>
                </div>
                <div className="text-xs opacity-80">
                  This 3-digit code is for online transactions
                </div>
              </div>

              {/* Balance Information */}
              <div className="mt-auto space-y-2">
                <div className="flex justify-between">
                  <span className="text-xs opacity-80">Available Balance</span>
                  <span className="font-semibold">
                    {card.current_balance_hp.toFixed(3)} HP
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs opacity-80">INR Equivalent</span>
                  <span className="font-semibold">
                    ₹{card.current_balance_inr.toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Card Controls */}
      <div className="mt-4 space-y-3">
        {/* Security Toggle */}
        {showSensitiveData && (
          <div className="flex items-center justify-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="space-x-2"
            >
              {showDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              <span>{showDetails ? 'Hide Details' : 'Show Details'}</span>
            </Button>
          </div>
        )}

        {/* Quick Actions */}
        <div className="flex space-x-2">
          {showSensitiveData && showDetails && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(getSensitiveCardData().fullNumber, 'Card number')}
                className="flex-1"
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy Number
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(getSensitiveCardData().cvv, 'CVV')}
                className="flex-1"
              >
                <Copy className="w-4 h-4 mr-1" />
                Copy CVV
              </Button>
            </>
          )}
        </div>

        {/* Status Control */}
        <div className="flex space-x-2">
          <Button
            variant={card.card_status === 'active' ? "destructive" : "default"}
            size="sm"
            onClick={handleStatusToggle}
            disabled={isUpdating}
            className="flex-1"
          >
            {card.card_status === 'active' ? (
              <>
                <Freeze className="w-4 h-4 mr-1" />
                {isUpdating ? 'Freezing...' : 'Freeze Card'}
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-1" />
                {isUpdating ? 'Activating...' : 'Activate Card'}
              </>
            )}
          </Button>
        </div>

        {/* Card Info */}
        <div className="text-center text-sm text-gray-600 space-y-1">
          <div className="flex items-center justify-center space-x-2">
            <CreditCard className="w-4 h-4" />
            <span>Virtual Debit Card</span>
          </div>
          <div className="flex items-center justify-center space-x-2 text-xs">
            <Clock className="w-3 h-3" />
            <span>Created {new Date(card.created_at).toLocaleDateString()}</span>
          </div>
          {card.last_used_at && (
            <div className="text-xs text-gray-500">
              Last used {new Date(card.last_used_at).toLocaleDateString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VirtualCardDisplay;