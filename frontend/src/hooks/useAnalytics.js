/**
 * React Hook for Analytics Tracking
 * Integrates with Firebase Analytics and backend analytics service
 */

import { useEffect, useCallback, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { AxzoraAnalytics, trackEvent, trackUserId, trackUserProperties, createPerformanceTrace } from '../config/firebase';
import { UserContext } from '../contexts/UserContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useAnalytics = () => {
  const location = useLocation();
  const { user } = useContext(UserContext);

  // Initialize user tracking when user changes
  useEffect(() => {
    if (user?.id) {
      trackUserId(user.id);
      trackUserProperties({
        user_type: user.type || 'standard',
        registration_date: user.created_at || new Date().toISOString(),
        wallet_balance: user.wallet_balance || 0,
        preferred_currency: 'HP'
      });
    }
  }, [user]);

  // Track page views
  useEffect(() => {
    const pageName = location.pathname.replace('/', '') || 'home';
    AxzoraAnalytics.trackPageView(pageName);
    
    // Also send to backend
    if (user?.id) {
      trackBackendEvent('page_view', {
        page_name: pageName,
        page_path: location.pathname,
        user_id: user.id
      });
    }
  }, [location, user]);

  // Backend event tracking
  const trackBackendEvent = useCallback(async (eventName, parameters = {}) => {
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-event`, {
        event_name: eventName,
        user_id: user?.id,
        parameters
      });
    } catch (error) {
      console.warn('Backend analytics tracking failed:', error);
    }
  }, [user]);

  // Track user journey steps
  const trackUserJourney = useCallback(async (journeyStep, metadata = {}) => {
    if (!user?.id) return;
    
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-user-journey`, {
        user_id: user.id,
        journey_step: journeyStep,
        metadata
      });
    } catch (error) {
      console.warn('User journey tracking failed:', error);
    }
  }, [user]);

  // Track business metrics
  const trackBusinessMetric = useCallback(async (metricName, value, currency = 'HP', metadata = {}) => {
    if (!user?.id) return;
    
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-business-metric`, {
        metric_name: metricName,
        value,
        currency,
        user_id: user.id,
        metadata
      });
    } catch (error) {
      console.warn('Business metric tracking failed:', error);
    }
  }, [user]);

  // Track errors
  const trackError = useCallback(async (errorType, errorMessage, endpoint = null, metadata = {}) => {
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-error`, {
        error_type: errorType,
        error_message: errorMessage,
        user_id: user?.id,
        endpoint,
        metadata
      });
    } catch (error) {
      console.warn('Error tracking failed:', error);
    }
  }, [user]);

  // Track performance metrics
  const trackPerformance = useCallback(async (operationName, durationMs, success, metadata = {}) => {
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-performance`, {
        operation_name: operationName,
        duration_ms: durationMs,
        success,
        user_id: user?.id,
        metadata
      });
    } catch (error) {
      console.warn('Performance tracking failed:', error);
    }
  }, [user]);

  // Axzora-specific tracking methods
  const trackHappyPaisaTransaction = useCallback(async (transactionType, amount, currency, transactionId) => {
    if (!user?.id) return;
    
    // Track in Firebase
    AxzoraAnalytics.trackWalletTransaction(transactionType, amount, currency);
    
    // Track in backend
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-happy-paisa-transaction`, {
        user_id: user.id,
        transaction_type: transactionType,
        amount,
        currency,
        transaction_id: transactionId
      });
    } catch (error) {
      console.warn('Happy Paisa transaction tracking failed:', error);
    }
  }, [user]);

  const trackBooking = useCallback(async (bookingType, bookingId, amount, status, metadata = {}) => {
    if (!user?.id) return;
    
    // Track in Firebase
    AxzoraAnalytics.trackBookingCompletion(bookingType, bookingId, amount, 'happy_paisa');
    
    // Track in backend
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-booking`, {
        user_id: user.id,
        booking_type: bookingType,
        booking_id: bookingId,
        amount,
        status,
        metadata
      });
    } catch (error) {
      console.warn('Booking tracking failed:', error);
    }
  }, [user]);

  const trackVoiceCommand = useCallback(async (commandType, success, durationMs, confidenceScore = null) => {
    if (!user?.id) return;
    
    // Track in Firebase
    AxzoraAnalytics.trackVoiceCommand(commandType, success, durationMs);
    
    // Track in backend
    try {
      await axios.post(`${BACKEND_URL}/api/analytics/track-voice-command`, {
        user_id: user.id,
        command_type: commandType,
        success,
        duration_ms: durationMs,
        confidence_score: confidenceScore
      });
    } catch (error) {
      console.warn('Voice command tracking failed:', error);
    }
  }, [user]);

  const trackFeatureUsage = useCallback((featureName, action, metadata = {}) => {
    // Track in Firebase
    AxzoraAnalytics.trackFeatureUsage(featureName, action, metadata);
    
    // Track in backend
    trackBackendEvent('feature_usage', {
      feature_name: featureName,
      action,
      ...metadata
    });
  }, [trackBackendEvent]);

  const trackPurchase = useCallback(async (items, totalValue, currency = 'HP') => {
    // Track in Firebase
    AxzoraAnalytics.trackPurchase(items, totalValue, currency);
    
    // Track business metric in backend
    await trackBusinessMetric('purchase_completed', totalValue, currency, {
      item_count: items.length,
      items: items.map(item => ({
        id: item.id,
        name: item.name,
        category: item.category,
        price: item.price,
        quantity: item.quantity
      }))
    });
  }, [trackBusinessMetric]);

  return {
    // Core tracking methods
    trackEvent: trackBackendEvent,
    trackUserJourney,
    trackBusinessMetric,
    trackError,
    trackPerformance,
    
    // Axzora-specific methods
    trackHappyPaisaTransaction,
    trackBooking,
    trackVoiceCommand,
    trackFeatureUsage,
    trackPurchase,
    
    // Performance monitoring
    createPerformanceTrace,
    
    // Firebase direct methods
    trackFirebaseEvent: trackEvent,
    trackFirebaseUserProperties: trackUserProperties
  };
};

export default useAnalytics;