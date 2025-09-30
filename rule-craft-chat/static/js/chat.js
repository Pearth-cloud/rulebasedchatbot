// static/js/chat.js
document.addEventListener("DOMContentLoaded", () => {
  const messagesEl = document.getElementById("messages");
  const inputEl = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");
  const themeToggle = document.getElementById("themeToggle");

  // Add a welcome message
  addBotMessage("Hello! I'm RuleCraft — a rule-based assistant. Try: 'weather in Delhi', 'tell me a joke', 'what is AI'.");

  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  themeToggle.addEventListener("click", () => {
    document.documentElement.classList.toggle("light");
  });

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    addUserMessage(text);
    inputEl.value = "";
    // show typing indicator
    const typingId = addBotTyping();

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      removeElementById(typingId);
      // small delay to feel natural
      await sleep(350 + Math.random() * 250);
      addBotMessage(data.reply || "No response.");
    } catch (err) {
      removeElementById(typingId);
      addBotMessage("Error contacting server. Try again later.");
      console.error(err);
    }
  }

  function addUserMessage(text) {
    const div = document.createElement("div");
    div.className = "msg user";
    div.innerHTML = `<div>${escapeHtml(text)}</div><div class="meta">You • ${timeNow()}</div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addBotMessage(text) {
    const div = document.createElement("div");
    div.className = "msg bot";
    div.innerHTML = `<div>${escapeHtml(text)}</div><div class="meta">RuleCraft • ${timeNow()}</div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addBotTyping() {
    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "msg bot";
    div.innerHTML = `<div>RuleCraft is typing<span class="dots">...</span></div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return id;
  }

  function removeElementById(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function timeNow() {
    const d = new Date();
    return d.toLocaleTimeString();
  }

  function sleep(ms) {
    return new Promise((res) => setTimeout(res, ms));
  }

  // simple HTML escape
  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
