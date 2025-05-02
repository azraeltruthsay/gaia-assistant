// conversation_archives.js - GAIA Archive Tab Logic

export function initializeConversationArchives() {
    console.log('📂 Initializing Conversation Archives UI');

    try {
        const docTabs = document.querySelector('.document-tabs');
        if (!docTabs) throw new Error('Document tabs container not found');

        const archivesTabBtn = document.createElement('button');
        archivesTabBtn.classList.add('doc-tab-btn');
        archivesTabBtn.textContent = 'Archives';
        archivesTabBtn.dataset.doctab = 'archives';
        archivesTabBtn.addEventListener('click', () => {
            document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById('archives-docs')?.classList.add('active');
        });

        docTabs.appendChild(archivesTabBtn);

        // Create container
        const container = document.createElement('div');
        container.id = 'archives-docs';
        container.classList.add('document-list', 'doc-tab');
        container.innerHTML = '<div class="loading-spinner">Loading archives...</div>';
        document.querySelector('.documents-container')?.appendChild(container);

        loadConversationArchives();
    } catch (e) {
        console.error('❌ Error setting up conversation archives:', e);
    }
}

async function loadConversationArchives() {
    try {
        const res = await fetch('/api/conversation/archives');
        const data = await res.json();

        const container = document.getElementById('archives-docs');
        if (!container) return;

        container.innerHTML = '';
        if (!data.archives || data.archives.length === 0) {
            container.innerHTML = '<p>No conversation archives found.</p>';
            return;
        }

        for (const archive of data.archives) {
            const item = document.createElement('div');
            item.classList.add('doc-entry');
            item.textContent = `[${archive.timestamp}] ${archive.summary}`;
            container.appendChild(item);
        }
    } catch (e) {
        console.error('Error loading conversation archives:', e);
        const container = document.getElementById('archives-docs');
        if (container) container.innerHTML = '<p>Error loading archives.</p>';
    }
}
