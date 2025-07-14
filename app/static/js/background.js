// background.js
// Sends manual background task triggers (embedding, summarization, etc.)

function logBackground(msg, level = "info") {
  const prefix = "[BG_TRIGGER]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 🔄 ${msg}`);
  }
}

// === Trigger task by type ===
async function triggerBackgroundTask(type) {
  if (!type) {
    logBackground("No task type specified", "warn");
    return;
  }

  setStatus(`⏳ Starting ${type} task...`);
  const result = await apiRequest("/api/background/trigger", "POST", { type });

  if (result?.success) {
    logBackground(`${type} task started successfully`);
    setStatus(`✅ ${type} task started`);
  } else {
    logBackground(`${type} task failed`, "error");
    setStatus(`❌ ${type} task failed`);
  }
}

// === Optional usage example ===
// document.getElementById("btn-embed").addEventListener("click", () => triggerBackgroundTask("embedding"));
// document.getElementById("btn-summary").addEventListener("click", () => triggerBackgroundTask("summarization"));
