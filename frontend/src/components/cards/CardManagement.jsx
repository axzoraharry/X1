import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Settings, 
  BarChart3, 
  Shield, 
  CreditCard,
  Loader2,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import { useUser } from '../../contexts/UserContext';
import { virtualCardService } from '../../services/virtualCardService';
import VirtualCardDisplay from './VirtualCardDisplay';
import CardCreationForm from './CardCreationForm';
import CardControlsPanel from './CardControlsPanel';
import CardTransactionHistory from './CardTransactionHistory';
import CardAnalytics from './CardAnalytics';

const CardManagement = () => {
  const { user } = useUser();
  const { toast } = useToast();
  
  const [cards, setCards] = useState([]);
  const [selectedCard, setSelectedCard] = useState(null);
  const [kycStatus, setKycStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user?.id) {
      loadUserData();
    }
  }, [user]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      
      // Load user cards and KYC status in parallel
      const [userCards, userKyc] = await Promise.all([
        virtualCardService.getUserCards(user.id),
        virtualCardService.getKycStatus(user.id)
      ]);
      
      setCards(userCards);
      setKycStatus(userKyc);
      
      if (userCards.length > 0) {
        setSelectedCard(userCards[0]);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      toast({
        title: "Loading Error",
        description: "Failed to load card data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCard = async (cardData) => {
    try {
      const newCard = await virtualCardService.createVirtualCard({
        ...cardData,
        user_id: user.id
      });
      
      setCards(prev => [...prev, newCard]);
      setSelectedCard(newCard);
      setShowCreateForm(false);
      
      toast({
        title: "Card Created!",
        description: "Your virtual debit card has been created successfully",
      });
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleCardStatusUpdate = (cardId, newStatus) => {
    setCards(prev => prev.map(card => 
      card.id === cardId ? { ...card, card_status: newStatus } : card
    ));
    
    if (selectedCard?.id === cardId) {
      setSelectedCard(prev => ({ ...prev, card_status: newStatus }));
    }
  };

  const handleKycComplete = async () => {
    try {
      // Create demo KYC for user
      await virtualCardService.createDemoKyc(user.id, user.name);
      
      // Reload KYC status
      const updatedKyc = await virtualCardService.getKycStatus(user.id);
      setKycStatus(updatedKyc);
      
      toast({
        title: "KYC Completed!",
        description: "You can now create virtual debit cards",
      });
    } catch (error) {
      toast({
        title: "KYC Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const renderKycStatus = () => {
    if (!kycStatus) {
      return (
        <Alert className="border-yellow-200 bg-yellow-50">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            <div className="space-y-3">
              <div>
                <strong>KYC Verification Required</strong>
                <p className="text-sm mt-1">
                  Complete KYC verification to create virtual debit cards and access higher transaction limits.
                </p>
              </div>
              <Button onClick={handleKycComplete} size="sm" className="bg-yellow-600 hover:bg-yellow-700">
                Complete KYC (Demo)
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      );
    }

    const statusConfig = {
      'approved': {
        icon: CheckCircle,
        color: 'text-green-600',
        bgColor: 'bg-green-50 border-green-200',
        message: 'KYC verification completed successfully'
      },
      'under_review': {
        icon: Loader2,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50 border-yellow-200',
        message: 'KYC verification is under review'
      },
      'rejected': {
        icon: XCircle,
        color: 'text-red-600',
        bgColor: 'bg-red-50 border-red-200',
        message: 'KYC verification was rejected'
      }
    };

    const config = statusConfig[kycStatus.kyc_status] || statusConfig['under_review'];
    const Icon = config.icon;

    return (
      <Alert className={config.bgColor}>
        <Icon className={`h-4 w-4 ${config.color} ${kycStatus.kyc_status === 'under_review' ? 'animate-spin' : ''}`} />
        <AlertDescription className={config.color}>
          <strong>KYC Status: {kycStatus.kyc_status.replace('_', ' ').toUpperCase()}</strong>
          <p className="text-sm mt-1">{config.message}</p>
        </AlertDescription>
      </Alert>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading your cards...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Virtual Debit Cards</h1>
          <p className="text-gray-600 mt-1">
            Manage your Happy Paisa virtual debit cards
          </p>
        </div>
        
        {kycStatus?.kyc_status === 'approved' && (
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="space-x-2"
            disabled={cards.length >= 1} // Limit to 1 card in demo
          >
            <Plus className="w-4 h-4" />
            <span>Create Card</span>
          </Button>
        )}
      </div>

      {/* KYC Status */}
      {renderKycStatus()}

      {/* Card Creation Form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <CardCreationForm
              onSubmit={handleCreateCard}
              onCancel={() => setShowCreateForm(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cards Overview */}
      {cards.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Virtual Cards Yet
            </h3>
            <p className="text-gray-600 mb-4">
              {kycStatus?.kyc_status === 'approved' 
                ? "Create your first virtual debit card to start spending Happy Paisa everywhere"
                : "Complete KYC verification to create your first virtual debit card"
              }
            </p>
            {kycStatus?.kyc_status === 'approved' && (
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Card
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Card Display */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CreditCard className="w-5 h-5" />
                  <span>Your Virtual Card</span>
                </CardTitle>
                <CardDescription>
                  Tap to flip and view details
                </CardDescription>
              </CardHeader>
              <CardContent>
                <VirtualCardDisplay
                  card={selectedCard}
                  showSensitiveData={true}
                  onStatusUpdate={handleCardStatusUpdate}
                />
              </CardContent>
            </Card>
          </div>

          {/* Card Management Tabs */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="transactions">Transactions</TabsTrigger>
                <TabsTrigger value="controls">Controls</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm font-medium">Card Status</span>
                      </div>
                      <Badge className={`mt-2 ${virtualCardService.getCardStatusColor(selectedCard?.card_status)}`}>
                        {selectedCard?.card_status?.toUpperCase()}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-4">
                      <div className="text-sm font-medium text-gray-600">Available Balance</div>
                      <div className="text-2xl font-bold mt-1">
                        {selectedCard?.current_balance_hp?.toFixed(3)} HP
                      </div>
                      <div className="text-sm text-gray-500">
                        ₹{selectedCard?.current_balance_inr?.toLocaleString()}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <Button variant="outline" onClick={() => setActiveTab('controls')}>
                        <Settings className="w-4 h-4 mr-2" />
                        Manage Controls
                      </Button>
                      <Button variant="outline" onClick={() => setActiveTab('analytics')}>
                        <BarChart3 className="w-4 h-4 mr-2" />
                        View Analytics
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="transactions">
                {selectedCard && (
                  <CardTransactionHistory cardId={selectedCard.id} userId={user.id} />
                )}
              </TabsContent>

              <TabsContent value="controls">
                {selectedCard && (
                  <CardControlsPanel 
                    card={selectedCard} 
                    onUpdate={() => loadUserData()} 
                  />
                )}
              </TabsContent>

              <TabsContent value="analytics">
                {selectedCard && (
                  <CardAnalytics cardId={selectedCard.id} userId={user.id} />
                )}
              </TabsContent>
            </Tabs>
          </div>
        </div>
      )}
    </div>
  );
};

export default CardManagement;