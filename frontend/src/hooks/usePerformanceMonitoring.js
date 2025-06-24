/**
 * React Hook for Performance Monitoring
 * Tracks page load times, API response times, and user interactions
 */

import { useEffect, useCallback, useRef } from 'react';
import { createPerformanceTrace } from '../config/firebase';
import { useAnalytics } from './useAnalytics';

export const usePerformanceMonitoring = () => {
  const { trackPerformance } = useAnalytics();
  const performanceTraces = useRef({});

  // Track page load performance
  useEffect(() => {
    const pageLoadTrace = createPerformanceTrace('page_load');
    if (pageLoadTrace) {
      pageLoadTrace.start();
      
      const handleLoad = () => {
        pageLoadTrace.stop();
        
        // Track performance metrics
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
          trackPerformance('page_load', perfData.loadEventEnd - perfData.loadEventStart, true, {
            dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
            first_paint: perfData.responseEnd - perfData.requestStart,
            page_path: window.location.pathname
          });
        }
      };

      if (document.readyState === 'complete') {
        handleLoad();
      } else {
        window.addEventListener('load', handleLoad);
        return () => window.removeEventListener('load', handleLoad);
      }
    }
  }, [trackPerformance]);

  // Start performance trace
  const startTrace = useCallback((traceName) => {
    const trace = createPerformanceTrace(traceName);
    if (trace) {
      trace.start();
      performanceTraces.current[traceName] = {
        trace,
        startTime: Date.now()
      };
    }
  }, []);

  // Stop performance trace
  const stopTrace = useCallback((traceName, success = true, metadata = {}) => {
    const traceData = performanceTraces.current[traceName];
    if (traceData) {
      traceData.trace.stop();
      const duration = Date.now() - traceData.startTime;
      
      trackPerformance(traceName, duration, success, metadata);
      
      delete performanceTraces.current[traceName];
    }
  }, [trackPerformance]);

  // Track API call performance
  const trackApiCall = useCallback(async (apiCall, operationName, metadata = {}) => {
    const startTime = Date.now();
    let success = false;
    let error = null;

    try {
      const result = await apiCall();
      success = true;
      return result;
    } catch (err) {
      error = err;
      throw err;
    } finally {
      const duration = Date.now() - startTime;
      
      trackPerformance(operationName, duration, success, {
        ...metadata,
        error_message: error?.message,
        error_status: error?.response?.status
      });
    }
  }, [trackPerformance]);

  // Track user interaction performance
  const trackInteraction = useCallback((interactionName, callback, metadata = {}) => {
    return async (...args) => {
      const startTime = Date.now();
      let success = false;
      let error = null;

      try {
        const result = await callback(...args);
        success = true;
        return result;
      } catch (err) {
        error = err;
        throw err;
      } finally {
        const duration = Date.now() - startTime;
        
        trackPerformance(`interaction_${interactionName}`, duration, success, {
          ...metadata,
          error_message: error?.message
        });
      }
    };
  }, [trackPerformance]);

  // Track component render performance
  const trackComponentPerformance = useCallback((componentName) => {
    const startTime = Date.now();
    
    return {
      finish: () => {
        const duration = Date.now() - startTime;
        trackPerformance(`component_render_${componentName}`, duration, true, {
          component_name: componentName
        });
      }
    };
  }, [trackPerformance]);

  return {
    startTrace,
    stopTrace,
    trackApiCall,
    trackInteraction,
    trackComponentPerformance
  };
};

export default usePerformanceMonitoring;