// GAIA UI Logic (merged)

// Smooth tab switching and initial state handling
document.addEventListener("DOMContentLoaded", function () {
  const tabButtons = document.querySelectorAll(".doc-tab-btn");
  const tabContents = document.querySelectorAll(".document-list");

  function switchTab(targetId) {
    tabButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.tab === targetId);
    });

    tabContents.forEach((content) => {
      content.classList.toggle("active", content.id === targetId);
    });
  }

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.tab;
      switchTab(targetId);
    });
  });

  // Ensure at least one tab is active on load
  const defaultTab = document.querySelector(".doc-tab-btn.active")?.dataset.tab || tabButtons[0]?.dataset.tab;
  if (defaultTab) {
    switchTab(defaultTab);
  }

  // Show tab content when using sidebar nav links (optional hook)
  window.changeDocTab = switchTab;
});

// Project dropdown toggle
const dropdownBtn = document.querySelector(".project-dropdown-btn");
const dropdownContent = document.querySelector(".project-dropdown-content");

if (dropdownBtn && dropdownContent) {
  dropdownBtn.addEventListener("click", function () {
    dropdownContent.classList.toggle("show");
  });

  window.addEventListener("click", function (e) {
    if (!dropdownBtn.contains(e.target) && !dropdownContent.contains(e.target)) {
      dropdownContent.classList.remove("show");
    }
  });
}

// Toast fade-out
function dismissToast(toastElement) {
  toastElement.classList.add("toast-out");
  setTimeout(() => toastElement.remove(), 300);
}

// Optional global close hook
window.dismissToast = dismissToast;
