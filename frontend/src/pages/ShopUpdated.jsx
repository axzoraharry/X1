import React, { useState, useEffect } from 'react';
import { ShoppingCart, Star, Heart, Search, Filter, Grid, List, Plus, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useUser } from '../contexts/UserContext';
import { useApi, useApiMutation } from '../hooks/useApi';
import { ecommerceService } from '../services/ecommerceService';
import { useToast } from '../hooks/use-toast';

const ShopPage = () => {
  const { user } = useUser();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('popular');

  // Fetch products
  const { 
    data: products, 
    loading: productsLoading, 
    error: productsError,
    refetch: refetchProducts 
  } = useApi(
    () => ecommerceService.searchProducts({
      query: searchQuery || undefined,
      category: selectedCategory !== 'all' ? selectedCategory : undefined,
      sort_by: sortBy
    }),
    [searchQuery, selectedCategory, sortBy]
  );

  // Fetch cart
  const { 
    data: cartItems, 
    loading: cartLoading,
    refetch: refetchCart 
  } = useApi(
    () => user ? ecommerceService.getCart(user.id) : Promise.resolve([]),
    [user?.id]
  );

  // Fetch categories
  const { data: categories } = useApi(
    () => ecommerceService.getCategories(),
    []
  );

  const { mutate: performMutation, loading: mutationLoading } = useApiMutation();

  const addToCart = async (product) => {
    if (!user) {
      toast({
        title: "Please Login",
        description: "You need to be logged in to add items to cart",
        variant: "destructive"
      });
      return;
    }

    try {
      await performMutation(() => ecommerceService.addToCart({
        user_id: user.id,
        product_id: product.id,
        quantity: 1
      }));
      
      toast({
        title: "Added to Cart",
        description: `${product.name} added to your cart!`,
      });
      
      refetchCart();
    } catch (error) {
      toast({
        title: "Add to Cart Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const getCartCount = () => {
    if (!cartItems) return 0;
    return cartItems.reduce((total, item) => total + item.cart_item.quantity, 0);
  };

  const getCartTotal = () => {
    if (!cartItems) return 0;
    return cartItems.reduce((total, item) => total + item.total_price_hp, 0);
  };

  const handleSearch = () => {
    refetchProducts();
  };

  const ProductCard = ({ product, viewMode }) => {
    const discount = product.original_price_inr ? 
      Math.round(((product.original_price_inr - product.price_inr) / product.original_price_inr) * 100) : 0;
    
    if (viewMode === 'list') {
      return (
        <Card className="hover:shadow-lg transition-all duration-300">
          <CardContent className="p-4">
            <div className="flex space-x-4">
              <img 
                src={product.image} 
                alt={product.name}
                className="w-24 h-24 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop';
                }}
              />
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold">{product.name}</h3>
                    <p className="text-sm text-muted-foreground">{product.brand}</p>
                  </div>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
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
                  {product.features?.slice(0, 3).map((feature, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold text-green-600">₹{product.price_inr.toLocaleString()}</span>
                      {product.original_price_inr && (
                        <>
                          <span className="text-sm text-muted-foreground line-through">₹{product.original_price_inr.toLocaleString()}</span>
                          {discount > 0 && <Badge variant="destructive" className="text-xs">{discount}% OFF</Badge>}
                        </>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{product.price_hp} HP</p>
                  </div>
                  <Button 
                    onClick={() => addToCart(product)}
                    disabled={mutationLoading || !product.in_stock}
                  >
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    {mutationLoading ? 'Adding...' : 'Add to Cart'}
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
              onError={(e) => {
                e.target.src = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop';
              }}
            />
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-2 right-2 h-8 w-8 p-0 bg-white/80 hover:bg-white"
            >
              <Heart className="h-4 w-4" />
            </Button>
            {discount > 0 && (
              <Badge variant="destructive" className="absolute top-2 left-2">
                {discount}% OFF
              </Badge>
            )}
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
              {product.features?.slice(0, 2).map((feature, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {feature}
                </Badge>
              ))}
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-green-600">₹{product.price_inr.toLocaleString()}</span>
                {product.original_price_inr && (
                  <span className="text-xs text-muted-foreground line-through">₹{product.original_price_inr.toLocaleString()}</span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">{product.price_hp} HP</p>
            </div>

            <Button 
              size="sm" 
              className="w-full"
              onClick={() => addToCart(product)}
              disabled={mutationLoading || !product.in_stock}
            >
              <Plus className="h-3 w-3 mr-1" />
              {mutationLoading ? 'Adding...' : product.in_stock ? 'Add to Cart' : 'Out of Stock'}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (!user) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <h2 className="text-lg font-semibold">Loading Shop...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Axzora E-commerce</h1>
          <p className="text-muted-foreground">Curated products with Happy Paisa rewards - Live Data</p>
        </div>
        <div className="relative">
          <Button className="flex items-center space-x-2" onClick={() => toast({
            title: "Cart",
            description: `${getCartCount()} items (${getCartTotal().toFixed(3)} HP total)`
          })}>
            <ShoppingCart className="h-5 w-5" />
            <span>Cart ({getCartCount()})</span>
            {cartLoading && <Loader2 className="h-4 w-4 animate-spin ml-2" />}
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
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
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
                  {categories?.map((category) => (
                    <SelectItem key={category} value={category.toLowerCase()}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popular">Most Popular</SelectItem>
                  <SelectItem value="price_low">Price: Low to High</SelectItem>
                  <SelectItem value="price_high">Price: High to Low</SelectItem>
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
      {getCartCount() > 0 && (
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold">Cart Summary - Live Data</h3>
                <p className="text-sm text-muted-foreground">
                  {getCartCount()} item(s) • Total: {getCartTotal().toFixed(3)} HP
                </p>
              </div>
              <div className="space-x-2">
                <Button variant="outline" size="sm" onClick={refetchCart}>
                  Refresh Cart
                </Button>
                <Button size="sm">Checkout</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Product Grid/List */}
      {productsLoading ? (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4">
                <div className="w-full h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-6 bg-gray-200 rounded w-1/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : productsError ? (
        <Card>
          <CardContent className="p-8 text-center">
            <h3 className="text-lg font-semibold text-red-600 mb-2">Error Loading Products</h3>
            <p className="text-muted-foreground mb-4">{productsError}</p>
            <Button onClick={refetchProducts}>Try Again</Button>
          </CardContent>
        </Card>
      ) : products && products.length > 0 ? (
        <div className={`grid gap-4 ${
          viewMode === 'grid' 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
            : 'grid-cols-1'
        }`}>
          {products.map((product) => (
            <ProductCard 
              key={product.id} 
              product={product} 
              viewMode={viewMode}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <h3 className="text-lg font-semibold mb-2">No Products Found</h3>
            <p className="text-muted-foreground">Try adjusting your search or filters</p>
          </CardContent>
        </Card>
      )}

      {/* Features Banner */}
      <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold">Why Shop with Axzora?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="flex items-center space-x-2">
                <ShoppingCart className="h-5 w-5" />
                <span>Real Happy Paisa Rewards</span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="h-5 w-5" />
                <span>Live Product Catalog</span>
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

export default ShopPage;