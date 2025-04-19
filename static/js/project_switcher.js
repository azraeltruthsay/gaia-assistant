// GAIA Project Switcher Interface
document.addEventListener('DOMContentLoaded', function() {
    console.log('Project Switcher script loaded');
    
    // Add project switcher to the header
    function addProjectSwitcher() {
        // Find the sidebar header
        const sidebarHeader = document.querySelector('.sidebar-header');
        if (!sidebarHeader) {
            console.error('Sidebar header not found');
            return;
        }
        
        // Create project switcher dropdown
        const projectSwitcher = document.createElement('div');
        projectSwitcher.className = 'project-switcher';
        projectSwitcher.innerHTML = `
            <div class="project-dropdown">
                <button id="current-project" class="project-dropdown-btn">
                    <span id="project-name">Loading...</span>
                    <i class="fas fa-caret-down"></i>
                </button>
                <div id="project-dropdown-content" class="project-dropdown-content">
                    <div class="loading-spinner project-spinner"></div>
                </div>
            </div>
        `;
        
        // Insert before the existing content
        sidebarHeader.insertBefore(projectSwitcher, sidebarHeader.firstChild);
        
        // Add CSS styles
        addProjectSwitcherStyles();
        
        // Add event handlers
        setupProjectSwitcherEvents();
        
        // Load projects
        loadProjects();
    }
    
    function addProjectSwitcherStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .project-switcher {
                margin-bottom: 0.5rem;
                width: 100%;
            }
            
            .project-dropdown {
                position: relative;
                width: 100%;
            }
            
            .project-dropdown-btn {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 0.5rem;
                border: none;
                border-radius: var(--radius-md);
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                font-size: 0.9rem;
            }
            
            .project-dropdown-btn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            .project-dropdown-content {
                display: none;
                position: absolute;
                background-color: var(--primary-light);
                min-width: 100%;
                box-shadow: var(--shadow-md);
                z-index: 1;
                border-radius: var(--radius-md);
                max-height: 300px;
                overflow-y: auto;
            }
            
            .project-dropdown-content.show {
                display: block;
            }
            
            .project-item {
                color: white;
                padding: 0.5rem;
                cursor: pointer;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .project-item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            .project-item.active {
                background-color: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            
            .project-spinner {
                margin: 1rem auto;
                border-color: rgba(255, 255, 255, 0.3);
                border-top-color: white;
            }
            
            .project-item-name {
                font-weight: bold;
                margin-bottom: 0.25rem;
            }
            
            .project-item-desc {
                font-size: 0.75rem;
                opacity: 0.8;
            }
            
            /* Add new project button */
            .add-project-btn {
                color: white;
                padding: 0.5rem;
                cursor: pointer;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.1);
                margin-top: 0.5rem;
                border-radius: var(--radius-md);
            }
            
            .add-project-btn:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            /* Project modal */
            .project-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 100;
                align-items: center;
                justify-content: center;
            }
            
            .project-modal.show {
                display: flex;
            }
            
            .project-modal-content {
                background-color: white;
                padding: 1rem;
                border-radius: var(--radius-md);
                max-width: 500px;
                width: 90%;
                box-shadow: var(--shadow-lg);
            }
            
            .project-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border-color);
            }
            
            .project-modal-header h3 {
                margin: 0;
                color: var(--primary-color);
            }
            
            .project-modal-close {
                cursor: pointer;
                font-size: 1.5rem;
                color: var(--text-light);
            }
            
            .project-form-group {
                margin-bottom: 1rem;
            }
            
            .project-form-group label {
                display: block;
                margin-bottom: 0.25rem;
                font-weight: bold;
                color: var(--text-color);
            }
            
            .project-form-group input,
            .project-form-group textarea {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
            }
            
            .project-form-group textarea {
                min-height: 100px;
                resize: vertical;
            }
            
            .project-form-actions {
                display: flex;
                justify-content: flex-end;
                gap: 0.5rem;
                margin-top: 1rem;
            }
            
            .project-form-actions button {
                padding: 0.5rem 1rem;
                border: none;
                border-radius: var(--radius-sm);
                cursor: pointer;
            }
            
            .project-form-actions .cancel-btn {
                background-color: var(--border-color);
                color: var(--text-color);
            }
            
            .project-form-actions .save-btn {
                background-color: var(--primary-color);
                color: white;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    function setupProjectSwitcherEvents() {
        // Toggle dropdown when button is clicked
        const dropdownBtn = document.getElementById('current-project');
        const dropdownContent = document.getElementById('project-dropdown-content');
        
        if (dropdownBtn && dropdownContent) {
            dropdownBtn.addEventListener('click', function() {
                dropdownContent.classList.toggle('show');
            });
            
            // Close dropdown when clicking outside
            window.addEventListener('click', function(event) {
                if (!event.target.matches('.project-dropdown-btn') && !event.target.closest('.project-dropdown-btn')) {
                    dropdownContent.classList.remove('show');
                }
            });
        }
    }
    
    function loadProjects() {
        const dropdownContent = document.getElementById('project-dropdown-content');
        const projectName = document.getElementById('project-name');
        
        if (!dropdownContent || !projectName) {
            console.error('Project dropdown elements not found');
            return;
        }
        
        // Show loading spinner
        dropdownContent.innerHTML = '<div class="loading-spinner project-spinner"></div>';
        
        fetchWithRetry('/api/projects')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Get current project
                let currentProject = null;
                const projects = data.projects || [];
                
                for (const project of projects) {
                    if (project.is_current) {
                        currentProject = project;
                        break;
                    }
                }
                
                // Update current project name
                if (currentProject) {
                    projectName.textContent = currentProject.name;
                } else if (projects.length > 0) {
                    projectName.textContent = projects[0].name;
                } else {
                    projectName.textContent = 'No Projects';
                }
                
                // Render project list
                let html = '';
                
                for (const project of projects) {
                    html += `
                        <div class="project-item ${project.is_current ? 'active' : ''}" data-id="${project.id}">
                            <div class="project-item-name">${project.name}</div>
                            <div class="project-item-desc">${project.description}</div>
                        </div>
                    `;
                }
                
                // Add 'Add Project' button
                html += `
                    <div class="add-project-btn">
                        <i class="fas fa-plus"></i> Add New Project
                    </div>
                `;
                
                dropdownContent.innerHTML = html;
                
                // Add click handlers for project items
                document.querySelectorAll('.project-item').forEach(item => {
                    item.addEventListener('click', function() {
                        const projectId = this.dataset.id;
                        switchProject(projectId);
                    });
                });
                
                // Add click handler for 'Add Project' button
                const addProjectBtn = document.querySelector('.add-project-btn');
                if (addProjectBtn) {
                    addProjectBtn.addEventListener('click', function() {
                        showAddProjectModal();
                    });
                }
            })
            .catch(err => {
                console.error('Error loading projects:', err);
                
                dropdownContent.innerHTML = `<div class="error-message">Error loading projects: ${err.message}</div>`;
                
                // Show toast if available
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to load projects: ${err.message}`);
                }
            });
    }
    
    function switchProject(projectId) {
        // Close dropdown
        const dropdownContent = document.getElementById('project-dropdown-content');
        if (dropdownContent) {
            dropdownContent.classList.remove('show');
        }
        
        // Show loading spinner
        const projectName = document.getElementById('project-name');
        if (projectName) {
            projectName.innerHTML = '<div class="loading-spinner" style="width: 20px; height: 20px;"></div>';
        }
        
        fetchWithRetry(`/api/projects/switch/${projectId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Update project name
                if (projectName && data.project && data.project.name) {
                    projectName.textContent = data.project.name;
                }
                
                // Show success message
                if (typeof showToast === 'function') {
                    showToast('success', 'Project Switched', `Switched to project: ${data.project.name}`);
                }
                
                // Reload page to refresh context
                setTimeout(() => {
                    location.reload();
                }, 1000);
            })
            .catch(err => {
                console.error('Error switching projects:', err);
                
                // Restore dropdown content
                loadProjects();
                
                // Show error message
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to switch projects: ${err.message}`);
                }
            });
    }
    
    function showAddProjectModal() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('project-modal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'project-modal';
            modal.className = 'project-modal';
            
            modal.innerHTML = `
                <div class="project-modal-content">
                    <div class="project-modal-header">
                        <h3>Add New Project</h3>
                        <span class="project-modal-close">&times;</span>
                    </div>
                    <form id="project-form">
                        <div class="project-form-group">
                            <label for="project-id">Project ID</label>
                            <input type="text" id="project-id" placeholder="e.g., development, research, etc." required>
                        </div>
                        <div class="project-form-group">
                            <label for="project-name">Project Name</label>
                            <input type="text" id="project-name-input" placeholder="e.g., Development Project" required>
                        </div>
                        <div class="project-form-group">
                            <label for="project-description">Description</label>
                            <textarea id="project-description" placeholder="Brief description of the project"></textarea>
                        </div>
                        <div class="project-form-group">
                            <label for="project-instructions">Instructions File</label>
                            <input type="text" id="project-instructions" placeholder="e.g., project_instructions.txt" required>
                        </div>
                        <div class="project-form-actions">
                            <button type="button" class="cancel-btn">Cancel</button>
                            <button type="submit" class="save-btn">Create Project</button>
                        </div>
                    </form>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Add event handlers
            const closeBtn = modal.querySelector('.project-modal-close');
            const cancelBtn = modal.querySelector('.cancel-btn');
            const form = modal.querySelector('#project-form');
            
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    modal.classList.remove('show');
                });
            }
            
            if (cancelBtn) {
                cancelBtn.addEventListener('click', function() {
                    modal.classList.remove('show');
                });
            }
            
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    createProject();
                });
            }
            
            // Close when clicking outside
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.classList.remove('show');
                }
            });
        }
        
        // Show modal
        modal.classList.add('show');
    }
    
    function createProject() {
        const projectId = document.getElementById('project-id');
        const projectName = document.getElementById('project-name-input');
        const projectDescription = document.getElementById('project-description');
        const projectInstructions = document.getElementById('project-instructions');
        
        if (!projectId || !projectName || !projectDescription || !projectInstructions) {
            console.error('Project form elements not found');
            return;
        }
        
        const data = {
            id: projectId.value.trim(),
            name: projectName.value.trim(),
            description: projectDescription.value.trim(),
            instructions_file: projectInstructions.value.trim(),
            is_default: false
        };
        
        // Validate required fields
        if (!data.id || !data.name || !data.instructions_file) {
            // Show error message
            if (typeof showToast === 'function') {
                showToast('error', 'Error', 'Please fill in all required fields');
            }
            return;
        }
        
        fetchWithRetry('/api/projects/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Close modal
                const modal = document.getElementById('project-modal');
                if (modal) {
                    modal.classList.remove('show');
                }
                
                // Show success message
                if (typeof showToast === 'function') {
                    showToast('success', 'Project Created', `Created project: ${data.project.name}`);
                }
                
                // Reload projects
                loadProjects();
            })
            .catch(err => {
                console.error('Error creating project:', err);
                
                // Show error message
                if (typeof showToast === 'function') {
                    showToast('error', 'Error', `Failed to create project: ${err.message}`);
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
    
    // Initialize project switcher
    function init() {
        addProjectSwitcher();
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