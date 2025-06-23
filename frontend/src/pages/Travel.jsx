import React, { useState } from 'react';
import { Plane, Hotel, Bus, Calendar, MapPin, Users, Search } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockFlights, mockHotels } from '../data/mockData';

const Travel = () => {
  const [searchData, setSearchData] = useState({
    from: 'NAG',
    to: 'GOA',
    departure: '2025-07-10',
    return: '2025-07-15',
    passengers: 2,
    class: 'economy'
  });

  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setSearchResults(mockFlights);
      setLoading(false);
    }, 1500);
  };

  const FlightCard = ({ flight }) => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Plane className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold">{flight.airline}</h3>
              <p className="text-sm text-muted-foreground">{flight.flight_number}</p>
            </div>
          </div>
          <Badge variant="secondary">{flight.stops === 0 ? 'Direct' : `${flight.stops} Stop(s)`}</Badge>
        </div>
        
        <div className="flex justify-between items-center mb-4">
          <div className="text-center">
            <p className="text-lg font-bold">{flight.departure_time}</p>
            <p className="text-sm text-muted-foreground">{flight.origin}</p>
          </div>
          <div className="flex-1 px-4">
            <div className="border-t-2 border-dashed border-gray-300 relative">
              <Plane className="h-4 w-4 text-gray-400 absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 rotate-90" />
            </div>
            <p className="text-xs text-center text-muted-foreground mt-1">{flight.duration}</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold">{flight.arrival_time}</p>
            <p className="text-sm text-muted-foreground">{flight.destination}</p>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <p className="text-2xl font-bold text-green-600">₹{flight.price_inr.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground">{flight.price_hp} HP</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">{flight.available_seats} seats left</p>
            <Button className="mt-2">Book Now</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const HotelCard = ({ hotel }) => (
    <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
      <CardContent className="p-4">
        <div className="flex space-x-4">
          <img 
            src={hotel.images[0]} 
            alt={hotel.name}
            className="w-24 h-24 object-cover rounded-lg"
          />
          <div className="flex-1">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold">{hotel.name}</h3>
              <div className="flex items-center space-x-1">
                <span className="text-sm font-bold">{hotel.rating}</span>
                <span className="text-yellow-400">★</span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mb-2">{hotel.location}</p>
            <div className="flex flex-wrap gap-1 mb-3">
              {hotel.amenities.slice(0, 3).map((amenity, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {amenity}
                </Badge>
              ))}
            </div>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-lg font-bold text-green-600">₹{hotel.price_per_night_inr.toLocaleString()}/night</p>
                <p className="text-sm text-muted-foreground">{hotel.price_per_night_hp} HP/night</p>
              </div>
              <Button>Book Hotel</Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Travel Booking</h1>
          <p className="text-muted-foreground">Find and book flights, hotels, and buses</p>
        </div>
        <div className="flex items-center space-x-2 bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-2 rounded-lg">
          <Plane className="h-5 w-5 text-blue-600" />
          <span className="text-sm font-medium">Powered by Mr. Happy AI</span>
        </div>
      </div>

      <Tabs defaultValue="flights" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="flights" className="flex items-center space-x-2">
            <Plane className="h-4 w-4" />
            <span>Flights</span>
          </TabsTrigger>
          <TabsTrigger value="hotels" className="flex items-center space-x-2">
            <Hotel className="h-4 w-4" />
            <span>Hotels</span>
          </TabsTrigger>
          <TabsTrigger value="buses" className="flex items-center space-x-2">
            <Bus className="h-4 w-4" />
            <span>Buses</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="flights" className="space-y-6">
          {/* Flight Search Form */}
          <Card>
            <CardHeader>
              <CardTitle>Search Flights</CardTitle>
              <CardDescription>Find the best flights for your journey</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">From</label>
                  <Input 
                    value={searchData.from} 
                    onChange={(e) => setSearchData({...searchData, from: e.target.value})}
                    placeholder="NAG"
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">To</label>
                  <Input 
                    value={searchData.to} 
                    onChange={(e) => setSearchData({...searchData, to: e.target.value})}
                    placeholder="GOA"
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Departure</label>
                  <Input 
                    type="date"
                    value={searchData.departure} 
                    onChange={(e) => setSearchData({...searchData, departure: e.target.value})}
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Return</label>
                  <Input 
                    type="date"
                    value={searchData.return} 
                    onChange={(e) => setSearchData({...searchData, return: e.target.value})}
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Passengers</label>
                  <Select value={searchData.passengers.toString()} onValueChange={(value) => setSearchData({...searchData, passengers: parseInt(value)})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 Passenger</SelectItem>
                      <SelectItem value="2">2 Passengers</SelectItem>
                      <SelectItem value="3">3 Passengers</SelectItem>
                      <SelectItem value="4">4 Passengers</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Class</label>
                  <Button 
                    onClick={handleSearch} 
                    className="w-full" 
                    disabled={loading}
                  >
                    {loading ? 'Searching...' : <><Search className="h-4 w-4 mr-2" />Search</>}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Flight Results */}
          {searchResults.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Available Flights</h2>
              <div className="grid gap-4">
                {searchResults.map((flight) => (
                  <FlightCard key={flight.id} flight={flight} />
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="hotels" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Find Hotels</CardTitle>
              <CardDescription>Discover comfortable stays for your trip</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="md:col-span-2">
                  <label className="text-sm font-medium">Destination</label>
                  <Input placeholder="Goa, India" />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Check-in</label>
                  <Input type="date" />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Check-out</label>
                  <Input type="date" />
                </div>
                <div className="md:col-span-1">
                  <label className="text-sm font-medium">Guests</label>
                  <Button className="w-full">
                    <Search className="h-4 w-4 mr-2" />
                    Search Hotels
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Popular Hotels in Goa</h2>
            <div className="grid gap-4">
              {mockHotels.map((hotel) => (
                <HotelCard key={hotel.id} hotel={hotel} />
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="buses" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Bus Booking</CardTitle>
              <CardDescription>Comfortable bus travel across India</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Bus className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Bus Booking Coming Soon</h3>
                <p className="text-muted-foreground">
                  We're working on integrating bus booking services. Stay tuned!
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Travel;