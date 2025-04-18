// GAIA Debug Script
// Add this to a new file named debug.js and include it in your index.html
// before your app.js file

// Debug configuration
const DEBUG = true;
const LOG_LEVEL = 'info'; // 'debug', 'info', 'warn', 'error'

// Logger function with levels
const Logger = {
    debug: function(message, data) {
        if (DEBUG && ['debug'].includes(LOG_LEVEL)) {
            console.debug(`[DEBUG] ${message}`, data || '');
        }
    },
    info: function(message, data) {
        if (DEBUG && ['debug', 'info'].includes(LOG_LEVEL)) {
            console.info(`[INFO] ${message}`, data || '');
        }
    },
    warn: function(message, data) {
        if (DEBUG && ['debug', 'info', 'warn'].includes(LOG_LEVEL)) {
            console.warn(`[WARN] ${message}`, data || '');
        }
    },
    error: function(message, data) {
        if (DEBUG && ['debug', 'info', 'warn', 'error'].includes(LOG_LEVEL)) {
            console.error(`[ERROR] ${message}`, data || '');
        }
    }
};

// Check if required libraries are loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check for marked.js
    if (typeof marked === 'undefined') {
        Logger.error('marked.js is not loaded!');
        // Add visible error to page
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = 'Error: marked.js library not loaded. Check console for details.';
        document.body.prepend(errorDiv);
    } else {
        Logger.info('marked.js loaded successfully', marked.version);
    }
    
    // Check for highlight.js
    if (typeof hljs === 'undefined') {
        Logger.error('highlight.js is not loaded!');
    } else {
        Logger.info('highlight.js loaded successfully');
    }
    
    // Monitor API requests
    const originalFetch = window.fetch;
    window.fetch = function() {
        Logger.debug('Fetch request', arguments[0]);
        const startTime = performance.now();
        
        return originalFetch.apply(this, arguments)
            .then(response => {
                const endTime = performance.now();
                Logger.info(`Fetch completed in ${Math.round(endTime - startTime)}ms`, {
                    url: arguments[0],
                    status: response.status
                });
                return response;
            })
            .catch(error => {
                Logger.error('Fetch error', { url: arguments[0], error });
                throw error;
            });
    };
    
    // Add performance monitoring
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            Logger.info(`Page load time: ${pageLoadTime}ms`);
            
            // Report on resource loading
            const resources = window.performance.getEntriesByType('resource');
            const slowResources = resources
                .filter(r => r.duration > 500)
                .sort((a, b) => b.duration - a.duration);
                
            if (slowResources.length > 0) {
                Logger.warn('Slow resources detected', slowResources.slice(0, 5));
            }
        }, 0);
    });
});

// Add retry mechanism for API calls
function fetchWithRetry(url, options = {}, maxRetries = 3) {
    return new Promise((resolve, reject) => {
        const attempt = (retryCount) => {
            fetch(url, options)
                .then(response => {
                    if (response.ok) {
                        resolve(response);
                    } else {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                })
                .catch(error => {
                    if (retryCount < maxRetries) {
                        const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
                        Logger.warn(`Retrying fetch in ${delay}ms (attempt ${retryCount + 1}/${maxRetries})`, { url, error });
                        setTimeout(() => attempt(retryCount + 1), delay);
                    } else {
                        Logger.error('Max retries reached', { url, error });
                        reject(error);
                    }
                });
        };
        
        attempt(0);
    });
}

// Export functions to global scope
window.Logger = Logger;
window.fetchWithRetry = fetchWithRetry;

// Test markdown rendering
function testMarkdownRendering() {
    try {
        const testMarkdown = "# Test\n\nThis is a **test** of markdown rendering.";
        const result = marked(testMarkdown);
        Logger.info('Markdown test result', result);
        return true;
    } catch (e) {
        Logger.error('Markdown rendering test failed', e);
        return false;
    }
}

// Run the test once libraries should be loaded
setTimeout(testMarkdownRendering, 1000);
