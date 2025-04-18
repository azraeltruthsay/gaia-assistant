// GAIA - D&D Campaign Assistant

// Marked.js fallback functionality
(function() {
    // Fix marked before using it
    if (typeof marked !== 'function') {
        // Try to access different versions/exposures of the marked library
        if (window.marked && typeof window.marked !== 'function') {
            if (window.marked.marked && typeof window.marked.marked === 'function') {
                window.marked = window.marked.marked;
            } else if (window.marked.parse && typeof window.marked.parse === 'function') {
                window.marked = function(text) {
                    return window.marked.parse(text);
                };
            } else {
                // Last resort fallback - very simple markdown renderer
                console.error('marked.js not available, using basic fallback renderer');
                window.marked = function(text) {
                    // Super simple markdown renderer for headings, bold, and paragraphs
                    return text
                        .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
                        .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
                        .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                        .replace(/`(.*?)`/g, '<code>$1</code>')
                        .split(/\n\n+/).map(p => `<p>${p}</p>`).join('');
                };
            }
        }
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    // Try to initialize marked.js if available
    try {
        if (typeof marked === 'function') {
            marked.setOptions({
                renderer: new marked.Renderer(),
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(lang, code).value;
                        } catch (err) {}
                    }
                    
                    if (typeof hljs !== 'undefined') {
                        return hljs.highlightAuto(code).value;
                    }
                    
                    return code;
                },
                pedantic: false,
                gfm: true,
                breaks: false,
                sanitize: false,
                smartLists: true,
                smartypants: false,
                xhtml: false
            });
        }
    } catch (e) {
        console.error('Error initializing marked.js:', e);
    }

    // DOM Elements
    const loadingScreen = document.getElementById('loading-screen');
    const initializationError = document.getElementById('initialization-error');
    const chatSection = document.getElementById('chat');
    const documentsSection = document.getElementById('documents');
    const uploadSection = document.getElementById('upload');
    const navButtons = document.querySelectorAll('.nav-btn');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const coreDocsContainer = document.getElementById('core-docs');
    const artifactsDocsContainer = document.getElementById('artifacts-docs');
    const docTabButtons = document.querySelectorAll('.doc-tab-btn');
    const documentViewer = document.getElementById('document-viewer');
    const documentTitle = document.getElementById('document-title');
    const documentContent = document.getElementById('document-content');
    const closeDocumentBtn = document.getElementById('close-document');
    const downloadDocumentBtn = document.getElementById('download-document');
    const documentSearch = document.getElementById('document-search');
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const uploadList = document.getElementById('upload-list');
    const previewModal = document.getElementById('preview-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalClose = document.querySelector('.modal-close');

    // App State
    let currentTab = 'chat';
    let currentDocTab = 'core';
    let isProcessingQuery = false;
    let currentViewingDocument = null;
    let documents = {
        core: [],
        artifacts: []
    };
    let uploadedFiles = [];
    let isInitialized = false;

    // Check initialization status
    checkInitStatus();

    // Navigation
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            changeTab(tabName);
        });
    });

    // Document Tabs
    docTabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const docTabName = button.dataset.doctab;
            changeDocTab(docTabName);
        });
    });

    // Chat Input
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);

    // Document Viewer
    closeDocumentBtn.addEventListener('click', () => {
        documentViewer.classList.remove('active');
        currentViewingDocument = null;
    });

    downloadDocumentBtn.addEventListener('click', () => {
        if (currentViewingDocument) {
            window.open(`/downloads/${currentViewingDocument}`, '_blank');
        }
    });

    // Document Search
    documentSearch.addEventListener('input', () => {
        const searchQuery = documentSearch.value.toLowerCase();
        filterDocuments(searchQuery);
    });

    // Upload Handling
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });

    // Modal
    modalClose.addEventListener('click', () => {
        previewModal.classList.remove('active');
    });

    previewModal.addEventListener('click', (e) => {
        if (e.target === previewModal) {
            previewModal.classList.remove('active');
        }
    });

    // Functions
    function checkInitStatus() {
        fetchWithRetry('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.initialized) {
                    isInitialized = true;
                    hideLoading();
                    loadDocuments();
                } else {
                    if (data.error) {
                        showInitializationError(data.error);
                    }
                    // Check again in 2 seconds
                    setTimeout(checkInitStatus, 2000);
                }
            })
            .catch(err => {
                console.error('Failed to check initialization status:', err);
                showInitializationError('Failed to connect to server. Please refresh the page and try again.');
            });
    }

    function showInitializationError(message) {
        initializationError.textContent = message;
        initializationError.classList.remove('hidden');
    }

    function hideLoading() {
        loadingScreen.classList.remove('active');
        chatSection.classList.add('active');
    }

    function changeTab(tabName) {
        // Hide all sections
        chatSection.classList.remove('active');
        documentsSection.classList.remove('active');
        uploadSection.classList.remove('active');
        
        // Remove active class from all buttons
        navButtons.forEach(btn => btn.classList.remove('active'));
        
        // Show selected section and activate button
        if (tabName === 'chat') {
            chatSection.classList.add('active');
        } else if (tabName === 'documents') {
            documentsSection.classList.add('active');
            if (!documents.core.length && !documents.artifacts.length) {
                loadDocuments();
            }
        } else if (tabName === 'upload') {
            uploadSection.classList.add('active');
        }
        
        document.querySelector(`.nav-btn[data-tab="${tabName}"]`).classList.add('active');
        currentTab = tabName;
    }

    function changeDocTab(docTabName) {
        // Remove active class from all buttons and tabs
        docTabButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
        
        // Show selected tab
        if (docTabName === 'core') {
            document.getElementById('core-docs').classList.add('active');
        } else if (docTabName === 'artifacts') {
            document.getElementById('artifacts-docs').classList.add('active');
        }
        
        document.querySelector(`.doc-tab-btn[data-doctab="${docTabName}"]`).classList.add('active');
        currentDocTab = docTabName;
    }

    function sendMessage() {
        const query = chatInput.value.trim();
        
        if (!query || isProcessingQuery || !isInitialized) return;
        
        // Add user message to chat
        addMessageToChat('user', query);
        
        // Clear input
        chatInput.value = '';
        
        // Show processing state
        isProcessingQuery = true;
        addMessageToChat('system', 'GAIA is processing your request...', 'processing-message');
        
        // Send query to server
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
            
            // Add AI response to chat
            addMessageToChat('ai', data.response);
            
            // If this was an artifact request, refresh documents
            if (query.toLowerCase().startsWith('artifact:') && data.artifact) {
                showToast('success', 'Artifact Generated', `Successfully created: ${data.artifact}`);
                loadDocuments();
            }
        })
        .catch(err => {
            // Remove processing message
            const processingMsg = document.querySelector('.processing-message');
            if (processingMsg) {
                processingMsg.remove();
            }
            
            console.error('Error sending message:', err);
            addMessageToChat('system', `Error: ${err.message}. Please try again.`);
            showToast('error', 'Error', err.message);
        })
        .finally(() => {
            isProcessingQuery = false;
        });
    }

    function addMessageToChat(type, content, className = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} ${className}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // If AI message, use marked to render markdown
        if (type === 'ai') {
            try {
                if (typeof marked === 'function') {
                    contentDiv.innerHTML = marked(content);
                } else {
                    // Fallback if marked isn't available
                    contentDiv.innerHTML = `<p>${content}</p>`;
                    console.error('marked is not available for rendering markdown');
                }
            } catch (e) {
                console.error('Error rendering markdown:', e);
                contentDiv.innerHTML = `<p>${content}</p>`;
            }
        } else {
            contentDiv.innerHTML = `<p>${content}</p>`;
        }
        
        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestamp);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function loadDocuments() {
        coreDocsContainer.innerHTML = '<div class="loading-spinner document-spinner"></div>';
        artifactsDocsContainer.innerHTML = '<div class="loading-spinner document-spinner"></div>';
        
        fetchWithRetry('/api/documents')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                documents.core = data.core_documentation || [];
                documents.artifacts = data.artifacts || [];
                
                renderDocuments('core', documents.core);
                renderDocuments('artifacts', documents.artifacts);
            })
            .catch(err => {
                console.error('Error loading documents:', err);
                coreDocsContainer.innerHTML = `<div class="error-message">Error loading documents: ${err.message}</div>`;
                artifactsDocsContainer.innerHTML = `<div class="error-message">Error loading documents: ${err.message}</div>`;
                showToast('error', 'Error', `Failed to load documents: ${err.message}`);
            });
    }

    function renderDocuments(type, docs) {
        const container = type === 'core' ? coreDocsContainer : artifactsDocsContainer;
        
        if (!docs.length) {
            container.innerHTML = `<div class="empty-message">No ${type === 'core' ? 'core documentation' : 'artifacts'} found.</div>`;
            return;
        }
        
        container.innerHTML = '';
        
        docs.forEach(doc => {
            const card = document.createElement('div');
            card.className = 'document-card';
            card.dataset.filename = doc.name;
            
            const icon = document.createElement('div');
            icon.className = 'document-icon';
            icon.innerHTML = '<i class="fas fa-file-alt"></i>';
            
            const title = document.createElement('div');
            title.className = 'document-title';
            title.textContent = doc.name;
            
            const meta = document.createElement('div');
            meta.className = 'document-meta';
            meta.textContent = `Modified: ${doc.modified}`;
            
            card.appendChild(icon);
            card.appendChild(title);
            card.appendChild(meta);
            
            card.addEventListener('click', () => {
                viewDocument(doc.name);
            });
            
            container.appendChild(card);
        });
    }

    function viewDocument(filename) {
        currentViewingDocument = filename;
        
        fetchWithRetry(`/api/document/${filename}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                documentTitle.textContent = filename;
                
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
                
                documentViewer.classList.add('active');
                
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
                console.error('Error viewing document:', err);
                showToast('error', 'Error', `Failed to load document: ${err.message}`);
            });
    }

    function filterDocuments(query) {
        const coreDocuments = document.querySelectorAll('#core-docs .document-card');
        const artifactDocuments = document.querySelectorAll('#artifacts-docs .document-card');
        
        [].concat(Array.from(coreDocuments), Array.from(artifactDocuments)).forEach(card => {
            const title = card.querySelector('.document-title').textContent.toLowerCase();
            if (title.includes(query)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }

    function handleFiles(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const extension = file.name.split('.').pop().toLowerCase();
            
            if (!['txt', 'rtf', 'docx', 'md'].includes(extension)) {
                showToast('error', 'Invalid File', `File type .${extension} is not supported.`);
                continue;
            }
            
            uploadFile(file);
        }
    }

    function uploadFile(file) {
        // Create a form data object
        const formData = new FormData();
        formData.append('file', file);
        
        // Add to upload list with processing status
        const fileId = Date.now() + '-' + file.name;
        addToUploadList(fileId, file.name, 'processing', 'Uploading...');
        
        // Upload the file
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.processed) {
                updateUploadStatus(fileId, 'success', 'Processed');
                showToast('success', 'Upload Complete', `File ${file.name} uploaded and processed successfully.`);
                loadDocuments();
            } else {
                updateUploadStatus(fileId, 'success', 'Uploaded (not processed)');
                showToast('warning', 'Upload Complete', `File ${file.name} uploaded but could not be processed.`);
            }
        })
        .catch(err => {
            console.error('Error uploading file:', err);
            updateUploadStatus(fileId, 'error', err.message);
            showToast('error', 'Upload Failed', err.message);
        });
    }

    function addToUploadList(id, name, status, message) {
        const item = document.createElement('div');
        item.className = 'upload-item';
        item.id = id;
        
        let statusIcon;
        if (status === 'processing') {
            statusIcon = '<i class="fas fa-spinner fa-spin upload-processing"></i>';
        } else if (status === 'success') {
            statusIcon = '<i class="fas fa-check-circle upload-success"></i>';
        } else if (status === 'error') {
            statusIcon = '<i class="fas fa-times-circle upload-error"></i>';
        }
        
        item.innerHTML = `
            <div class="upload-item-icon">
                <i class="fas fa-file"></i>
            </div>
            <div class="upload-item-details">
                <div class="upload-item-name">${name}</div>
                <div class="upload-item-meta">
                    <span class="upload-item-status">${message}</span>
                </div>
            </div>
            <div class="upload-item-actions">
                ${statusIcon}
            </div>
        `;
        
        uploadList.appendChild(item);
        uploadedFiles.push({ id, name, status, message });
    }

    function updateUploadStatus(id, status, message) {
        const item = document.getElementById(id);
        if (!item) return;
        
        const statusElement = item.querySelector('.upload-item-status');
        const iconContainer = item.querySelector('.upload-item-actions');
        
        statusElement.textContent = message;
        
        let statusIcon;
        if (status === 'processing') {
            statusIcon = '<i class="fas fa-spinner fa-spin upload-processing"></i>';
        } else if (status === 'success') {
            statusIcon = '<i class="fas fa-check-circle upload-success"></i>';
        } else if (status === 'error') {
            statusIcon = '<i class="fas fa-times-circle upload-error"></i>';
        }
        
        iconContainer.innerHTML = statusIcon;
        
        // Update in our array
        const fileIndex = uploadedFiles.findIndex(file => file.id === id);
        if (fileIndex !== -1) {
            uploadedFiles[fileIndex].status = status;
            uploadedFiles[fileIndex].message = message;
        }
    }

    function showToast(type, title, message) {
        // Check if toast container exists, if not create it
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon;
        if (type === 'success') {
            icon = '<i class="fas fa-check-circle"></i>';
        } else if (type === 'error') {
            icon = '<i class="fas fa-times-circle"></i>';
        } else if (type === 'warning') {
            icon = '<i class="fas fa-exclamation-triangle"></i>';
        } else {
            icon = '<i class="fas fa-info-circle"></i>';
        }
        
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <div class="toast-close"><i class="fas fa-times"></i></div>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Add close handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('toast-out');
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('toast-out');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }
        }, 5000);
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
});