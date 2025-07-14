// project_switcher.js
// Handles switching between GAIA projects via dropdown

function logProject(msg, level = "info") {
  const prefix = "[GAIA_PROJECT]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 🔀 ${msg}`);
  }
}

// === DOM Elements ===
const dropdown = document.getElementById("project-dropdown");

async function loadProjectList() {
  if (!dropdown) {
    logProject("Dropdown element not found", "error");
    return;
  }

  const data = await apiRequest("/api/projects/list", "GET");
  if (!data || !Array.isArray(data.projects)) {
    logProject("Failed to retrieve project list", "error");
    return;
  }

  dropdown.innerHTML = ""; // Clear
  data.projects.forEach((project) => {
    const opt = document.createElement("option");
    opt.value = project;
    opt.textContent = project;
    dropdown.appendChild(opt);
  });

  logProject("Project list loaded");
}

async function switchProject(project) {
  if (!project) {
    logProject("No project selected", "warn");
    return;
  }

  const result = await apiRequest("/api/projects/switch", "POST", { project });
  if (result?.success) {
    logProject(`Switched to: ${project}`);
    setStatus(`🔁 Switched to: ${project}`);
  } else {
    logProject("Switch failed", "error");
    setStatus("⚠️ Switch failed.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadProjectList();
  if (dropdown) {
    dropdown.addEventListener("change", (e) => {
      const selected = e.target.value;
      switchProject(selected);
    });
  }
});
