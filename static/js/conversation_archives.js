// GAIA Conversation Archives Management
document.addEventListener('DOMContentLoaded', function() {
    console.log('Conversation Archives script loaded');
    
    // Create archives section in documents tab
    function setupArchivesSection() {
        // Add new tab for archives in the document section
        const docTabs = document.querySelector('.document-tabs');
        if (!docTabs) {
            console.error('Document tabs not found');
            return;
        }
        
        // Add archives tab button
        const archivesTabBtn = document.createElement('button');
        archivesTabBtn.className = 'doc-tab-btn';
        archivesTabBtn.dataset.doctab = 'archives';
        archivesTabBtn.textContent = 'Conversation Archives';
        docTabs.appendChild(archivesTabBtn);
        
        // Add archives container
        const docsContainer = document.querySelector('.documents-container');
        if (!docsContainer) {
            console.error('Documents container not found');
            return;
        }
        
        // Create archives container
        const archivesContainer = document.createElement('div');
        archivesContainer.id = 'archives-docs';
        archivesContainer.className = 'document-list doc-tab';
        archivesContainer.innerHTML = '<div class="loading-spinner document-spinner"></div>';
        docsContainer.insertBefore(archivesContainer, document.getElementById('document-viewer'));
        
        // Add event listener to tab button
        archivesTabBtn.addEventListener('click', function() {
            changeDocTab('archives');
            loadArchives();
        });
        
        console.log('Archives section set up successfully');
    }
    
    // Load archives from API
    function loadArchives() {
        const archivesContainer = document.getElementById('archives-docs');
        if (!archivesContainer) {
            console.error('Archives container not found');
            return;
        }
        
        archivesContainer.innerHTML = '<div class="loading-spinner document-spinner"></div>';
        
        fetchWithRetry('/api/conversation/archives')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (!data.archives || data.archives.length === 0) {
                    archivesContainer.innerHTML = '<div class="empty-message">No conversation archives found.</div>';
                    return;
                }
                
                // Render archives
                archivesContainer.innerHTML = '';
                
                // Sort by timestamp (most recent first)
                const archives = data.archives.sort((a, b) => {
                    return new Date(b.timestamp) - new Date(a.timestamp);
                });
                
                archives.forEach(archive => {
                    const card = document.createElement('div');
                    card.className = 'document-card';
                    card.dataset.archiveId = archive.id;
                    
                    const icon = document.createElement('div');
                    icon.className = 'document-icon';
                    icon.innerHTML = '<i class="fas fa-comments"></i>';
                    
                    const timestamp = new Date(archive.timestamp);
                    const formattedTime = timestamp.toLocaleString();
                    
                    const title = document.createElement('div');
                    title.className = 'document-title';
                    title.textContent = `Conversation ${formattedTime}`;
                    
                    const meta = document.createElement('div');
                    meta.className = 'document-meta';
                    
                    // Show first 50 chars of summary
                    let summaryPreview = archive.summary;
                    if (summaryPreview.length > 50) {
                        summaryPreview = summaryPreview.substring(0, 47) + '...';
                    }
                    meta.textContent = summaryPreview;
                    
                    card.appendChild(icon);
                    card.appendChild(title);
                    card.appendChild(meta);
                    
                    card.addEventListener('click', function() {
                        viewArchive(archive.id);
                    });
                    
                    archivesContainer.appendChild(card);
                });
            })
            .catch(err => {
                console.error('Error loading archives:', err);
                archivesContainer.innerHTML = `<div class="error-message">Error loading archives: ${err.message}</div>`;
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to load archives: ${err.message}`);
                }
            });
    }
    
    // View a specific archive
    function viewArchive(archiveId) {
        const documentViewer = document.getElementById('document-viewer');
        const documentTitle = document.getElementById('document-title');
        const documentContent = document.getElementById('document-content');
        
        if (!documentViewer || !documentTitle || !documentContent) {
            console.error('Document viewer elements not found');
            return;
        }
        
        // Show loading state
        documentContent.innerHTML = '<div class="loading-spinner"></div>';
        documentViewer.classList.add('active');
        
        fetchWithRetry(`/api/conversation/archive/${archiveId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                documentTitle.textContent = `Conversation Archive: ${archiveId}`;
                
                try {
                    if (typeof marked === 'function') {
                        documentContent.innerHTML = marked(data.content);
                    } else {
                        documentContent.innerHTML = `<pre>${data.content}</pre>`;
                        console.error('marked is not available for rendering document');
                    }
                } catch (e) {
                    console.error('Error rendering document markdown:', e);
                    documentContent.innerHTML = `<pre>${data.content}</pre>`;
                }
                
                // Apply syntax highlighting to code blocks if highlight.js is available
                if (typeof hljs !== 'undefined') {
                    document.querySelectorAll('pre code').forEach((block) => {
                        try {
                            hljs.highlightBlock(block);
                        } catch (e) {
                            console.error('Error applying syntax highlighting:', e);
                        }
                    });
                }
            })
            .catch(err => {
                console.error('Error viewing archive:', err);
                documentContent.innerHTML = `<div class="error-message">Error viewing archive: ${err.message}</div>`;
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to view archive: ${err.message}`);
                }
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
    
    // Add archive summary button to chat interface
    function addArchiveButton() {
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
        archiveButton.style.cssText = `
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: var(--transition);
            margin-right: 5px;
        `;
        
        archiveButton.addEventListener('click', archiveCurrentConversation);
        
        // Insert before send button
        const sendButton = document.getElementById('send-button');
        if (sendButton) {
            chatContainer.insertBefore(archiveButton, sendButton);
        } else {
            chatContainer.appendChild(archiveButton);
        }
    }
    
    // Archive current conversation
    function archiveCurrentConversation() {
        // Show archiving indicator
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) {
            console.error('Chat messages container not found');
            return;
        }
        
        const processingDiv = document.createElement('div');
        processingDiv.className = 'message system archiving-message';
        processingDiv.innerHTML = `
            <div class="message-content"><p>Archiving conversation...</p></div>
            <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        chatMessages.appendChild(processingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        fetchWithRetry('/api/conversation/summary', {
            method: 'GET'
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
                    <p>Conversation archived successfully.</p>
                    <p><strong>Summary:</strong> ${data.summary}</p>
                    <p>You can view all archived conversations in the "Conversation Archives" tab under Documents.</p>
                </div>
                <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
            `;
            chatMessages.appendChild(confirmationDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Show toast if available
            if (typeof showToast === 'function') {
                showToast('success', 'Conversation Archived', 'Conversation has been summarized and archived.');
            }
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
    
    // Find and attach to changeDocTab function
    function monkeyPatchChangeDocTab() {
        if (typeof window.changeDocTab === 'function') {
            // Store original function
            const originalChangeDocTab = window.changeDocTab;
            
            // Replace with modified version
            window.changeDocTab = function(docTabName) {
                // Remove active class from all buttons and tabs
                document.querySelectorAll('.doc-tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab
                if (docTabName === 'core') {
                    document.getElementById('core-docs').classList.add('active');
                } else if (docTabName === 'artifacts') {
                    document.getElementById('artifacts-docs').classList.add('active');
                } else if (docTabName === 'archives') {
                    document.getElementById('archives-docs').classList.add('active');
                }
                
                document.querySelector(`.doc-tab-btn[data-doctab="${docTabName}"]`).classList.add('active');
            };
            
            console.log('Successfully patched changeDocTab function');
        } else {
            console.error('changeDocTab function not found in global scope');
            
            // Provide fallback implementation
            window.changeDocTab = function(docTabName) {
                document.querySelectorAll('.doc-tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
                
                if (docTabName === 'core') {
                    document.getElementById('core-docs').classList.add('active');
                } else if (docTabName === 'artifacts') {
                    document.getElementById('artifacts-docs').classList.add('active');
                } else if (docTabName === 'archives') {
                    document.getElementById('archives-docs').classList.add('active');
                }
                
                document.querySelector(`.doc-tab-btn[data-doctab="${docTabName}"]`).classList.add('active');
            };
            
            console.log('Created new changeDocTab function');
        }
    }
    
    // Initialize conversation archives functionality
    function init() {
        // Set up archives section
        setupArchivesSection();
        
        // Add archive button to chat interface
        addArchiveButton();
        
        // Monkey patch changeDocTab function
        monkeyPatchChangeDocTab();
    }
    
    // Initialize when the app is ready
    let checkInitInterval = setInterval(function() {
        if (document.getElementById('loading-screen') && 
            !document.getElementById('loading-screen').classList.contains('active')) {
            clearInterval(checkInitInterval);
            init();
        }
    }, 1000);
});