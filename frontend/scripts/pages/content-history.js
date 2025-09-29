/**
 * Content History Page JavaScript
 * Handles content history display and management
 */

document.addEventListener('DOMContentLoaded', function() {
  initContentHistoryPage();
});

/**
 * Initialize content history page functionality
 */
function initContentHistoryPage() {
  console.log('Content History page initialized');
  
  // Setup history placeholder for now
  setupHistoryPlaceholder();
  
  // Load content history
  loadContentHistory();
}

/**
 * Setup history placeholder content
 * This will be replaced with actual history implementation in later tasks
 */
function setupHistoryPlaceholder() {
  const contentList = document.getElementById('content-list');
  
  if (contentList) {
    // Show loading state initially
    window.DOMUtils.showLoading(contentList, 'Loading content history...');
    
    // Simulate loading delay
    setTimeout(() => {
      showPlaceholderHistory(contentList);
    }, 1000);
  }
}

/**
 * Show placeholder history content
 * @param {HTMLElement} container - Container element
 */
function showPlaceholderHistory(container) {
  container.innerHTML = `
    <div class="empty-state">
      <h3>No Content History Yet</h3>
      <p>
        Your generated content will appear here once you start creating content briefs.
        The history will show all your past content generation requests with their status and results.
      </p>
      <div class="mt-6">
        <a href="content-brief.html" class="btn btn-primary">Create Your First Content</a>
      </div>
    </div>
    
    <div class="mt-8">
      <div class="alert alert-info">
        <strong>Coming Soon:</strong> Content history will include:
        <ul style="margin: 1rem 0 0 1.5rem;">
          <li>List of all content generation requests</li>
          <li>Status tracking (pending, processing, completed, failed)</li>
          <li>Content previews and full results</li>
          <li>Cultural adaptation notes and quality scores</li>
          <li>Export and sharing options</li>
          <li>Search and filtering capabilities</li>
        </ul>
      </div>
    </div>
  `;
}

/**
 * Load content history from API
 */
async function loadContentHistory() {
  try {
    console.log('Loading content history...');
    
    // This will be implemented when the backend is ready
    // const history = await window.api.getContentHistory();
    // displayContentHistory(history);
    
    console.log('Content history loaded (placeholder)');
  } catch (error) {
    console.warn('Could not load content history:', error);
    showHistoryError();
  }
}

/**
 * Display content history
 * @param {Array} historyItems - Array of content history items
 */
function displayContentHistory(historyItems) {
  const contentList = document.getElementById('content-list');
  
  if (!contentList) return;
  
  if (!historyItems || historyItems.length === 0) {
    showEmptyHistory(contentList);
    return;
  }
  
  // Clear container
  contentList.innerHTML = '';
  
  // Create history cards
  historyItems.forEach(item => {
    const card = createHistoryCard(item);
    contentList.appendChild(card);
  });
}

/**
 * Create history card element
 * @param {Object} item - History item data
 * @returns {HTMLElement} Card element
 */
function createHistoryCard(item) {
  const card = window.DOMUtils.createElement('div', ['card', 'content-card']);
  
  card.innerHTML = `
    <div class="card-header">
      <div>
        <h3 class="card-title">${item.title || 'Untitled Content'}</h3>
        <div class="content-meta">
          <span>Created: ${new Date(item.createdAt).toLocaleDateString()}</span>
          <span>Language: ${item.targetLanguage} (${item.targetRegion})</span>
          <span>Type: ${item.contentType}</span>
        </div>
      </div>
      <div class="content-status ${item.status}">
        ${item.status}
      </div>
    </div>
    
    <div class="card-body">
      <div class="content-preview">
        ${item.preview || 'No preview available'}
      </div>
      
      ${item.tags ? `
        <div class="content-tags">
          ${item.tags.map(tag => `<span class="content-tag">${tag}</span>`).join('')}
        </div>
      ` : ''}
    </div>
    
    <div class="card-footer">
      <div class="content-meta">
        ${item.qualityScore ? `Quality Score: ${item.qualityScore}%` : ''}
      </div>
      <div class="card-actions">
        <button class="btn btn-sm btn-secondary" onclick="viewContent('${item.id}')">
          View
        </button>
        ${item.status === 'completed' ? `
          <button class="btn btn-sm btn-primary" onclick="exportContent('${item.id}')">
            Export
          </button>
        ` : ''}
      </div>
    </div>
  `;
  
  // Add click handler for card
  card.addEventListener('click', (event) => {
    // Don't trigger if clicking on buttons
    if (!event.target.closest('button')) {
      viewContent(item.id);
    }
  });
  
  return card;
}

/**
 * Show empty history state
 * @param {HTMLElement} container - Container element
 */
function showEmptyHistory(container) {
  container.innerHTML = `
    <div class="empty-state">
      <h3>No Content History</h3>
      <p>You haven't created any content yet. Start by creating your first content brief!</p>
      <a href="content-brief.html" class="btn btn-primary">Create Content</a>
    </div>
  `;
}

/**
 * Show error when history cannot be loaded
 */
function showHistoryError() {
  const contentList = document.getElementById('content-list');
  
  if (contentList) {
    window.DOMUtils.showError(
      contentList, 
      'Could not load content history. Please try again later.'
    );
  }
}

/**
 * View specific content item
 * @param {string} contentId - Content ID
 */
function viewContent(contentId) {
  console.log(`Viewing content: ${contentId}`);
  
  // This will navigate to content detail page when implemented
  // For now, just show an alert
  alert(`Content viewing will be implemented in later tasks. Content ID: ${contentId}`);
}

/**
 * Export content item
 * @param {string} contentId - Content ID
 */
function exportContent(contentId) {
  console.log(`Exporting content: ${contentId}`);
  
  // This will implement content export when backend is ready
  alert(`Content export will be implemented in later tasks. Content ID: ${contentId}`);
}

/**
 * Content history page handler for page manager
 */
const contentHistoryPageHandler = {
  init: function(data = {}) {
    console.log('Content History page handler initialized');
    
    // Setup search and filtering
    this.setupSearch();
    
    // Setup refresh functionality
    this.setupRefresh();
  },
  
  destroy: function() {
    console.log('Content History page cleanup');
    
    // Clear any polling timers
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  
  setupSearch: function() {
    // Will implement search functionality
    console.log('Search setup (placeholder)');
  },
  
  setupRefresh: function() {
    // Auto-refresh history periodically
    console.log('Auto-refresh setup (placeholder)');
    
    // Refresh every 30 seconds if there are pending items
    this.refreshTimer = setInterval(() => {
      this.checkForUpdates();
    }, 30000);
  },
  
  checkForUpdates: function() {
    // Check for status updates on pending content
    console.log('Checking for content updates...');
    
    // Will implement when backend is ready
  },
  
  refreshHistory: function() {
    // Manually refresh the history
    loadContentHistory();
  }
};

// Register with page manager
if (window.pageManager) {
  window.pageManager.register('content-history', contentHistoryPageHandler);
}

// Export for potential use in other modules
window.contentHistoryPageHandler = contentHistoryPageHandler;
window.viewContent = viewContent;
window.exportContent = exportContent;