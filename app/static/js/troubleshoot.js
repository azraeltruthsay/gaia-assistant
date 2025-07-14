// troubleshoot.js
// Embedded developer diagnostics panel for GAIA debug tools

// === Logger ===
function logTroubleshoot(message, level = "info") {
  const prefix = "[GAIA_DEBUG]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${message}`); break;
    case "error": console.error(`${prefix} ❌ ${message}`); break;
    default: console.log(`${prefix} 🛠️ ${message}`);
  }
}

// === Trigger endpoints ===
async function triggerSelfReflection() {
  try {
    logTroubleshoot("Triggering self-reflection...");
    const res = await fetch("/api/reflect", { method: "POST" });
    const data = await res.json();
    logTroubleshoot(`Reflection: ${data.message || "Completed."}`);
  } catch (err) {
    logTroubleshoot(`Reflection failed: ${err}`, "error");
  }
}

async function triggerCodebaseAnalysis() {
  try {
    logTroubleshoot("Triggering codebase analysis...");
    const res = await fetch("/api/analyze/codebase", { method: "POST" });
    const data = await res.json();
    logTroubleshoot(`Codebase analysis: ${data.message || "Done."}`);
  } catch (err) {
    logTroubleshoot(`Code analysis failed: ${err}`, "error");
  }
}

async function triggerVectorReembedding() {
  try {
    logTroubleshoot("Triggering re-embedding of all documents...");
    const res = await fetch("/api/embed/all", { method: "POST" });
    const data = await res.json();
    logTroubleshoot(`Embedding: ${data.message || "Completed."}`);
  } catch (err) {
    logTroubleshoot(`Embedding failed: ${err}`, "error");
  }
}

// === UI Panel ===
function createDiagnosticsPanel() {
  const panel = document.createElement("div");
  panel.id = "diagnostic-panel";
  panel.style.position = "fixed";
  panel.style.bottom = "1rem";
  panel.style.right = "1rem";
  panel.style.padding = "1rem";
  panel.style.background = "#1c1c1c";
  panel.style.border = "1px solid #444";
  panel.style.borderRadius = "8px";
  panel.style.color = "#fff";
  panel.style.zIndex = "9999";
  panel.style.display = "none";

  panel.innerHTML = `
    <strong>🧪 GAIA Diagnostics</strong><br/><br/>
    <button id="btn-reflect">Reflect</button>
    <button id="btn-analyze">Analyze Codebase</button>
    <button id="btn-embed">Re-Embed</button>
  `;

  document.body.appendChild(panel);

  document.getElementById("btn-reflect").addEventListener("click", triggerSelfReflection);
  document.getElementById("btn-analyze").addEventListener("click", triggerCodebaseAnalysis);
  document.getElementById("btn-embed").addEventListener("click", triggerVectorReembedding);
}

function createToggleButton() {
  const btn = document.createElement("button");
  btn.id = "diagnostic-toggle";
  btn.innerText = "🛠️ Diagnostics";
  btn.style.position = "fixed";
  btn.style.bottom = "1rem";
  btn.style.left = "1rem";
  btn.style.zIndex = "10000";
  btn.style.padding = "0.5rem 1rem";
  btn.style.background = "#333";
  btn.style.color = "#fff";
  btn.style.border = "none";
  btn.style.borderRadius = "6px";
  btn.style.cursor = "pointer";

  btn.addEventListener("click", () => {
    const panel = document.getElementById("diagnostic-panel");
    panel.style.display = panel.style.display === "none" ? "block" : "none";
  });

  document.body.appendChild(btn);
}

// === Load on DOM ready ===
document.addEventListener("DOMContentLoaded", () => {
  createDiagnosticsPanel();
  createToggleButton();
  logTroubleshoot("Diagnostics panel ready.");
});
