// ui.js — Tab Navigation and UI Interactions for GAIA

// Ensure DOM is ready
window.addEventListener("DOMContentLoaded", () => {
    // Sidebar navigation
    const navButtons = document.querySelectorAll(".nav-btn");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.dataset.tab;
            switchTab(targetTab);
        });
    });
});

// Global tab switcher
export function switchTab(tabName) {
    // Hide all tab sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
    });

    // Show the selected one
    const activeTab = document.getElementById(tabName);
    if (activeTab) {
        activeTab.style.display = 'block';
        activeTab.classList.add('active');
    }

    // Highlight the correct nav button
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
}
