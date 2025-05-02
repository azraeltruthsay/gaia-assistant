// startup.js — Initializes GAIA frontend after backend readiness
import { switchTab } from './ui.js';

// Fetch GAIA status from the API
async function checkInitStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        console.log("[GAIA Startup] Raw API status response: ", status);

        if (status.initialized) {
            console.log("[GAIA Startup] Initialization complete. UI transitioned to chat.");
            switchTab("chat");

            // Failsafe to ensure visibility
            const chatEl = document.getElementById("chat");
            if (chatEl) {
                chatEl.style.display = "block";
                chatEl.classList.add("active");
            } else {
                console.warn("[GAIA Startup] #chat section not found in DOM.");
            }
        } else {
            console.log("[GAIA Startup] AI not ready. Will retry shortly.");
            retryInitCheck();
        }
    } catch (error) {
        console.error("[GAIA Startup] Error fetching status:", error);
        retryInitCheck();
    }
}

// Retry loop if initialization hasn't completed
function retryInitCheck() {
    setTimeout(() => checkInitStatus(), 3000);
}

// DOM-ready startup entry point
console.log("[GAIA Startup] Script loaded");
document.addEventListener("DOMContentLoaded", () => {
    checkInitStatus();
});
