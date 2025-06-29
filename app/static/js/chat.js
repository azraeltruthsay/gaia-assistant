// chat.js (cleaned up version)

// Handle user input and send it to the backend
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatLog = document.getElementById("chat-log");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  appendMessage("user", userMessage);
  chatInput.value = "";
  chatInput.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    });

    const data = await response.json();
    const gaiaReply = data.response || "[No response from GAIA]";

    appendMessage("gaia", gaiaReply);
    console.log("GAIA responded:", gaiaReply);
  } catch (err) {
    appendMessage("error", "Failed to fetch GAIA response.");
    console.error("[CHAT ERROR]", err);
  } finally {
    chatInput.disabled = false;
    chatInput.focus();
  }
});

function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);

  if (sender === "gaia") {
    msg.innerHTML = `<strong>GAIA:</strong> ${sanitizeHTML(text)}`;
  } else if (sender === "user") {
    msg.innerHTML = `<strong>You:</strong> ${sanitizeHTML(text)}`;
  } else {
    msg.classList.add("error");
    msg.textContent = text;
  }

  chatLog.appendChild(msg);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function sanitizeHTML(html) {
  const div = document.createElement("div");
  div.textContent = html;
  return div.innerHTML;
} // prevents rogue HTML or script injection
