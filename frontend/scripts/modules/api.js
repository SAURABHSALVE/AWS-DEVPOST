/**
 * API Service Module
 * Handles all communication with the backend API
 */

class ApiService {
  constructor() {
    // Configure base URL for backend connection
    this.baseUrl = 'http://localhost:8080/api';
    this.healthUrl = 'http://localhost:8080';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  /**
   * Make HTTP request with error handling
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>} Response data
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          await this.parseErrorResponse(response)
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      // Network or other errors
      throw new ApiError(
        'Network error or server unavailable',
        0,
        { message: error.message }
      );
    }
  }

  /**
   * Parse error response from server
   * @param {Response} response - Fetch response object
   * @returns {Promise<Object>} Error details
   */
  async parseErrorResponse(response) {
    try {
      return await response.json();
    } catch {
      return { message: response.statusText };
    }
  }

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response data
   */
  async get(endpoint, params = {}) {
    let url = endpoint;
    
    // Add query parameters if provided
    if (Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          searchParams.append(key, params[key]);
        }
      });
      url += '?' + searchParams.toString();
    }

    return this.request(url);
  }

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body data
   * @returns {Promise<Object>} Response data
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // Content-specific API methods

  /**
   * Submit content brief for processing
   * @param {Object} contentBrief - Content brief data
   * @returns {Promise<Object>} Content request response
   */
  async submitContentBrief(contentBrief) {
    return this.post('/content/generate', contentBrief);
  }

  /**
   * Get content generation status
   * @param {string} requestId - Content request ID
   * @returns {Promise<Object>} Status response
   */
  async getContentStatus(requestId) {
    return this.get(`/content/status/${requestId}`);
  }

  /**
   * Get generated content
   * @param {string} requestId - Content request ID
   * @returns {Promise<Object>} Generated content
   */
  async getGeneratedContent(requestId) {
    return this.get(`/content/result/${requestId}`);
  }

  /**
   * Get content history
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Object>} Content history
   */
  async getContentHistory(filters = {}) {
    return this.get('/content/history', filters);
  }

  /**
   * Get cultural profiles
   * @returns {Promise<Object>} Available cultural profiles
   */
  async getCulturalProfiles() {
    return this.get('/cultural/profiles');
  }

  /**
   * Get supported languages
   * @returns {Promise<Object>} Supported languages
   */
  async getSupportedLanguages() {
    return this.get('/cultural/languages');
  }

  /**
   * Health check
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    const url = `${this.healthUrl}/health`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new ApiError(`Health check failed: ${response.status}`, response.status);
    }
    return await response.json();
  }

  /**
   * API status check
   * @returns {Promise<Object>} API status
   */
  async apiStatus() {
    return this.get('/status');
  }
}

/**
 * Custom API Error class
 */
class ApiError extends Error {
  constructor(message, status, details = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }

  /**
   * Check if error is a specific HTTP status
   * @param {number} status - HTTP status code
   * @returns {boolean} True if error matches status
   */
  isStatus(status) {
    return this.status === status;
  }

  /**
   * Check if error is a client error (4xx)
   * @returns {boolean} True if client error
   */
  isClientError() {
    return this.status >= 400 && this.status < 500;
  }

  /**
   * Check if error is a server error (5xx)
   * @returns {boolean} True if server error
   */
  isServerError() {
    return this.status >= 500 && this.status < 600;
  }

  /**
   * Check if error is a network error
   * @returns {boolean} True if network error
   */
  isNetworkError() {
    return this.status === 0;
  }
}

// Create singleton instance
const apiService = new ApiService();

// Export for use in other modules
window.ApiService = ApiService;
window.ApiError = ApiError;
window.api = apiService;