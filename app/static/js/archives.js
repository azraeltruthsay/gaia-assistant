// archives.js
// Loads and displays past GAIA conversation sessions

function logArchives(msg, level = "info") {
  const prefix = "[ARCHIVES_UI]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 📚 ${msg}`);
  }
}

// === Fetch list of archived conversations ===
async function loadArchivesList() {
  const container = document.getElementById("archive-list");
  if (!container) {
    logArchives("Missing #archive-list element", "error");
    return;
  }

  const result = await apiRequest("/api/archives/list", "GET");
  if (!result?.archives) {
    logArchives("Failed to fetch archive list", "error");
    return;
  }

  container.innerHTML = "";
  result.archives.forEach(archive => {
    const btn = document.createElement("button");
    btn.textContent = archive.title || archive.id;
    btn.className = "archive-button";
    btn.onclick = () => loadArchiveDetails(archive.id);
    container.appendChild(btn);
  });

  logArchives("Loaded archive list");
}

// === Load full archive detail ===
async function loadArchiveDetails(id) {
  const viewer = document.getElementById("archive-viewer");
  if (!viewer) {
    logArchives("Missing #archive-viewer element", "error");
    return;
  }

  const result = await apiRequest(`/api/archives/view/${id}`, "GET");
  if (!result?.content) {
    logArchives(`Failed to load archive ${id}`, "error");
    return;
  }

  viewer.textContent = result.content;
  viewer.style.display = "block";
  logArchives(`Displayed archive ${id}`);
}

// === Start on page load ===
document.addEventListener("DOMContentLoaded", () => {
  logArchives("Bootstrapping archive interface");
  loadArchivesList();
});
