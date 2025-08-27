/**
 * RoomRadar GDPR-Compliant Cookie Banner
 * Version: 1.0.0
 * Author: RoomRadar Team
 */

(function() {
  'use strict';

  // Cookie Banner Configuration
  const COOKIE_CONFIG = {
    storageKey: 'roomradar-cookie-consent',
    version: '1.0',
    bannerId: 'cookie-banner',
    modalId: 'cookie-modal',
    cookiePolicyUrl: './assets/pages/cookie-policy.html',
    privacyPolicyUrl: '/privacy.html',
    consentExpiryDays: 30 // GDPR compliance: consent expires after 30 days
  };

  // Multilingual Banner Text
  const BANNER_TEXT = {
    en: {
      title: "We value your privacy",
      description: "We use cookies to enhance your experience, analyze site usage, and assist in marketing. You can customize your preferences below.",
      acceptAll: "Accept All",
      rejectAll: "Reject All",
      customize: "Customize",
      save: "Save Preferences",
      learnMore: "Learn More",
      modalTitle: "Cookie Preferences",
      modalDescription: "Choose which cookies you allow us to use. Essential cookies are always enabled as they are necessary for the website to function properly."
    },
    es: {
      title: "Valoramos tu privacidad",
      description: "Utilizamos cookies para mejorar tu experiencia, analizar el uso del sitio y asistir en marketing. Puedes personalizar tus preferencias abajo.",
      acceptAll: "Aceptar Todo",
      rejectAll: "Rechazar Todo",
      customize: "Personalizar",
      save: "Guardar Preferencias",
      learnMore: "Más Información",
      modalTitle: "Preferencias de Cookies",
      modalDescription: "Elige qué cookies nos permites usar. Las cookies esenciales siempre están habilitadas ya que son necesarias para que el sitio web funcione correctamente."
    },
    it: {
      title: "Rispettiamo la tua privacy",
      description: "Utilizziamo cookie per migliorare la tua esperienza, analizzare l'utilizzo del sito e assistere nel marketing. Puoi personalizzare le tue preferenze qui sotto.",
      acceptAll: "Accetta Tutto",
      rejectAll: "Rifiuta Tutto",
      customize: "Personalizza",
      save: "Salva Preferenze",
      learnMore: "Per Saperne di Più",
      modalTitle: "Preferenze Cookie",
      modalDescription: "Scegli quali cookie ci permetti di utilizzare. I cookie essenziali sono sempre abilitati poiché sono necessari per il corretto funzionamento del sito web."
    }
  };

  // Cookie Categories Configuration
  const COOKIE_CATEGORIES = {
    essential: {
      name: {
        en: "Essential Cookies",
        es: "Cookies Esenciales",
        it: "Cookie Essenziali"
      },
      description: {
        en: "Required for basic site functionality and security. These cookies cannot be disabled.",
        es: "Necesarias para la funcionalidad básica del sitio y seguridad. Estas cookies no se pueden deshabilitar.",
        it: "Necessari per la funzionalità di base del sito e la sicurezza. Questi cookie non possono essere disabilitati."
      },
      cookies: ["session_id", "csrf_token", "cookie_consent"],
      canDisable: false,
      alwaysEnabled: true
    },
    analytics: {
      name: {
        en: "Analytics Cookies",
        es: "Cookies de Análisis",
        it: "Cookie di Analisi"
      },
      description: {
        en: "Help us understand how visitors use our site to improve performance and user experience.",
        es: "Nos ayudan a entender cómo los visitantes usan nuestro sitio para mejorar el rendimiento y la experiencia del usuario.",
        it: "Ci aiutano a capire come i visitanti utilizzano il nostro sito per migliorare le prestazioni e l'esperienza utente."
      },
      cookies: ["_ga", "_gat", "_gid", "_ga_*"],
      canDisable: true,
      alwaysEnabled: false
    },
    marketing: {
      name: {
        en: "Marketing Cookies",
        es: "Cookies de Marketing",
        it: "Cookie di Marketing"
      },
      description: {
        en: "Used to show you relevant ads and measure campaign effectiveness. These cookies may be set by third-party advertisers.",
        es: "Se utilizan para mostrarte anuncios relevantes y medir la efectividad de las campañas. Estas cookies pueden ser establecidas por anunciantes de terceros.",
        it: "Utilizzati per mostrarti annunci pertinenti e misurare l'efficacia delle campagne. Questi cookie possono essere impostati da inserzionisti terzi."
      },
      cookies: ["_fbp", "google_ads", "_gcl_au", "fbp"],
      canDisable: true,
      alwaysEnabled: false
    },
    preferences: {
      name: {
        en: "Preference Cookies",
        es: "Cookies de Preferencias",
        it: "Cookie di Preferenze"
      },
      description: {
        en: "Store your preferences and settings to provide a personalized experience.",
        es: "Almacenan tus preferencias y configuraciones para proporcionar una experiencia personalizada.",
        it: "Memorizzano le tue preferenze e impostazioni per fornire un'esperienza personalizzata."
      },
      cookies: ["language", "theme", "user_preferences"],
      canDisable: true,
      alwaysEnabled: false
    }
  };

  // Cookie Banner Class
  class CookieBanner {
    constructor() {
      this.consent = this.getStoredConsent();
      this.currentLanguage = this.detectLanguage();
      this.banner = null;
      this.modal = null;
      this.isInitialized = false;
      
      this.init();
    }

    // Initialize the cookie banner
    init() {
      if (this.isInitialized) return;
      
      // Check if consent is valid and not expired
      if (this.consent && this.isConsentValid()) {
        this.applyConsent();
        return;
      }

      // Create and show banner
      this.createBanner();
      this.createModal();
      this.showBanner();
      
      this.isInitialized = true;
    }

    // Detect user language - Force English for now
    detectLanguage() {
      // Force English for all users
      return 'en';
      
      // Uncomment below to enable multilingual support
      // const browserLang = navigator.language || navigator.userLanguage;
      // const langCode = browserLang.split('-')[0];
      // return BANNER_TEXT[langCode] ? langCode : 'en';
    }

    // Get stored consent from localStorage
    getStoredConsent() {
      try {
        const stored = localStorage.getItem(COOKIE_CONFIG.storageKey);
        return stored ? JSON.parse(stored) : null;
      } catch (error) {
        console.warn('Error reading cookie consent:', error);
        return null;
      }
    }

    // Check if consent is still valid (not expired)
    isConsentValid() {
      if (!this.consent || !this.consent.timestamp) return false;
      
      // Check version compatibility
      if (this.consent.version !== COOKIE_CONFIG.version) return false;
      
      // Check if consent has expired (30 days from timestamp)
      const consentDate = new Date(this.consent.timestamp);
      const expiryDate = new Date(consentDate.getTime() + (COOKIE_CONFIG.consentExpiryDays * 24 * 60 * 60 * 1000));
      const now = new Date();
      
      return now < expiryDate;
    }

    // Store consent in localStorage
    storeConsent(consent) {
      try {
        const consentData = {
          ...consent,
          timestamp: Date.now(),
          version: COOKIE_CONFIG.version
        };
        localStorage.setItem(COOKIE_CONFIG.storageKey, JSON.stringify(consentData));
        this.consent = consentData;
      } catch (error) {
        console.error('Error storing cookie consent:', error);
      }
    }

    // Create the banner HTML
    createBanner() {
      const text = BANNER_TEXT[this.currentLanguage];
      
      const bannerHTML = `
        <div id="${COOKIE_CONFIG.bannerId}" class="cookie-banner">
          <div class="cookie-banner-content">
            <div class="cookie-banner-header">
              <div class="cookie-banner-icon">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <div class="cookie-banner-text">
                <h3 class="cookie-banner-title">${text.title}</h3>
                <p class="cookie-banner-description">${text.description}</p>
                <div class="cookie-banner-description-links">
                  <a href="#" class="cookie-banner-link" data-action="customize">${text.customize}</a>
                  <span class="cookie-banner-separator"> - </span>
                  <a href="${COOKIE_CONFIG.cookiePolicyUrl}" class="cookie-banner-link" target="_blank">${text.learnMore}</a>
                </div>
              </div>
            </div>
            <div class="cookie-banner-actions">
              <div class="cookie-banner-main-actions">
                <button class="cookie-banner-btn cookie-banner-btn-secondary" data-action="reject-all">
                  ${text.rejectAll}
                </button>
                <button class="cookie-banner-btn cookie-banner-btn-primary" data-action="accept-all">
                  ${text.acceptAll}
                </button>
              </div>
              <div class="cookie-banner-text-links">
                <a href="#" class="cookie-banner-link" data-action="customize">${text.customize}</a>
                <span class="cookie-banner-separator"> - </span>
                <a href="${COOKIE_CONFIG.cookiePolicyUrl}" class="cookie-banner-link" target="_blank">${text.learnMore}</a>
              </div>
            </div>
          </div>
        </div>
      `;

      document.body.insertAdjacentHTML('beforeend', bannerHTML);
      this.banner = document.getElementById(COOKIE_CONFIG.bannerId);
      this.attachBannerEvents();
    }

    // Create the modal HTML
    createModal() {
      const text = BANNER_TEXT[this.currentLanguage];
      
      let categoriesHTML = '';
      Object.keys(COOKIE_CATEGORIES).forEach(categoryKey => {
        const category = COOKIE_CATEGORIES[categoryKey];
        const categoryText = category.name[this.currentLanguage];
        const categoryDesc = category.description[this.currentLanguage];
        
        categoriesHTML += `
          <div class="cookie-category ${categoryKey}">
            <div class="cookie-category-header">
              <h4 class="cookie-category-title">${categoryText}</h4>
              <label class="cookie-toggle">
                <input type="checkbox" 
                       data-category="${categoryKey}" 
                       ${category.alwaysEnabled ? 'checked disabled' : ''}
                       ${this.consent && this.consent[categoryKey] ? 'checked' : ''}>
                <span class="cookie-toggle-slider"></span>
              </label>
            </div>
            <p class="cookie-category-description">${categoryDesc}</p>
            <p class="cookie-category-cookies">${category.cookies.join(', ')}</p>
          </div>
        `;
      });

      const modalHTML = `
        <div id="${COOKIE_CONFIG.modalId}" class="cookie-modal">
          <div class="cookie-modal-content">
            <div class="cookie-modal-header">
              <h2 class="cookie-modal-title">${text.modalTitle}</h2>
              <button class="cookie-modal-close" aria-label="Close" data-action="close-modal">×</button>
            </div>
            <div class="cookie-modal-body">
              <p>${text.modalDescription}</p>
              ${categoriesHTML}
            </div>
            <div class="cookie-modal-footer">
              <button class="cookie-banner-btn cookie-banner-btn-secondary" data-action="close-modal">
                Cancel
              </button>
              <button class="cookie-banner-btn cookie-banner-btn-primary" data-action="save-preferences">
                ${text.save}
              </button>
            </div>
          </div>
        </div>
      `;

      document.body.insertAdjacentHTML('beforeend', modalHTML);
      this.modal = document.getElementById(COOKIE_CONFIG.modalId);
      this.attachModalEvents();
    }

    // Attach event listeners to banner
    attachBannerEvents() {
      if (!this.banner) return;

      this.banner.addEventListener('click', (e) => {
        const action = e.target.closest('[data-action]')?.dataset.action;
        
        switch (action) {
          case 'accept-all':
            this.acceptAll();
            break;
          case 'reject-all':
            this.rejectAll();
            break;
          case 'customize':
            this.showModal();
            break;
        }
      });
    }

    // Attach event listeners to modal
    attachModalEvents() {
      if (!this.modal) return;

      this.modal.addEventListener('click', (e) => {
        const action = e.target.closest('[data-action]')?.dataset.action;
        
        switch (action) {
          case 'close-modal':
            this.hideModal();
            break;
          case 'save-preferences':
            this.savePreferences();
            break;
        }
      });

      // Close modal when clicking outside
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) {
          this.hideModal();
        }
      });

      // Close modal with Escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.modal.classList.contains('show')) {
          this.hideModal();
        }
      });
    }

    // Show the banner
    showBanner() {
      if (!this.banner) return;
      
      // Small delay to ensure smooth animation
      setTimeout(() => {
        this.banner.classList.add('show');
        this.banner.classList.add('cookie-slide-up');
      }, 100);
    }

    // Hide the banner
    hideBanner() {
      if (!this.banner) return;
      
      this.banner.classList.remove('show');
      setTimeout(() => {
        this.banner.classList.add('hidden');
      }, 300);
    }

    // Show the modal
    showModal() {
      if (!this.modal) return;
      
      this.modal.classList.add('show');
      this.modal.classList.add('cookie-fade-in');
      
      // Focus management for accessibility
      const firstFocusable = this.modal.querySelector('input[type="checkbox"]:not([disabled])');
      if (firstFocusable) {
        firstFocusable.focus();
      }
    }

    // Hide the modal
    hideModal() {
      if (!this.modal) return;
      
      this.modal.classList.remove('show');
      this.modal.classList.remove('cookie-fade-in');
    }

    // Accept all cookies
    acceptAll() {
      const consent = {
        essential: true,
        analytics: true,
        marketing: true,
        preferences: true
      };
      
      this.storeConsent(consent);
      this.applyConsent();
      this.hideBanner();
    }

    // Reject all non-essential cookies
    rejectAll() {
      const consent = {
        essential: true,
        analytics: false,
        marketing: false,
        preferences: false
      };
      
      this.storeConsent(consent);
      this.applyConsent();
      this.hideBanner();
    }

    // Save custom preferences
    savePreferences() {
      const consent = {
        essential: true // Always true
      };

      // Get values from checkboxes
      Object.keys(COOKIE_CATEGORIES).forEach(categoryKey => {
        const category = COOKIE_CATEGORIES[categoryKey];
        if (!category.alwaysEnabled) {
          const checkbox = this.modal.querySelector(`input[data-category="${categoryKey}"]`);
          consent[categoryKey] = checkbox ? checkbox.checked : false;
        }
      });

      this.storeConsent(consent);
      this.applyConsent();
      this.hideModal();
      this.hideBanner();
    }

    // Apply consent settings
    applyConsent() {
      if (!this.consent) return;

      // Apply analytics consent
      if (this.consent.analytics) {
        this.loadAnalytics();
      }

      // Apply marketing consent
      if (this.consent.marketing) {
        this.loadMarketing();
      }

      // Apply preferences consent
      if (this.consent.preferences) {
        this.loadPreferences();
      }

      // Dispatch custom event for other scripts
      window.dispatchEvent(new CustomEvent('cookieConsentUpdated', {
        detail: this.consent
      }));
    }

    // Load analytics scripts
    loadAnalytics() {
      // Google Analytics
      if (typeof gtag !== 'undefined') {
        gtag('consent', 'update', {
          'analytics_storage': 'granted'
        });
      }
    }

    // Load marketing scripts
    loadMarketing() {
      // Facebook Pixel
      if (typeof fbq !== 'undefined') {
        fbq('consent', 'grant');
      }
    }

    // Load preferences scripts
    loadPreferences() {
      // Load user preferences
      console.log('Loading user preferences...');
    }

    // Get current consent for a category
    getConsent(category) {
      return this.consent && this.consent[category] === true;
    }

    // Update consent (for external use)
    updateConsent(newConsent) {
      this.storeConsent(newConsent);
      this.applyConsent();
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.roomradarCookieBanner = new CookieBanner();
    });
  } else {
    window.roomradarCookieBanner = new CookieBanner();
  }

  // Public API
  window.RoomRadarCookies = {
    // Get consent for a specific category
    getConsent: (category) => {
      return window.roomradarCookieBanner?.getConsent(category) || false;
    },

    // Update consent
    updateConsent: (consent) => {
      window.roomradarCookieBanner?.updateConsent(consent);
    },

    // Show banner again (for testing or user preference changes)
    showBanner: () => {
      window.roomradarCookieBanner?.showBanner();
    },

    // Get current consent object
    getConsentObject: () => {
      return window.roomradarCookieBanner?.consent || null;
    }
  };

})();
