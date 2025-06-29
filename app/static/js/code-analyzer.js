// code-analyzer.js
// Triggers frontend-initiated codebase and function-level analysis via GAIA

function logAnalyzer(msg, level = "info") {
  const prefix = "[ANALYZER_UI]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 🔍 ${msg}`);
  }
}

// === Codebase Analysis ===
async function triggerCodeAnalysis() {
  logAnalyzer("Requesting full codebase analysis...");
  setStatus("🧠 Analyzing full codebase...");

  const result = await apiRequest("/api/analyze/codebase", "POST");

  if (result?.message) {
    logAnalyzer(`Codebase analysis complete: ${result.message}`);
    setStatus(`✅ ${result.message}`);
    displayCodeSummary(result.summary || "Full analysis complete.");
  } else {
    logAnalyzer("Code analysis failed", "error");
    setStatus("⚠️ Code analysis failed.");
  }
}

function displayCodeSummary(text) {
  const panel = document.getElementById("code-summary");
  if (!panel) {
    logAnalyzer("No #code-summary element found", "warn");
    return;
  }

  panel.textContent = text;
  panel.style.display = "block";
}

// === Function Analysis ===
async function triggerFunctionAnalysis() {
  logAnalyzer("Requesting function-level analysis...");
  setStatus("📘 Extracting function metadata...");

  const result = await apiRequest("/api/analyze/functions", "POST");

  if (result?.message) {
    logAnalyzer(`Function summary complete: ${result.message}`);
    setStatus(`✅ ${result.message}`);
    displayFunctionSummary(result.summary || "Function metadata extracted.");
  } else {
    logAnalyzer("Function analysis failed", "error");
    setStatus("⚠️ Function extraction failed.");
  }
}

function displayFunctionSummary(text) {
  const panel = document.getElementById("function-summary");
  if (!panel) {
    logAnalyzer("No #function-summary element found", "warn");
    return;
  }

  panel.textContent = text;
  panel.style.display = "block";
}

// === Event Binding ===
document.addEventListener("DOMContentLoaded", () => {
  const btnCode = document.getElementById("btn-analyze-code");
  const btnFunc = document.getElementById("btn-analyze-functions");

  if (btnCode) {
    btnCode.addEventListener("click", triggerCodeAnalysis);
    logAnalyzer("Bound: #btn-analyze-code");
  } else {
    logAnalyzer("Missing #btn-analyze-code", "warn");
  }

  if (btnFunc) {
    btnFunc.addEventListener("click", triggerFunctionAnalysis);
    logAnalyzer("Bound: #btn-analyze-functions");
  } else {
    logAnalyzer("Missing #btn-analyze-functions", "warn");
  }
});
