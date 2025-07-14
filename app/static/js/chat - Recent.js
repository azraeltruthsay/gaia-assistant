// chat.js
// Handles chat interaction between user and GAIA

function logChat(msg, level = "info") {
  const prefix = "[CHAT_UI]";
  switch (level) {
    case "warn": console.warn(`${prefix} ⚠️ ${msg}`); break;
    case "error": console.error(`${prefix} ❌ ${msg}`); break;
    default: console.log(`${prefix} 💬 ${msg}`);
  }
}

function setStatus(statusText) {
  const statusElement = document.getElementById("status");
  if (statusElement) {
    statusElement.innerText = statusText;
    statusElement.style.display = statusText ? "block" : "none";
  }
}

// === DOM Elements ===
const chatInput = document.getElementById("chat-input");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");


// === Event Handling ===
if (chatForm && chatInput && chatLog) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    appendMessage("user", query);
    chatInput.value = "";

    setStatus("⏳ Thinking...");
	const response = await apiRequest("/api/chat", "POST", { query });

    if (response?.response) {
      appendMessage("gaia", response.response);
      logChat("Response received");
    } else {
      appendMessage("gaia", "⚠️ No response received.");
      logChat("Empty or failed response", "warn");
    }
    setStatus(""); // Clear status
  });
} else {
  logChat("Missing DOM elements: chat-form, chat-input, or chat-log", "error");
}

// === Render a message ===
function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.innerHTML = `<strong>${sender === "user" ? "You" : "GAIA"}:</strong> ${text}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}
