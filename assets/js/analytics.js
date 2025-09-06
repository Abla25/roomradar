// Google Analytics 4 Integration for RoomRadar
// This file handles all analytics tracking without affecting existing functionality

class RoomRadarAnalytics {
  constructor(measurementId) {
    this.measurementId = measurementId;
    this.initialized = false;
    this.pageStartTime = Date.now();
    this.currentCity = null;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.init());
    } else {
      this.init();
    }
  }

  async init() {
    try {
      console.log('🔍 Initializing RoomRadar Analytics...');
      
      // Load Google Analytics script
      await this.loadGoogleAnalytics();
      
      // Configure gtag
      this.configureGtag();
      
      // Set up page tracking
      this.trackPageView();
      
      // Set up event listeners for city selection
      this.setupCityTracking();
      
      // Set up time tracking
      this.setupTimeTracking();
      
      // Set up user interaction tracking
      this.setupInteractionTracking();
      
      this.initialized = true;
      console.log('✅ RoomRadar Analytics initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize RoomRadar Analytics:', error);
    }
  }

  loadGoogleAnalytics() {
    return new Promise((resolve, reject) => {
      // Check if gtag is already loaded
      if (window.gtag) {
        resolve();
        return;
      }

      // Create script tag for gtag
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${this.measurementId}`;
      
      script.onload = () => {
        // Initialize gtag
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        window.gtag = gtag;
        
        gtag('js', new Date());
        resolve();
      };
      
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  configureGtag() {
    // Configure Google Analytics with privacy-friendly settings
    gtag('config', this.measurementId, {
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
        'custom_parameter_2': 'user_type'
      }
    });

    console.log('⚙️ Google Analytics configured');
  }

  trackPageView() {
    const pageName = this.getPageName();
    const pageTitle = document.title;
    
    gtag('event', 'page_view', {
      page_title: pageTitle,
      page_location: window.location.href,
      page_name: pageName
    });

    console.log(`📄 Page view tracked: ${pageName}`);
  }

  setupCityTracking() {
    // Track city selection from dropdown
    const citySelectors = [
      '#city-select',
      '.city-selector',
      '[data-city]'
    ];

    citySelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        element.addEventListener('change', (e) => {
          const selectedCity = e.target.value || e.target.dataset.city;
          if (selectedCity) {
            this.trackCitySelection(selectedCity);
          }
        });
        
        element.addEventListener('click', (e) => {
          const selectedCity = e.target.dataset.city || e.target.textContent.trim();
          if (selectedCity && ['Barcelona', 'Rome', 'London', 'Roma'].includes(selectedCity)) {
            this.trackCitySelection(selectedCity);
          }
        });
      });
    });

    // Track city from URL or page content
    this.detectAndTrackCurrentCity();
  }

  trackCitySelection(city) {
    // Normalize city names
    const normalizedCity = this.normalizeCity(city);
    this.currentCity = normalizedCity;

    gtag('event', 'city_selected', {
      event_category: 'User Interaction',
      event_label: normalizedCity,
      selected_city: normalizedCity
    });

    // Set user property for demographic analysis
    gtag('set', {
      custom_parameter_1: normalizedCity,
      user_properties: {
        preferred_city: normalizedCity
      }
    });

    console.log(`🏙️ City selection tracked: ${normalizedCity}`);
  }

  detectAndTrackCurrentCity() {
    // Try to detect city from various sources
    let detectedCity = null;

    // From URL
    const url = window.location.href.toLowerCase();
    if (url.includes('barcelona')) detectedCity = 'Barcelona';
    else if (url.includes('rome') || url.includes('roma')) detectedCity = 'Rome';
    else if (url.includes('london')) detectedCity = 'London';

    // From page content
    if (!detectedCity) {
      const pageText = document.body.textContent.toLowerCase();
      if (pageText.includes('barcelona') && pageText.includes('listings')) detectedCity = 'Barcelona';
      else if ((pageText.includes('rome') || pageText.includes('roma')) && pageText.includes('listings')) detectedCity = 'Rome';
      else if (pageText.includes('london') && pageText.includes('listings')) detectedCity = 'London';
    }

    // From data attributes or selected elements
    if (!detectedCity) {
      const activeCity = document.querySelector('.city-active, .selected-city, [data-city-active="true"]');
      if (activeCity) {
        detectedCity = activeCity.dataset.city || activeCity.textContent.trim();
      }
    }

    if (detectedCity) {
      this.trackCitySelection(detectedCity);
    }
  }

  setupTimeTracking() {
    // Track time spent on page
    let timeOnPage = 0;
    const startTime = Date.now();

    // Track every 30 seconds
    const timeInterval = setInterval(() => {
      timeOnPage = Math.floor((Date.now() - startTime) / 1000);
      
      // Send time tracking event every 30 seconds
      if (timeOnPage > 0 && timeOnPage % 30 === 0) {
        gtag('event', 'time_on_page', {
          event_category: 'Engagement',
          event_label: this.getPageName(),
          value: timeOnPage,
          non_interaction: true
        });
      }
    }, 30000);

    // Track when user leaves page
    window.addEventListener('beforeunload', () => {
      clearInterval(timeInterval);
      const finalTime = Math.floor((Date.now() - startTime) / 1000);
      
      gtag('event', 'page_exit', {
        event_category: 'Engagement',
        event_label: this.getPageName(),
        value: finalTime,
        selected_city: this.currentCity || 'unknown'
      });
    });

    // Track when page becomes hidden/visible (tab switching)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        gtag('event', 'page_hidden', {
          event_category: 'Engagement',
          event_label: this.getPageName(),
          non_interaction: true
        });
      } else {
        gtag('event', 'page_visible', {
          event_category: 'Engagement',
          event_label: this.getPageName(),
          non_interaction: true
        });
      }
    });
  }

  setupInteractionTracking() {
    // Track important user interactions
    
    // Track search interactions
    const searchElements = document.querySelectorAll('input[type="search"], .search-input, #search');
    searchElements.forEach(element => {
      element.addEventListener('input', this.debounce(() => {
        if (element.value.length > 2) {
          gtag('event', 'search', {
            search_term: element.value,
            event_category: 'User Interaction'
          });
        }
      }, 1000));
    });

    // Track filter usage
    const filterElements = document.querySelectorAll('.filter, .filter-button, [data-filter]');
    filterElements.forEach(element => {
      element.addEventListener('click', () => {
        const filterType = element.dataset.filter || element.textContent.trim();
        gtag('event', 'filter_used', {
          event_category: 'User Interaction',
          event_label: filterType,
          selected_city: this.currentCity || 'unknown'
        });
      });
    });

    // Track listing interactions
    const listingElements = document.querySelectorAll('.listing, .room-card, [data-listing-id]');
    listingElements.forEach(element => {
      element.addEventListener('click', () => {
        const listingId = element.dataset.listingId || 'unknown';
        gtag('event', 'listing_clicked', {
          event_category: 'User Interaction',
          event_label: listingId,
          selected_city: this.currentCity || 'unknown'
        });
      });
    });

    // Track authentication events
    if (window.auth) {
      // This integrates with existing Firebase auth
      const checkAuthState = () => {
        if (window.auth.currentUser) {
          gtag('event', 'user_authenticated', {
            event_category: 'User Authentication',
            user_type: 'authenticated'
          });
          
          gtag('set', {
            user_id: window.auth.currentUser.uid,
            user_properties: {
              user_type: 'authenticated'
            }
          });
        } else {
          gtag('set', {
            user_properties: {
              user_type: 'anonymous'
            }
          });
        }
      };

      // Check immediately and set up listener
      checkAuthState();
      if (window.auth.onAuthStateChanged) {
        window.auth.onAuthStateChanged(checkAuthState);
      }
    }
  }

  // Utility methods
  getPageName() {
    const path = window.location.pathname;
    if (path === '/' || path === '/index.html') return 'Homepage';
    if (path.includes('profile')) return 'Profile';
    if (path.includes('faq')) return 'FAQ';
    if (path.includes('how-it-works')) return 'How It Works';
    if (path.includes('privacy')) return 'Privacy Policy';
    if (path.includes('terms')) return 'Terms of Service';
    if (path.includes('cookie')) return 'Cookie Policy';
    return path.replace('/', '').replace('.html', '') || 'Unknown';
  }

  normalizeCity(city) {
    const cityMap = {
      'barcelona': 'Barcelona',
      'rome': 'Rome',
      'roma': 'Rome',
      'london': 'London'
    };
    return cityMap[city.toLowerCase()] || city;
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Public methods for custom tracking
  trackCustomEvent(eventName, parameters = {}) {
    if (!this.initialized) {
      console.warn('Analytics not initialized yet');
      return;
    }

    gtag('event', eventName, {
      event_category: 'Custom',
      selected_city: this.currentCity || 'unknown',
      ...parameters
    });

    console.log(`📊 Custom event tracked: ${eventName}`, parameters);
  }

  setUserProperty(property, value) {
    if (!this.initialized) {
      console.warn('Analytics not initialized yet');
      return;
    }

    gtag('set', {
      user_properties: {
        [property]: value
      }
    });
  }
}

// Make analytics available globally
window.RoomRadarAnalytics = RoomRadarAnalytics;

// Auto-initialize if measurement ID is provided
if (window.GA_MEASUREMENT_ID) {
  window.analytics = new RoomRadarAnalytics(window.GA_MEASUREMENT_ID);
}

export default RoomRadarAnalytics;
