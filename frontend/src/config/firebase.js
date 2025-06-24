// Firebase Analytics Configuration for Axzora Mr. Happy 2.0
import { initializeApp } from "firebase/app";
import { getAnalytics, logEvent, setUserProperties, setUserId } from "firebase/analytics";
import { getPerformance, trace } from "firebase/performance";

// Firebase Configuration (Replace with actual credentials)
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "demo-api-key-replace-with-real",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "axzora-mr-happy.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "axzora-mr-happy",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "axzora-mr-happy.appspot.com",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "123456789012",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:123456789012:web:abcdef123456789",
  measurementId: process.env.REACT_APP_GA_MEASUREMENT_ID || "G-XXXXXXXXXX"
};

// Initialize Firebase
let app = null;
let analytics = null;
let performance = null;

// Create mock implementations for Firebase services
const createMockAnalytics = () => {
  return {
    logEvent: (name, params) => console.log(`[Mock Analytics] Event: ${name}`, params),
    setUserId: (id) => console.log(`[Mock Analytics] Set User ID: ${id}`),
    setUserProperties: (props) => console.log(`[Mock Analytics] Set User Properties:`, props)
  };
};

try {
  // Check if we're using demo keys
  const isDemoKey = firebaseConfig.apiKey === "demo-api-key-replace-with-real";
  
  if (isDemoKey) {
    console.log("Using mock Firebase implementation due to demo API keys");
    // Create mock implementations
    app = { name: "[Mock Firebase App]" };
    analytics = createMockAnalytics();
    performance = {
      trace: (name) => ({
        start: () => console.log(`[Mock Performance] Started trace: ${name}`),
        stop: () => console.log(`[Mock Performance] Stopped trace: ${name}`)
      })
    };
  } else {
    // Only initialize in browser environment with real keys
    if (typeof window !== 'undefined') {
      app = initializeApp(firebaseConfig);
      analytics = getAnalytics(app);
      performance = getPerformance(app);
      
      // Log initial app load
      logEvent(analytics, "app_initialized", {
        app_version: "2.0",
        platform: "web"
      });
    }
  }
} catch (error) {
  console.warn("Firebase Analytics initialization failed:", error);
  
  // Create mock implementations as fallback
  app = { name: "[Mock Firebase App]" };
  analytics = createMockAnalytics();
  performance = {
    trace: (name) => ({
      start: () => console.log(`[Mock Performance] Started trace: ${name}`),
      stop: () => console.log(`[Mock Performance] Stopped trace: ${name}`)
    })
  };
}

// Analytics Event Types for Axzora Mr. Happy 2.0
export const AnalyticsEvents = {
  // User Actions
  USER_SIGNUP: 'user_signup',
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  
  // Happy Paisa Wallet Events
  WALLET_BALANCE_VIEWED: 'wallet_balance_viewed',
  WALLET_TRANSACTION: 'wallet_transaction',
  CURRENCY_CONVERSION: 'currency_conversion',
  WALLET_TOP_UP: 'wallet_top_up',
  
  // Travel Booking Events
  FLIGHT_SEARCH: 'flight_search',
  FLIGHT_SELECTED: 'flight_selected',
  FLIGHT_BOOKING_STARTED: 'flight_booking_started',
  FLIGHT_BOOKING_COMPLETED: 'flight_booking_completed',
  HOTEL_SEARCH: 'hotel_search',
  HOTEL_BOOKING: 'hotel_booking',
  
  // Recharge Events
  MOBILE_RECHARGE_INITIATED: 'mobile_recharge_initiated',
  MOBILE_RECHARGE_COMPLETED: 'mobile_recharge_completed',
  DTH_RECHARGE: 'dth_recharge',
  UTILITY_BILL_PAYMENT: 'utility_bill_payment',
  
  // E-commerce Events
  PRODUCT_VIEWED: 'product_viewed',
  PRODUCT_ADDED_TO_CART: 'product_added_to_cart',
  CART_VIEWED: 'cart_viewed',
  PURCHASE_INITIATED: 'purchase_initiated',
  PURCHASE_COMPLETED: 'purchase_completed',
  
  // Mr. Happy Voice Assistant Events
  VOICE_COMMAND_STARTED: 'voice_command_started',
  VOICE_COMMAND_COMPLETED: 'voice_command_completed',
  VOICE_COMMAND_FAILED: 'voice_command_failed',
  
  // Automation Events
  AUTOMATION_TRIGGERED: 'automation_triggered',
  NOTIFICATION_SENT: 'notification_sent',
  AI_ANALYSIS_REQUESTED: 'ai_analysis_requested',
  
  // Navigation Events
  PAGE_VIEW: 'page_view',
  FEATURE_ACCESSED: 'feature_accessed',
  
  // Error Events
  API_ERROR: 'api_error',
  UI_ERROR: 'ui_error'
};

// Analytics Helper Functions
export const trackEvent = (eventName, parameters = {}) => {
  if (analytics) {
    try {
      if (typeof analytics.logEvent === 'function') {
        // Real Firebase analytics
        logEvent(analytics, eventName, {
          timestamp: new Date().toISOString(),
          ...parameters
        });
      } else {
        // Mock analytics
        analytics.logEvent(eventName, {
          timestamp: new Date().toISOString(),
          ...parameters
        });
      }
    } catch (error) {
      console.warn("Analytics event tracking failed:", error);
    }
  }
};

export const trackUserProperties = (properties) => {
  if (analytics) {
    try {
      if (typeof analytics.setUserProperties === 'function') {
        // Real Firebase analytics
        setUserProperties(analytics, properties);
      } else {
        // Mock analytics
        analytics.setUserProperties(properties);
      }
    } catch (error) {
      console.warn("User properties tracking failed:", error);
    }
  }
};

export const trackUserId = (userId) => {
  if (analytics) {
    try {
      if (typeof analytics.setUserId === 'function') {
        // Real Firebase analytics
        setUserId(analytics, userId);
      } else {
        // Mock analytics
        analytics.setUserId(userId);
      }
    } catch (error) {
      console.warn("User ID tracking failed:", error);
    }
  }
};

// Performance Monitoring
export const createPerformanceTrace = (traceName) => {
  if (performance) {
    try {
      if (typeof performance.trace === 'function') {
        // Real Firebase performance
        return trace(performance, traceName);
      } else {
        // Mock performance
        return performance.trace(traceName);
      }
    } catch (error) {
      console.warn("Performance trace creation failed:", error);
      return null;
    }
  }
  return null;
};

// Enhanced Event Tracking for Axzora Specific Events
export const AxzoraAnalytics = {
  // Happy Paisa Wallet Analytics
  trackWalletTransaction: (type, amount, currency = 'HP') => {
    trackEvent(AnalyticsEvents.WALLET_TRANSACTION, {
      transaction_type: type,
      amount: amount,
      currency: currency,
      conversion_rate: currency === 'HP' ? 1000 : 0.001
    });
  },

  // Travel Booking Analytics
  trackFlightSearch: (origin, destination, dates, passengers) => {
    trackEvent(AnalyticsEvents.FLIGHT_SEARCH, {
      origin: origin,
      destination: destination,
      departure_date: dates.departure,
      return_date: dates.return,
      passenger_count: passengers
    });
  },

  trackBookingCompletion: (type, bookingId, amount, paymentMethod) => {
    trackEvent(type === 'flight' ? AnalyticsEvents.FLIGHT_BOOKING_COMPLETED : AnalyticsEvents.HOTEL_BOOKING, {
      booking_id: bookingId,
      amount: amount,
      payment_method: paymentMethod,
      booking_type: type
    });
  },

  // E-commerce Analytics
  trackPurchase: (items, totalValue, currency = 'HP') => {
    trackEvent(AnalyticsEvents.PURCHASE_COMPLETED, {
      currency: currency,
      value: totalValue,
      items: items.map(item => ({
        item_id: item.id,
        item_name: item.name,
        category: item.category,
        quantity: item.quantity,
        price: item.price
      }))
    });
  },

  // Voice Assistant Analytics
  trackVoiceCommand: (command, success, duration) => {
    trackEvent(success ? AnalyticsEvents.VOICE_COMMAND_COMPLETED : AnalyticsEvents.VOICE_COMMAND_FAILED, {
      command_type: command,
      duration_ms: duration,
      success: success
    });
  },

  // Page Navigation Analytics
  trackPageView: (pageName, previousPage = null) => {
    trackEvent(AnalyticsEvents.PAGE_VIEW, {
      page_title: pageName,
      page_location: window.location.href,
      previous_page: previousPage
    });
  },

  // Feature Usage Analytics
  trackFeatureUsage: (featureName, action, metadata = {}) => {
    trackEvent(AnalyticsEvents.FEATURE_ACCESSED, {
      feature_name: featureName,
      action: action,
      ...metadata
    });
  }
};

export { analytics, performance };
export default app;