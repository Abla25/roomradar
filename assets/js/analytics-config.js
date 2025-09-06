// Google Analytics Configuration for RoomRadar
// This file centralizes the Analytics configuration across all pages

// ⚠️ IMPORTANT: Replace this with your actual Google Analytics 4 Measurement ID
// You can find this in Google Analytics > Admin > Data Streams > Web > Measurement ID
export const GA_MEASUREMENT_ID = 'G-3135P792LN'; // TODO: Replace with your actual GA4 Measurement ID

// Analytics configuration options
export const ANALYTICS_CONFIG = {
  // Privacy settings
  anonymize_ip: true,
  allow_google_signals: true,
  allow_ad_personalization_signals: false,
  
  // Enhanced measurements (automatically track scroll, outbound clicks, etc.)
  enhanced_measurements: {
    scrolls: true,
    outbound_clicks: true,
    site_search: false,
    video_engagement: false,
    file_downloads: true
  },
  
  // Custom parameters
  custom_map: {
    'custom_parameter_1': 'selected_city',
    'custom_parameter_2': 'user_type',
    'custom_parameter_3': 'page_source'
  }
};

// Function to check if Analytics is properly configured
export function isAnalyticsConfigured() {
  return GA_MEASUREMENT_ID && GA_MEASUREMENT_ID !== 'G-XXXXXXXXXX';
}

// Function to get the measurement ID
export function getMeasurementId() {
  if (!isAnalyticsConfigured()) {
    console.warn('⚠️ Google Analytics Measurement ID not configured. Please update GA_MEASUREMENT_ID in analytics-config.js');
    return null;
  }
  return GA_MEASUREMENT_ID;
}

// Function to initialize analytics with consistent configuration
export async function initializeAnalytics(pageName = 'Unknown Page') {
  const measurementId = getMeasurementId();
  if (!measurementId) {
    console.warn(`⚠️ Analytics not initialized for ${pageName} - missing configuration`);
    return null;
  }

  try {
    const { default: RoomRadarAnalytics } = await import('./analytics.js');
    const analytics = new RoomRadarAnalytics(measurementId);
    
    console.log(`📊 RoomRadar Analytics initialized for ${pageName}`);
    return analytics;
  } catch (error) {
    console.error(`❌ Failed to initialize analytics for ${pageName}:`, error);
    return null;
  }
}

// Export for backwards compatibility
export default {
  GA_MEASUREMENT_ID,
  ANALYTICS_CONFIG,
  isAnalyticsConfigured,
  getMeasurementId,
  initializeAnalytics
};
