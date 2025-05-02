// background.js - Handles background processing tasks for GAIA

import { updateInitializationStatus } from './ui.js';
// Import anything else needed later (e.g., background_processing_ui.js utilities)
// import { updateBackgroundStatus } from './background_processing_ui.js'; (future)

let backgroundWorkerRunning = false;

export function initializeBackgroundTasks() {
    if (backgroundWorkerRunning) {
        console.warn('⚠️ Background worker already running.');
        return;
    }
    backgroundWorkerRunning = true;
    console.log('🛠️ Background processing started.');

    workerLoop();
}

async function workerLoop() {
    while (backgroundWorkerRunning) {
        try {
            await processBackgroundTasks();
        } catch (error) {
            console.error('Background worker error:', error);
        }
        await sleep(5000); // Wait 5 seconds between background cycles
    }
}

async function processBackgroundTasks() {
    console.log('🔄 Checking background tasks...');

    // Example placeholder: document embedding, summarization, etc.
    // Replace these with actual API calls or local processing as needed
    try {
        const response = await fetch('/api/background-tasks', { method: 'POST' });
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Background task processed:', data);
        } else {
            console.warn('⚠️ Background task API failed:', response.status);
        }
    } catch (error) {
        console.error('Error communicating with background task API:', error);
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Optional: Stop background tasks manually
export function stopBackgroundTasks() {
    backgroundWorkerRunning = false;
    console.log('🛑 Background processing stopped.');
}
