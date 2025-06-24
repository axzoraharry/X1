import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CreditCard, User, DollarSign, Settings } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { Alert, AlertDescription } from '../ui/alert';
import { virtualCardService } from '../../services/virtualCardService';

const CardCreationForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    card_holder_name: '',
    initial_load_amount_hp: '',
    daily_limit_inr: '25000',
    monthly_limit_inr: '100000',
    per_transaction_limit_inr: '15000',
    international_transactions_enabled: false,
    online_transactions_enabled: true,
    atm_withdrawals_enabled: true
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors = {};

    // Validate cardholder name
    const nameError = virtualCardService.validateCardholderName(formData.card_holder_name);
    if (nameError) newErrors.card_holder_name = nameError;

    // Validate load amount
    if (formData.initial_load_amount_hp) {
      const amountError = virtualCardService.validateLoadAmount(parseFloat(formData.initial_load_amount_hp));
      if (amountError) newErrors.initial_load_amount_hp = amountError;
    }

    // Validate daily limit
    const limitError = virtualCardService.validateDailyLimit(parseFloat(formData.daily_limit_inr));
    if (limitError) newErrors.daily_limit_inr = limitError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      const cardData = {
        card_holder_name: formData.card_holder_name.trim(),
        initial_load_amount_hp: parseFloat(formData.initial_load_amount_hp) || 0,
        controls: {
          daily_limit_inr: parseFloat(formData.daily_limit_inr),
          monthly_limit_inr: parseFloat(formData.monthly_limit_inr),
          per_transaction_limit_inr: parseFloat(formData.per_transaction_limit_inr),
          international_transactions_enabled: formData.international_transactions_enabled,
          online_transactions_enabled: formData.online_transactions_enabled,
          atm_withdrawals_enabled: formData.atm_withdrawals_enabled,
          allowed_merchant_categories: [
            "groceries", "fuel", "restaurants", "online_shopping", 
            "travel", "entertainment", "healthcare", "education", "utilities", "other"
          ],
          blocked_merchant_categories: []
        }
      };

      await onSubmit(cardData);
    } catch (error) {
      console.error('Card creation error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-2xl mx-auto"
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="w-5 h-5 text-blue-600" />
            <span>Create Virtual Debit Card</span>
          </CardTitle>
          <CardDescription>
            Set up your new virtual debit card with custom controls and limits
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                <User className="w-4 h-4" />
                <span>Basic Information</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cardholderName">Cardholder Name *</Label>
                  <Input
                    id="cardholderName"
                    value={formData.card_holder_name}
                    onChange={(e) => handleInputChange('card_holder_name', e.target.value)}
                    placeholder="Enter full name as per ID"
                    className={errors.card_holder_name ? 'border-red-500' : ''}
                  />
                  {errors.card_holder_name && (
                    <p className="text-sm text-red-600">{errors.card_holder_name}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="initialAmount">Initial Load Amount (HP)</Label>
                  <Input
                    id="initialAmount"
                    type="number"
                    step="0.001"
                    min="0"
                    max="100"
                    value={formData.initial_load_amount_hp}
                    onChange={(e) => handleInputChange('initial_load_amount_hp', e.target.value)}
                    placeholder="0.000"
                    className={errors.initial_load_amount_hp ? 'border-red-500' : ''}
                  />
                  {errors.initial_load_amount_hp && (
                    <p className="text-sm text-red-600">{errors.initial_load_amount_hp}</p>
                  )}
                  <p className="text-xs text-gray-500">
                    Optional: Load Happy Paisa onto your card
                  </p>
                </div>
              </div>
            </div>

            {/* Spending Limits */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                <DollarSign className="w-4 h-4" />
                <span>Spending Limits</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dailyLimit">Daily Limit (₹)</Label>
                  <Select 
                    value={formData.daily_limit_inr} 
                    onValueChange={(value) => handleInputChange('daily_limit_inr', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10000">₹10,000</SelectItem>
                      <SelectItem value="25000">₹25,000</SelectItem>
                      <SelectItem value="50000">₹50,000</SelectItem>
                      <SelectItem value="100000">₹1,00,000</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.daily_limit_inr && (
                    <p className="text-sm text-red-600">{errors.daily_limit_inr}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="monthlyLimit">Monthly Limit (₹)</Label>
                  <Select 
                    value={formData.monthly_limit_inr} 
                    onValueChange={(value) => handleInputChange('monthly_limit_inr', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="50000">₹50,000</SelectItem>
                      <SelectItem value="100000">₹1,00,000</SelectItem>
                      <SelectItem value="200000">₹2,00,000</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="transactionLimit">Per Transaction (₹)</Label>
                  <Select 
                    value={formData.per_transaction_limit_inr} 
                    onValueChange={(value) => handleInputChange('per_transaction_limit_inr', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5000">₹5,000</SelectItem>
                      <SelectItem value="15000">₹15,000</SelectItem>
                      <SelectItem value="25000">₹25,000</SelectItem>
                      <SelectItem value="50000">₹50,000</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Transaction Controls */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                <Settings className="w-4 h-4" />
                <span>Transaction Controls</span>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="onlineTransactions"
                    checked={formData.online_transactions_enabled}
                    onCheckedChange={(checked) => handleInputChange('online_transactions_enabled', checked)}
                  />
                  <Label htmlFor="onlineTransactions" className="font-normal">
                    Enable Online Transactions
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="atmWithdrawals"
                    checked={formData.atm_withdrawals_enabled}
                    onCheckedChange={(checked) => handleInputChange('atm_withdrawals_enabled', checked)}
                  />
                  <Label htmlFor="atmWithdrawals" className="font-normal">
                    Enable ATM Withdrawals
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="internationalTransactions"
                    checked={formData.international_transactions_enabled}
                    onCheckedChange={(checked) => handleInputChange('international_transactions_enabled', checked)}
                  />
                  <Label htmlFor="internationalTransactions" className="font-normal">
                    Enable International Transactions
                  </Label>
                </div>
              </div>
            </div>

            {/* Compliance Notice */}
            <Alert>
              <AlertDescription className="text-sm">
                <strong>Important:</strong> Your card will be issued on the RuPay network with full regulatory compliance. 
                All transactions are subject to RBI guidelines and your Happy Paisa wallet balance.
              </AlertDescription>
            </Alert>

            {/* Actions */}
            <div className="flex space-x-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                className="flex-1"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="flex-1"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Creating Card...' : 'Create Virtual Card'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default CardCreationForm;