// GAIA Background Processing UI
document.addEventListener('DOMContentLoaded', function() {
    console.log('Background Processing UI script loaded');
    
    // Create background processing UI in archives tab
    function setupBackgroundProcessingUI() {
        // Modify the conversation archives section
        const archivesContainer = document.getElementById('archives-docs');
        if (!archivesContainer) {
            console.error('Archives container not found');
            return;
        }
        
        // Add background processing status indicator
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'background-status-indicator';
        statusIndicator.className = 'background-status-indicator';
        statusIndicator.innerHTML = `
            <div class="status-header">
                <h3>Background Processing Status</h3>
                <button id="refresh-status" class="btn-primary">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
            <div class="status-content">
                <div class="loading-spinner"></div>
                <p>Loading background processing status...</p>
            </div>
        `;
        
        // Insert before the document list
        if (archivesContainer.firstChild) {
            archivesContainer.insertBefore(statusIndicator, archivesContainer.firstChild);
        } else {
            archivesContainer.appendChild(statusIndicator);
        }
        
        // Add CSS styles
        addBackgroundProcessingStyles();
        
        // Initialize events
        setupBackgroundProcessingEvents();
        
        // Initial status check
        checkBackgroundStatus();
        
        console.log('Background processing UI set up successfully');
    }
    
    function addBackgroundProcessingStyles() {
        // Create style element
        const style = document.createElement('style');
        style.textContent = `
            .background-status-indicator {
                background-color: white;
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-sm);
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .status-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            
            .status-content {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .status-section {
                margin-bottom: 1rem;
            }
            
            .status-section h4 {
                margin-bottom: 0.5rem;
                color: var(--primary-color);
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem;
                border-radius: var(--radius-sm);
                background-color: #f9fafb;
                margin-bottom: 0.25rem;
            }
            
            .status-item-label {
                font-weight: bold;
            }
            
            .status-item-value {
                color: var(--text-light);
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background-color: #e5e7eb;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 0.5rem;
            }
            
            .progress-bar-fill {
                height: 100%;
                background-color: var(--primary-color);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .task-list {
                max-height: 200px;
                overflow-y: auto;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
                padding: 0.5rem;
                margin-top: 0.5rem;
            }
            
            .task-item {
                padding: 0.5rem;
                border-radius: var(--radius-sm);
                margin-bottom: 0.25rem;
                background-color: #f9fafb;
            }
            
            .task-item-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.25rem;
            }
            
            .task-item-type {
                font-weight: bold;
            }
            
            .task-item-status {
                font-size: 0.875rem;
            }
            
            .task-item-status.pending {
                color: #f59e0b;
            }
            
            .task-item-status.processing {
                color: #3b82f6;
            }
            
            .task-item-status.completed {
                color: #10b981;
            }
            
            .task-item-status.failed {
                color: #ef4444;
            }
            
            .task-item-created {
                font-size: 0.75rem;
                color: var(--text-light);
            }
            
            .empty-message {
                text-align: center;
                color: var(--text-light);
                padding: 1rem;
            }
            
            .archive-item {
                margin-bottom: 1rem;
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-sm);
                background-color: white;
                overflow: hidden;
            }
            
            .archive-item-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem 1rem;
                background-color: var(--primary-color);
                color: white;
            }
            
            .archive-item-title {
                font-weight: bold;
            }
            
            .archive-item-timestamp {
                font-size: 0.75rem;
                opacity: 0.8;
            }
            
            .archive-item-content {
                padding: 1rem;
            }
            
            .archive-item-summary {
                margin-bottom: 0.5rem;
            }
            
            .archive-item-keywords {
                display: flex;
                flex-wrap: wrap;
                gap: 0.25rem;
                margin-top: 0.5rem;
            }
            
            .archive-item-keyword {
                background-color: #e5e7eb;
                color: var(--text-color);
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
                border-radius: 9999px;
            }
            
            .archive-item-actions {
                display: flex;
                justify-content: flex-end;
                gap: 0.5rem;
                margin-top: 0.5rem;
                padding-top: 0.5rem;
                border-top: 1px solid var(--border-color);
            }
            
            .archive-button {
                background-color: var(--primary-color);
                color: white;
                border-radius: var(--radius-md);
                width: 45px;
                height: 45px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: var(--transition);
                margin-right: 5px;
            }
            
            .archive-button-bg {
                background-color: var(--primary-color);
                color: white;
                border: none;
                border-radius: var(--radius-md);
                padding: 0.5rem 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                transition: var(--transition);
            }
            
            .archive-button-bg:hover,
            .archive-button:hover {
                background-color: var(--primary-light);
            }
        `;
        
        document.head.appendChild(style);
    }
    
    function setupBackgroundProcessingEvents() {
        // Setup refresh button
        const refreshButton = document.getElementById('refresh-status');
        if (refreshButton) {
            refreshButton.addEventListener('click', checkBackgroundStatus);
        }
        
        // Setup archive button events
        const archiveButton = document.getElementById('archive-conversation');
        if (archiveButton) {
            // Replace click handler
            const oldClickHandler = archiveButton.onclick;
            archiveButton.onclick = function(e) {
                e.preventDefault();
                archiveConversationBackground();
                return false;
            };
        } else {
            // Create button if it doesn't exist
            addBackgroundArchiveButton();
        }
    }
    
    function addBackgroundArchiveButton() {
        const chatContainer = document.querySelector('.chat-input-container');
        if (!chatContainer) {
            console.error('Chat input container not found');
            return;
        }
        
        const archiveButton = document.createElement('button');
        archiveButton.id = 'archive-conversation';
        archiveButton.title = 'Archive current conversation';
        archiveButton.className = 'archive-button';
        archiveButton.innerHTML = '<i class="fas fa-archive"></i>';
        
        archiveButton.addEventListener('click', archiveConversationBackground);
        
        // Insert before send button
        const sendButton = document.getElementById('send-button');
        if (sendButton) {
            chatContainer.insertBefore(archiveButton, sendButton);
        } else {
            chatContainer.appendChild(archiveButton);
        }
    }
    
    function checkBackgroundStatus() {
        const statusContent = document.querySelector('.status-content');
        if (!statusContent) {
            console.error('Status content not found');
            return;
        }
        
        // Show loading spinner
        statusContent.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Loading background processing status...</p>
        `;
        
        fetchWithRetry('/api/background/status')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                const status = data.status;
                
                // Render status
                let html = '';
                
                // Tasks section
                html += `
                    <div class="status-section">
                        <h4>Processing Tasks</h4>
                        <div class="status-item">
                            <span class="status-item-label">Current Status:</span>
                            <span class="status-item-value">${status.tasks.is_processing ? 'Processing' : 'Idle'}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-item-label">Pending Tasks:</span>
                            <span class="status-item-value">${status.tasks.pending_count}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-item-label">Completed Tasks:</span>
                            <span class="status-item-value">${status.tasks.completed_count}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-item-label">Failed Tasks:</span>
                            <span class="status-item-value">${status.tasks.failed_count}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-bar-fill" style="width: ${calculateProgressPercentage(status.tasks)}%"></div>
                        </div>
                    </div>
                `;
                
                // Archives section
                html += `
                    <div class="status-section">
                        <h4>Conversation Archives</h4>
                        <div class="status-item">
                            <span class="status-item-label">Total Archives:</span>
                            <span class="status-item-value">${status.archives.total_archives}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-item-label">Processed Archives:</span>
                            <span class="status-item-value">${status.archives.processed_archives}</span>
                        </div>
                        <div class="status-item">
                            <span class="status-item-label">Pending Archives:</span>
                            <span class="status-item-value">${status.archives.pending_archives}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-bar-fill" style="width: ${calculateArchiveProgressPercentage(status.archives)}%"></div>
                        </div>
                    </div>
                `;
                
                // Current task section
                if (status.tasks.current_task) {
                    const task = status.tasks.current_task;
                    html += `
                        <div class="status-section">
                            <h4>Current Task</h4>
                            <div class="task-item">
                                <div class="task-item-header">
                                    <span class="task-item-type">${task.type}</span>
                                    <span class="task-item-status ${task.status}">${task.status}</span>
                                </div>
                                <div class="task-item-created">Created: ${formatDate(task.created)}</div>
                            </div>
                        </div>
                    `;
                }
                
                // Top keywords section
                if (status.archives.top_keywords && status.archives.top_keywords.length > 0) {
                    html += `
                        <div class="status-section">
                            <h4>Top Keywords</h4>
                            <div class="archive-item-keywords">
                                ${status.archives.top_keywords.map(keyword => 
                                    `<span class="archive-item-keyword">${keyword[0]} (${keyword[1]})</span>`
                                ).join('')}
                            </div>
                        </div>
                    `;
                }
                
                statusContent.innerHTML = html;
            })
            .catch(err => {
                console.error('Error checking background status:', err);
                statusContent.innerHTML = `
                    <div class="error-message">
                        Error checking background status: ${err.message}
                    </div>
                `;
            });
    }
    
    function calculateProgressPercentage(tasks) {
        const total = tasks.pending_count + tasks.completed_count + tasks.failed_count;
        if (total === 0) return 0;
        return Math.round((tasks.completed_count / total) * 100);
    }
    
    function calculateArchiveProgressPercentage(archives) {
        const total = archives.total_archives;
        if (total === 0) return 0;
        return Math.round((archives.processed_archives / total) * 100);
    }
    
    function formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            return dateString;
        }
    }
    
    function archiveConversationBackground() {
        // Show archiving indicator
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) {
            console.error('Chat messages container not found');
            return;
        }
        
        const processingDiv = document.createElement('div');
        processingDiv.className = 'message system archiving-message';
        processingDiv.innerHTML = `
            <div class="message-content"><p>Archiving conversation for background processing...</p></div>
            <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        chatMessages.appendChild(processingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        fetchWithRetry('/api/conversation/archive/background', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            // Remove archiving message
            const archivingMsg = document.querySelector('.archiving-message');
            if (archivingMsg) {
                archivingMsg.remove();
            }
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add confirmation message
            const confirmationDiv = document.createElement('div');
            confirmationDiv.className = 'message system';
            confirmationDiv.innerHTML = `
                <div class="message-content">
                    <p>Conversation scheduled for background processing.</p>
                    <p><strong>Initial Summary:</strong> ${data.summary}</p>
                    <p>The background processor will analyze this conversation during idle time to extract and structure the most important information.</p>
                    <p>You can view all archived conversations and processing status in the "Conversation Archives" tab under Documents.</p>
                </div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            chatMessages.appendChild(confirmationDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Show toast if available
            if (typeof showToast === 'function') {
                showToast('success', 'Conversation Archived', 'Conversation has been scheduled for background processing.');
            }
            
            // Register this as user activity
            registerUserActivity();
        })
        .catch(err => {
            // Remove archiving message
            const archivingMsg = document.querySelector('.archiving-message');
            if (archivingMsg) {
                archivingMsg.remove();
            }
            
            console.error('Error archiving conversation:', err);
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message system';
            errorDiv.innerHTML = `
                <div class="message-content"><p>Error archiving conversation: ${err.message}. Please try again.</p></div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            chatMessages.appendChild(errorDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Show toast if available
            if (typeof showToast === 'function') {
                showToast('error', 'Error', `Failed to archive conversation: ${err.message}`);
            }
        });
    }
    
    function registerUserActivity() {
        // Send activity ping to backend
        fetch('/api/background/register_activity', {
            method: 'POST'
        }).catch(err => {
            console.error('Error registering user activity:', err);
        });
    }
    
    // Utility function for fetch with retry
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
    
    // Initialize when the app is ready and archives are loaded
    let checkInitInterval = setInterval(function() {
        const archivesContainer = document.getElementById('archives-docs');
        if (archivesContainer && 
            document.getElementById('loading-screen') && 
            !document.getElementById('loading-screen').classList.contains('active')) {
            clearInterval(checkInitInterval);
            setupBackgroundProcessingUI();
            
            // Set up activity tracking
            document.addEventListener('mousemove', function() {
                registerUserActivity();
            });
            document.addEventListener('keypress', function() {
                registerUserActivity();
            });
            document.addEventListener('click', function() {
                registerUserActivity();
            });
        }
    }, 1000);
});