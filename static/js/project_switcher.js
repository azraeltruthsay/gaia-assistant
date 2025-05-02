// project_switcher.js — Handles frontend project selection for GAIA

// DOM Ready
window.addEventListener("DOMContentLoaded", () => {
    const projectDropdown = document.getElementById("project-dropdown");
    if (!projectDropdown) return;

    projectDropdown.addEventListener("change", async () => {
        const selectedProject = projectDropdown.value;
        console.log(`[GAIA] Switching to project: ${selectedProject}`);

        try {
            const response = await fetch(`/api/switch_project?name=${encodeURIComponent(selectedProject)}`, {
                method: "POST"
            });

            if (!response.ok) throw new Error("Project switch failed");
            const result = await response.json();
            if (result.success) {
                localStorage.setItem("gaia_active_project", selectedProject);
                window.location.reload();
            } else {
                alert("Failed to switch project. See logs for details.");
            }
        } catch (err) {
            console.error("[GAIA] Error switching project:", err);
            alert("Could not switch project due to a network or server error.");
        }
    });

    // Optional: auto-select from saved value
    const savedProject = localStorage.getItem("gaia_active_project");
    if (savedProject) {
        projectDropdown.value = savedProject;
    }
});
