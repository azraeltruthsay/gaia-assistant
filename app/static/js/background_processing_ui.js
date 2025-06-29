// background_processing_ui.js

let backgroundPollingEnabled = false;
let pollingInterval = null;

function updateBackgroundStatus() {
  fetch('/api/background/status')
    .then(response => response.json())
    .then(data => {
      console.log("[BG_UI] 🔄 Updated background task UI", data);
      // TODO: Insert logic here to update the DOM based on `data`
    })
    .catch(err => {
      console.warn("[BG_UI] ❌ Failed to fetch background status:", err);
    });
}

function startBackgroundPolling() {
  if (!backgroundPollingEnabled) return;
  pollingInterval = setInterval(updateBackgroundStatus, 10000); // Every 10s
  console.log("[BG_UI] 🔄 Polling for background status...");
}

function stopBackgroundPolling() {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = null;
  console.log("[BG_UI] 🛑 Stopped background polling.");
}

// Manually call this from UI if needed
updateBackgroundStatus();

// Disabled by default
// startBackgroundPolling();
