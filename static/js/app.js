// app.js - Central GAIA frontend bootstrapper

import { startGaiaSession } from './startup.js';
import { initializeUI } from './ui.js';
import { initializeChat } from './chat.js';
import { initializeConversationArchives } from './conversation_archives.js';
import { initializeBackgroundUI } from './background_processing_ui.js';
import { initializeCodeAnalyzer } from './code-analyzer.js';

// Entry point triggered on DOM load
window.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 GAIA frontend booting...');
    try {
        startGaiaSession();
    } catch (err) {
        console.error('❌ Error during GAIA startup:', err);
        const errBox = document.getElementById('initialization-error');
        if (errBox) {
            errBox.textContent = 'Frontend startup error. Check console logs.';
            errBox.classList.remove('hidden');
        }
    }
});

// Manual app-level initializer, safe to call externally
export function initializeApp() {
    console.log('🌟 GAIA App Initialized');
    try {
        initializeUI();                    // Sidebar tab navigation
        initializeChat();                  // Chat module listeners
        initializeConversationArchives();  // Archives document tab
        initializeBackgroundUI();          // Background processor panel
        initializeCodeAnalyzer();          // Code analysis tab
    } catch (e) {
        console.error('❌ Failed to fully initialize GAIA modules:', e);
    }
}
