// code-analyzer.js - Adds tab and placeholder for code analysis

export function initializeCodeAnalyzer() {
    console.log('🧪 Initializing Code Analyzer UI');

    const docTabs = document.querySelector('.document-tabs');
    if (!docTabs) {
        console.error('Document tabs not found');
        return;
    }

    // Prevent duplicate tab creation
    if (document.querySelector('[data-doctab="code"]')) return;

    const codeTabBtn = document.createElement('button');
    codeTabBtn.className = 'doc-tab-btn';
    codeTabBtn.dataset.doctab = 'code';
    codeTabBtn.textContent = 'Code Analysis';
    docTabs.appendChild(codeTabBtn);

    const docsContainer = document.querySelector('.documents-container');
    if (!docsContainer) {
        console.error('Documents container not found');
        return;
    }

    const container = document.createElement('div');
    container.id = 'code-docs';
    container.classList.add('document-list', 'doc-tab');
    container.innerHTML = '<p>Code analysis panel coming soon...</p>';
    docsContainer.appendChild(container);

    codeTabBtn.addEventListener('click', () => {
        document.querySelectorAll('.doc-tab').forEach(tab => tab.classList.remove('active'));
        container.classList.add('active');
    });
}
