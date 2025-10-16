const apiBase = "http://0.0.0.0:8000";

let sessionId = null;
let topicSet = false;

// Elements
const setBtn = document.getElementById("setParams");
const startBtn = document.getElementById("startInterview");
const sendBtn = document.getElementById("sendResponse");

const topicSection = document.getElementById("topicSection");
const nameSection = document.getElementById("nameSection");
const chatSection = document.getElementById("chatSection");

const topicInput = document.getElementById("topic");
const descInput = document.getElementById("description");
const nameInput = document.getElementById("candidateName");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

// Disable buttons initially
startBtn.disabled = true;
sendBtn.disabled = true;

function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function alertPopup(msg) {
  alert(msg);
}

// === STEP 1: Topic Phase ===
setBtn.addEventListener("click", async () => {
  const topic = topicInput.value.trim();
  const description = descInput.value.trim();

  if (!topic) return alertPopup("⚠️ Please enter an interview topic first.");

  try {
    const res = await fetch(`${apiBase}/set_params`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interview_topic: topic,
        description: description || ""
      })
    });

    const data = await res.json();

    if (data.message) {
      topicSet = true;
      alertPopup("✅ Topic set successfully!");
      topicSection.style.display = "none";
      nameSection.style.display = "block"; // Reveal Step 2
      startBtn.disabled = false;           // Enable start interview
    }
  } catch (err) {
    console.error(err);
    alertPopup("❌ Failed to set topic. Please try again.");
  }
});

// === STEP 2: Name Phase ===
startBtn.addEventListener("click", async () => {
  const name = nameInput.value.trim();
  if (!topicSet) return alertPopup("⚠️ Set a topic first!");
  if (!name) return alertPopup("⚠️ Enter your name!");

  try {
    const res = await fetch(`${apiBase}/interview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });

    const data = await res.json();
    sessionId = data.session_id;
    appendMessage("interviewer", data.message);

    nameSection.style.display = "none";
    chatSection.style.display = "block"; // Reveal Step 3
    sendBtn.disabled = false;             // Enable chat
  } catch (err) {
    console.error(err);
    alertPopup("❌ Could not start interview.");
  }
});

// === STEP 3: Chat Phase ===
sendBtn.addEventListener("click", async () => {
  const input = userInput.value.trim();
  if (!input) return;

  appendMessage("user", input);
  userInput.value = "";

  try {
    const res = await fetch(`${apiBase}/response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, user_input: input })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value);
      chatBox.lastChild?.remove(); // remove last partial
      appendMessage("interviewer", buffer);
    }
  } catch (err) {
    console.error(err);
    appendMessage("interviewer", "⚠️ Response failed. Try again.");
  }
});
