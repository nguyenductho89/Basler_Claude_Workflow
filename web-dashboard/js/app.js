/**
 * Main application for Circle Measurement System Web Dashboard
 */

const App = {
    /**
     * Initialize the application
     */
    init() {
        console.log('Initializing Web Dashboard...');

        // Set up video stream
        this.setupVideoStream();

        // Connect WebSocket
        this.setupWebSocket();

        // Load initial data
        this.loadInitialData();

        // Set up periodic updates
        this.setupPeriodicUpdates();

        console.log('Web Dashboard initialized');
    },

    /**
     * Set up video stream
     */
    setupVideoStream() {
        const videoElement = document.getElementById('videoStream');
        const overlay = document.getElementById('videoOverlay');

        if (videoElement) {
            videoElement.src = API.getVideoStreamUrl();

            videoElement.onload = () => {
                if (overlay) {
                    overlay.classList.add('hidden');
                }
            };

            videoElement.onerror = () => {
                if (overlay) {
                    overlay.classList.remove('hidden');
                    overlay.querySelector('span').textContent = 'Video unavailable';
                }
            };
        }
    },

    /**
     * Set up WebSocket connection and handlers
     */
    setupWebSocket() {
        // Register event handlers
        WebSocketClient.on('detection_result', (data) => {
            this.updateDetectionResults(data);
        });

        WebSocketClient.on('statistics_update', (data) => {
            this.updateStatistics(data);
        });

        WebSocketClient.on('io_status', (data) => {
            this.updateIOStatus(data);
        });

        WebSocketClient.on('system_status', (data) => {
            this.updateSystemStatus(data);
        });

        WebSocketClient.on('recipe_changed', (data) => {
            this.updateRecipeInfo(data);
        });

        // Connect
        WebSocketClient.connect();
    },

    /**
     * Load initial data from API
     */
    async loadInitialData() {
        try {
            // Load status
            const status = await API.getStatus();
            this.updateSystemStatus(status);

            // Load statistics
            const stats = await API.getStatistics();
            this.updateStatistics(stats);

            // Load recipes
            const recipes = await API.getRecipes();
            if (recipes.current) {
                const recipe = await API.getRecipe(recipes.current);
                this.updateRecipeInfo(recipe);
            }

            // Load history
            const history = await API.getHistory(50);
            this.updateHistory(history.items);

            // Load IO status
            const io = await API.getIOStatus();
            this.updateIOStatus(io);

        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    },

    /**
     * Set up periodic updates for data that doesn't come via WebSocket
     */
    setupPeriodicUpdates() {
        // Update statistics every 5 seconds
        setInterval(async () => {
            try {
                const stats = await API.getStatistics();
                this.updateStatistics(stats);
            } catch (error) {
                console.error('Error updating statistics:', error);
            }
        }, 5000);

        // Update IO status every 500ms
        setInterval(async () => {
            try {
                const io = await API.getIOStatus();
                this.updateIOStatus(io);
            } catch (error) {
                console.error('Error updating IO status:', error);
            }
        }, 500);
    },

    /**
     * Update detection results display
     * @param {object} data - Detection result data
     */
    updateDetectionResults(data) {
        const container = document.getElementById('resultsContainer');
        const timeElement = document.getElementById('detectionTime');

        if (!container) return;

        // Handle different data formats
        let circles = [];
        if (Array.isArray(data)) {
            circles = data;
        } else if (data && data.circles) {
            circles = data.circles;
        }

        if (circles.length === 0) {
            container.innerHTML = '<div class="no-results">No circles detected</div>';
            return;
        }

        let html = '';
        circles.forEach((circle, index) => {
            const status = (circle.status || 'NONE').toUpperCase();
            const statusClass = status === 'OK' ? 'ok' : status === 'NG' ? 'ng' : '';

            html += `
                <div class="circle-result ${statusClass}">
                    <span class="diameter">${(circle.diameter_mm || 0).toFixed(3)} mm</span>
                    <span class="status ${statusClass}">${status}</span>
                </div>
            `;
        });

        container.innerHTML = html;

        // Update detection time
        if (timeElement && data.detection_time_ms) {
            timeElement.textContent = `Detection time: ${data.detection_time_ms.toFixed(1)} ms`;
        }

        // Add to history
        this.addToHistory(circles);
    },

    /**
     * Update statistics display
     * @param {object} data - Statistics data
     */
    updateStatistics(data) {
        const elements = {
            statTotal: data.total_inspections || 0,
            statOk: data.ok_count || 0,
            statNg: data.ng_count || 0,
            statOkRate: `${(data.ok_rate || 0).toFixed(1)}%`,
            statThroughput: `${(data.throughput_per_minute || 0).toFixed(1)}/min`,
            statRuntime: this.formatRuntime(data.runtime_seconds || 0)
        };

        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }
    },

    /**
     * Update IO status display
     * @param {object} data - IO status data
     */
    updateIOStatus(data) {
        const setLed = (id, active) => {
            const element = document.getElementById(id);
            if (element) {
                if (active) {
                    element.classList.add('active');
                } else {
                    element.classList.remove('active');
                }
            }
        };

        setLed('ioTrigger', data.trigger_state);
        setLed('ioReady', data.system_ready);
        setLed('ioOk', data.result_ok);
        setLed('ioNg', data.result_ng);
        setLed('ioEnable', data.system_enable);

        const recipeElement = document.getElementById('ioRecipe');
        if (recipeElement) {
            recipeElement.textContent = data.recipe_index || 0;
        }
    },

    /**
     * Update system status display
     * @param {object} data - System status data
     */
    updateSystemStatus(data) {
        const fpsElement = document.getElementById('fpsDisplay');
        const cameraElement = document.getElementById('cameraStatus');

        if (fpsElement) {
            fpsElement.textContent = `FPS: ${(data.fps || 0).toFixed(1)}`;
        }

        if (cameraElement) {
            cameraElement.textContent = `Camera: ${data.camera_connected ? 'Connected' : 'Disconnected'}`;
        }
    },

    /**
     * Update recipe info display
     * @param {object} data - Recipe data
     */
    updateRecipeInfo(data) {
        const nameElement = document.getElementById('recipeName');
        const nominalElement = document.getElementById('recipeNominal');
        const toleranceElement = document.getElementById('recipeTolerance');

        if (nameElement) {
            nameElement.textContent = `Recipe: ${data.name || '--'}`;
        }

        if (nominalElement && data.tolerance_config) {
            nominalElement.textContent = `Nominal: ${data.tolerance_config.nominal_mm || '--'} mm`;
        }

        if (toleranceElement && data.tolerance_config) {
            toleranceElement.textContent = `Tolerance: +/- ${data.tolerance_config.tolerance_mm || '--'} mm`;
        }
    },

    /**
     * Update history display
     * @param {array} items - History items
     */
    updateHistory(items) {
        const tbody = document.getElementById('historyBody');
        if (!tbody) return;

        let html = '';
        items.forEach(item => {
            const time = new Date(item.timestamp).toLocaleTimeString();
            const circles = item.circles || [];
            const diameter = circles.length > 0 ? circles[0].diameter_mm.toFixed(3) : '--';
            const status = (item.overall_status || 'NONE').toUpperCase();
            const statusClass = status === 'OK' ? 'status-ok' : status === 'NG' ? 'status-ng' : '';

            html += `
                <tr>
                    <td>${time}</td>
                    <td>${diameter}</td>
                    <td class="${statusClass}">${status}</td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    },

    /**
     * Add detection result to history table
     * @param {array} circles - Detected circles
     */
    addToHistory(circles) {
        const tbody = document.getElementById('historyBody');
        if (!tbody || circles.length === 0) return;

        const time = new Date().toLocaleTimeString();
        const diameter = circles[0].diameter_mm.toFixed(3);
        const status = (circles[0].status || 'NONE').toUpperCase();
        const statusClass = status === 'OK' ? 'status-ok' : status === 'NG' ? 'status-ng' : '';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${time}</td>
            <td>${diameter}</td>
            <td class="${statusClass}">${status}</td>
        `;

        tbody.insertBefore(row, tbody.firstChild);

        // Keep only last 50 rows
        while (tbody.children.length > 50) {
            tbody.removeChild(tbody.lastChild);
        }
    },

    /**
     * Format runtime in HH:MM:SS
     * @param {number} seconds - Runtime in seconds
     * @returns {string} Formatted time
     */
    formatRuntime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        return [hours, minutes, secs]
            .map(v => v.toString().padStart(2, '0'))
            .join(':');
    }
};

/**
 * Export statistics (called from button)
 */
function exportStatistics() {
    API.exportStatistics();
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
