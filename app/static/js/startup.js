// startup.js
// Handles initial GAIA boot status checks and system alerts

// === Logger ===
function logStartup(msg, level = "info") {
  const prefix = "[GAIA_STARTUP]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 🚀 ${msg}`);
  }
}

// === Status Helpers ===
function updateStartupStatus(message, level = "info") {
  logStartup(message, level);
  const box = document.getElementById("status-box");
  if (box) {
    box.textContent = message;
    box.style.display = "block";
  } else {
    logStartup("Missing #status-box element", "warn");
  }
}

// === Check API Readiness ===
async function checkAppStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.initialized) {
      updateStartupStatus("🧠 GAIA not yet initialized. Awaiting core identity or model boot...", "warn");
    } else {
      updateStartupStatus("✅ GAIA initialized successfully");
    }
  } catch (err) {
    updateStartupStatus(`Failed to check status: ${err}`, "error");
  }
}

// === On Load ===
document.addEventListener("DOMContentLoaded", () => {
  logStartup("Script loaded");
  checkAppStatus();
});
