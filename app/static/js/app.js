// app.js
// Main frontend boot script for GAIA Assistant UI

function logApp(msg, level = "info") {
  const prefix = "[GAIA_APP]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 🌐 ${msg}`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  logApp("Frontend initialized");

  // Check for core UI elements
  const chatForm = document.getElementById("chat-form");
  const statusBox = document.getElementById("status-box");

  if (!chatForm) logApp("Missing #chat-form", "warn");
  if (!statusBox) logApp("Missing #status-box", "warn");

  // Optionally: display version, load runtime config
  const version = "v1.0"; // Can be injected from backend
  logApp(`GAIA Web UI ready — ${version}`);
});
