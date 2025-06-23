import React, { useState } from 'react';
import { ShoppingCart, Star, Heart, Search, Filter, Grid, List, Plus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { mockProducts } from '../data/mockData';

const Shop = () => {
  const [cartItems, setCartItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('popular');

  const addToCart = (product) => {
    const existingItem = cartItems.find(item => item.id === product.id);
    if (existingItem) {
      setCartItems(cartItems.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCartItems([...cartItems, { ...product, quantity: 1 }]);
    }
    alert(`${product.name} added to cart!`);
  };

  const getCartCount = () => {
    return cartItems.reduce((total, item) => total + item.quantity, 0);
  };

  const getCartTotal = () => {
    return cartItems.reduce((total, item) => total + (item.price_hp * item.quantity), 0);
  };

  const ProductCard = ({ product, viewMode }) => {
    const discount = Math.round(((product.original_price_inr - product.price_inr) / product.original_price_inr) * 100);
    
    if (viewMode === 'list') {
      return (
        <Card className="hover:shadow-lg transition-all duration-300">
          <CardContent className="p-4">
            <div className="flex space-x-4">
              <img 
                src={product.image} 
                alt={product.name}
                className="w-24 h-24 object-cover rounded-lg"
              />
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold">{product.name}</h3>
                    <p className="text-sm text-muted-foreground">{product.brand}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                  >
                    <Heart className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="flex items-center space-x-2 mb-2">
                  <div className="flex items-center">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm ml-1">{product.rating}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">({product.reviews_count} reviews)</span>
                  <Badge variant="secondary" className="text-xs">{product.category}</Badge>
                </div>

                <div className="flex flex-wrap gap-1 mb-3">
                  {product.features.slice(0, 3).map((feature, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold text-green-600">₹{product.price_inr.toLocaleString()}</span>
                      <span className="text-sm text-muted-foreground line-through">₹{product.original_price_inr.toLocaleString()}</span>
                      <Badge variant="destructive" className="text-xs">{discount}% OFF</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{product.price_hp} HP</p>
                  </div>
                  <Button onClick={() => addToCart(product)}>
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Add to Cart
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card className="hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
        <CardContent className="p-4">
          <div className="relative mb-4">
            <img 
              src={product.image} 
              alt={product.name}
              className="w-full h-48 object-cover rounded-lg"
            />
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-2 right-2 h-8 w-8 p-0 bg-white/80 hover:bg-white"
            >
              <Heart className="h-4 w-4" />
            </Button>
            <Badge variant="destructive" className="absolute top-2 left-2">
              {discount}% OFF
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div>
              <h3 className="font-semibold text-sm">{product.name}</h3>
              <p className="text-xs text-muted-foreground">{product.brand}</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center">
                <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                <span className="text-xs ml-1">{product.rating}</span>
              </div>
              <span className="text-xs text-muted-foreground">({product.reviews_count})</span>
            </div>

            <div className="flex flex-wrap gap-1">
              {product.features.slice(0, 2).map((feature, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {feature}
                </Badge>
              ))}
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-green-600">₹{product.price_inr.toLocaleString()}</span>
                <span className="text-xs text-muted-foreground line-through">₹{product.original_price_inr.toLocaleString()}</span>
              </div>
              <p className="text-xs text-muted-foreground">{product.price_hp} HP</p>
            </div>

            <Button 
              size="sm" 
              className="w-full"
              onClick={() => addToCart(product)}
            >
              <Plus className="h-3 w-3 mr-1" />
              Add to Cart
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Axzora E-commerce</h1>
          <p className="text-muted-foreground">Curated products with Happy Paisa rewards</p>
        </div>
        <div className="relative">
          <Button className="flex items-center space-x-2">
            <ShoppingCart className="h-5 w-5" />
            <span>Cart ({getCartCount()})</span>
          </Button>
          {getCartCount() > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0 text-xs flex items-center justify-center"
            >
              {getCartCount()}
            </Badge>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="electronics">Electronics</SelectItem>
                  <SelectItem value="wearables">Wearables</SelectItem>
                  <SelectItem value="food">Food & Beverage</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popular">Most Popular</SelectItem>
                  <SelectItem value="price-low">Price: Low to High</SelectItem>
                  <SelectItem value="price-high">Price: High to Low</SelectItem>
                  <SelectItem value="rating">Highest Rated</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex rounded-md border">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="rounded-r-none"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="rounded-l-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cart Summary */}
      {cartItems.length > 0 && (
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold">Cart Summary</h3>
                <p className="text-sm text-muted-foreground">
                  {getCartCount()} item(s) • Total: {getCartTotal().toFixed(3)} HP
                </p>
              </div>
              <div className="space-x-2">
                <Button variant="outline" size="sm">View Cart</Button>
                <Button size="sm">Checkout</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Product Grid/List */}
      <div className={`grid gap-4 ${
        viewMode === 'grid' 
          ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
          : 'grid-cols-1'
      }`}>
        {mockProducts.map((product) => (
          <ProductCard 
            key={product.id} 
            product={product} 
            viewMode={viewMode}
          />
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <Button variant="outline" size="lg">
          Load More Products
        </Button>
      </div>

      {/* Features Banner */}
      <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold">Why Shop with Axzora?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="flex items-center space-x-2">
                <ShoppingCart className="h-5 w-5" />
                <span>Happy Paisa Rewards</span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5" />
                <span>Curated Quality Products</span>
              </div>
              <div className="flex items-center space-x-2">
                <Heart className="h-5 w-5" />
                <span>AI-Powered Recommendations</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Shop;