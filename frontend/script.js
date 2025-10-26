const API =  "https://estatebot-uaak.onrender.com";

const chatBody = document.getElementById("chatBody");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function appendBot(text) {
  const d = document.createElement("div");
  d.className = "bot-message";
  d.innerText = text;
  chatBody.appendChild(d);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function appendUser(text) {
  const d = document.createElement("div");
  d.className = "user-message";
  d.innerText = text;
  chatBody.appendChild(d);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function appendProperty(p) {
  const card = document.createElement("div");
  card.className = "property-card";
  card.innerHTML = `
    <div class='property-title'>${p.title}</div>
    <div class='property-meta'>${p.location} • ${p.bhk} BHK • ${p.type}</div>
    <div class='property-price'>₹ ${Number(p.price).toLocaleString()}</div>
  `;
  chatBody.appendChild(card);
  chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendQuery(q) {
  appendUser(q);
  appendBot("Thinking...");
  try {
    const res = await fetch(API + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });
    const data = await res.json();

    // remove the "Thinking..." placeholder
    const bots = chatBody.querySelectorAll(".bot-message");
    if (bots.length) bots[bots.length - 1].remove();

    appendBot(data.message);

    if (data.mode === "search" && data.results && data.results.length > 0) {
      data.results.forEach((r) => appendProperty(r));
      setTimeout(() => {
        appendBot(
          "If you'd like, I can connect you with an agent! Please share your name, email, and phone number."
        );
      }, 800);
    }
  } catch (err) {
    console.error(err);
    appendBot("Server error. Make sure the backend is running on port 5000.");
  }
}

sendBtn.addEventListener("click", () => {
  const q = userInput.value.trim();
  if (!q) return;
  sendQuery(q);
  userInput.value = "";
});

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});
