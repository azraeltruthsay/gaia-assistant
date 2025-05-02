// background_processing_ui.js — Full featured background task status panel

export function initializeBackgroundUI() {
    console.log('🧠 Initializing Background Processing Panel');
    try {
        setupBackgroundProcessingUI();
    } catch (e) {
        console.error('❌ Failed to initialize background panel:', e);
    }
}

function setupBackgroundProcessingUI() {
    const container = document.getElementById('archives-docs');
    if (!container) {
        console.warn('⚠️ Archives container not found');
        return;
    }

    const panel = document.createElement('div');
    panel.id = 'background-status-indicator';
    panel.className = 'background-status-indicator';
    panel.innerHTML = `
        <div class="status-header">
            <h3>Background Processing Status</h3>
            <button id="refresh-status" class="btn-primary">
                <i class="fas fa-sync-alt"></i> Refresh
            </button>
        </div>
        <div class="status-content">
            <div class="loading-spinner"></div>
            <p id="bg-status-msg">Loading background processing status...</p>
        </div>
    `;

    container.prepend(panel);
    addBackgroundProcessingStyles();
    setupBackgroundProcessingEvents();
    checkBackgroundStatus();
    setInterval(checkBackgroundStatus, 10000);
}

function setupBackgroundProcessingEvents() {
    const refreshBtn = document.getElementById('refresh-status');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            console.log('🔄 Manual background status refresh');
            checkBackgroundStatus();
        });
    }
}

async function checkBackgroundStatus() {
    const statusText = document.getElementById('bg-status-msg');
    if (!statusText) return;

    try {
        const res = await fetch('/api/background/status');
        const data = await res.json();
        const pending = data?.status?.tasks?.length || 0;
        const archives = data?.status?.archives?.length || 0;

        statusText.innerHTML = `Tasks: <strong>${pending}</strong> | Archives: <strong>${archives}</strong>`;
    } catch (e) {
        console.error('Failed to fetch background processor status:', e);
        statusText.textContent = 'Failed to load status.';
    }
}

function addBackgroundProcessingStyles() {
    const style = document.createElement('style');
    style.textContent = `
    .background-status-indicator {
        margin-top: 10px;
        padding: 10px;
        background: #f4f4f4;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    .background-status-indicator .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .background-status-indicator .btn-primary {
        padding: 5px 10px;
        background-color: #007acc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .background-status-indicator .btn-primary:hover {
        background-color: #005f9e;
    }
    .background-status-indicator .status-content {
        margin-top: 10px;
    }
    `;
    document.head.appendChild(style);
}
