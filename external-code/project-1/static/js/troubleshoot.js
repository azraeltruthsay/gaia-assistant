// GAIA Troubleshooting Panel
document.addEventListener('DOMContentLoaded', function() {
    console.log('GAIA Troubleshooting tool loaded');

    // Create diagnostic panel
    const diagnosticPanel = document.createElement('div');
    diagnosticPanel.id = 'diagnostic-panel';
    diagnosticPanel.style.cssText = `
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(30, 58, 138, 0.9);
        color: white;
        padding: 10px;
        font-family: monospace;
        font-size: 12px;
        max-height: 300px;
        overflow-y: auto;
        z-index: 9999;
        display: none;
        border-top: 2px solid #0ea5e9;
    `;
    
    // Add toggle button
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Show Diagnostics';
    toggleButton.style.cssText = `
        position: fixed;
        bottom: 10px;
        right: 10px;
        z-index: 10000;
        padding: 5px 10px;
        background: #1e3a8a;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        opacity: 0.8;
    `;
    
    // Create control panel
    const controlPanel = document.createElement('div');
    controlPanel.style.cssText = `
        display: flex;
        justify-content: space-between;
        padding: 5px;
        background: rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    `;
    
    controlPanel.innerHTML = `
        <div>
            <button id="run-diagnostics" style="background:#0ea5e9;border:none;color:white;padding:3px 8px;border-radius:3px;margin-right:5px;">Run Diagnostics</button>
            <button id="test-chat" style="background:#10b981;border:none;color:white;padding:3px 8px;border-radius:3px;margin-right:5px;">Test Chat</button>
            <button id="clear-logs" style="background:#ef4444;border:none;color:white;padding:3px 8px;border-radius:3px;">Clear Logs</button>
        </div>
        <div>
            <button id="close-diagnostics" style="background:none;border:none;color:white;">×</button>
        </div>
    `;
    
    diagnosticPanel.appendChild(controlPanel);
    
    // Add to document
    document.body.appendChild(diagnosticPanel);
    document.body.appendChild(toggleButton);
    
    // Log function that doesn't rely on console[type]
    function diagLog(message, type = 'info') {
        // Create log entry element
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        
        // Style based on type
        let borderColor = type === 'error' ? '#ef4444' : 
                          type === 'warning' ? '#f59e0b' : '#10b981';
        
        logEntry.style.cssText = `
            margin: 2px 0;
            padding: 3px 6px;
            border-left: 3px solid ${borderColor};
            font-family: monospace;
            word-break: break-word;
        `;
        
        // Add timestamp and message
        const timestamp = new Date().toLocaleTimeString();
        logEntry.textContent = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
        
        // Add to panel
        diagnosticPanel.appendChild(logEntry);
        diagnosticPanel.scrollTop = diagnosticPanel.scrollHeight;
        
        // Log to console safely
        if (type === 'error') {
            console.error(message);
        } else if (type === 'warning') {
            console.warn(message);
        } else {
            console.log(message);
        }
    }
    
    // Make diagLog available globally
    window.diagLog = diagLog;
    
    // Toggle panel visibility
    toggleButton.addEventListener('click', function() {
        if (diagnosticPanel.style.display === 'none') {
            diagnosticPanel.style.display = 'block';
            toggleButton.textContent = 'Hide Diagnostics';
            runDiagnostics();
        } else {
            diagnosticPanel.style.display = 'none';
            toggleButton.textContent = 'Show Diagnostics';
        }
    });
    
    // Set up control panel buttons
    document.getElementById('run-diagnostics').addEventListener('click', runDiagnostics);
    document.getElementById('test-chat').addEventListener('click', testChat);
    document.getElementById('clear-logs').addEventListener('click', function() {
        // Remove all log entries but keep the control panel
        const logs = diagnosticPanel.querySelectorAll('.log-entry');
        logs.forEach(log => log.remove());
        diagLog('Logs cleared', 'info');
    });
    
    document.getElementById('close-diagnostics').addEventListener('click', function() {
        diagnosticPanel.style.display = 'none';
        toggleButton.textContent = 'Show Diagnostics';
    });
    
    // Run diagnostics function
    function runDiagnostics() {
        diagLog('Starting diagnostics...', 'info');
        
        // Test basic functionality
        diagLog('Testing basic functionality...', 'info');
        testBasicFunctionality();
        
        // Check JavaScript libraries
        diagLog('Checking JavaScript libraries...', 'info');
        checkLibraries();
        
        // Test API endpoints
        diagLog('Testing API endpoints...', 'info');
        testAPIEndpoints();
        
        // Check environment
        diagLog('Checking environment...', 'info');
        checkEnvironment();
        
        // Test markdown rendering
        diagLog('Testing markdown rendering...', 'info');
        testMarkdownRendering();
        
        diagLog('Diagnostics complete', 'info');
    }
    
    function testBasicFunctionality() {
        // Check for essential DOM elements
        const requiredElements = [
            { id: 'chat-input', name: 'Chat Input Field' },
            { id: 'send-button', name: 'Send Button' },
            { id: 'chat-messages', name: 'Chat Messages Container' }
        ];
        
        requiredElements.forEach(element => {
            const el = document.getElementById(element.id);
            if (el) {
                diagLog(`✓ ${element.name} found`, 'info');
            } else {
                diagLog(`✗ ${element.name} not found`, 'error');
            }
        });
        
        // Check for event listeners on chat elements
        try {
            const chatInput = document.getElementById('chat-input');
            const sendButton = document.getElementById('send-button');
            
            if (chatInput && window.getEventListeners) {
                const listeners = window.getEventListeners(chatInput);
                diagLog(`Chat input has ${listeners.keydown ? listeners.keydown.length : 0} keydown listeners`, 'info');
            }
            
            if (sendButton && window.getEventListeners) {
                const listeners = window.getEventListeners(sendButton);
                diagLog(`Send button has ${listeners.click ? listeners.click.length : 0} click listeners`, 'info');
            }
        } catch (e) {
            diagLog('Could not check event listeners: ' + e.message, 'warning');
        }
        
        // Check global state
        if (window.isProcessingQuery !== undefined) {
            diagLog(`Processing query state: ${window.isProcessingQuery}`, 'info');
        } else {
            diagLog('Processing query state not found in global scope', 'warning');
        }
    }
    
    function checkLibraries() {
        // Check for marked.js
        if (typeof marked === 'undefined') {
            diagLog('marked.js is not defined', 'error');
        } else if (typeof marked !== 'function') {
            diagLog(`marked.js is defined but is not a function (type: ${typeof marked})`, 'warning');
            
            // Inspect the marked object
            if (typeof marked === 'object') {
                diagLog('marked properties: ' + Object.keys(marked).join(', '), 'info');
                
                if (marked.marked && typeof marked.marked === 'function') {
                    diagLog('Found marked.marked function - this may be the correct function to use', 'info');
                }
                
                if (marked.parse && typeof marked.parse === 'function') {
                    diagLog('Found marked.parse function - this may be the correct function to use', 'info');
                }
            }
        } else {
            diagLog('marked.js is available as a function', 'info');
            
            // Test marked functionality
            try {
                const testOutput = marked('# Test');
                diagLog('Markdown test result: ' + testOutput, 'info');
            } catch (e) {
                diagLog('Error testing marked.js: ' + e.message, 'error');
            }
        }
        
        // Check for highlight.js
        if (typeof hljs === 'undefined') {
            diagLog('highlight.js is not defined', 'error');
        } else {
            diagLog('highlight.js is available', 'info');
        }
        
        // Check for Font Awesome
        const hasFontAwesome = document.querySelector('link[href*="font-awesome"]') !== null;
        if (!hasFontAwesome) {
            diagLog('Font Awesome CSS may not be loaded', 'warning');
        } else {
            diagLog('Font Awesome CSS appears to be loaded', 'info');
        }
    }
    
    function testAPIEndpoints() {
        // Test status endpoint
        fetch('/api/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                diagLog('API status response: ' + JSON.stringify(data), 'info');
                if (data.initialized) {
                    diagLog('✓ System is initialized and ready', 'info');
                } else {
                    diagLog('✗ System is not initialized: ' + (data.error || 'No error details'), 'warning');
                }
            })
            .catch(error => {
                diagLog('API status test failed: ' + error.message, 'error');
            });
        
        // Test documents endpoint
        fetch('/api/documents')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const coreCount = data.core_documentation ? data.core_documentation.length : 0;
                const artifactCount = data.artifacts ? data.artifacts.length : 0;
                diagLog(`Documents API: ${coreCount} core docs, ${artifactCount} artifacts`, 'info');
            })
            .catch(error => {
                diagLog('Documents API test failed: ' + error.message, 'error');
            });
    }
    
    function checkEnvironment() {
        diagLog('Browser: ' + navigator.userAgent, 'info');
        diagLog('Viewport size: ' + window.innerWidth + 'x' + window.innerHeight, 'info');
        diagLog('Page URL: ' + window.location.href, 'info');
        
        // Check for service worker
        if ('serviceWorker' in navigator) {
            diagLog('Service Worker API is available', 'info');
        } else {
            diagLog('Service Worker API is not available', 'warning');
        }
        
        // Check for localStorage
        try {
            localStorage.setItem('test', 'test');
            localStorage.removeItem('test');
            diagLog('localStorage is available', 'info');
        } catch (e) {
            diagLog('localStorage is not available: ' + e.message, 'warning');
        }
        
        // List loaded scripts
        const scripts = document.querySelectorAll('script');
        diagLog(`${scripts.length} scripts loaded:`, 'info');
        scripts.forEach((script, index) => {
            const src = script.src || '[inline script]';
            diagLog(`  Script ${index+1}: ${src}`, 'info');
        });
        
        // List loaded stylesheets
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        diagLog(`${stylesheets.length} stylesheets loaded:`, 'info');
        stylesheets.forEach((stylesheet, index) => {
            diagLog(`  Stylesheet ${index+1}: ${stylesheet.href}`, 'info');
        });
    }
    
    function testMarkdownRendering() {
        // Create test element for markdown rendering
        const testDiv = document.createElement('div');
        testDiv.style.cssText = 'margin-top: 10px; padding: 5px; border: 1px dashed #666; background: rgba(255,255,255,0.1);';
        
        // Test markdown rendering
        try {
            const testMarkdown = "# Markdown Test\n\n**Bold** and *italic* text\n\n```\ncode block\n```";
            testDiv.innerHTML = '<h3 style="margin:5px 0;">Markdown Rendering Test:</h3>';
            
            if (typeof marked === 'function') {
                testDiv.innerHTML += marked(testMarkdown);
                diagLog('✓ Markdown rendering test completed', 'info');
            } else if (marked && typeof marked.parse === 'function') {
                testDiv.innerHTML += marked.parse(testMarkdown);
                diagLog('✓ Markdown rendering test using marked.parse completed', 'info');
            } else if (marked && typeof marked.marked === 'function') {
                testDiv.innerHTML += marked.marked(testMarkdown);
                diagLog('✓ Markdown rendering test using marked.marked completed', 'info');
            } else {
                testDiv.innerHTML += '<p>Cannot test markdown rendering - marked is not a function</p>';
                diagLog('✗ Cannot test markdown rendering - marked is not a function', 'warning');
            }
        } catch (e) {
            testDiv.innerHTML += '<p>Error testing markdown: ' + e.message + '</p>';
            diagLog('✗ Error during markdown rendering test: ' + e.message, 'error');
        }
        
        // Add test div to panel
        diagnosticPanel.appendChild(testDiv);
    }
    
    function testChat() {
        diagLog('Testing chat functionality...', 'info');
        
        // Check if chat input and send button exist
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        
        if (!chatInput || !sendButton) {
            diagLog('Chat elements not found', 'error');
            return;
        }
        
        // Check if sendMessage function exists
        let sendMessageFn = null;
        
        // Try to find the function
        if (window.sendMessage) {
            sendMessageFn = window.sendMessage;
            diagLog('Found global sendMessage function', 'info');
        } else if (window.enhancedSendMessage) {
            sendMessageFn = window.enhancedSendMessage;
            diagLog('Found global enhancedSendMessage function', 'info');
        } else {
            // Look at button event handlers
            try {
                const clickHandlers = window.getEventListeners ? 
                    window.getEventListeners(sendButton).click : null;
                
                if (clickHandlers && clickHandlers.length > 0) {
                    diagLog(`Found ${clickHandlers.length} click handlers on send button`, 'info');
                } else {
                    diagLog('No click handlers found on send button', 'warning');
                }
            } catch (e) {
                diagLog('Could not inspect button event handlers: ' + e.message, 'warning');
            }
        }
        
        // Test chat with a simple message
        const testMessage = 'This is a test message from the diagnostic panel';
        diagLog(`Setting test message: "${testMessage}"`, 'info');
        chatInput.value = testMessage;
        
        // Click the send button
        diagLog('Clicking send button...', 'info');
        sendButton.click();
        
        // Check if API call was made
        diagLog('Test message sent. Check network tab for API calls.', 'info');
        diagLog('Check chat window for test message and response.', 'info');
    }
    
    // Expose diagnostic functions globally
    window.gaiaRunDiagnostics = runDiagnostics;
    window.gaiaTestChat = testChat;
    window.gaiaDiagLog = diagLog;
    
    diagLog('GAIA Troubleshooting tool initialized', 'info');
});