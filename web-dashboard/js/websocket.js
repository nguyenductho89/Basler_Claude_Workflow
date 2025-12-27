/**
 * WebSocket client for Circle Measurement System Web Dashboard
 */

const WebSocketClient = {
    socket: null,
    reconnectInterval: 3000,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,
    handlers: {},

    /**
     * Connect to WebSocket server
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/live`;

        console.log('Connecting to WebSocket:', wsUrl);

        try {
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
            };

            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.scheduleReconnect();
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.socket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    },

    /**
     * Handle incoming WebSocket message
     * @param {string} data - Raw message data
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            const { event, data: eventData } = message;

            // Call registered handler
            if (this.handlers[event]) {
                this.handlers[event](eventData);
            }

            // Always log for debugging
            console.debug('WebSocket event:', event, eventData);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    },

    /**
     * Register event handler
     * @param {string} eventType - Event type to handle
     * @param {function} handler - Handler function
     */
    on(eventType, handler) {
        this.handlers[eventType] = handler;
    },

    /**
     * Remove event handler
     * @param {string} eventType - Event type to remove
     */
    off(eventType) {
        delete this.handlers[eventType];
    },

    /**
     * Send message to server
     * @param {object} data - Data to send
     */
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    },

    /**
     * Send ping to keep connection alive
     */
    ping() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send('ping');
        }
    },

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts})`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnect attempts reached');
        }
    },

    /**
     * Update connection status in UI
     * @param {boolean} connected - Connection status
     */
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            const dot = statusElement.querySelector('.status-dot');
            const text = statusElement.querySelector('.status-text');

            if (connected) {
                dot.classList.remove('disconnected');
                dot.classList.add('connected');
                text.textContent = 'Connected';
            } else {
                dot.classList.remove('connected');
                dot.classList.add('disconnected');
                text.textContent = 'Disconnected';
            }
        }
    },

    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    },

    /**
     * Check if connected
     * @returns {boolean} Connection status
     */
    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }
};
