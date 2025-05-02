// background_processing_ui.legacy.js — Archived minimal version

document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/background-tasks")
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("background-tasks");
            container.innerHTML = "";
            if (!data || data.length === 0) {
                container.textContent = "No background tasks found.";
                return;
            }

            data.forEach(task => {
                const taskElement = renderTask(task);
                container.appendChild(taskElement);
            });
        })
        .catch(err => {
            console.error("Failed to load background tasks:", err);
            const container = document.getElementById("background-tasks");
            container.textContent = "Failed to load background task data.";
        });
});

function renderTask(task) {
    const div = document.createElement("div");
    div.className = "task-entry";

    const title = document.createElement("h4");
    title.textContent = task.name || "Unnamed Task";
    div.appendChild(title);

    const status = document.createElement("p");
    status.textContent = "Status: " + (task.status || "Unknown");
    div.appendChild(status);

    return div;
}
