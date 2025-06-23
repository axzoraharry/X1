// Mock data for Axzora's Mr. Happy 2.0

export const mockUser = {
  id: "axzora_user_123",
  name: "Rohan Sharma",
  email: "rohan@example.com",
  avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
  location: "Nagpur, India"
};

export const mockHappyPaisaWallet = {
  balance_hp: 5.25,
  balance_inr_equiv: 5250.00,
  recent_transactions: [
    {
      id: "txn_abc",
      type: "debit",
      amount_hp: 0.5,
      description: "Coffee at Cafe Bliss",
      timestamp: "2025-06-23T09:00:00Z",
      category: "Food",
      status: "completed"
    },
    {
      id: "txn_def",
      type: "credit", 
      amount_hp: 2.0,
      description: "Client Payment - Design Project",
      timestamp: "2025-06-22T14:30:00Z",
      category: "Work",
      status: "completed"
    },
    {
      id: "txn_ghi",
      type: "debit",
      amount_hp: 0.299,
      description: "Mobile Recharge - Jio",
      timestamp: "2025-06-22T10:15:00Z",
      category: "Recharge",
      status: "completed"
    },
    {
      id: "txn_jkl",
      type: "debit",
      amount_hp: 1.2,
      description: "Flight Booking - Mumbai",
      timestamp: "2025-06-21T16:45:00Z",
      category: "Travel",
      status: "completed"
    }
  ],
  spending_breakdown: {
    "Food": 0.8,
    "Travel": 1.2,
    "Recharge": 0.5,
    "Shopping": 0.6,
    "Entertainment": 0.3
  },
  budget_status: {
    "Food": { limit: 1.0, spent: 0.8, status: "under_budget" },
    "Travel": { limit: 2.0, spent: 1.2, status: "under_budget" },
    "Shopping": { limit: 1.0, spent: 0.6, status: "under_budget" }
  }
};

export const mockFlights = [
  {
    id: "flight_1",
    airline: "IndiGo",
    flight_number: "6E-123",
    origin: "NAG",
    destination: "GOA",
    departure_time: "08:30",
    arrival_time: "10:15",
    duration: "1h 45m",
    price_inr: 4999,
    price_hp: 4.999,
    stops: 0,
    aircraft: "A320",
    available_seats: 23
  },
  {
    id: "flight_2",
    airline: "Air India",
    flight_number: "AI-456",
    origin: "NAG",
    destination: "GOA",
    departure_time: "14:20",
    arrival_time: "16:30",
    duration: "2h 10m",
    price_inr: 5499,
    price_hp: 5.499,
    stops: 0,
    aircraft: "A321",
    available_seats: 15
  },
  {
    id: "flight_3",
    airline: "SpiceJet",
    flight_number: "SG-789",
    origin: "NAG",
    destination: "GOA",
    departure_time: "19:45",
    arrival_time: "21:35",
    duration: "1h 50m",
    price_inr: 3999,
    price_hp: 3.999,
    stops: 0,
    aircraft: "B737",
    available_seats: 31
  }
];

export const mockHotels = [
  {
    id: "hotel_1",
    name: "Taj Exotica Resort & Spa",
    location: "Benaulim, South Goa",
    rating: 4.8,
    price_per_night_inr: 12000,
    price_per_night_hp: 12.0,
    images: ["https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=400&h=300&fit=crop"],
    amenities: ["Pool", "Spa", "Beach Access", "Wi-Fi", "Restaurant"],
    reviews_count: 1247,
    available_rooms: 3
  },
  {
    id: "hotel_2", 
    name: "The Leela Goa",
    location: "Cavelossim Beach, South Goa",
    rating: 4.7,
    price_per_night_inr: 8500,
    price_per_night_hp: 8.5,
    images: ["https://images.unsplash.com/photo-1578774204375-826dc5d996ed?w=400&h=300&fit=crop"],
    amenities: ["Pool", "Beach Access", "Wi-Fi", "Gym", "Restaurant"],
    reviews_count: 892,
    available_rooms: 7
  },
  {
    id: "hotel_3",
    name: "Novotel Goa Dona Sylvia Resort",
    location: "Cavelossim Beach, South Goa", 
    rating: 4.5,
    price_per_night_inr: 6500,
    price_per_night_hp: 6.5,
    images: ["https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=300&fit=crop"],
    amenities: ["Pool", "Beach Access", "Wi-Fi", "Kids Club", "Restaurant"],
    reviews_count: 654,
    available_rooms: 12
  }
];

export const mockRechargePlans = {
  jio: [
    {
      id: "jio_1",
      amount: 299,
      amount_hp: 0.299,
      validity: "28 days",
      data: "2GB/day",
      calls: "Unlimited",
      sms: "100/day",
      description: "Popular Plan"
    },
    {
      id: "jio_2", 
      amount: 599,
      amount_hp: 0.599,
      validity: "84 days",
      data: "2GB/day",
      calls: "Unlimited",
      sms: "100/day",
      description: "Long Validity"
    },
    {
      id: "jio_3",
      amount: 149,
      amount_hp: 0.149,
      validity: "20 days",
      data: "1GB/day",
      calls: "Unlimited",
      sms: "100/day",
      description: "Budget Plan"
    }
  ],
  airtel: [
    {
      id: "airtel_1",
      amount: 319,
      amount_hp: 0.319,
      validity: "30 days",
      data: "2.5GB/day",
      calls: "Unlimited",
      sms: "100/day",
      description: "Popular Plan"
    },
    {
      id: "airtel_2",
      amount: 549,
      amount_hp: 0.549,
      validity: "56 days",
      data: "2GB/day",
      calls: "Unlimited",
      sms: "100/day",
      description: "Best Value"
    }
  ]
};

export const mockProducts = [
  {
    id: "prod_1",
    name: "Wireless Earbuds Pro",
    brand: "TechSound",
    price_inr: 4999,
    price_hp: 4.999,
    original_price_inr: 6999,
    rating: 4.5,
    reviews_count: 234,
    image: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300&h=300&fit=crop",
    category: "Electronics",
    in_stock: true,
    features: ["Noise Cancellation", "20hr Battery", "Quick Charge", "Water Resistant"]
  },
  {
    id: "prod_2",
    name: "Smart Watch X",
    brand: "FitTech",
    price_inr: 8999,
    price_hp: 8.999,
    original_price_inr: 12999,
    rating: 4.3,
    reviews_count: 156,
    image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
    category: "Wearables",
    in_stock: true,
    features: ["Heart Rate Monitor", "GPS", "Water Proof", "7-day Battery"]
  },
  {
    id: "prod_3",
    name: "Premium Coffee Beans",
    brand: "Roast Masters",
    price_inr: 899,
    price_hp: 0.899,
    original_price_inr: 1299,
    rating: 4.7,
    reviews_count: 89,
    image: "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300&h=300&fit=crop",
    category: "Food & Beverage",
    in_stock: true,
    features: ["Arabica Beans", "Medium Roast", "Single Origin", "500g Pack"]
  }
];

export const mockGitActivity = [
  {
    id: "git_1",
    type: "commit",
    message: "Added new payment integration",
    timestamp: "2025-06-23T08:30:00Z",
    author: "dev-team",
    repository: "mrhappy-webapp"
  },
  {
    id: "git_2",
    type: "issue",
    title: "UI improvements for mobile view",
    status: "open",
    timestamp: "2025-06-22T15:20:00Z",
    repository: "mrhappy-webapp"
  },
  {
    id: "git_3",
    type: "pr",
    title: "Feature: Voice command integration",
    status: "merged",
    timestamp: "2025-06-21T11:45:00Z",
    repository: "mycroft-core-custom"
  }
];

export const mockWeather = {
  location: "Nagpur",
  temperature: "35°C",
  condition: "Sunny",
  humidity: "68%",
  wind: "12 km/h",
  forecast: "Tomorrow: 32°C, Chance of rain"
};

export const mockNotifications = [
  {
    id: "notif_1",
    type: "payment",
    title: "Payment Successful",
    message: "Your recharge of ₹299 was successful",
    timestamp: "2025-06-23T09:15:00Z",
    read: false
  },
  {
    id: "notif_2",
    type: "travel",
    title: "Flight Price Drop",
    message: "Mumbai flight price dropped by ₹500",
    timestamp: "2025-06-22T14:30:00Z",
    read: false
  },
  {
    id: "notif_3",
    type: "wallet",
    title: "Low Balance Alert",
    message: "Happy Paisa balance is below 1 HP",
    timestamp: "2025-06-22T10:00:00Z",
    read: true
  }
];