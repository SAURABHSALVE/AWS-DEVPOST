/**
 * Home Page JavaScript
 * Handles home page functionality and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
  initHomePage();
});

/**
 * Initialize home page functionality
 */
function initHomePage() {
  // Check API health on page load
  checkApiHealth();
  
  // Setup feature card interactions
  setupFeatureCards();
  
  // Setup call-to-action buttons
  setupCTAButtons();
}

/**
 * Check API health and show status
 */
async function checkApiHealth() {
  try {
    const health = await window.api.healthCheck();
    console.log('API Health:', health);
    
    // Could show a subtle indicator if needed
    showApiStatus('healthy');
  } catch (error) {
    console.warn('API Health Check Failed:', error);
    showApiStatus('unhealthy');
  }
}

/**
 * Show API status indicator
 * @param {string} status - API status (healthy/unhealthy)
 */
function showApiStatus(status) {
  // For now, just log. Could add a subtle indicator later
  if (status === 'unhealthy') {
    console.warn('Backend API appears to be unavailable');
  }
}

/**
 * Setup feature card hover effects and interactions
 */
function setupFeatureCards() {
  const featureCards = document.querySelectorAll('.feature-card');
  
  featureCards.forEach(card => {
    // Add click handler for potential future functionality
    card.addEventListener('click', function() {
      const title = this.querySelector('h3').textContent;
      console.log(`Feature clicked: ${title}`);
      
      // Could navigate to specific feature or show more info
      // For now, just navigate to content creation
      window.router.navigate('/pages/content-brief.html');
    });
    
    // Add keyboard navigation support
    card.setAttribute('tabindex', '0');
    card.addEventListener('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        this.click();
      }
    });
  });
}

/**
 * Setup call-to-action button functionality
 */
function setupCTAButtons() {
  const ctaButtons = document.querySelectorAll('.hero-actions .btn');
  
  ctaButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      const href = this.getAttribute('href');
      
      // Add analytics or tracking here if needed
      console.log(`CTA clicked: ${href}`);
      
      // Add loading state for better UX
      if (href.includes('content-brief')) {
        this.classList.add('btn-loading');
        
        // Remove loading state after navigation
        setTimeout(() => {
          this.classList.remove('btn-loading');
        }, 1000);
      }
    });
  });
}

/**
 * Home page handler for page manager
 */
const homePageHandler = {
  init: function(data = {}) {
    console.log('Home page initialized');
    
    // Any additional initialization when navigating to home
    this.setupDynamicContent();
  },
  
  destroy: function() {
    console.log('Home page cleanup');
    
    // Cleanup any event listeners or timers if needed
  },
  
  setupDynamicContent: function() {
    // Could load dynamic content like recent activity, stats, etc.
    // For now, just ensure everything is properly initialized
    
    // Example: Update feature descriptions based on user preferences
    this.updateFeatureDescriptions();
  },
  
  updateFeatureDescriptions: function() {
    // Could customize feature descriptions based on user data
    // For now, keep static content
  }
};

// Register with page manager
if (window.pageManager) {
  window.pageManager.register('home', homePageHandler);
}

// Export for potential use in other modules
window.homePageHandler = homePageHandler;