// GAIA Code Analyzer Interface
document.addEventListener('DOMContentLoaded', function() {
    console.log('Code Analyzer script loaded');
    
    // Create code analyzer section in documents tab
    function setupCodeAnalyzerSection() {
        // Add new tab for code analyzer in the document section
        const docTabs = document.querySelector('.document-tabs');
        if (!docTabs) {
            console.error('Document tabs not found');
            return;
        }
        
        // Add code analyzer tab button
        const codeTabBtn = document.createElement('button');
        codeTabBtn.className = 'doc-tab-btn';
        codeTabBtn.dataset.doctab = 'code';
        codeTabBtn.textContent = 'Code Analysis';
        docTabs.appendChild(codeTabBtn);
        
        // Add code analyzer container
        const docsContainer = document.querySelector('.documents-container');
        if (!docsContainer) {
            console.error('Documents container not found');
            return;
        }
        
        // Create code analyzer container
        const codeContainer = document.createElement('div');
        codeContainer.id = 'code-docs';
        codeContainer.className = 'document-list doc-tab';
        
        // Set up code analyzer UI
        codeContainer.innerHTML = `
            <div class="code-analyzer-container">
                <div class="code-files-section">
                    <h3>Code Files</h3>
                    <div class="code-files-actions">
                        <button id="refresh-code-files" class="btn-primary">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button id="upload-code-file" class="btn-primary">
                            <i class="fas fa-upload"></i> Upload
                        </button>
                    </div>
                    <div class="code-files-tree">
                        <div class="loading-spinner" id="code-files-loading"></div>
                        <div id="code-files-list" class="tree-view"></div>
                    </div>
                </div>
                
                <div class="code-analysis-section">
                    <div id="code-file-view" class="hidden">
                        <h3 id="code-file-title">Filename</h3>
                        <div class="code-file-actions">
                            <button id="analyze-code-file" class="btn-primary">
                                <i class="fas fa-search"></i> Analyze
                            </button>
                            <button id="close-code-file" class="btn-secondary">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                        <div id="code-file-content" class="code-content"></div>
                    </div>
                    
                    <div id="code-analysis-view" class="hidden">
                        <h3>Code Analysis</h3>
                        <div class="code-analysis-actions">
                            <button id="generate-code-artifact" class="btn-primary">
                                <i class="fas fa-file-code"></i> Generate Documentation
                            </button>
                            <button id="close-code-analysis" class="btn-secondary">
                                <i class="fas fa-times"></i> Close
                            </button>
                        </div>
                        <div id="code-analysis-content" class="analysis-content"></div>
                    </div>
                    
                    <div id="code-upload-view" class="hidden">
                        <h3>Upload Code File</h3>
                        <div class="code-upload-container">
                            <div class="code-upload-area" id="code-upload-area">
                                <div class="upload-icon">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                </div>
                                <p>Drag and drop code files here</p>
                                <p class="upload-subtitle">or</p>
                                <label for="code-file-input" class="upload-btn">Browse Files</label>
                                <input type="file" id="code-file-input" accept=".py,.js,.ts,.html,.css,.json,.xml,.yaml,.yml,.md,.c,.cpp,.h,.cs,.java,.go,.rb,.php" hidden>
                                <p class="code-upload-note">Files will be saved to the external code directory</p>
                            </div>
                            <div class="directory-input">
                                <label for="code-directory-input">Save to directory:</label>
                                <input type="text" id="code-directory-input" placeholder="e.g., project/src">
                            </div>
                            <div class="code-upload-actions">
                                <button id="cancel-code-upload" class="btn-secondary">
                                    <i class="fas fa-times"></i> Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        docsContainer.insertBefore(codeContainer, document.getElementById('document-viewer'));
        
        // Add event listener to tab button
        codeTabBtn.addEventListener('click', function() {
            changeDocTab('code');
            loadCodeFiles();
        });
        
        // Add CSS styles
        addCodeAnalyzerStyles();
        
        console.log('Code analyzer section set up successfully');
        
        // Set up event handlers
        setupCodeAnalyzerEvents();
    }
    
    function addCodeAnalyzerStyles() {
        // Create style element
        const style = document.createElement('style');
        style.textContent = `
            .code-analyzer-container {
                display: flex;
                height: 70vh;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            
            .code-files-section {
                flex: 1;
                max-width: 300px;
                background: white;
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-sm);
                padding: 1rem;
                display: flex;
                flex-direction: column;
            }
            
            .code-analysis-section {
                flex: 3;
                background: white;
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-sm);
                padding: 1rem;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .code-files-actions, .code-file-actions, .code-analysis-actions, .code-upload-actions {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
            }
            
            .btn-primary, .btn-secondary {
                padding: 0.5rem 1rem;
                border-radius: var(--radius-md);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.875rem;
            }
            
            .btn-primary {
                background: var(--primary-color);
                color: white;
            }
            
            .btn-secondary {
                background: #f3f4f6;
                color: var(--text-color);
                border: 1px solid var(--border-color);
            }
            
            .code-files-tree {
                flex-grow: 1;
                overflow-y: auto;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
            }
            
            .tree-view {
                padding: 0.5rem;
            }
            
            .tree-item {
                padding: 0.25rem 0.5rem;
                cursor: pointer;
                border-radius: var(--radius-sm);
                margin-bottom: 0.25rem;
                user-select: none;
            }
            
            .tree-item:hover {
                background: #f9fafb;
            }
            
            .tree-item.active {
                background: #e5e7eb;
            }
            
            .tree-item i {
                margin-right: 0.5rem;
                width: 1rem;
                text-align: center;
            }
            
            .code-content, .analysis-content {
                flex-grow: 1;
                overflow-y: auto;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
                padding: 1rem;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.875rem;
                line-height: 1.5;
                white-space: pre-wrap;
                max-height: 500px;
            }
            
            .directory-input {
                margin: 1rem 0;
            }
            
            .directory-input input {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
                margin-top: 0.25rem;
            }
            
            .code-upload-container {
                display: flex;
                flex-direction: column;
            }
            
            .code-upload-area {
                border: 2px dashed var(--border-color);
                border-radius: var(--radius-lg);
                padding: 2rem;
                text-align: center;
                margin-bottom: 1rem;
                transition: var(--transition);
            }
            
            .code-upload-area.drag-over {
                border-color: var(--primary-color);
                background-color: rgba(30, 58, 138, 0.05);
            }
            
            .code-upload-note {
                font-size: 0.75rem;
                color: var(--text-light);
                margin-top: 1rem;
            }
			.hidden {
                display: none;
            }
            
            /* Language-specific icons */
            .lang-py i { color: #3776AB; }
            .lang-js i { color: #F7DF1E; }
            .lang-ts i { color: #3178C6; }
            .lang-html i { color: #E34F26; }
            .lang-css i { color: #1572B6; }
            .lang-java i { color: #007396; }
            .lang-go i { color: #00ADD8; }
            .lang-rb i { color: #CC342D; }
            .lang-cs i { color: #178600; }
            .lang-php i { color: #777BB4; }
            .lang-sh i { color: #4EAA25; }
            .lang-md i { color: #083fa1; }
            .lang-json i { color: #000000; }
            .lang-xml i { color: #F16529; }
            .lang-yaml i { color: #FF0000; }
            
            /* Code highlight theme */
            pre code {
                background-color: #1f2937;
                color: white;
                padding: 1rem;
                border-radius: var(--radius-md);
                overflow-x: auto;
                margin-bottom: 1rem;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    function setupCodeAnalyzerEvents() {
        // Refresh code files button
        const refreshButton = document.getElementById('refresh-code-files');
        if (refreshButton) {
            refreshButton.addEventListener('click', loadCodeFiles);
        }
        
        // Upload code file button
        const uploadButton = document.getElementById('upload-code-file');
        if (uploadButton) {
            uploadButton.addEventListener('click', showCodeUploadView);
        }
        
        // Close code file button
        const closeCodeFileButton = document.getElementById('close-code-file');
        if (closeCodeFileButton) {
            closeCodeFileButton.addEventListener('click', hideCodeFileView);
        }
        
        // Analyze code file button
        const analyzeButton = document.getElementById('analyze-code-file');
        if (analyzeButton) {
            analyzeButton.addEventListener('click', analyzeCurrentCodeFile);
        }
        
        // Close code analysis button
        const closeAnalysisButton = document.getElementById('close-code-analysis');
        if (closeAnalysisButton) {
            closeAnalysisButton.addEventListener('click', hideCodeAnalysisView);
        }
        
        // Generate code artifact button
        const generateArtifactButton = document.getElementById('generate-code-artifact');
        if (generateArtifactButton) {
            generateArtifactButton.addEventListener('click', generateCodeArtifact);
        }
        
        // Cancel code upload button
        const cancelUploadButton = document.getElementById('cancel-code-upload');
        if (cancelUploadButton) {
            cancelUploadButton.addEventListener('click', hideCodeUploadView);
        }
        
        // Code file input
        const codeFileInput = document.getElementById('code-file-input');
        if (codeFileInput) {
            codeFileInput.addEventListener('change', handleCodeFileSelect);
        }
        
        // Code upload area drag and drop
        const uploadArea = document.getElementById('code-upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', function() {
                uploadArea.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                
                if (e.dataTransfer.files.length) {
                    handleCodeFileSelect(e);
                }
            });
        }
    }
    
    // Current state
    let currentCodeFile = null;
    let currentCodeAnalysis = null;
    
    // Load code files
    function loadCodeFiles() {
        const codeFilesList = document.getElementById('code-files-list');
        const codeFilesLoading = document.getElementById('code-files-loading');
        
        if (!codeFilesList || !codeFilesLoading) {
            console.error('Code files elements not found');
            return;
        }
        
        // Show loading spinner
        codeFilesList.innerHTML = '';
        codeFilesLoading.style.display = 'block';
        
        fetchWithRetry('/api/code')
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                codeFilesLoading.style.display = 'none';
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                if (!data.code_files || data.code_files.length === 0) {
                    codeFilesList.innerHTML = '<div class="empty-message">No code files found. Upload some code to get started.</div>';
                    return;
                }
                
                // Group files by directory
                const filesByDir = {};
                data.code_files.forEach(file => {
                    const parts = file.path.split('/');
                    let dirPath = '';
                    
                    // If file is directly in the root
                    if (parts.length === 1) {
                        if (!filesByDir['']) {
                            filesByDir[''] = [];
                        }
                        filesByDir[''].push(file);
                    } else {
                        // Handle directories
                        const fileName = parts.pop();
                        const dir = parts.join('/');
                        
                        if (!filesByDir[dir]) {
                            filesByDir[dir] = [];
                        }
                        
                        filesByDir[dir].push({
                            ...file,
                            name: fileName
                        });
                    }
                });
                
                // Render the file tree
                const dirs = Object.keys(filesByDir).sort();
                
                let html = '';
                
                // Root files first
                if (filesByDir[''] && filesByDir[''].length > 0) {
                    filesByDir[''].forEach(file => {
                        const fileName = file.path;
                        html += createFileItem(file.path, fileName, file.language, file.full_path);
                    });
                }
                
                // Then directories
                dirs.filter(dir => dir !== '').forEach(dir => {
                    // Create directory item
                    html += `<div class="tree-directory">
                        <div class="tree-item directory">
                            <i class="fas fa-folder"></i>${dir}
                        </div>
                        <div class="tree-directory-content" style="padding-left: 1rem;">`;
                    
                    // Add files in this directory
                    filesByDir[dir].forEach(file => {
                        html += createFileItem(file.path, file.name, file.language, file.full_path);
                    });
                    
                    html += `</div></div>`;
                });
                
                codeFilesList.innerHTML = html;
                
                // Add click handlers to file items
                document.querySelectorAll('.tree-item.file').forEach(item => {
                    item.addEventListener('click', function() {
                        const filePath = this.dataset.path;
                        const fullPath = this.dataset.fullPath;
                        loadCodeFile(filePath, fullPath);
                    });
                });
            })
            .catch(err => {
                codeFilesLoading.style.display = 'none';
                console.error('Error loading code files:', err);
                
                codeFilesList.innerHTML = `<div class="error-message">Error loading code files: ${err.message}</div>`;
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to load code files: ${err.message}`);
                }
            });
    }
    
    function createFileItem(path, name, language, fullPath) {
        // Determine icon based on file extension
        let iconClass = 'fa-file-code';
        let langClass = '';
        
        if (language) {
            langClass = `lang-${language.toLowerCase().replace(/[^a-z0-9]/g, '')}`;
        }
        
        return `<div class="tree-item file ${langClass}" data-path="${path}" data-full-path="${fullPath}">
            <i class="fas ${iconClass}"></i>${name}
        </div>`;
    }
    
    function loadCodeFile(filePath, fullPath) {
        // Update current code file
        currentCodeFile = {
            path: filePath,
            fullPath: fullPath
        };
        
        // Get filename from path
        const fileName = filePath.split('/').pop();
        
        // Update file view
        const codeFileTitle = document.getElementById('code-file-title');
        const codeFileContent = document.getElementById('code-file-content');
        
        if (!codeFileTitle || !codeFileContent) {
            console.error('Code file view elements not found');
            return;
        }
        
        // Show code file view
        document.getElementById('code-file-view').classList.remove('hidden');
        document.getElementById('code-analysis-view').classList.add('hidden');
        document.getElementById('code-upload-view').classList.add('hidden');
        
        // Update title
        codeFileTitle.textContent = fileName;
        
        // Show loading
        codeFileContent.innerHTML = '<div class="loading-spinner"></div>';
        
        // Try the dedicated code file API first
        fetchWithRetry(`/api/code/file?filepath=${encodeURIComponent(filePath)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Determine language based on file extension
                const extension = fileName.split('.').pop().toLowerCase();
                let language = data.language || '';
                
                if (!language) {
                    switch (extension) {
                        case 'py': language = 'python'; break;
                        case 'js': language = 'javascript'; break;
                        case 'ts': language = 'typescript'; break;
                        case 'html': language = 'html'; break;
                        case 'css': language = 'css'; break;
                        case 'json': language = 'json'; break;
                        case 'xml': language = 'xml'; break;
                        case 'yaml':
                        case 'yml': language = 'yaml'; break;
                        case 'md': language = 'markdown'; break;
                        case 'c':
                        case 'cpp':
                        case 'h': language = 'cpp'; break;
                        case 'cs': language = 'csharp'; break;
                        case 'java': language = 'java'; break;
                        case 'go': language = 'go'; break;
                        case 'rb': language = 'ruby'; break;
                        case 'php': language = 'php'; break;
                        case 'sh':
                        case 'bash': language = 'bash'; break;
                        default: language = 'plaintext';
                    }
                }
                
                // Render code with syntax highlighting
                if (typeof hljs !== 'undefined') {
                    try {
                        const highlighted = hljs.highlight(data.content, { language }).value;
                        codeFileContent.innerHTML = `<pre><code class="language-${language} hljs">${highlighted}</code></pre>`;
                    } catch (e) {
                        console.error('Error highlighting code:', e);
                        codeFileContent.innerHTML = `<pre><code>${data.content}</code></pre>`;
                    }
                } else {
                    codeFileContent.innerHTML = `<pre><code>${data.content}</code></pre>`;
                }
            })
            .catch(err => {
                console.error('Error loading code file with dedicated API:', err);
                
                // Fallback to the general document API
                fetchWithRetry(`/api/document/${filePath}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        
                        // Determine language based on file extension
                        const extension = fileName.split('.').pop().toLowerCase();
                        let language = 'plaintext';
                        
                        switch (extension) {
                            case 'py': language = 'python'; break;
                            case 'js': language = 'javascript'; break;
                            case 'ts': language = 'typescript'; break;
                            case 'html': language = 'html'; break;
                            case 'css': language = 'css'; break;
                            case 'json': language = 'json'; break;
                            case 'xml': language = 'xml'; break;
                            case 'yaml':
                            case 'yml': language = 'yaml'; break;
                            case 'md': language = 'markdown'; break;
                            case 'c':
                            case 'cpp':
                            case 'h': language = 'cpp'; break;
                            case 'cs': language = 'csharp'; break;
                            case 'java': language = 'java'; break;
                            case 'go': language = 'go'; break;
                            case 'rb': language = 'ruby'; break;
                            case 'php': language = 'php'; break;
                            case 'sh':
                            case 'bash': language = 'bash'; break;
                            default: language = 'plaintext';
                        }
                        
                        // Render code with syntax highlighting
                        if (typeof hljs !== 'undefined') {
                            try {
                                const highlighted = hljs.highlight(data.content, { language }).value;
                                codeFileContent.innerHTML = `<pre><code class="language-${language} hljs">${highlighted}</code></pre>`;
                            } catch (e) {
                                console.error('Error highlighting code:', e);
                                codeFileContent.innerHTML = `<pre><code>${data.content}</code></pre>`;
                            }
                        } else {
                            codeFileContent.innerHTML = `<pre><code>${data.content}</code></pre>`;
                        }
                    })
                    .catch(innerErr => {
                        console.error('Both API attempts failed:', innerErr);
                        codeFileContent.innerHTML = `<div class="error-message">Error loading file: ${err.message}<br>Fallback also failed: ${innerErr.message}</div>`;
                        
                        // Show toast if available
                        if (typeof showToast === 'function') {
                            showToast('error', 'Error', `Failed to load file: ${err.message}`);
                        }
                    });
            });
    }
	function hideCodeFileView() {
        document.getElementById('code-file-view').classList.add('hidden');
        currentCodeFile = null;
    }
    
    function analyzeCurrentCodeFile() {
        if (!currentCodeFile) {
            console.error('No code file selected');
            
            // Show toast if available
            if (typeof showToast === 'function') {
                showToast('error', 'Error', 'No code file selected');
            }
            
            return;
        }
        
        const codeAnalysisContent = document.getElementById('code-analysis-content');
        
        if (!codeAnalysisContent) {
            console.error('Code analysis view not found');
            return;
        }
        
        // Show analysis view
        document.getElementById('code-analysis-view').classList.remove('hidden');
        
        // Show loading
        codeAnalysisContent.innerHTML = '<div class="loading-spinner"></div>';
        
        // Fetch analysis
        fetchWithRetry('/api/code/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filepath: currentCodeFile.path
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Store current analysis
                currentCodeAnalysis = data.analysis;
                
                // Render analysis
                let html = '<div class="analysis-section">';
                
                // Summary
                html += `<h4>Summary</h4>
                <p>${data.analysis.summary || 'No summary available'}</p>`;
                
                // Key components
                if (data.analysis.components && data.analysis.components.length > 0) {
                    html += '<h4>Key Components</h4><ul>';
                    data.analysis.components.forEach(component => {
                        html += `<li>${component}</li>`;
                    });
                    html += '</ul>';
                }
                
                // Potential improvements
                if (data.analysis.improvements && data.analysis.improvements.length > 0) {
                    html += '<h4>Potential Improvements</h4><ul>';
                    data.analysis.improvements.forEach(improvement => {
                        html += `<li>${improvement}</li>`;
                    });
                    html += '</ul>';
                }
                
                // Issues
                if (data.analysis.issues && data.analysis.issues.length > 0) {
                    html += '<h4>Issues</h4><ul>';
                    data.analysis.issues.forEach(issue => {
                        html += `<li>${issue}</li>`;
                    });
                    html += '</ul>';
                }
                
                // Complexity rating
                if (data.analysis.complexity_rating) {
                    html += `<h4>Complexity Rating</h4>
                    <p>${data.analysis.complexity_rating}/10</p>`;
                }
                
                html += '</div>';
                
                codeAnalysisContent.innerHTML = html;
            })
            .catch(err => {
                console.error('Error analyzing code:', err);
                codeAnalysisContent.innerHTML = `<div class="error-message">Error analyzing code: ${err.message}</div>`;
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to analyze code: ${err.message}`);
                }
            });
    }
    
    function hideCodeAnalysisView() {
        document.getElementById('code-analysis-view').classList.add('hidden');
        currentCodeAnalysis = null;
    }
    
    function generateCodeArtifact() {
        if (!currentCodeFile) {
            console.error('No code file selected');
            
            // Show toast if available
            if (typeof showToast === 'function') {
                showToast('error', 'Error', 'No code file selected');
            }
            
            return;
        }
        
        // Get filename from path
        const fileName = currentCodeFile.path.split('/').pop();
        
        // Generate artifact prompt
        let prompt = `Generate a detailed code analysis and documentation for the file ${fileName}`;
        
        if (currentCodeAnalysis) {
            prompt += `. The code's purpose is: ${currentCodeAnalysis.summary}`;
            
            if (currentCodeAnalysis.complexity_rating) {
                prompt += `. This code has a complexity rating of ${currentCodeAnalysis.complexity_rating}/10`;
            }
        }
        
        // Add to chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = `artifact: ${prompt}`;
            
            // Switch to chat view
            const chatTabBtn = document.querySelector('.nav-btn[data-tab="chat"]');
            if (chatTabBtn) {
                chatTabBtn.click();
            }
            
            // Focus chat input
            chatInput.focus();
            
            // Show toast
            if (typeof showToast === 'function') {
                showToast('info', 'Artifact Prompt Ready', 'Press Enter to send the prompt and generate the artifact');
            }
        }
    }
    
    function showCodeUploadView() {
        document.getElementById('code-file-view').classList.add('hidden');
        document.getElementById('code-analysis-view').classList.add('hidden');
        document.getElementById('code-upload-view').classList.remove('hidden');
    }
    
    function hideCodeUploadView() {
        document.getElementById('code-upload-view').classList.add('hidden');
    }
    
    function handleCodeFileSelect(event) {
        const files = event.dataTransfer ? event.dataTransfer.files : event.target.files;
        
        if (!files || files.length === 0) {
            return;
        }
        
        // Get directory input
        const directoryInput = document.getElementById('code-directory-input');
        const directory = directoryInput ? directoryInput.value.trim() : '';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', files[0]);
        formData.append('directory', directory);
        
        // Show loading
        const uploadArea = document.getElementById('code-upload-area');
        if (uploadArea) {
            uploadArea.innerHTML = '<div class="loading-spinner"></div><p>Uploading file...</p>';
        }
        
        // Upload file
        fetch('/api/code/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Show success message
                if (uploadArea) {
                    uploadArea.innerHTML = `
                        <div class="upload-success">
                            <i class="fas fa-check-circle"></i>
                            <p>File uploaded successfully!</p>
                            <p>Language: ${data.language}</p>
                            <p>Created ${data.chunks} chunks for indexing</p>
                        </div>
                    `;
                }
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('success', 'Upload Complete', `File uploaded and processed successfully.`);
                }
                
                // Reload code files after a delay
                setTimeout(() => {
                    loadCodeFiles();
                    hideCodeUploadView();
                }, 2000);
            })
            .catch(err => {
                console.error('Error uploading file:', err);
                
                // Show error message
                if (uploadArea) {
                    uploadArea.innerHTML = `
                        <div class="upload-error">
                            <i class="fas fa-times-circle"></i>
                            <p>Error uploading file: ${err.message}</p>
                            <p>Please try again.</p>
                        </div>
                    `;
                }
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Upload Failed', err.message);
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
    
    // Helper function to check if changeDocTab exists and create it if not
    function ensureChangeDocTabExists() {
        if (typeof window.changeDocTab !== 'function') {
            console.warn('changeDocTab function not found, creating a new one');
            
            window.changeDocTab = function(docTabName) {
                document.querySelectorAll('.doc-tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
                
                if (docTabName === 'core') {
                    document.getElementById('core-docs').classList.add('active');
                } else if (docTabName === 'artifacts') {
                    document.getElementById('artifacts-docs').classList.add('active');
                } else if (docTabName === 'archives') {
                    if (document.getElementById('archives-docs')) {
                        document.getElementById('archives-docs').classList.add('active');
                    }
                } else if (docTabName === 'code') {
                    document.getElementById('code-docs').classList.add('active');
                }
                
                document.querySelector(`.doc-tab-btn[data-doctab="${docTabName}"]`).classList.add('active');
            };
        } else {
            // Monkey patch the existing changeDocTab function
            const originalChangeDocTab = window.changeDocTab;
            
            window.changeDocTab = function(docTabName) {
                document.querySelectorAll('.doc-tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
                
                if (docTabName === 'core') {
                    document.getElementById('core-docs').classList.add('active');
                } else if (docTabName === 'artifacts') {
                    document.getElementById('artifacts-docs').classList.add('active');
                } else if (docTabName === 'archives') {
                    if (document.getElementById('archives-docs')) {
                        document.getElementById('archives-docs').classList.add('active');
                    }
                } else if (docTabName === 'code') {
                    document.getElementById('code-docs').classList.add('active');
                }
                
                document.querySelector(`.doc-tab-btn[data-doctab="${docTabName}"]`).classList.add('active');
            };
        }
    }
    
    // Initialize code analyzer
    function init() {
        // Ensure the changeDocTab function exists
        ensureChangeDocTabExists();
        
        // Set up code analyzer section
        setupCodeAnalyzerSection();
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