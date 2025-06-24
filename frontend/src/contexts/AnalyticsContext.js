/**
 * Analytics Context Provider
 * Global analytics state management and tracking
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { UserContext } from './UserContext';

const AnalyticsContext = createContext();

export const useAnalyticsContext = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalyticsContext must be used within an AnalyticsProvider');
  }
  return context;
};

export const AnalyticsProvider = ({ children }) => {
  const [analyticsEnabled, setAnalyticsEnabled] = useState(true);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [sessionStartTime] = useState(Date.now());
  const { user } = useContext(UserContext);
  const analytics = useAnalytics();

  // Track session start
  useEffect(() => {
    if (analyticsEnabled && user?.id) {
      analytics.trackEvent('session_start', {
        session_id: sessionId,
        user_id: user.id,
        user_type: user.type || 'standard',
        timestamp: new Date().toISOString()
      });
    }
  }, [analytics, analyticsEnabled, sessionId, user]);

  // Track session end on unmount
  useEffect(() => {
    return () => {
      if (analyticsEnabled && user?.id) {
        const sessionDuration = Date.now() - sessionStartTime;
        analytics.trackEvent('session_end', {
          session_id: sessionId,
          session_duration_ms: sessionDuration,
          user_id: user.id,
          timestamp: new Date().toISOString()
        });
      }
    };
  }, [analytics, analyticsEnabled, sessionId, sessionStartTime, user]);

  // Enhanced tracking methods with session context
  const trackWithSession = useCallback((eventName, parameters = {}) => {
    if (!analyticsEnabled) return;
    
    analytics.trackEvent(eventName, {
      session_id: sessionId,
      session_duration_ms: Date.now() - sessionStartTime,
      ...parameters
    });
  }, [analytics, analyticsEnabled, sessionId, sessionStartTime]);

  const trackUserAction = useCallback((action, category, label = null, value = null) => {
    trackWithSession('user_action', {
      action,
      category,
      label,
      value,
      timestamp: new Date().toISOString()
    });
  }, [trackWithSession]);

  const trackError = useCallback((error, context = null) => {
    if (!analyticsEnabled) return;
    
    analytics.trackError('frontend_error', error.message, context, {
      session_id: sessionId,
      error_stack: error.stack,
      error_name: error.name,
      timestamp: new Date().toISOString()
    });
  }, [analytics, analyticsEnabled, sessionId]);

  const trackConversion = useCallback((conversionType, value, currency = 'HP') => {
    if (!analyticsEnabled) return;
    
    analytics.trackBusinessMetric(`conversion_${conversionType}`, value, currency, {
      session_id: sessionId,
      conversion_type: conversionType,
      timestamp: new Date().toISOString()
    });
  }, [analytics, analyticsEnabled, sessionId]);

  // A/B Testing support
  const [abTestVariants, setAbTestVariants] = useState({});
  
  const trackAbTest = useCallback((testName, variant) => {
    setAbTestVariants(prev => ({ ...prev, [testName]: variant }));
    
    trackWithSession('ab_test_assignment', {
      test_name: testName,
      variant,
      timestamp: new Date().toISOString()
    });
  }, [trackWithSession]);

  // Privacy controls
  const enableAnalytics = useCallback(() => {
    setAnalyticsEnabled(true);
    trackWithSession('analytics_enabled', {
      enabled_at: new Date().toISOString()
    });
  }, [trackWithSession]);

  const disableAnalytics = useCallback(() => {
    trackWithSession('analytics_disabled', {
      disabled_at: new Date().toISOString()
    });
    setAnalyticsEnabled(false);
  }, [trackWithSession]);

  const contextValue = {
    // Core analytics
    ...analytics,
    
    // Session tracking
    sessionId,
    sessionStartTime,
    analyticsEnabled,
    
    // Enhanced tracking methods
    trackWithSession,
    trackUserAction,
    trackError,
    trackConversion,
    
    // A/B Testing
    abTestVariants,
    trackAbTest,
    
    // Privacy controls
    enableAnalytics,
    disableAnalytics,
    
    // Convenience methods for common Axzora events
    trackWalletAction: (action, amount, currency) => {
      analytics.trackHappyPaisaTransaction(action, amount, currency, `txn_${Date.now()}`);
    },
    
    trackBookingAction: (type, step, metadata = {}) => {
      analytics.trackUserJourney(`booking_${type}_${step}`, metadata);
    },
    
    trackVoiceAction: (command, success, duration) => {
      analytics.trackVoiceCommand(command, success, duration);
    },
    
    trackFeatureDiscovery: (feature) => {
      analytics.trackFeatureUsage(feature, 'discovered', {
        discovery_timestamp: new Date().toISOString()
      });
    },
    
    trackFeatureAdoption: (feature) => {
      analytics.trackFeatureUsage(feature, 'adopted', {
        adoption_timestamp: new Date().toISOString()
      });
    }
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export default AnalyticsContext;