// GAIA Chat Fix - Proper message handling and response cleanup
document.addEventListener('DOMContentLoaded', function() {
    console.log('GAIA Chat Fix script loaded');
    
    // Get the chat elements
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatInput || !sendButton || !chatMessages) {
        console.error('Required chat elements not found!');
        return;
    }
    
    // Flag to track if we're currently processing a query
    let isProcessingQuery = false;

    // Function to safely use the marked library
    function safeMarked(text) {
        if (!text) {
            return '';
        }
        
        try {
            // Direct function
            if (typeof marked === 'function') {
                return marked(text);
            }
            
            // Check if marked.parse is available
            if (marked && typeof marked.parse === 'function') {
                return marked.parse(text);
            }
            
            // Check if marked.marked is available
            if (marked && typeof marked.marked === 'function') {
                return marked.marked(text);
            }
            
            // Fallback to simple HTML conversion
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;')
                .replace(/^##\s+(.*?)$/gm, '<h2>$1</h2>')
                .replace(/^#\s+(.*?)$/gm, '<h1>$1</h1>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
        } catch (error) {
            console.error('Error using marked library:', error);
            return `<p>${text}</p>`;
        }
    }
    
    // Function to clean up AI responses
    function cleanAIResponse(text) {
        if (!text) return '';
        
        // First trim whitespace
        let cleaned = text.trim();
        
        // Remove common prefixes
        const prefixes = [
            'GAIA:', 
            'Answer:', 
            'Response:', 
            'AI:', 
            'Assistant:', 
            'Here is the information about',
            'Here\'s the information about',
            'Here\'s the answer:'
        ];
        
        for (const prefix of prefixes) {
            if (cleaned.startsWith(prefix)) {
                cleaned = cleaned.substring(prefix.length).trim();
                break;
            }
        }
        
        // Remove any conversation markers
        if (cleaned.includes('Human:') || cleaned.includes('GAIA:') || cleaned.includes('User:')) {
            // Take only first part before any conversation markers
            cleaned = cleaned.split(/Human:|GAIA:|User:/)[0].trim();
        }
        
        // Check for sections that don't belong
        const sectionHeaders = [
            'SECTION I:',
            'SECTION II:',
            'SECTION III:',
            'SECTION IV:',
            'SECTION V:'
        ];
        
        for (const header of sectionHeaders) {
            if (cleaned.includes(header) && !cleaned.startsWith(header)) {
                // Find the position of the first section header that doesn't belong
                const position = cleaned.indexOf(header);
                if (position > 50) { // Only truncate if we have enough good content before
                    cleaned = cleaned.substring(0, position).trim();
                }
            }
        }
        
        // Check if response appears to be cut off mid-sentence
        const lastChar = cleaned.slice(-1);
        if (lastChar && !'.!?'.includes(lastChar)) {
            // Find the last complete sentence if possible
            const lastPeriod = Math.max(
                cleaned.lastIndexOf('.'), 
                cleaned.lastIndexOf('!'), 
                cleaned.lastIndexOf('?')
            );
            
            if (lastPeriod > cleaned.length * 0.7) { // Only truncate if we've got most of the content
                cleaned = cleaned.substring(0, lastPeriod + 1);
            }
        }
        
        return cleaned;
    }
    
    // Enhanced function to send a message
    function enhancedSendMessage() {
        const query = chatInput.value.trim();
        
        if (!query || isProcessingQuery) {
            return;
        }
        
        console.log('Sending message:', query);
        
        // Add user message to chat
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-content"><p>${query}</p></div>
            <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        chatMessages.appendChild(messageDiv);
        
        // Clear input
        chatInput.value = '';
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Show processing state
        isProcessingQuery = true;
        const processingDiv = document.createElement('div');
        processingDiv.className = 'message system processing-message';
        processingDiv.innerHTML = `
            <div class="message-content"><p>GAIA is processing your request...</p></div>
            <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        chatMessages.appendChild(processingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Function to retry fetch operations
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
                                console.warn(`Retrying fetch in ${delay}ms (attempt ${retryCount + 1}/${maxRetries})`, { url, error });
                                setTimeout(() => attempt(retryCount + 1), delay);
                            } else {
                                console.error('Max retries reached', { url, error });
                                reject(error);
                            }
                        });
                };
                
                attempt(0);
            });
        }
        
        // Send query to server with retry
        fetchWithRetry('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(data => {
            // Remove processing message
            const processingMsg = document.querySelector('.processing-message');
            if (processingMsg) {
                processingMsg.remove();
            }
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Get the AI response and clean it up
            let response = cleanAIResponse(data.response);
            
            // Add AI response to chat
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'message ai';
            
            // Render the response as markdown
            let contentHtml = safeMarked(response);
            
            aiMessageDiv.innerHTML = `
                <div class="message-content">${contentHtml}</div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            chatMessages.appendChild(aiMessageDiv);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // If this was an artifact request, update documents
            if (query.toLowerCase().startsWith('artifact:') && data.artifact) {
                try {
                    if (typeof showToast === 'function') {
                        showToast('success', 'Artifact Generated', `Successfully created: ${data.artifact}`);
                    }
                    
                    // Try to reload documents if the function exists
                    if (typeof loadDocuments === 'function') {
                        loadDocuments();
                    }
                } catch (e) {
                    console.error('Error handling artifact:', e);
                }
            }
        })
        .catch(err => {
            // Remove processing message
            const processingMsg = document.querySelector('.processing-message');
            if (processingMsg) {
                processingMsg.remove();
            }
            
            console.error('Error sending message:', err);
            
            // Add error message to chat
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message system';
            errorDiv.innerHTML = `
                <div class="message-content"><p>Error: ${err.message}. Please try again.</p></div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            chatMessages.appendChild(errorDiv);
            
            // Show toast if available
            try {
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', err.message);
                }
            } catch (e) {
                console.error('Error showing toast:', e);
            }
        })
        .finally(() => {
            isProcessingQuery = false;
        });
    }
    
    // Add enhanced event handlers that override the original ones
    
    // 1. Direct keydown handler
    chatInput.removeEventListener('keydown', window.originalKeydownHandler);
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            enhancedSendMessage();
            return false;
        }
    });
    
    // 2. Direct click handler
    sendButton.removeEventListener('click', window.originalClickHandler);
    sendButton.addEventListener('click', function(e) {
        e.preventDefault();
        enhancedSendMessage();
        return false;
    });
    
    console.log('GAIA Chat Fix: Enhanced message handlers installed');
});