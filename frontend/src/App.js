import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [products, setProducts] = useState([]);
  const [activeTab, setActiveTab] = useState("marketplace");
  const [voiceCommand, setVoiceCommand] = useState("");
  const [voiceResponse, setVoiceResponse] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [newProduct, setNewProduct] = useState({
    title: "",
    description: "",
    price_hp: "",
    category: "electronics",
    image_url: ""
  });
  const [marketplaceStats, setMarketplaceStats] = useState({});

  useEffect(() => {
    loadMarketplaceData();
    // Create default user if none exists
    createDefaultUser();
  }, []);

  const createDefaultUser = async () => {
    try {
      const response = await axios.post(`${API}/users`, {
        username: "demo_user",
        email: "demo@example.com"
      });
      setCurrentUser(response.data);
    } catch (error) {
      console.error("Error creating user:", error);
    }
  };

  const loadMarketplaceData = async () => {
    try {
      const [productsRes, statsRes] = await Promise.all([
        axios.get(`${API}/products`),
        axios.get(`${API}/stats`)
      ]);
      setProducts(productsRes.data);
      setMarketplaceStats(statsRes.data);
    } catch (error) {
      console.error("Error loading marketplace data:", error);
    }
  };

  const handleVoiceCommand = async () => {
    if (!voiceCommand.trim() || !currentUser) return;
    
    setIsListening(true);
    try {
      const response = await axios.post(`${API}/voice/command`, {
        command: voiceCommand,
        user_id: currentUser.id
      });
      setVoiceResponse(response.data.response);
      
      // Refresh user data after voice command
      const userResponse = await axios.get(`${API}/users/${currentUser.id}`);
      setCurrentUser(userResponse.data);
    } catch (error) {
      console.error("Error processing voice command:", error);
      setVoiceResponse("Sorry, I couldn't process that command.");
    }
    setIsListening(false);
  };

  const createProduct = async () => {
    if (!currentUser) return;
    
    try {
      await axios.post(`${API}/products?seller_id=${currentUser.id}`, newProduct);
      setNewProduct({
        title: "",
        description: "",
        price_hp: "",
        category: "electronics",
        image_url: ""
      });
      loadMarketplaceData();
      setActiveTab("marketplace");
    } catch (error) {
      console.error("Error creating product:", error);
    }
  };

  const buyProduct = async (productId) => {
    if (!currentUser) return;
    
    try {
      await axios.post(`${API}/transactions?product_id=${productId}&buyer_id=${currentUser.id}`);
      // Refresh data
      loadMarketplaceData();
      const userResponse = await axios.get(`${API}/users/${currentUser.id}`);
      setCurrentUser(userResponse.data);
    } catch (error) {
      console.error("Error buying product:", error);
      alert("Transaction failed. Please check your balance.");
    }
  };

  const addHappyPaisa = async () => {
    if (!currentUser) return;
    
    const amount = prompt("Enter INR amount to convert to Happy Paisa (1000 INR = 1 HP):");
    if (!amount || isNaN(amount) || amount <= 0) return;
    
    try {
      const response = await axios.post(`${API}/happy-paisa/mint/${currentUser.id}?amount_inr=${amount}`);
      console.log("Mint response:", response.data);
      
      // Refresh user data
      const userResponse = await axios.get(`${API}/users/${currentUser.id}`);
      setCurrentUser(userResponse.data);
      
      const hpAmount = (amount / 1000).toFixed(3);
      alert(`Successfully added ${hpAmount} HP from ₹${amount}!`);
    } catch (error) {
      console.error("Error adding Happy Paisa:", error);
      alert("Failed to add Happy Paisa. Please try again.");
    }
  };

  const ProductCard = ({ product }) => (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {product.image_url && (
        <img src={product.image_url} alt={product.title} className="w-full h-48 object-cover rounded-md mb-4" />
      )}
      <h3 className="text-xl font-semibold mb-2">{product.title}</h3>
      <p className="text-gray-600 mb-3">{product.description}</p>
      <div className="flex justify-between items-center mb-3">
        <span className="text-2xl font-bold text-purple-600">{product.price_hp} HP</span>
        <span className="text-sm text-gray-500">₹{product.price_inr}</span>
      </div>
      <div className="flex justify-between items-center mb-4">
        <span className="text-sm text-gray-500">By {product.seller_username}</span>
        <span className="text-sm text-gray-500">{product.views} views</span>
      </div>
      <button
        onClick={() => buyProduct(product.id)}
        disabled={!currentUser || currentUser.happy_paisa_balance < product.price_hp}
        className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        Buy with Happy Paisa
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-purple-600">Happy Paisa Marketplace</h1>
              <span className="text-sm text-gray-500">Powered by Mr. Happy AI</span>
            </div>
            
            {currentUser && (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-500">Welcome, {currentUser.username}</p>
                  <p className="text-lg font-semibold text-purple-600">
                    {currentUser.happy_paisa_balance.toFixed(3)} HP
                  </p>
                </div>
                <button
                  onClick={addHappyPaisa}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  Add HP
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Voice Assistant */}
      <div className="bg-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <input
                type="text"
                value={voiceCommand}
                onChange={(e) => setVoiceCommand(e.target.value)}
                placeholder="Ask Mr. Happy anything... 'Check my balance' or 'List my phone for 0.5 HP'"
                className="w-full px-4 py-2 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-300"
                onKeyPress={(e) => e.key === 'Enter' && handleVoiceCommand()}
              />
            </div>
            <button
              onClick={handleVoiceCommand}
              disabled={isListening}
              className="bg-purple-700 text-white px-6 py-2 rounded-md hover:bg-purple-800 disabled:bg-purple-400 transition-colors"
            >
              {isListening ? "Thinking..." : "Ask Mr. Happy"}
            </button>
          </div>
          
          {voiceResponse && (
            <div className="mt-3 p-3 bg-purple-700 rounded-md">
              <p className="text-sm">
                <span className="font-semibold">Mr. Happy:</span> {voiceResponse}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {["marketplace", "sell", "wallet", "stats"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 border-b-2 font-medium text-sm capitalize transition-colors ${
                  activeTab === tab
                    ? "border-purple-500 text-purple-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "marketplace" && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Marketplace</h2>
              <p className="text-gray-600">{products.length} products available</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
            
            {products.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No products available yet.</p>
                <p className="text-gray-400">Be the first to list something!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "sell" && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Sell Your Product</h2>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Product Title</label>
                  <input
                    type="text"
                    value={newProduct.title}
                    onChange={(e) => setNewProduct({...newProduct, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter product title"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={newProduct.description}
                    onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Describe your product"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Price (Happy Paisa)</label>
                    <input
                      type="number"
                      step="0.001"
                      value={newProduct.price_hp}
                      onChange={(e) => setNewProduct({...newProduct, price_hp: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="0.050"
                    />
                    {newProduct.price_hp && (
                      <p className="text-sm text-gray-500 mt-1">
                        ≈ ₹{(parseFloat(newProduct.price_hp) * 1000).toLocaleString()}
                      </p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select
                      value={newProduct.category}
                      onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="electronics">Electronics</option>
                      <option value="fashion">Fashion</option>
                      <option value="home">Home</option>
                      <option value="books">Books</option>
                      <option value="sports">Sports</option>
                      <option value="services">Services</option>
                      <option value="digital">Digital</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Image URL (Optional)</label>
                  <input
                    type="url"
                    value={newProduct.image_url}
                    onChange={(e) => setNewProduct({...newProduct, image_url: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="https://example.com/image.jpg"
                  />
                </div>
                
                <button
                  onClick={createProduct}
                  className="w-full bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 transition-colors font-medium"
                >
                  List Product
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "wallet" && currentUser && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Your Wallet</h2>
            
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Happy Paisa Balance</h3>
                <p className="text-4xl font-bold text-purple-600 mb-2">
                  {currentUser.happy_paisa_balance.toFixed(3)} HP
                </p>
                <p className="text-gray-500">
                  ≈ ₹{(currentUser.happy_paisa_balance * 1000).toLocaleString()}
                </p>
                
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Total Transactions</p>
                    <p className="text-2xl font-semibold">{currentUser.total_transactions}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">User Rating</p>
                    <p className="text-2xl font-semibold">{currentUser.rating}/5</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Wallet Features</h3>
              <div className="space-y-3">
                <button
                  onClick={addHappyPaisa}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                >
                  Add Happy Paisa (INR → HP)
                </button>
                <button
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                  onClick={() => alert("P2P transfer coming soon!")}
                >
                  Send to Friend
                </button>
                <button
                  className="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors"
                  onClick={() => alert("Withdrawal feature coming soon!")}
                >
                  Withdraw to Bank
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "stats" && (
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Marketplace Statistics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Total Users</h3>
                <p className="text-3xl font-bold text-purple-600">{marketplaceStats.total_users || 0}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Total Products</h3>
                <p className="text-3xl font-bold text-blue-600">{marketplaceStats.total_products || 0}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Total Transactions</h3>
                <p className="text-3xl font-bold text-green-600">{marketplaceStats.total_transactions || 0}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <h3 className="text-lg font-medium text-gray-900 mb-2">HP in Circulation</h3>
                <p className="text-3xl font-bold text-orange-600">
                  {(marketplaceStats.total_happy_paisa_circulation || 0).toFixed(3)}
                </p>
                <p className="text-sm text-gray-500">
                  ≈ ₹{(marketplaceStats.total_inr_equivalent || 0).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="mt-8 bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">About Happy Paisa</h3>
              <div className="space-y-3 text-gray-600">
                <p>• <strong>Fixed Peg:</strong> 1 Happy Paisa = ₹1,000 INR</p>
                <p>• <strong>Blockchain:</strong> Built on Polkadot Substrate (Coming Soon)</p>
                <p>• <strong>Voice AI:</strong> Powered by Mr. Happy Assistant</p>
                <p>• <strong>P2P Trading:</strong> Direct peer-to-peer transactions</p>
                <p>• <strong>Escrow:</strong> Secure transaction protection</p>
                <p>• <strong>Transparent:</strong> All transactions are auditable</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;