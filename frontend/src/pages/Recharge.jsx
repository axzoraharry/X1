import React, { useState } from 'react';
import { Smartphone, Tv, Zap, Wifi, Phone, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockRechargePlans } from '../data/mockData';

const Recharge = () => {
  const [selectedOperator, setSelectedOperator] = useState('jio');
  const [mobileNumber, setMobileNumber] = useState('');
  const [selectedPlan, setSelectedPlan] = useState(null);

  const handleRecharge = (plan) => {
    if (!mobileNumber) {
      alert('Please enter mobile number');
      return;
    }
    alert(`Recharging ${mobileNumber} with ₹${plan.amount} plan using Happy Paisa!`);
  };

  const PlanCard = ({ plan, isSelected, onSelect }) => (
    <Card 
      className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
      }`}
      onClick={() => onSelect(plan)}
    >
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-lg font-bold text-green-600">₹{plan.amount}</h3>
            <p className="text-sm text-muted-foreground">{plan.amount_hp} HP</p>
          </div>
          <Badge variant={plan.description === 'Popular Plan' ? 'default' : 'secondary'}>
            {plan.description}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Validity:</span>
            <span className="font-medium">{plan.validity}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Data:</span>
            <span className="font-medium">{plan.data}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Calls:</span>
            <span className="font-medium">{plan.calls}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>SMS:</span>
            <span className="font-medium">{plan.sms}</span>
          </div>
        </div>

        <Button 
          className="w-full mt-4" 
          variant={isSelected ? 'default' : 'outline'}
          onClick={(e) => {
            e.stopPropagation();
            handleRecharge(plan);
          }}
        >
          {isSelected ? 'Recharge Now' : 'Select Plan'}
        </Button>
      </CardContent>
    </Card>
  );

  const ServiceCard = ({ icon: Icon, title, description, badge, onClick }) => (
    <Card className="cursor-pointer hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1" onClick={onClick}>
      <CardContent className="p-6 text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="h-8 w-8 text-blue-600" />
        </div>
        <h3 className="font-semibold mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground mb-3">{description}</p>
        {badge && <Badge variant="secondary">{badge}</Badge>}
      </CardContent>
    </Card>
  );

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Recharge & Bill Payment</h1>
          <p className="text-muted-foreground">Quick recharges and bill payments with Happy Paisa</p>
        </div>
        <div className="flex items-center space-x-2 bg-gradient-to-r from-green-50 to-blue-50 px-4 py-2 rounded-lg">
          <Smartphone className="h-5 w-5 text-green-600" />
          <span className="text-sm font-medium">Instant Recharge</span>
        </div>
      </div>

      <Tabs defaultValue="mobile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="mobile" className="flex items-center space-x-2">
            <Smartphone className="h-4 w-4" />
            <span>Mobile</span>
          </TabsTrigger>
          <TabsTrigger value="dth" className="flex items-center space-x-2">
            <Tv className="h-4 w-4" />
            <span>DTH/TV</span>
          </TabsTrigger>
          <TabsTrigger value="utilities" className="flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Utilities</span>
          </TabsTrigger>
          <TabsTrigger value="broadband" className="flex items-center space-x-2">
            <Wifi className="h-4 w-4" />
            <span>Broadband</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mobile" className="space-y-6">
          {/* Mobile Recharge Form */}
          <Card>
            <CardHeader>
              <CardTitle>Mobile Recharge</CardTitle>
              <CardDescription>Recharge your mobile with Happy Paisa</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium">Mobile Number</label>
                  <Input
                    type="tel"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    placeholder="Enter 10-digit mobile number"
                    maxLength="10"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Operator</label>
                  <Select value={selectedOperator} onValueChange={setSelectedOperator}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="jio">Jio</SelectItem>
                      <SelectItem value="airtel">Airtel</SelectItem>
                      <SelectItem value="vi">Vi (Vodafone Idea)</SelectItem>
                      <SelectItem value="bsnl">BSNL</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button 
                    className="w-full"
                    onClick={() => mobileNumber && alert(`Detected operator: ${selectedOperator.toUpperCase()}`)}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Detect Operator
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recharge Plans */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Available Plans - {selectedOperator.toUpperCase()}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mockRechargePlans[selectedOperator]?.map((plan) => (
                <PlanCard
                  key={plan.id}
                  plan={plan}
                  isSelected={selectedPlan?.id === plan.id}
                  onSelect={setSelectedPlan}
                />
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="dth" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ServiceCard
              icon={Tv}
              title="Tata Sky"
              description="DTH recharge and channel packages"
              onClick={() => alert('Tata Sky recharge coming soon!')}
            />
            <ServiceCard
              icon={Tv}
              title="Dish TV"
              description="Quick DTH recharge with Happy Paisa"
              onClick={() => alert('Dish TV recharge coming soon!')}
            />
            <ServiceCard
              icon={Tv}
              title="Airtel Digital TV"
              description="Digital TV recharge and plans"
              onClick={() => alert('Airtel Digital TV recharge coming soon!')}
            />
            <ServiceCard
              icon={Tv}
              title="Sun Direct"
              description="South India's leading DTH service"
              onClick={() => alert('Sun Direct recharge coming soon!')}
            />
            <ServiceCard
              icon={Tv}
              title="Videocon D2H"
              description="Digital TV recharge solutions"
              onClick={() => alert('Videocon D2H recharge coming soon!')}
            />
            <ServiceCard
              icon={Tv}
              title="DD Free Dish"
              description="Free-to-air DTH services"
              badge="Free"
              onClick={() => alert('DD Free Dish information coming soon!')}
            />
          </div>
        </TabsContent>

        <TabsContent value="utilities" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ServiceCard
              icon={Zap}
              title="Electricity Bill"
              description="Pay electricity bills across India"
              onClick={() => alert('Electricity bill payment coming soon!')}
            />
            <ServiceCard
              icon={Zap}
              title="Gas Bill"
              description="LPG and PNG bill payments"
              onClick={() => alert('Gas bill payment coming soon!')}
            />
            <ServiceCard
              icon={Phone}
              title="Landline"
              description="BSNL, Airtel landline bill payments"
              onClick={() => alert('Landline bill payment coming soon!')}
            />
            <ServiceCard
              icon={Zap}
              title="Water Bill"
              description="Municipal water bill payments"
              onClick={() => alert('Water bill payment coming soon!')}
            />
            <ServiceCard
              icon={Zap}
              title="Piped Gas"
              description="PNG bill payments made easy"
              onClick={() => alert('Piped gas bill payment coming soon!')}
            />
            <ServiceCard
              icon={Zap}
              title="Metro Card"
              description="Recharge metro cards"
              badge="New"
              onClick={() => alert('Metro card recharge coming soon!')}
            />
          </div>
        </TabsContent>

        <TabsContent value="broadband" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ServiceCard
              icon={Wifi}
              title="JioFiber"
              description="High-speed broadband bill payments"
              onClick={() => alert('JioFiber bill payment coming soon!')}
            />
            <ServiceCard
              icon={Wifi}
              title="Airtel Xstream"
              description="Broadband and fiber bill payments"
              onClick={() => alert('Airtel Xstream bill payment coming soon!')}
            />
            <ServiceCard
              icon={Wifi}
              title="BSNL Broadband"
              description="Government broadband services"
              onClick={() => alert('BSNL broadband bill payment coming soon!')}
            />
            <ServiceCard
              icon={Wifi}
              title="ACT Fibernet"
              description="Local broadband service provider"
              onClick={() => alert('ACT Fibernet bill payment coming soon!')}
            />
            <ServiceCard
              icon={Wifi}
              title="Hathway"
              description="Cable and broadband services"
              onClick={() => alert('Hathway bill payment coming soon!')}
            />
            <ServiceCard
              icon={Wifi}
              title="Tikona"
              description="Wireless broadband services"
              onClick={() => alert('Tikona bill payment coming soon!')}
            />
          </div>
        </TabsContent>
      </Tabs>

      {/* Recent Recharges */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Recharges</CardTitle>
          <CardDescription>Your recent recharge history</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Smartphone className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-sm">Mobile Recharge - Jio</p>
                  <p className="text-xs text-muted-foreground">9876543210 • Yesterday</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">₹299</p>
                <Badge variant="default" className="text-xs">Success</Badge>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Tv className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-sm">DTH Recharge - Tata Sky</p>
                  <p className="text-xs text-muted-foreground">Account: 123456789 • 2 days ago</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">₹399</p>
                <Badge variant="default" className="text-xs">Success</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Recharge;