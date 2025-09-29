/**
 * Simple Router Module
 * Handles client-side navigation and page routing
 */

class Router {
  constructor() {
    this.routes = new Map();
    this.currentRoute = null;
    this.basePath = '';
    
    // Initialize router
    this.init();
  }

  /**
   * Initialize the router
   */
  init() {
    // Handle browser back/forward buttons
    window.addEventListener('popstate', (event) => {
      this.handleRoute(window.location.pathname);
    });

    // Handle initial page load
    this.handleRoute(window.location.pathname);
    
    // Handle navigation clicks
    this.setupNavigationHandlers();
  }

  /**
   * Register a route
   * @param {string} path - Route path
   * @param {Function} handler - Route handler function
   */
  register(path, handler) {
    this.routes.set(path, handler);
  }

  /**
   * Navigate to a route
   * @param {string} path - Target path
   * @param {boolean} pushState - Whether to push to browser history
   */
  navigate(path, pushState = true) {
    if (pushState && path !== window.location.pathname) {
      window.history.pushState({}, '', path);
    }
    
    this.handleRoute(path);
  }

  /**
   * Handle route navigation
   * @param {string} path - Current path
   */
  handleRoute(path) {
    // Normalize path
    const normalizedPath = this.normalizePath(path);
    
    // Find matching route
    const handler = this.routes.get(normalizedPath);
    
    if (handler) {
      this.currentRoute = normalizedPath;
      handler(normalizedPath);
    } else {
      // Handle 404 or default route
      this.handle404(normalizedPath);
    }
    
    // Update active navigation links
    this.updateActiveNavigation(normalizedPath);
  }

  /**
   * Normalize path for consistent routing
   * @param {string} path - Raw path
   * @returns {string} Normalized path
   */
  normalizePath(path) {
    // Remove base path if present
    if (this.basePath && path.startsWith(this.basePath)) {
      path = path.substring(this.basePath.length);
    }
    
    // Ensure path starts with /
    if (!path.startsWith('/')) {
      path = '/' + path;
    }
    
    // Remove trailing slash (except for root)
    if (path.length > 1 && path.endsWith('/')) {
      path = path.slice(0, -1);
    }
    
    return path;
  }

  /**
   * Handle 404 errors
   * @param {string} path - Requested path
   */
  handle404(path) {
    console.warn(`Route not found: ${path}`);
    
    // For SPA, we might want to redirect to home or show 404 page
    // For now, just log the error
    this.currentRoute = null;
  }

  /**
   * Setup navigation click handlers
   */
  setupNavigationHandlers() {
    document.addEventListener('click', (event) => {
      const link = event.target.closest('a[href]');
      
      if (!link) return;
      
      const href = link.getAttribute('href');
      
      // Only handle internal links
      if (this.isInternalLink(href)) {
        event.preventDefault();
        this.navigate(href);
      }
    });
  }

  /**
   * Check if link is internal
   * @param {string} href - Link href
   * @returns {boolean} True if internal link
   */
  isInternalLink(href) {
    // Skip external links, mailto, tel, etc.
    if (href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('tel:')) {
      return false;
    }
    
    // Skip hash links for now
    if (href.startsWith('#')) {
      return false;
    }
    
    return true;
  }

  /**
   * Update active navigation links
   * @param {string} currentPath - Current active path
   */
  updateActiveNavigation(currentPath) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });
    
    // Add active class to current page link
    const activeLink = document.querySelector(`.nav-link[href="${currentPath}"]`) ||
                      document.querySelector(`.nav-link[href=".${currentPath}"]`) ||
                      document.querySelector(`.nav-link[href="..${currentPath}"]`);
    
    if (activeLink) {
      activeLink.classList.add('active');
    }
  }

  /**
   * Get current route
   * @returns {string|null} Current route path
   */
  getCurrentRoute() {
    return this.currentRoute;
  }

  /**
   * Check if currently on a specific route
   * @param {string} path - Path to check
   * @returns {boolean} True if on specified route
   */
  isCurrentRoute(path) {
    return this.currentRoute === this.normalizePath(path);
  }
}

/**
 * Page Manager - Handles page-specific functionality
 */
class PageManager {
  constructor() {
    this.currentPage = null;
    this.pageHandlers = new Map();
  }

  /**
   * Register page handler
   * @param {string} pageName - Page identifier
   * @param {Object} handler - Page handler with init/destroy methods
   */
  register(pageName, handler) {
    this.pageHandlers.set(pageName, handler);
  }

  /**
   * Load page
   * @param {string} pageName - Page to load
   * @param {Object} data - Optional data to pass to page
   */
  loadPage(pageName, data = {}) {
    // Cleanup current page
    if (this.currentPage && this.pageHandlers.has(this.currentPage)) {
      const currentHandler = this.pageHandlers.get(this.currentPage);
      if (currentHandler.destroy) {
        currentHandler.destroy();
      }
    }

    // Load new page
    if (this.pageHandlers.has(pageName)) {
      const handler = this.pageHandlers.get(pageName);
      if (handler.init) {
        handler.init(data);
      }
      this.currentPage = pageName;
    }
  }

  /**
   * Get current page
   * @returns {string|null} Current page name
   */
  getCurrentPage() {
    return this.currentPage;
  }
}

// Utility functions for common DOM operations
const DOMUtils = {
  /**
   * Show loading state
   * @param {HTMLElement} element - Element to show loading in
   * @param {string} message - Loading message
   */
  showLoading(element, message = 'Loading...') {
    element.innerHTML = `
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">${message}</div>
      </div>
    `;
  },

  /**
   * Show error message
   * @param {HTMLElement} element - Element to show error in
   * @param {string} message - Error message
   */
  showError(element, message = 'An error occurred') {
    element.innerHTML = `
      <div class="alert alert-error">
        <strong>Error:</strong> ${message}
      </div>
    `;
  },

  /**
   * Show success message
   * @param {HTMLElement} element - Element to show success in
   * @param {string} message - Success message
   */
  showSuccess(element, message = 'Success!') {
    element.innerHTML = `
      <div class="alert alert-success">
        <strong>Success:</strong> ${message}
      </div>
    `;
  },

  /**
   * Create element with classes and content
   * @param {string} tag - HTML tag
   * @param {string|Array} classes - CSS classes
   * @param {string} content - Inner content
   * @returns {HTMLElement} Created element
   */
  createElement(tag, classes = [], content = '') {
    const element = document.createElement(tag);
    
    if (typeof classes === 'string') {
      classes = [classes];
    }
    
    classes.forEach(cls => element.classList.add(cls));
    
    if (content) {
      element.innerHTML = content;
    }
    
    return element;
  }
};

// Create singleton instances
const router = new Router();
const pageManager = new PageManager();

// Export for use in other modules
window.Router = Router;
window.PageManager = PageManager;
window.DOMUtils = DOMUtils;
window.router = router;
window.pageManager = pageManager;