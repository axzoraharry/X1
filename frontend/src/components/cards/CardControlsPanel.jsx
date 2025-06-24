import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  DollarSign, 
  Shield, 
  Globe, 
  CreditCard, 
  AlertTriangle,
  Save,
  RotateCcw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Separator } from '../ui/separator';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { virtualCardService } from '../../services/virtualCardService';

const CardControlsPanel = ({ card, onUpdate }) => {
  const { toast } = useToast();
  const [controls, setControls] = useState(card.controls);
  const [isUpdating, setIsUpdating] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleControlChange = (field, value) => {
    setControls(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  };

  const handleSaveChanges = async () => {
    setIsUpdating(true);
    try {
      await virtualCardService.updateCardControls(card.id, card.user_id, controls);
      
      if (onUpdate) {
        onUpdate();
      }
      
      setHasChanges(false);
      toast({
        title: "Controls Updated",
        description: "Your card controls have been updated successfully",
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

  const handleResetChanges = () => {
    setControls(card.controls);
    setHasChanges(false);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Spending Limits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <span>Spending Limits</span>
          </CardTitle>
          <CardDescription>
            Set daily, monthly, and per-transaction limits for your card
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dailyLimit">Daily Limit</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₹</span>
                <Input
                  id="dailyLimit"
                  type="number"
                  value={controls.daily_limit_inr}
                  onChange={(e) => handleControlChange('daily_limit_inr', parseInt(e.target.value))}
                  className="pl-8"
                  min="1000"
                  max="200000"
                />
              </div>
              <p className="text-xs text-gray-500">Min: ₹1,000 | Max: ₹2,00,000</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="monthlyLimit">Monthly Limit</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₹</span>
                <Input
                  id="monthlyLimit"
                  type="number"
                  value={controls.monthly_limit_inr}
                  onChange={(e) => handleControlChange('monthly_limit_inr', parseInt(e.target.value))}
                  className="pl-8"
                  min="10000"
                  max="2400000"
                />
              </div>
              <p className="text-xs text-gray-500">Min: ₹10,000 | Max: ₹24,00,000</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="transactionLimit">Per Transaction</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₹</span>
                <Input
                  id="transactionLimit"
                  type="number"
                  value={controls.per_transaction_limit_inr}
                  onChange={(e) => handleControlChange('per_transaction_limit_inr', parseInt(e.target.value))}
                  className="pl-8"
                  min="100"
                  max="50000"
                />
              </div>
              <p className="text-xs text-gray-500">Min: ₹100 | Max: ₹50,000</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transaction Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5 text-blue-600" />
            <span>Transaction Controls</span>
          </CardTitle>
          <CardDescription>
            Enable or disable specific types of transactions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <CreditCard className="w-4 h-4 text-gray-600" />
                  <Label htmlFor="onlineTransactions">Online Transactions</Label>
                </div>
                <p className="text-sm text-gray-500">
                  Enable purchases on e-commerce websites and apps
                </p>
              </div>
              <Switch
                id="onlineTransactions"
                checked={controls.online_transactions_enabled}
                onCheckedChange={(checked) => handleControlChange('online_transactions_enabled', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <CreditCard className="w-4 h-4 text-gray-600" />
                  <Label htmlFor="atmWithdrawals">ATM Withdrawals</Label>
                </div>
                <p className="text-sm text-gray-500">
                  Allow cash withdrawals from ATMs
                </p>
              </div>
              <Switch
                id="atmWithdrawals"
                checked={controls.atm_withdrawals_enabled}
                onCheckedChange={(checked) => handleControlChange('atm_withdrawals_enabled', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Globe className="w-4 h-4 text-gray-600" />
                  <Label htmlFor="internationalTransactions">International Transactions</Label>
                </div>
                <p className="text-sm text-gray-500">
                  Enable transactions outside India (higher fees may apply)
                </p>
              </div>
              <Switch
                id="internationalTransactions"
                checked={controls.international_transactions_enabled}
                onCheckedChange={(checked) => handleControlChange('international_transactions_enabled', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security & Compliance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-purple-600" />
            <span>Security & Compliance</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">RBI Compliance Information</p>
                <ul className="text-sm space-y-1">
                  <li>• All transactions are subject to RBI PPI Master Direction limits</li>
                  <li>• Daily limits cannot exceed ₹2,00,000 for full KYC users</li>
                  <li>• International transactions require additional verification</li>
                  <li>• Suspicious activities will be automatically flagged</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      {hasChanges && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex space-x-3"
        >
          <Button
            variant="outline"
            onClick={handleResetChanges}
            disabled={isUpdating}
            className="flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset Changes</span>
          </Button>
          
          <Button
            onClick={handleSaveChanges}
            disabled={isUpdating}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{isUpdating ? 'Saving...' : 'Save Changes'}</span>
          </Button>
        </motion.div>
      )}
    </div>
  );
};

export default CardControlsPanel;