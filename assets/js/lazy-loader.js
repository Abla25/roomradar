// Lazy Loading System for RoomRadar
// Improves performance by loading components only when needed

class LazyLoader {
  constructor() {
    this.loadedComponents = new Set();
    this.loadingPromises = new Map();
  }

  // Lazy load navbar
  async loadNavbar() {
    if (this.loadedComponents.has('navbar')) {
      return;
    }

    if (this.loadingPromises.has('navbar')) {
      return this.loadingPromises.get('navbar');
    }

    const loadPromise = this._loadComponent('navbar', 'assets/navbar.html', 'navbar-container');
    this.loadingPromises.set('navbar', loadPromise);
    
    try {
      await loadPromise;
      this.loadedComponents.add('navbar');
      this.loadingPromises.delete('navbar');
    } catch (error) {
      this.loadingPromises.delete('navbar');
      throw error;
    }
  }

  // Lazy load footer
  async loadFooter() {
    if (this.loadedComponents.has('footer')) {
      return;
    }

    if (this.loadingPromises.has('footer')) {
      return this.loadingPromises.get('footer');
    }

    const loadPromise = this._loadComponent('footer', 'assets/footer.html', 'footer-container');
    this.loadingPromises.set('footer', loadPromise);
    
    try {
      await loadPromise;
      this.loadedComponents.add('footer');
      this.loadingPromises.delete('footer');
    } catch (error) {
      this.loadingPromises.delete('footer');
      throw error;
    }
  }

  // Generic component loader
  async _loadComponent(name, url, containerId) {
    const startTime = performance.now();
    
    try {
      console.log(`🔄 Loading ${name} component...`);
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to load ${name}: ${response.status}`);
      }
      
      const html = await response.text();
      const container = document.getElementById(containerId);
      
      if (container) {
        container.innerHTML = html;
        
        const loadTime = performance.now() - startTime;
        console.log(`✅ ${name} loaded in ${loadTime.toFixed(2)}ms`);
        
        // Trigger custom event for component loaded
        window.dispatchEvent(new CustomEvent(`${name}Loaded`, { detail: { loadTime } }));
        
        return html;
      } else {
        throw new Error(`Container ${containerId} not found`);
      }
    } catch (error) {
      console.error(`❌ Error loading ${name}:`, error);
      throw error;
    }
  }

  // Preload components in background
  preloadComponents(components = ['navbar', 'footer']) {
    components.forEach(component => {
      if (component === 'navbar' && !this.loadedComponents.has('navbar')) {
        this.loadNavbar().catch(() => {}); // Silent fail for preloading
      } else if (component === 'footer' && !this.loadedComponents.has('footer')) {
        this.loadFooter().catch(() => {}); // Silent fail for preloading
      }
    });
  }

  // Check if component is loaded
  isLoaded(component) {
    return this.loadedComponents.has(component);
  }

  // Clear cache (useful for testing)
  clearCache() {
    this.loadedComponents.clear();
    this.loadingPromises.clear();
  }
}

// Create global instance
window.lazyLoader = new LazyLoader();

// Export for module usage
export default window.lazyLoader;

