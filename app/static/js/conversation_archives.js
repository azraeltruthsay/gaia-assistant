// conversation_archives.js
// UI logic for loading, displaying, filtering, and managing archived conversations

const archiveList = document.getElementById("archive-list");
const archiveFilter = document.getElementById("archive-filter");
const archiveReloadBtn = document.getElementById("archive-reload");

// === Logger ===
function logArchive(message, level = "info") {
  const prefix = "[ARCHIVE_UI]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${message}`); break;
    case "error": console.error(`${prefix} ❌ ${message}`); break;
    default: console.log(`${prefix} 🗂️ ${message}`);
  }
}

// === Initialization ===
document.addEventListener("DOMContentLoaded", () => {
  if (archiveReloadBtn) archiveReloadBtn.addEventListener("click", loadArchives);
  if (archiveFilter) archiveFilter.addEventListener("input", filterArchives);
  loadArchives();
});

// === Fetch and display archives ===
async function loadArchives() {
  logArchive("Fetching archived conversations...");
  if (!archiveList) {
    logArchive("archive-list element missing", "error");
    return;
  }

  try {
    const res = await fetch("/api/conversations/archived");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderArchiveList(data.archives);
  } catch (err) {
    logArchive(`Failed to load archives: ${err}`, "error");
    archiveList.innerHTML = `<li class='error'>❌ Failed to load archives</li>`;
  }
}

function renderArchiveList(archives) {
  archiveList.innerHTML = "";
  if (!Array.isArray(archives) || archives.length === 0) {
    archiveList.innerHTML = "<li>No archived conversations found.</li>";
    return;
  }

  archives.forEach(archive => {
    const item = document.createElement("li");
    item.classList.add("archive-item");
    item.dataset.title = archive.title || "";
    item.textContent = `${archive.timestamp} — ${archive.title}`;
    item.addEventListener("click", () => loadArchiveDetails(archive.id));
    archiveList.appendChild(item);
  });

  logArchive(`Rendered ${archives.length} archives.`);
}

function filterArchives() {
  const query = archiveFilter.value.toLowerCase();
  const items = archiveList.querySelectorAll(".archive-item");

  items.forEach(item => {
    const title = item.dataset.title.toLowerCase();
    item.style.display = title.includes(query) ? "block" : "none";
  });

  logArchive(`Filter applied: '${query}'`);
}

async function loadArchiveDetails(id) {
  logArchive(`Loading details for archive ID ${id}`);
  try {
    const res = await fetch(`/api/conversations/archive/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    displayArchiveDetails(data);
  } catch (err) {
    logArchive(`Failed to load archive ID ${id}: ${err}`, "error");
  }
}

function displayArchiveDetails(data) {
  // Placeholder — define DOM target and rendering method
  logArchive(`Displaying archive '${data.title}'`);
  alert(`Conversation: ${data.title}\n\n${data.messages.join("\n")}`);
}
