/**
 * REST API client for Circle Measurement System Web Dashboard
 */

const API = {
    baseUrl: '',  // Will be set based on current location

    /**
     * Initialize API with base URL
     */
    init() {
        this.baseUrl = `${window.location.protocol}//${window.location.host}`;
    },

    /**
     * Make API request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },

    /**
     * Get system status
     * @returns {Promise} System status data
     */
    async getStatus() {
        return this.request('/api/status');
    },

    /**
     * Get production statistics
     * @returns {Promise} Statistics data
     */
    async getStatistics() {
        return this.request('/api/statistics');
    },

    /**
     * Get recipe list
     * @returns {Promise} Recipe list data
     */
    async getRecipes() {
        return this.request('/api/recipes');
    },

    /**
     * Get recipe details
     * @param {string} name - Recipe name
     * @returns {Promise} Recipe details
     */
    async getRecipe(name) {
        return this.request(`/api/recipes/${encodeURIComponent(name)}`);
    },

    /**
     * Get IO status
     * @returns {Promise} IO status data
     */
    async getIOStatus() {
        return this.request('/api/io/status');
    },

    /**
     * Get calibration info
     * @returns {Promise} Calibration data
     */
    async getCalibration() {
        return this.request('/api/calibration');
    },

    /**
     * Get measurement history
     * @param {number} limit - Maximum items to return
     * @param {number} offset - Skip first N items
     * @returns {Promise} History data
     */
    async getHistory(limit = 100, offset = 0) {
        return this.request(`/api/history?limit=${limit}&offset=${offset}`);
    },

    /**
     * Export statistics as CSV
     */
    exportStatistics() {
        const url = `${this.baseUrl}/api/statistics/export`;
        window.open(url, '_blank');
    },

    /**
     * Get video stream URL
     * @returns {string} MJPEG stream URL
     */
    getVideoStreamUrl() {
        return `${this.baseUrl}/stream/video`;
    }
};

// Initialize API on load
API.init();
